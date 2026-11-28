//! Three-player postflop API (`/api/mw/*`): build a 3-way spot, solve it on
//! the GPU when it fits (CPU otherwise), browse, save and load. Status and
//! node replies use the heads-up field names, so the Setup & Solve and
//! Browse pages read both kinds of spot the same way. One postflop spot is
//! loaded at a time: building or loading a 3-way spot drops the heads-up
//! session and the other way round (`drop_session`).

use std::{
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, LazyLock, Mutex,
    },
    time::Instant,
};

use axum::{
    extract::State,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use solver::{
    cfr::Algorithm,
    multiway::{
        query::{exploit_view, node_view, MwNodeView},
        tree::MwTreeConfig,
        MwSolver, MwSpot, MwSpotConfig, NP,
    },
    query::{ExploitView, PathStep},
    store::Storage,
    tree::{parse_sizes, StreetSizing},
};

use crate::{bad_request, lock_unpoisoned, panic_msg, ApiError, AppState};

/// Largest tree the builder will attempt (nodes).
const MAX_NODES: usize = 150_000_000;
const SAVE_DIR: &str = "saves/3way";

#[derive(Default)]
struct MwState {
    session: Mutex<Option<MwSession>>,
    status: Arc<Mutex<MwStatus>>,
}

struct MwSession {
    solver: Arc<Mutex<MwSolver>>,
    stop: Arc<AtomicBool>,
    /// Set when the session is being replaced: a solve stopped for that
    /// skips its last accuracy check, which nobody would read.
    discard: Arc<AtomicBool>,
    worker: Option<std::thread::JoinHandle<()>>,
}

static MW: LazyLock<MwState> = LazyLock::new(MwState::default);

/// Handlers waiting on the solver. The CPU solve holds the solver for a
/// whole iteration and takes it again at once, and std's mutex is not fair,
/// so a Browse request made during a solve would wait until the solve ends.
/// Handlers lock through `handler_lock`; the solve gives way to them between
/// iterations.
static WAITERS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

fn handler_lock(m: &Mutex<MwSolver>) -> std::sync::MutexGuard<'_, MwSolver> {
    WAITERS.fetch_add(1, Ordering::SeqCst);
    let g = lock_unpoisoned(m);
    WAITERS.fetch_sub(1, Ordering::SeqCst);
    g
}

/// Solve side: with the solver unlocked, let waiting handlers take it
/// (bounded, so a handler that never wakes cannot stall the solve).
fn yield_to_waiters() {
    for _ in 0..200 {
        if WAITERS.load(Ordering::SeqCst) == 0 {
            return;
        }
        std::thread::sleep(std::time::Duration::from_millis(1));
    }
}

#[derive(Clone, Serialize, Default)]
pub struct MwTreeInfo {
    pub board: String,
    pub nodes: usize,
    pub action_nodes: usize,
    pub entries: u64,
    pub hands: [usize; NP],
    /// Solver memory (MB) as stored (compressed), the heads-up field name.
    pub arena_mb: f64,
    pub arena_mb_f32: f64,
    /// Estimated GPU memory for a fully resident f32 solve (`vram_mb`, the
    /// heads-up field name), and the least the GPU solver can work with
    /// (16-bit arenas, subtrees swept in groups). 0 without CUDA.
    pub vram_mb: f64,
    pub gpu_min_mb: f64,
    /// GPU memory free for a solve (MB) and whether a GPU can be used.
    pub gpu_cap_mb: u64,
    pub gpu_available: bool,
    pub build_secs: f64,
}

#[derive(Clone, Serialize)]
pub struct MwHistoryPoint {
    pub iteration: u32,
    pub exploit_pct: f64,
    pub elapsed_secs: f64,
}

#[derive(Clone, Serialize, Default)]
pub struct MwStatus {
    /// idle | building | ready | running | done | stopped | error
    pub state: String,
    pub iteration: u32,
    pub exploit_pct: f64,
    pub gaps: [f64; NP],
    pub evs: [f64; NP],
    pub elapsed_secs: f64,
    pub iters_per_sec: f64,
    /// True while the current/last solve ran on the GPU, and the memory it
    /// took there (MB).
    pub gpu: bool,
    pub gpu_used_mb: f64,
    /// Why a solve that could have used the GPU is on the CPU.
    pub gpu_note: String,
    pub error: String,
    pub history: Vec<MwHistoryPoint>,
    pub tree: Option<MwTreeInfo>,
    /// The spot as built (or as rebuilt from a save), so the page can fill
    /// the form in.
    pub spot_request: Option<MwSpotRequest>,
}

pub fn routes() -> Router<Arc<AppState>> {
    Router::new()
        .route("/api/mw/spot", post(build))
        .route("/api/mw/solve", post(solve))
        .route("/api/mw/stop", post(stop))
        .route("/api/mw/status", get(status))
        .route("/api/mw/node", post(node))
        .route("/api/mw/exploit", post(exploit))
        .route("/api/mw/save", post(save))
        .route("/api/mw/load", post(load))
        .route("/api/mw/saves", get(list_saves))
}

#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct SizeRow {
    bet: String,
    raise: String,
}

#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MwSpotRequest {
    board: String,
    /// Ranges in postflop action order (first to act first).
    ranges: [String; NP],
    starting_pot: f64,
    stacks: [f64; NP],
    /// Flop, turn and river sizes (rows for streets before the board's are
    /// ignored), shared by all three players.
    sizes: Vec<SizeRow>,
    #[serde(default)]
    rake_pct: f64,
    #[serde(default)]
    rake_cap: f64,
    #[serde(default)]
    max_raises: Option<u8>,
    #[serde(default)]
    allin_threshold: Option<f64>,
    #[serde(default)]
    add_allin: bool,
    /// Tournament payouts: terminals pay ICM prize-equity changes.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    icm: Option<solver::icm::postflop::PostflopIcm>,
    /// The players' seat names in action order (labels only; kept in saves).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    seats: Option<[String; NP]>,
}

/// The request that rebuilds `config` (a loaded save fills the form from it).
fn spot_request_from_config(config: &MwSpotConfig) -> MwSpotRequest {
    let t = &config.tree;
    MwSpotRequest {
        board: config.board.clone(),
        ranges: config.ranges.clone(),
        starting_pot: t.starting_pot,
        stacks: t.stacks,
        sizes: t.sizing[0]
            .iter()
            .map(|x| SizeRow {
                bet: crate::sizes_to_string(&x.bet),
                raise: crate::sizes_to_string(&x.raise),
            })
            .collect(),
        rake_pct: t.rake_pct * 100.0,
        rake_cap: t.rake_cap,
        max_raises: Some(t.max_raises),
        allin_threshold: Some(t.allin_threshold * 100.0),
        add_allin: t.add_allin,
        icm: t.icm.clone(),
        seats: config.seats.clone(),
    }
}

fn spot_config(req: &MwSpotRequest) -> Result<MwSpotConfig, String> {
    // a NaN pot or stack is not positive and must not slip through
    if req.starting_pot.is_nan()
        || req.starting_pot <= 0.0
        || req.stacks.iter().any(|&s| s.is_nan() || s <= 0.0)
    {
        return Err("pot and stacks must be positive".into());
    }
    if !(0.0..=100.0).contains(&req.rake_pct) {
        return Err("rake % must be between 0 and 100".into());
    }
    let mut streets: [StreetSizing; 3] = Default::default();
    for (i, row) in req.sizes.iter().take(3).enumerate() {
        streets[i] = StreetSizing {
            bet: parse_sizes(&row.bet)?,
            raise: parse_sizes(&row.raise)?,
            donk: Vec::new(),
        };
    }
    let mut t = MwTreeConfig::uniform(req.starting_pot, req.stacks[0], &[], &[]);
    t.stacks = req.stacks;
    t.rake_pct = req.rake_pct / 100.0;
    t.rake_cap = req.rake_cap;
    t.sizing = std::array::from_fn(|_| streets.clone());
    if let Some(m) = req.max_raises {
        t.max_raises = m;
    }
    if let Some(a) = req.allin_threshold {
        if !(a > 0.0 && a <= 100.0) {
            return Err("all-in threshold must be in (0, 100]".into());
        }
        t.allin_threshold = a / 100.0;
    }
    t.add_allin = req.add_allin;
    t.icm = req.icm.clone();
    let seats = req
        .seats
        .as_ref()
        .map(|s| s.clone().map(|x| x.trim().chars().take(12).collect()));
    Ok(MwSpotConfig {
        board: req.board.clone(),
        ranges: req.ranges.clone(),
        tree: t,
        seats,
    })
}

fn tree_info(spot: &MwSpot, build_secs: f64) -> MwTreeInfo {
    #[cfg(feature = "gpu")]
    let (gpu_mb, gpu_min_mb) = {
        let (full, min) = solver::multiway::gpu::estimate_device_bytes(spot, Algorithm::Dcfr);
        (full as f64 / 1e6, min as f64 / 1e6)
    };
    #[cfg(not(feature = "gpu"))]
    let (gpu_mb, gpu_min_mb) = (0.0, 0.0);
    let (gpu_cap_mb, gpu_available) = crate::gpu_budget();
    MwTreeInfo {
        board: spot.config.board.clone(),
        nodes: spot.tree.nodes.len(),
        action_nodes: spot.num_action_nodes(),
        entries: spot.tree.data_size.iter().sum(),
        hands: std::array::from_fn(|k| spot.hands[k].len()),
        arena_mb: spot.arena_bytes(Storage::Compressed) as f64 / 1e6,
        arena_mb_f32: spot.arena_bytes(Storage::F32) as f64 / 1e6,
        vram_mb: gpu_mb,
        gpu_min_mb,
        gpu_cap_mb,
        gpu_available,
        build_secs,
    }
}

fn ram_cap_mb() -> f64 {
    if let Some(v) = std::env::var("SOLVER_MEM_MB")
        .ok()
        .and_then(|v| v.parse::<f64>().ok())
    {
        return v;
    }
    solver::sysmem::avail_mem_mb()
        .map(|a| a * 0.8)
        .unwrap_or(48_000.0)
}

/// Solver memory (MB) of the loaded 3-way spot, credited back to the RAM
/// cap while its replacement is checked (it is freed before the new arenas
/// are allocated). A manual SOLVER_MEM_MB cap gets no credit.
pub(crate) fn arena_credit_mb() -> f64 {
    if std::env::var("SOLVER_MEM_MB").is_ok() {
        return 0.0;
    }
    0.8 * lock_unpoisoned(&MW.status)
        .tree
        .as_ref()
        .map(|t| t.arena_mb)
        .unwrap_or(0.0)
}

/// Stops and joins the solve worker, if one is running. The session stays.
fn stop_worker(discard: bool) {
    let worker = {
        let mut g = lock_unpoisoned(&MW.session);
        g.as_mut().and_then(|s| {
            if discard {
                s.discard.store(true, Ordering::Relaxed);
            }
            s.stop.store(true, Ordering::Relaxed);
            s.worker.take()
        })
    };
    if let Some(w) = worker {
        let _ = w.join();
    }
}

/// Stops any running 3-way solve and unloads the 3-way spot. Called when a
/// heads-up spot is built or loaded (one postflop spot at a time), and
/// before a new 3-way spot is installed.
pub(crate) fn drop_session() {
    stop_worker(true);
    *lock_unpoisoned(&MW.session) = None;
    *lock_unpoisoned(&MW.status) = MwStatus::default();
}

/// `request` is the spot as the page sent it (echoed back word for word, so
/// the page can tell its form still describes the tree); a loaded save has
/// none and gets one rebuilt from its config.
fn install(solver: MwSolver, info: MwTreeInfo, state: &str, request: Option<MwSpotRequest>) {
    let spot_request = request.unwrap_or_else(|| spot_request_from_config(&solver.spot.config));
    *lock_unpoisoned(&MW.session) = Some(MwSession {
        solver: Arc::new(Mutex::new(solver)),
        stop: Arc::new(AtomicBool::new(false)),
        discard: Arc::new(AtomicBool::new(false)),
        worker: None,
    });
    let mut st = lock_unpoisoned(&MW.status);
    *st = MwStatus {
        state: state.into(),
        tree: Some(info),
        spot_request: Some(spot_request),
        ..Default::default()
    };
}

/// Unloads whatever postflop spot is loaded, heads-up or 3-way.
async fn drop_all(app: &Arc<AppState>) -> Result<(), ApiError> {
    let app = app.clone();
    tokio::task::spawn_blocking(move || {
        crate::stop_current(&app, true);
        drop_session();
    })
    .await
    .map_err(|e| bad_request(e.to_string()))
}

async fn build(
    State(app): State<Arc<AppState>>,
    Json(req): Json<MwSpotRequest>,
) -> Result<Json<MwTreeInfo>, ApiError> {
    let cfg = spot_config(&req).map_err(bad_request)?;
    // Validate, then swap: the new spot is built and sized before the loaded
    // one is touched, so a refused build leaves an unsaved solve intact.
    let (spot, secs) = tokio::task::spawn_blocking(move || -> Result<(MwSpot, f64), String> {
        let t0 = Instant::now();
        let spot = MwSpot::new_with_limit(cfg, Some(MAX_NODES))?;
        Ok((spot, t0.elapsed().as_secs_f64()))
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    let info = tree_info(&spot, secs);
    let cap = ram_cap_mb() + arena_credit_mb() + crate::old_arena_credit_mb(&app);
    if info.arena_mb > cap {
        return Err(bad_request(format!(
            "this tree needs {:.0} MB of solver memory, over the RAM cap of {cap:.0} MB; \
             use fewer bet sizes or a later street",
            info.arena_mb
        )));
    }
    drop_all(&app).await?;
    let solver =
        tokio::task::spawn_blocking(move || MwSolver::new(Arc::new(spot), Storage::Compressed))
            .await
            .map_err(|e| bad_request(e.to_string()))?;
    install(solver, info.clone(), "ready", Some(req));
    Ok(Json(info))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct SolveRequest {
    #[serde(default = "default_iters")]
    max_iterations: u32,
    #[serde(default = "default_target")]
    target_exploit_pct: f64,
    #[serde(default = "default_check")]
    check_every: u32,
    /// auto | gpu | cpu
    #[serde(default)]
    engine: Option<String>,
    #[serde(default)]
    algorithm: Option<String>,
}
fn default_iters() -> u32 {
    1000
}
fn default_target() -> f64 {
    0.3
}
fn default_check() -> u32 {
    10
}

async fn solve(Json(req): Json<SolveRequest>) -> Result<Json<serde_json::Value>, ApiError> {
    let mut g = lock_unpoisoned(&MW.session);
    let sess = g
        .as_mut()
        .ok_or_else(|| bad_request("no 3-way spot built yet"))?;
    if lock_unpoisoned(&MW.status).state == "running" {
        return Err((StatusCode::CONFLICT, "already running".into()));
    }
    if let Some(w) = sess.worker.take() {
        let _ = w.join();
    }
    if let Some(a) = &req.algorithm {
        lock_unpoisoned(&sess.solver).algo = Algorithm::parse(a).map_err(bad_request)?;
    }
    let engine = req.engine.clone().unwrap_or_else(|| "auto".into());
    if !matches!(engine.as_str(), "auto" | "gpu" | "cpu") {
        return Err(bad_request("engine must be auto, gpu or cpu"));
    }
    sess.stop.store(false, Ordering::Relaxed);
    {
        let mut st = lock_unpoisoned(&MW.status);
        st.state = "running".into();
        st.error.clear();
        st.gpu_note.clear();
        st.gpu = false;
        st.gpu_used_mb = 0.0;
        st.history.clear();
    }
    let solver = sess.solver.clone();
    let stop = sess.stop.clone();
    let discard = sess.discard.clone();
    let status = MW.status.clone();
    sess.worker = Some(std::thread::spawn(move || {
        let st2 = status.clone();
        let r = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            run(solver, stop, discard, status, req, engine)
        }));
        let mut st = lock_unpoisoned(&st2);
        match r {
            Ok(Ok(final_state)) => st.state = final_state.into(),
            Ok(Err(e)) => {
                st.state = "error".into();
                st.error = e;
            }
            Err(p) => {
                st.state = "error".into();
                st.error = format!("solver panicked: {}", panic_msg(&*p));
            }
        }
    }));
    Ok(Json(serde_json::json!({"ok": true})))
}

fn record(status: &Mutex<MwStatus>, pr: &solver::multiway::MwProgress, base_iter: u32, gpu: bool) {
    let mut st = lock_unpoisoned(status);
    st.iteration = pr.iteration;
    st.exploit_pct = pr.exploit_pct_pot;
    st.gaps = pr.gaps;
    st.evs = pr.evs;
    st.elapsed_secs = pr.elapsed_secs;
    st.iters_per_sec = if pr.elapsed_secs > 0.0 {
        (pr.iteration - base_iter) as f64 / pr.elapsed_secs
    } else {
        0.0
    };
    st.gpu = gpu;
    if st
        .history
        .last()
        .is_some_and(|h| h.iteration == pr.iteration)
    {
        st.history.pop();
    }
    st.history.push(MwHistoryPoint {
        iteration: pr.iteration,
        exploit_pct: pr.exploit_pct_pot,
        elapsed_secs: pr.elapsed_secs,
    });
}

/// Solve worker: GPU when allowed and it fits, else CPU. Returns the final
/// state name.
fn run(
    solver: Arc<Mutex<MwSolver>>,
    stop: Arc<AtomicBool>,
    discard: Arc<AtomicBool>,
    status: Arc<Mutex<MwStatus>>,
    req: SolveRequest,
    engine: String,
) -> Result<&'static str, String> {
    let check = req.check_every.max(1);
    #[cfg(feature = "gpu")]
    if engine != "cpu" {
        let gpu = {
            let mut s = lock_unpoisoned(&solver);
            s.ensure_symmetric();
            solver::multiway::gpu::MwGpuSolver::from_solver(&s)
        };
        match gpu {
            Ok(mut g) => {
                {
                    let mut st = lock_unpoisoned(&status);
                    st.gpu = true;
                    st.gpu_used_mb = g.device_bytes() as f64 / 1e6;
                }
                let base = g.iteration;
                let start = Instant::now();
                let mut last_sync = Instant::now();
                // A download costs about a second per 20 GB of arenas; keep
                // it under ~10% of the solve time.
                let mut sync_every = 3.0f64;
                let mut synced = true;
                let mut done = false;
                // An evaluation costs about two iterations; on big trees,
                // space checks so they stay under ~20% of the solve time.
                let mut eval_cost = 0.0f64;
                let mut last_check = Instant::now();
                while g.iteration < base + req.max_iterations && !stop.load(Ordering::Relaxed) {
                    g.iterate()?;
                    g.synchronize()?;
                    synced = false;
                    let k = g.iteration - base;
                    let due =
                        k % check == 0 && last_check.elapsed().as_secs_f64() >= 4.0 * eval_cost;
                    if due || k >= req.max_iterations {
                        let te = Instant::now();
                        let pr = g.progress(start.elapsed().as_secs_f64())?;
                        eval_cost = te.elapsed().as_secs_f64();
                        last_check = Instant::now();
                        record(&status, &pr, base, true);
                        done = pr.exploit_pct_pot <= req.target_exploit_pct;
                        // Keep the browsable copy fresh without paying for a
                        // download at every check.
                        if done || last_sync.elapsed().as_secs_f64() > sync_every {
                            let t = Instant::now();
                            let s = g.to_cpu()?;
                            *lock_unpoisoned(&solver) = s;
                            sync_every = sync_every.max(10.0 * t.elapsed().as_secs_f64());
                            last_sync = Instant::now();
                            synced = true;
                        }
                        if done {
                            break;
                        }
                    }
                }
                if !synced && !discard.load(Ordering::Relaxed) {
                    let pr = g.progress(start.elapsed().as_secs_f64())?;
                    record(&status, &pr, base, true);
                    *lock_unpoisoned(&solver) = g.to_cpu()?;
                }
                return Ok(if done {
                    "done"
                } else if stop.load(Ordering::Relaxed) {
                    "stopped"
                } else {
                    "done"
                });
            }
            Err(e) if engine == "gpu" => return Err(format!("GPU solve unavailable: {e}")),
            Err(e) => {
                lock_unpoisoned(&status).gpu_note =
                    format!("on the CPU, the GPU could not take it ({e})")
            }
        }
    }
    #[cfg(not(feature = "gpu"))]
    if engine == "gpu" {
        return Err("this copy of GTOpen cannot use a GPU: set Solve on to Auto or CPU".into());
    }
    let base = lock_unpoisoned(&solver).iteration;
    let start = Instant::now();
    let mut done = false;
    let mut checked = base;
    loop {
        if stop.load(Ordering::Relaxed) {
            break;
        }
        yield_to_waiters();
        let mut s = lock_unpoisoned(&solver);
        if s.iteration >= base + req.max_iterations {
            break;
        }
        s.iterate();
        let k = s.iteration - base;
        if k.is_multiple_of(check) || k >= req.max_iterations {
            let pr = s.progress(start.elapsed().as_secs_f64());
            checked = s.iteration;
            drop(s);
            record(&status, &pr, base, false);
            if pr.exploit_pct_pot <= req.target_exploit_pct {
                done = true;
                break;
            }
        }
    }
    // A stopped solve measures its accuracy once more, so the figure shown
    // belongs to the strategies it leaves (skipped when the spot is being
    // replaced).
    if !discard.load(Ordering::Relaxed) {
        let s = lock_unpoisoned(&solver);
        if s.iteration > checked {
            let pr = s.progress(start.elapsed().as_secs_f64());
            drop(s);
            record(&status, &pr, base, false);
        }
    }
    Ok(if done || !stop.load(Ordering::Relaxed) {
        "done"
    } else {
        "stopped"
    })
}

/// Returns when the solve has ended (after its last accuracy check).
async fn stop() -> Json<serde_json::Value> {
    tokio::task::spawn_blocking(|| stop_worker(false))
        .await
        .ok();
    Json(serde_json::json!({"ok": true}))
}

async fn status() -> Json<MwStatus> {
    let mut st = lock_unpoisoned(&MW.status).clone();
    if st.state.is_empty() {
        st.state = "idle".into();
    }
    Json(st)
}

fn session_solver() -> Result<Arc<Mutex<MwSolver>>, ApiError> {
    lock_unpoisoned(&MW.session)
        .as_ref()
        .map(|s| s.solver.clone())
        .ok_or_else(|| bad_request("no 3-way spot built yet"))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct NodeRequest {
    path: Vec<PathStep>,
}

async fn node(Json(req): Json<NodeRequest>) -> Result<Json<MwNodeView>, ApiError> {
    let solver = session_solver()?;
    let v = tokio::task::spawn_blocking(move || {
        let mut s = handler_lock(&solver);
        s.ensure_symmetric();
        node_view(&s, &req.path)
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    Ok(Json(v))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ExploitRequest {
    path: Vec<PathStep>,
    exploiter: usize,
}

async fn exploit(Json(req): Json<ExploitRequest>) -> Result<Json<ExploitView>, ApiError> {
    let solver = session_solver()?;
    let v = tokio::task::spawn_blocking(move || {
        let mut s = handler_lock(&solver);
        s.ensure_symmetric();
        exploit_view(&s, &req.path, req.exploiter)
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    Ok(Json(v))
}

fn save_path(name: &str) -> Result<std::path::PathBuf, String> {
    let clean: String = name
        .trim()
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || matches!(c, ' ' | '-' | '_' | '.') {
                c
            } else {
                '-'
            }
        })
        .collect();
    let clean = clean.trim_matches('.').trim().to_string();
    if clean.is_empty() {
        return Err("save name is empty".into());
    }
    Ok(std::path::Path::new(SAVE_DIR).join(format!("{clean}.gtomw")))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct NameRequest {
    name: String,
}

async fn save(Json(req): Json<NameRequest>) -> Result<Json<serde_json::Value>, ApiError> {
    let solver = session_solver()?;
    let path = save_path(&req.name).map_err(bad_request)?;
    let exploit = {
        let st = lock_unpoisoned(&MW.status);
        (st.iteration > 0).then_some(st.exploit_pct)
    };
    let out = path.clone();
    tokio::task::spawn_blocking(move || -> Result<(), String> {
        std::fs::create_dir_all(SAVE_DIR).map_err(|e| e.to_string())?;
        let mut s = handler_lock(&solver);
        s.ensure_symmetric();
        let tmp = path.with_extension("tmp");
        let f = std::fs::File::create(&tmp).map_err(|e| e.to_string())?;
        solver::multiway::save::save(&s, exploit, f)?;
        std::fs::rename(&tmp, &path).map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    Ok(Json(
        serde_json::json!({"ok": true, "path": out.to_string_lossy()}),
    ))
}

async fn load(
    State(app): State<Arc<AppState>>,
    Json(req): Json<NameRequest>,
) -> Result<Json<MwStatus>, ApiError> {
    let path = save_path(&req.name).map_err(bad_request)?;
    // Vet the file before the loaded spot is dropped for it.
    let probe = path.clone();
    tokio::task::spawn_blocking(move || {
        let f = std::fs::File::open(&probe).map_err(|e| format!("{}: {e}", probe.display()))?;
        solver::multiway::save::peek(f).map(|_| ())
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    drop_all(&app).await?;
    let (s, hdr, secs) = tokio::task::spawn_blocking(move || {
        let t0 = Instant::now();
        let f = std::fs::File::open(&path).map_err(|e| format!("{}: {e}", path.display()))?;
        let (s, hdr) = solver::multiway::save::load(f, Storage::Compressed)?;
        Ok::<_, String>((s, hdr, t0.elapsed().as_secs_f64()))
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    let info = tree_info(&s.spot, secs);
    let iteration = s.iteration;
    install(s, info, "done", None);
    let mut st = lock_unpoisoned(&MW.status);
    st.iteration = iteration;
    st.exploit_pct = hdr.exploit_pct_pot.unwrap_or(0.0);
    if let Some(e) = hdr.exploit_pct_pot {
        st.history.push(MwHistoryPoint {
            iteration,
            exploit_pct: e,
            elapsed_secs: 0.0,
        });
    }
    Ok(Json(st.clone()))
}

#[derive(Serialize)]
struct SaveEntry {
    name: String,
    board: String,
    iteration: u32,
    exploit_pct: Option<f64>,
}

async fn list_saves() -> Json<Vec<SaveEntry>> {
    let mut out = Vec::new();
    if let Ok(rd) = std::fs::read_dir(SAVE_DIR) {
        for e in rd.flatten() {
            let p = e.path();
            if p.extension().and_then(|x| x.to_str()) != Some("gtomw") {
                continue;
            }
            let Ok(f) = std::fs::File::open(&p) else {
                continue;
            };
            if let Ok(h) = solver::multiway::save::peek(f) {
                out.push(SaveEntry {
                    name: p
                        .file_stem()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .into_owned(),
                    board: h.config.board,
                    iteration: h.iteration,
                    exploit_pct: h.exploit_pct_pot,
                });
            }
        }
    }
    out.sort_by(|a, b| a.name.cmp(&b.name));
    Json(out)
}
