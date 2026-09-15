//! One disposable conditional study, independent of the normal sessions.
use super::*;
use solver::preflop::PreflopSolver;
use std::sync::atomic::AtomicU64;

static NEXT_ID: AtomicU64 = AtomicU64::new(1);
pub(super) struct Job {
    id: u64,
    stop: Arc<AtomicBool>,
    status: Arc<Mutex<StudyStatus>>,
    solver: Arc<Mutex<Option<PreflopSolver>>>,
}
#[derive(Clone, Serialize)]
struct StudyStatus {
    id: u64,
    state: String,
    iteration: u32,
    max_iterations: u32,
    gap: Option<f64>,
    seconds: f64,
    error: String,
    plan: serde_json::Value,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(super) struct Id {
    id: u64,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(super) struct Start {
    id: u64,
    ranges: Vec<String>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(super) struct Node {
    id: u64,
    path: Vec<usize>,
}

fn busy(state: &AppState) -> bool {
    state.status.lock().unwrap().state == "running"
        || state.report.lock().unwrap().running
        || state
            .preflop
            .lock()
            .unwrap()
            .as_ref()
            .is_some_and(|s| s.status.lock().unwrap().state == "running")
}
fn conflict(msg: &str) -> ApiError {
    (StatusCode::CONFLICT, msg.into())
}

pub(super) async fn plan(
    State(state): State<Arc<AppState>>,
    Json(req): Json<PfPathRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    if busy(&state) {
        return Err(conflict(
            "Finish the active solve or report before preparing a focused study",
        ));
    }
    let (source, _, _) = pf_session(&state)?;
    let (info,study)=tokio::task::spawn_blocking(move || {
        let s=pf_solver_lock(&source);
        let info=s.focus_plan(&req.path)?;
        // Empty ranges remain empty in the review form and cannot be submitted.
        // A temporary full range only permits constructing the immutable geometry.
        let defaults:Vec<String>=info.ranges.iter().map(|r|if r.is_empty(){"22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+,72o+,62o+,52o+,42o+,32o".into()}else{r.clone()}).collect();
        let study=s.focused(&req.path,&defaults)?;
        let mut info=serde_json::to_value(info).map_err(|e|e.to_string())?;
        info["source_path"]=serde_json::json!(req.path);
        info["ante"]=serde_json::json!(s.cfg.ante);
        info["line"]=serde_json::json!(s.node_view(&req.path)?.history.iter().filter_map(|h|h.chosen.map(|a|format!("{}: {}",h.actor_pos,h.actions[a].label))).collect::<Vec<_>>());
        Ok::<_,String>((info,study))
    }).await.map_err(|e|bad_request(e.to_string()))?.map_err(bad_request)?;
    let mut slot = state.focus.lock().unwrap();
    if slot
        .as_ref()
        .is_some_and(|j| j.status.lock().unwrap().state == "running")
    {
        return Err(conflict("A focused study is already running"));
    }
    let id = NEXT_ID.fetch_add(1, Ordering::Relaxed);
    let status = StudyStatus {
        id,
        state: "ready".into(),
        iteration: 0,
        max_iterations: 2000,
        gap: None,
        seconds: 0.,
        error: String::new(),
        plan: info,
    };
    let response = serde_json::to_value(&status).unwrap();
    *slot = Some(Job {
        id,
        stop: Arc::new(AtomicBool::new(false)),
        status: Arc::new(Mutex::new(status)),
        solver: Arc::new(Mutex::new(Some(study))),
    });
    Ok(Json(response))
}

pub(super) async fn start(
    State(state): State<Arc<AppState>>,
    Json(req): Json<Start>,
) -> Result<Json<serde_json::Value>, ApiError> {
    if busy(&state) {
        return Err(conflict(
            "Finish the active solve or report before starting a focused study",
        ));
    }
    if !cfg!(feature = "gpu") || !gpu_enabled() {
        return Err(bad_request("Focused studies require the GPU build"));
    }
    let slot = state.focus.lock().unwrap();
    let j = slot
        .as_ref()
        .filter(|j| j.id == req.id)
        .ok_or_else(|| bad_request("Study expired; open a new focused study"))?;
    let mut st = j.status.lock().unwrap();
    if st.state != "ready" {
        return Err(conflict("Open a new study to change its incoming ranges"));
    }
    let mut guard = j.solver.lock().unwrap();
    guard
        .as_mut()
        .ok_or_else(|| bad_request("Study unavailable"))?
        .set_focus_ranges(&req.ranges)
        .map_err(bad_request)?;
    st.plan["ranges"] = serde_json::json!(req.ranges);
    let mut study = guard.take().unwrap();
    let stop = j.stop.clone();
    let status = j.status.clone();
    let result = j.solver.clone();
    st.state = "running".into();
    let app = state.clone();
    std::thread::spawn(move || {
        let began = std::time::Instant::now();
        let work =
            std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| -> Result<bool, String> {
                study.set_stop_flag(Some(stop.clone()));
                #[cfg(feature = "gpu")]
                {
                    let (mut gpu, _) = solver::preflop::gpu::PreflopGpu::new_throughput(
                        &study,
                        gpu_budget().0.min(4096),
                    )?;
                    for i in 1..=2000 {
                        // Yield the device if the user starts their normal work.
                        if busy(&app) {
                            stop.store(true, Ordering::Relaxed);
                        }
                        if stop.load(Ordering::Relaxed)
                            || !gpu.try_iterate(&mut study, Some(&stop))?
                        {
                            return Ok(false);
                        }
                        {
                            let mut s = status.lock().unwrap();
                            s.iteration = i;
                            s.seconds = began.elapsed().as_secs_f64();
                        }
                        if i % 25 == 0 || i == 2000 {
                            let (gaps, _) = gpu.gaps_and_evs()?;
                            if stop.load(Ordering::Relaxed) {
                                return Ok(false);
                            }
                            let gap: f64 = gaps
                                .iter()
                                .enumerate()
                                .filter(|(p, _)| !study.seat_frozen[*p])
                                .map(|(_, g)| g.max(0.))
                                .sum();
                            if !gap.is_finite() {
                                return Err("Invalid focused accuracy result".into());
                            }
                            status.lock().unwrap().gap = Some(gap);
                            if gap <= 0.005 || i == 2000 {
                                gpu.sync_to_cpu(&mut study)?;
                                return Ok(true);
                            }
                        }
                    }
                }
                Err("GPU focused study unavailable".into())
            }));
        study.set_stop_flag(None);
        // The GPU has been released before completion becomes visible.
        let mut s = status.lock().unwrap();
        s.seconds = began.elapsed().as_secs_f64();
        match work {
            Ok(Ok(true)) if !stop.load(Ordering::Relaxed) => {
                s.state = if s.gap.is_some_and(|g| g <= 0.005) {
                    "done"
                } else {
                    "limit_reached"
                }
                .into();
                *result.lock().unwrap() = Some(study);
            }
            Ok(Ok(_)) => s.state = "cancelled".into(),
            Ok(Err(e)) => {
                s.state = "error".into();
                s.error = e;
            }
            Err(e) => {
                s.state = "error".into();
                s.error = panic_msg(e.as_ref()).into();
            }
        }
    });
    Ok(Json(serde_json::json!({"id":req.id})))
}

pub(super) async fn status(
    State(state): State<Arc<AppState>>,
    Json(req): Json<Id>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let slot = state.focus.lock().unwrap();
    let j = slot
        .as_ref()
        .filter(|j| j.id == req.id)
        .ok_or_else(|| bad_request("Study expired"))?;
    let out = serde_json::to_value(&*j.status.lock().unwrap()).unwrap();
    Ok(Json(out))
}
pub(super) async fn stop(
    State(state): State<Arc<AppState>>,
    Json(req): Json<Id>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let slot = state.focus.lock().unwrap();
    let j = slot
        .as_ref()
        .filter(|j| j.id == req.id)
        .ok_or_else(|| bad_request("Study expired"))?;
    j.stop.store(true, Ordering::Relaxed);
    Ok(Json(serde_json::json!({"ok":true})))
}
pub(super) async fn node(
    State(state): State<Arc<AppState>>,
    Json(req): Json<Node>,
) -> Result<Json<solver::preflop::PreflopNodeView>, ApiError> {
    if req.path.len() > 64 {
        return Err(bad_request("Invalid study path"));
    }
    let solver = {
        let slot = state.focus.lock().unwrap();
        let j = slot
            .as_ref()
            .filter(|j| j.id == req.id)
            .ok_or_else(|| bad_request("Study expired"))?;
        let st = j.status.lock().unwrap();
        if st.state != "done" && st.state != "limit_reached" {
            return Err(conflict("Wait for the focused study to finish"));
        }
        j.solver.clone()
    };
    let view = tokio::task::spawn_blocking(move || {
        solver
            .lock()
            .unwrap()
            .as_ref()
            .ok_or("Study unavailable")?
            .node_view(&req.path)
    })
    .await
    .map_err(|e| bad_request(e.to_string()))?
    .map_err(bad_request)?;
    Ok(Json(view))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    async fn focus_snapshot_is_separate_and_ids_and_busy_work_are_guarded() {
        let state = Arc::new(AppState::default());
        let cfg=serde_json::from_value(serde_json::json!({"positions":["SB","BB"],"posts":[0.5,1],"stack":10,
            "limp":false,"open_raises":[],"raise_mults":[],"max_raises":1,"add_allin":true,"realization":"raw"})).unwrap();
        let s = PreflopSolver::new(
            cfg,
            Arc::new(solver::preflop::equity::EquityTable::build(1)),
        )
        .unwrap();
        let before = serde_json::to_value(s.node_view(&[]).unwrap()).unwrap();
        let source = Arc::new(Mutex::new(s));
        *state.preflop.lock().unwrap() = Some(PreflopSession {
            solver: source.clone(),
            stop: Arc::new(AtomicBool::new(false)),
            status: Arc::new(Mutex::new(PreflopStatus::default())),
            worker: None,
        });
        let prepared = plan(State(state.clone()), Json(PfPathRequest { path: vec![1] }))
            .await
            .unwrap()
            .0;
        let id = prepared["id"].as_u64().unwrap();
        assert!(node(State(state.clone()), Json(Node { id, path: vec![] }))
            .await
            .is_err());
        assert!(status(State(state.clone()), Json(Id { id: id + 1 }))
            .await
            .is_err());
        state.report.lock().unwrap().running = true;
        assert!(start(
            State(state.clone()),
            Json(Start {
                id,
                ranges: vec!["AA".into(), "KK".into()]
            })
        )
        .await
        .is_err());
        state.report.lock().unwrap().running = false;
        let _ = stop(State(state.clone()), Json(Id { id })).await.unwrap();
        assert!(state
            .focus
            .lock()
            .unwrap()
            .as_ref()
            .unwrap()
            .stop
            .load(Ordering::Relaxed));
        assert_eq!(
            before,
            serde_json::to_value(source.lock().unwrap().node_view(&[]).unwrap()).unwrap()
        );
    }
}
