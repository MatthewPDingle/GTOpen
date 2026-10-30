//! Three-player postflop API (`/api/mw/*`): build a 3-way spot, solve it on
//! the GPU when it fits (CPU otherwise), browse, save and load. Independent
//! of the heads-up session so both can live side by side.

use crate::{bad_request, lock_unpoisoned, panic_msg, ApiError};
use axum::http::StatusCode;
use axum::routing::{get, post};
use axum::{Json, Router};
use serde::{Deserialize, Serialize};
use solver::cfr::Algorithm;
use solver::multiway::query::{node_view, MwNodeView, MwStep};
use solver::multiway::tree::MwTreeConfig;
use solver::multiway::{MwSolver, MwSpot, MwSpotConfig, NP};
use solver::store::Storage;
use solver::tree::{parse_sizes, StreetSizing};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, LazyLock, Mutex};
use std::time::Instant;

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
    worker: Option<std::thread::JoinHandle<()>>,
}

static MW: LazyLock<MwState> = LazyLock::new(MwState::default);

#[derive(Clone, Serialize, Default)]
pub struct MwTreeInfo {
    pub board: String,
    pub nodes: usize,
    pub action_nodes: usize,
    pub entries: u64,
    pub hands: [usize; NP],
    pub arena_mb_f32: f64,
    pub arena_mb_compressed: f64,
    /// Estimated GPU memory for a fully resident f32 solve, and the least
    /// the GPU solver can work with (16-bit arenas, subtrees swept in
    /// groups). 0 without CUDA.
    pub gpu_mb: f64,
    pub gpu_min_mb: f64,
    pub build_secs: f64,
}

#[derive(Clone, Serialize, Default)]
pub struct MwStatus {
    /// idle | building | ready | running | done | stopped | error
    pub state: String,
    pub iteration: u32,
    pub exploit_pct: f64,
    pub gaps: [f64; NP],
    pub evs: [f64; NP],
    pub elapsed: f64,
    pub iters_per_sec: f64,
    pub engine: String,
    pub note: String,
    pub error: String,
    /// (iteration, exploitability % pot, elapsed seconds)
    pub history: Vec<(u32, f64, f64)>,
    pub tree: Option<MwTreeInfo>,
}

pub fn routes<S: Clone + Send + Sync + 'static>() -> Router<S> {
    Router::new()
        .route("/api/mw/spot", post(build))
        .route("/api/mw/solve", post(solve))
        .route("/api/mw/stop", post(stop))
        .route("/api/mw/status", get(status))
        .route("/api/mw/node", post(node))
        .route("/api/mw/save", post(save))
        .route("/api/mw/load", post(load))
        .route("/api/mw/saves", get(list_saves))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct SizeRow {
    bet: String,
    raise: String,
}

#[derive(Deserialize)]
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
}

fn spot_config(req: &MwSpotRequest) -> Result<MwSpotConfig, String> {
    if !(req.starting_pot > 0.0) || req.stacks.iter().any(|&s| !(s > 0.0)) {
        return Err("pot and stacks must be positive".into());
    }
    if !(0.0..=100.0).contains(&req.rake_pct) {
        return Err("rake % must be between 0 and 100".into());
    }
    let mut streets: [StreetSizing; 3] = Default::default();
    for (i, row) in req.sizes.iter().take(3).enumerate() {
        streets[i] = StreetSizing { bet: parse_sizes(&row.bet)?, raise: parse_sizes(&row.raise)?, donk: Vec::new() };
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
    Ok(MwSpotConfig { board: req.board.clone(), ranges: req.ranges.clone(), tree: t })
}

fn tree_info(spot: &MwSpot, build_secs: f64) -> MwTreeInfo {
    #[cfg(feature = "gpu")]
    let (gpu_mb, gpu_min_mb) = {
        let (full, min) = solver::multiway::gpu::estimate_device_bytes(spot, Algorithm::Dcfr);
        (full as f64 / 1e6, min as f64 / 1e6)
    };
    #[cfg(not(feature = "gpu"))]
    let (gpu_mb, gpu_min_mb) = (0.0, 0.0);
    MwTreeInfo {
        board: spot.config.board.clone(),
        nodes: spot.tree.nodes.len(),
        action_nodes: spot.num_action_nodes(),
        entries: spot.tree.data_size.iter().sum(),
        hands: std::array::from_fn(|k| spot.hands[k].len()),
        arena_mb_f32: spot.arena_bytes(Storage::F32) as f64 / 1e6,
        arena_mb_compressed: spot.arena_bytes(Storage::Compressed) as f64 / 1e6,
        gpu_mb,
        gpu_min_mb,
        build_secs,
    }
}

fn ram_cap_mb() -> f64 {
    if let Some(v) = std::env::var("SOLVER_MEM_MB").ok().and_then(|v| v.parse::<f64>().ok()) {
        return v;
    }
    solver::sysmem::avail_mem_mb().map(|a| a * 0.8).unwrap_or(48_000.0)
}

/// Stops and joins the current worker (if any) and drops the session.
fn stop_session() {
    let worker = {
        let mut g = lock_unpoisoned(&MW.session);
        g.as_mut().and_then(|s| {
            s.stop.store(true, Ordering::Relaxed);
            s.worker.take()
        })
    };
    if let Some(w) = worker {
        let _ = w.join();
    }
}

fn install(solver: MwSolver, info: MwTreeInfo, state: &str) {
    *lock_unpoisoned(&MW.session) =
        Some(MwSession { solver: Arc::new(Mutex::new(solver)), stop: Arc::new(AtomicBool::new(false)), worker: None });
    let mut st = lock_unpoisoned(&MW.status);
    *st = MwStatus { state: state.into(), tree: Some(info), ..Default::default() };
}

async fn build(Json(req): Json<MwSpotRequest>) -> Result<Json<MwTreeInfo>, ApiError> {
    let cfg = spot_config(&req).map_err(bad_request)?;
    stop_session();
    lock_unpoisoned(&MW.status).state = "building".into();
    let res = tokio::task::spawn_blocking(move || -> Result<(MwSpot, f64), String> {
        let t0 = Instant::now();
        let spot = MwSpot::new_with_limit(cfg, Some(MAX_NODES))?;
        Ok((spot, t0.elapsed().as_secs_f64()))
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?;
    let (spot, secs) = match res {
        Ok(x) => x,
        Err(e) => {
            let mut st = lock_unpoisoned(&MW.status);
            st.state = "error".into();
            st.error = e.clone();
            return Err(bad_request(e));
        }
    };
    let info = tree_info(&spot, secs);
    let cap = ram_cap_mb();
    if info.arena_mb_compressed > cap {
        lock_unpoisoned(&MW.status).state = "idle".into();
        return Err(bad_request(format!(
            "this tree needs {:.0} MB of solver memory (compressed), over the RAM cap of {cap:.0} MB; \
             use fewer bet sizes or a later street",
            info.arena_mb_compressed
        )));
    }
    let solver = MwSolver::new(Arc::new(spot), Storage::Compressed);
    install(solver, info.clone(), "ready");
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
    let sess = g.as_mut().ok_or_else(|| bad_request("no 3-way spot built yet"))?;
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
        st.note.clear();
        st.history.clear();
    }
    let solver = sess.solver.clone();
    let stop = sess.stop.clone();
    let status = MW.status.clone();
    sess.worker = Some(std::thread::spawn(move || {
        let st2 = status.clone();
        let r = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| run(solver, stop, status, req, engine)));
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

fn record(status: &Mutex<MwStatus>, pr: &solver::multiway::MwProgress, base_iter: u32, engine: &str) {
    let mut st = lock_unpoisoned(status);
    st.iteration = pr.iteration;
    st.exploit_pct = pr.exploit_pct_pot;
    st.gaps = pr.gaps;
    st.evs = pr.evs;
    st.elapsed = pr.elapsed_secs;
    st.iters_per_sec = if pr.elapsed_secs > 0.0 { (pr.iteration - base_iter) as f64 / pr.elapsed_secs } else { 0.0 };
    st.engine = engine.into();
    st.history.push((pr.iteration, pr.exploit_pct_pot, pr.elapsed_secs));
}

/// Solve worker: GPU when allowed and it fits, else CPU. Returns the final
/// state name.
fn run(
    solver: Arc<Mutex<MwSolver>>,
    stop: Arc<AtomicBool>,
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
                lock_unpoisoned(&status).note = g.describe();
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
                    let due = k % check == 0 && last_check.elapsed().as_secs_f64() >= 4.0 * eval_cost;
                    if due || k >= req.max_iterations {
                        let te = Instant::now();
                        let pr = g.progress(start.elapsed().as_secs_f64())?;
                        eval_cost = te.elapsed().as_secs_f64();
                        last_check = Instant::now();
                        record(&status, &pr, base, "gpu");
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
                if !synced {
                    let pr = g.progress(start.elapsed().as_secs_f64())?;
                    record(&status, &pr, base, "gpu");
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
            Err(e) => lock_unpoisoned(&status).note = format!("CPU (GPU unavailable: {e})"),
        }
    }
    #[cfg(not(feature = "gpu"))]
    if engine == "gpu" {
        return Err("this server was built without CUDA support".into());
    }
    if lock_unpoisoned(&status).note.is_empty() {
        lock_unpoisoned(&status).note = format!("CPU, {} threads", rayon::current_num_threads());
    }
    let base = lock_unpoisoned(&solver).iteration;
    let start = Instant::now();
    let mut done = false;
    loop {
        if stop.load(Ordering::Relaxed) {
            break;
        }
        let mut s = lock_unpoisoned(&solver);
        if s.iteration >= base + req.max_iterations {
            break;
        }
        s.iterate();
        let k = s.iteration - base;
        if k % check == 0 || k >= req.max_iterations {
            let pr = s.progress(start.elapsed().as_secs_f64());
            drop(s);
            record(&status, &pr, base, "cpu");
            if pr.exploit_pct_pot <= req.target_exploit_pct {
                done = true;
                break;
            }
        }
    }
    Ok(if done || !stop.load(Ordering::Relaxed) { "done" } else { "stopped" })
}

async fn stop() -> Json<serde_json::Value> {
    if let Some(s) = lock_unpoisoned(&MW.session).as_ref() {
        s.stop.store(true, Ordering::Relaxed);
    }
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
    path: Vec<MwStep>,
    #[serde(default = "yes")]
    ev: bool,
}
fn yes() -> bool {
    true
}

async fn node(Json(req): Json<NodeRequest>) -> Result<Json<MwNodeView>, ApiError> {
    let solver = session_solver()?;
    let v = tokio::task::spawn_blocking(move || {
        let mut s = lock_unpoisoned(&solver);
        s.ensure_symmetric();
        node_view(&s, &req.path, req.ev)
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
        .map(|c| if c.is_ascii_alphanumeric() || matches!(c, ' ' | '-' | '_' | '.') { c } else { '-' })
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
        let mut s = lock_unpoisoned(&solver);
        s.ensure_symmetric();
        let tmp = path.with_extension("tmp");
        let f = std::fs::File::create(&tmp).map_err(|e| e.to_string())?;
        solver::multiway::save::save(&s, exploit, f)?;
        std::fs::rename(&tmp, &path).map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    Ok(Json(serde_json::json!({"ok": true, "path": out.to_string_lossy()})))
}

async fn load(Json(req): Json<NameRequest>) -> Result<Json<MwStatus>, ApiError> {
    let path = save_path(&req.name).map_err(bad_request)?;
    stop_session();
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
    install(s, info, "stopped");
    let mut st = lock_unpoisoned(&MW.status);
    st.iteration = iteration;
    st.exploit_pct = hdr.exploit_pct_pot.unwrap_or(0.0);
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
            let Ok(f) = std::fs::File::open(&p) else { continue };
            if let Ok(h) = solver::multiway::save::peek(f) {
                out.push(SaveEntry {
                    name: p.file_stem().unwrap_or_default().to_string_lossy().into_owned(),
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
