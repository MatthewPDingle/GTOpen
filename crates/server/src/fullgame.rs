//! Heads-up preflop-to-river games (`solver::fullgame`) behind the Preflop
//! Lab's "Solve through river" source: build and solve in a background
//! worker, report progress, walk the preflop tree, and open any flop of a
//! called line in Browse as an ordinary postflop session.

use super::{bad_request, install_session, lock_unpoisoned, spot_request_from_config, stop_current, tree_info,
    ApiError, AppState, Session, StatusInfo};
use axum::extract::State;
use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};
use solver::fullgame::{Evaluation, FullGame, FullGameConfig, SupportSeed};
use solver::preflop::PreflopConfig;
use solver::tree::{parse_sizes, StreetSizing};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Instant;

/// A full game owned by whichever thread holds the slot's mutex.
/// SAFETY: the game's CUDA objects are only used under that mutex, and its
/// continuations never capture CUDA graphs (the non-Send part of a GPU
/// solver); every device call binds the shared primary context first.
pub(crate) struct SendGame(FullGame);
unsafe impl Send for SendGame {}
impl std::ops::Deref for SendGame { type Target = FullGame; fn deref(&self) -> &FullGame { &self.0 } }
impl std::ops::DerefMut for SendGame { fn deref_mut(&mut self) -> &mut FullGame { &mut self.0 } }

#[derive(Default)]
pub(crate) struct Slot {
    game: Arc<Mutex<Option<SendGame>>>,
    status: Arc<Mutex<FgStatus>>,
    stop: Arc<AtomicBool>,
    worker: Mutex<Option<std::thread::JoinHandle<()>>>,
    /// Readers waiting for the game; the worker lets them in between iterations.
    waiting: Arc<std::sync::atomic::AtomicUsize>,
}

/// Locks the game for a reader, ahead of the solve worker's next iteration.
fn read_game<R>(slot: &Slot, f: impl FnOnce(&mut Option<SendGame>) -> R) -> R {
    slot.waiting.fetch_add(1, Ordering::SeqCst);
    let r = f(&mut lock_unpoisoned(&slot.game));
    slot.waiting.fetch_sub(1, Ordering::SeqCst);
    r
}

#[derive(Clone, Serialize, Default)]
pub(crate) struct FgStatus {
    /// idle | building | running | done | stopped | error
    state: String,
    iteration: u32,
    target_iterations: u32,
    evaluation: Option<Evaluation>,
    /// Gap after each evaluation: (iteration, gap_total).
    gaps: Vec<(u32, f64)>,
    log: Vec<String>,
    error: String,
    seconds: f64,
    seconds_per_iteration: f64,
    device_gb: f64,
    host_gb: f64,
    continuations: usize,
    parked: usize,
    flops: Vec<String>,
    lines: Vec<FgLine>,
    config: Option<FullGameConfig>,
}

#[derive(Clone, Serialize)]
struct FgLine {
    line: String,
    path: Vec<usize>,
    pot: f64,
    behind: f64,
    support: [usize; 2],
}

fn sizes(s: &str, field: &str) -> Result<Vec<solver::tree::BetSize>, ApiError> {
    parse_sizes(s).map_err(|e| bad_request(format!("{field}: {e}")))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct SolveRequest {
    /// Required for a new game; omitted with `resume` to continue the current one.
    #[serde(default)]
    preflop: Option<PreflopConfig>,
    #[serde(default = "default_flops")]
    flops: usize,
    #[serde(default = "default_iterations")]
    iterations: u32,
    #[serde(default = "default_eval_every")]
    eval_every: u32,
    #[serde(default)]
    target_gap: f64,
    /// Postflop bet and raise sizes per street, as in Setup ("33", "3x", "a").
    #[serde(default = "default_menu")]
    menu: [[String; 2]; 3],
    #[serde(default = "default_min_freq")]
    min_freq: f64,
    #[serde(default)]
    resume: bool,
}

fn default_flops() -> usize { 4 }
fn default_iterations() -> u32 { 500 }
fn default_eval_every() -> u32 { 50 }
fn default_min_freq() -> f64 { 0.01 }
fn default_menu() -> [[String; 2]; 3] {
    [["33".into(), "3x".into()], ["75".into(), "a".into()], ["75".into(), "a".into()]]
}

fn game_config(req: &SolveRequest, preflop: PreflopConfig) -> Result<FullGameConfig, ApiError> {
    if preflop.positions.len() != 2 {
        return Err(bad_request("solving through the river needs a two-player game (SB vs BB)"));
    }
    if !(1..=64).contains(&req.flops) {
        return Err(bad_request("flops must be between 1 and 64"));
    }
    let street = |i: usize| -> Result<StreetSizing, ApiError> {
        Ok(StreetSizing {
            bet: sizes(&req.menu[i][0], "bet")?,
            raise: sizes(&req.menu[i][1], "raise")?,
            donk: vec![],
        })
    };
    let streets = [street(0)?, street(1)?, street(2)?];
    Ok(FullGameConfig {
        preflop,
        flops: solver::cards::canonical_flops_subset(req.flops).into_iter().map(|(b, w)| (b, w as f64)).collect(),
        oop: streets.clone(),
        ip: streets,
        max_raises: 1,
        allin_threshold: 0.85,
        add_allin: false,
        f32_state: false,
        resident_flops: None,
        support: Some(SupportSeed { iterations: 1000, min_freq: req.min_freq, expand_at: vec![100, 250] }),
    })
}

fn describe(game: &FullGame, st: &mut FgStatus) {
    st.device_gb = game.device_bytes() as f64 / 1e9;
    st.host_gb = game.host_bytes() as f64 / 1e9;
    st.continuations = game.continuations();
    st.parked = game.parked();
    st.flops = game.config.flops.iter().map(|f| f.0.clone()).collect();
    st.lines = game.leaves.iter().map(|l| FgLine {
        line: l.line.clone(), path: l.path.clone(), pot: l.pot, behind: l.behind,
        support: [0, 1].map(|s| l.support[s].iter().filter(|&&x| x).count()),
    }).collect();
    st.config = Some(game.config.clone());
}

fn log(status: &Mutex<FgStatus>, line: &str) {
    println!("fullgame: {line}");
    let mut st = lock_unpoisoned(status);
    st.log.push(line.to_string());
    let excess = st.log.len().saturating_sub(40);
    st.log.drain(..excess);
}

pub(crate) async fn solve(State(state): State<Arc<AppState>>, Json(req): Json<SolveRequest>)
    -> Result<Json<FgStatus>, ApiError> {
    if !(req.target_gap >= 0.0) || !(req.min_freq > 0.0 && req.min_freq < 1.0) {
        return Err(bad_request("target_gap must be >= 0 and min_freq in (0, 1)"));
    }
    let preflop_running = lock_unpoisoned(&state.preflop).as_ref()
        .is_some_and(|s| lock_unpoisoned(&s.status).state == "running");
    if preflop_running {
        return Err((StatusCode::CONFLICT, "stop the Preflop Lab solve first: both use the GPU".into()));
    }
    let slot = &state.fullgame;
    {
        let st = lock_unpoisoned(&slot.status);
        if st.state == "building" || st.state == "running" {
            return Err((StatusCode::CONFLICT, "a full-game solve is already running".into()));
        }
    }
    if let Some(h) = lock_unpoisoned(&slot.worker).take() {
        let _ = h.join();
    }
    let config = if req.resume {
        if lock_unpoisoned(&slot.game).is_none() {
            return Err(bad_request("no full game to continue"));
        }
        None
    } else {
        let pf = req.preflop.clone().ok_or_else(|| bad_request("preflop config required"))?;
        Some(game_config(&req, pf)?)
    };
    // The postflop session's GPU solve would compete for memory: stop it
    // (its solver stays loaded and browsable).
    let st2 = state.clone();
    tokio::task::spawn_blocking(move || stop_current(&st2, false)).await.map_err(|e| bad_request(e.to_string()))?;

    let (game, status, stop, waiting) = (slot.game.clone(), slot.status.clone(), slot.stop.clone(), slot.waiting.clone());
    stop.store(false, Ordering::Relaxed);
    {
        let mut st = lock_unpoisoned(&status);
        if config.is_some() {
            *st = FgStatus::default();
        }
        st.state = if config.is_some() { "building" } else { "running" }.into();
        st.error.clear();
        st.target_iterations = st.iteration + req.iterations;
    }
    let (iterations, every, target) = (req.iterations, req.eval_every.max(1), req.target_gap);
    let handle = std::thread::spawn(move || {
        let start = Instant::now();
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| -> Result<&'static str, String> {
            if let Some(config) = config {
                // Free the previous game's memory before building the next.
                *lock_unpoisoned(&game) = None;
                let built = FullGame::build(config, &mut |m| log(&status, m))?;
                let mut st = lock_unpoisoned(&status);
                describe(&built, &mut st);
                st.state = "running".into();
                drop(st);
                *lock_unpoisoned(&game) = Some(SendGame(built));
            }
            let train = Instant::now();
            let first = lock_unpoisoned(&status).iteration;
            for k in 1..=iterations {
                if stop.load(Ordering::Relaxed) {
                    return Ok("stopped");
                }
                while waiting.load(Ordering::SeqCst) > 0 {
                    std::thread::sleep(std::time::Duration::from_millis(2));
                }
                let mut guard = lock_unpoisoned(&game);
                let g = guard.as_mut().ok_or("the full game was released")?;
                g.iterate()?;
                let t = g.iteration;
                if let Some(seed) = g.config.support.clone() {
                    if seed.expand_at.contains(&t) {
                        let rebuilt = g.expand_support(seed.min_freq, &mut |m| log(&status, m))?;
                        log(&status, &format!("iteration {t}: support grown on {} lines", rebuilt.len()));
                        describe(g, &mut lock_unpoisoned(&status));
                    }
                }
                // Right after a support rebuild the restarted flops are far from
                // converged; skip that evaluation rather than report a spike.
                let grown = g.config.support.as_ref().is_some_and(|s| s.expand_at.contains(&t));
                let evaluate = (k % every == 0 && !grown) || k == iterations;
                let ev = if evaluate { Some(g.evaluate()?) } else { None };
                drop(guard);
                let mut st = lock_unpoisoned(&status);
                st.iteration = t;
                st.seconds = start.elapsed().as_secs_f64();
                st.seconds_per_iteration = train.elapsed().as_secs_f64() / (t - first) as f64;
                if let Some(ev) = ev {
                    st.gaps.push((t, ev.gap_total));
                    let done = ev.gap_total < target;
                    st.evaluation = Some(ev);
                    if done {
                        return Ok("done");
                    }
                }
            }
            Ok("done")
        }));
        let mut st = lock_unpoisoned(&status);
        st.seconds = start.elapsed().as_secs_f64();
        match outcome {
            Ok(Ok(state)) => st.state = state.into(),
            Ok(Err(e)) => { st.state = "error".into(); st.error = e; }
            Err(_) => { st.state = "error".into(); st.error = "the full-game worker panicked".into(); }
        }
    });
    *lock_unpoisoned(&slot.worker) = Some(handle);
    Ok(Json(lock_unpoisoned(&slot.status).clone()))
}

pub(crate) async fn status(State(state): State<Arc<AppState>>) -> Json<FgStatus> {
    Json(lock_unpoisoned(&state.fullgame.status).clone())
}

pub(crate) async fn stop(State(state): State<Arc<AppState>>) -> Json<FgStatus> {
    state.fullgame.stop.store(true, Ordering::Relaxed);
    Json(lock_unpoisoned(&state.fullgame.status).clone())
}

/// Frees the game's GPU and pinned host memory.
pub(crate) async fn release(State(state): State<Arc<AppState>>) -> Result<Json<FgStatus>, ApiError> {
    let slot = state.clone();
    tokio::task::spawn_blocking(move || {
        let s = &slot.fullgame;
        s.stop.store(true, Ordering::Relaxed);
        if let Some(h) = lock_unpoisoned(&s.worker).take() {
            let _ = h.join();
        }
        *lock_unpoisoned(&s.game) = None;
        *lock_unpoisoned(&s.status) = FgStatus { state: "idle".into(), ..Default::default() };
    }).await.map_err(|e| bad_request(e.to_string()))?;
    Ok(Json(lock_unpoisoned(&state.fullgame.status).clone()))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct NodeRequest {
    path: Vec<usize>,
}

pub(crate) async fn node(State(state): State<Arc<AppState>>, Json(req): Json<NodeRequest>)
    -> Result<Json<serde_json::Value>, ApiError> {
    let st = state.clone();
    tokio::task::spawn_blocking(move || read_game(&st.fullgame, |guard| {
        let g = guard.as_ref().ok_or_else(|| bad_request("no full game yet: solve one first"))?;
        g.node_view(&req.path).map_err(bad_request)
    })).await.map_err(|e| bad_request(e.to_string()))?.map(Json)
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct BrowseRequest {
    leaf: usize,
    flop: usize,
}

/// Replaces the postflop session with one flop of a called line.
pub(crate) async fn browse(State(state): State<Arc<AppState>>, Json(req): Json<BrowseRequest>)
    -> Result<Json<serde_json::Value>, ApiError> {
    let st = state.clone();
    let solver = tokio::task::spawn_blocking(move || read_game(&st.fullgame, |guard| {
        let g = guard.as_mut().ok_or_else(|| bad_request("no full game yet: solve one first"))?;
        g.flop_solver(req.leaf, req.flop).map_err(bad_request)
    })).await.map_err(|e| bad_request(e.to_string()))??;
    let info = tree_info(&solver.spot, solver.arena_bytes() as f64 / 1e6);
    let status = StatusInfo {
        state: "done".to_string(),
        iteration: solver.iteration,
        tree: Some(info.clone()),
        spot_request: spot_request_from_config(&solver.spot.config),
        ..Default::default()
    };
    let session = Session {
        solver: Arc::new(Mutex::new(solver)),
        stop: Arc::new(AtomicBool::new(false)),
        worker: None,
        lock_gen: Arc::new(std::sync::atomic::AtomicU64::new(0)),
    };
    let st = state.clone();
    tokio::task::spawn_blocking(move || install_session(&st, session, status))
        .await.map_err(|e| bad_request(e.to_string()))?;
    Ok(Json(serde_json::to_value(info).unwrap()))
}
