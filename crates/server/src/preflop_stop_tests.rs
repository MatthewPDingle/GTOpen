//! Preflop Lab STOP over HTTP: the solve ends with one last accuracy check,
//! so the gap it reports belongs to the strategies it leaves; a session that
//! is being replaced ends without one.
use axum::{
    body::{to_bytes, Body},
    http::Request,
};
use tower::ServiceExt;

use super::*;

fn app(state: &Arc<AppState>) -> Router {
    Router::new()
        .route("/api/preflop/solve", post(pf_solve))
        .route("/api/preflop/stop", post(pf_stop))
        .route("/api/preflop/status", get(pf_status))
        .with_state(state.clone())
}

async fn call(state: &Arc<AppState>, request: Request<Body>) -> (StatusCode, serde_json::Value) {
    let response = app(state).oneshot(request).await.unwrap();
    let status = response.status();
    let text = String::from_utf8(
        to_bytes(response.into_body(), usize::MAX)
            .await
            .unwrap()
            .to_vec(),
    )
    .unwrap();
    (
        status,
        serde_json::from_str(&text).unwrap_or(serde_json::Value::String(text)),
    )
}

async fn post_json(
    state: &Arc<AppState>,
    path: &str,
    body: serde_json::Value,
) -> (StatusCode, serde_json::Value) {
    call(
        state,
        Request::post(path)
            .header("content-type", "application/json")
            .body(Body::from(body.to_string()))
            .unwrap(),
    )
    .await
}

async fn http_status(state: &Arc<AppState>) -> serde_json::Value {
    call(
        state,
        Request::get("/api/preflop/status")
            .body(Body::empty())
            .unwrap(),
    )
    .await
    .1
}

/// A fresh 3-handed 20bb game, nothing solved.
fn session(realization: serde_json::Value) -> Arc<AppState> {
    static EQ: std::sync::OnceLock<Arc<solver::preflop::equity::EquityTable>> =
        std::sync::OnceLock::new();
    let eq = EQ
        .get_or_init(|| Arc::new(solver::preflop::equity::EquityTable::build(1000)))
        .clone();
    let mut cfg = serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 20.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "limp": false
    });
    cfg.as_object_mut()
        .unwrap()
        .extend(realization.as_object().unwrap().clone());
    let s = solver::preflop::PreflopSolver::new(serde_json::from_value(cfg).unwrap(), eq).unwrap();
    let status = PreflopStatus {
        state: "idle".into(),
        ..Default::default()
    };
    let state = Arc::new(AppState::default());
    *state.preflop.lock().unwrap() = Some(PreflopSession {
        solver: Arc::new(Mutex::new(s)),
        stop: Arc::new(AtomicBool::new(false)),
        abandon: Arc::new(AtomicBool::new(false)),
        status: Arc::new(Mutex::new(status)),
        worker: None,
    });
    state
}

/// Start a solve that never ends by itself and wait until it has `iterations` behind it.
async fn solve_until(state: &Arc<AppState>, check_every: u32, iterations: u32) {
    let (code, out) = post_json(
        state,
        "/api/preflop/solve",
        serde_json::json!({"iterations": 1_000_000, "check_every": check_every, "target_gap": 0.0}),
    )
    .await;
    assert_eq!(code, StatusCode::OK, "{out}");
    let (_, _, status) = pf_session(state).unwrap();
    while status.lock().unwrap().iteration < iterations {
        tokio::time::sleep(std::time::Duration::from_millis(2)).await;
    }
}

async fn join(state: &Arc<AppState>) -> PreflopStatus {
    let handle = state
        .preflop
        .lock()
        .unwrap()
        .as_mut()
        .unwrap()
        .worker
        .take()
        .unwrap();
    tokio::task::spawn_blocking(move || handle.join().unwrap())
        .await
        .unwrap();
    pf_session(state).unwrap().2.lock().unwrap().clone()
}

fn assert_close(a: &[f64], b: &[f64]) {
    assert_eq!(a.len(), b.len());
    for (x, y) in a.iter().zip(b) {
        assert!((x - y).abs() < 1e-9, "{a:?} vs {b:?}");
    }
}

#[tokio::test]
async fn stop_ends_with_the_gap_of_the_strategies_it_leaves() {
    let state = session(serde_json::json!({"realization": "raw"}));
    // no scheduled check ever comes: the only measurement is the one STOP asks for
    solve_until(&state, 1_000_000, 5).await;
    assert_eq!(http_status(&state).await["stopping"], false);
    let (code, _) = post_json(&state, "/api/preflop/stop", serde_json::json!({})).await;
    assert_eq!(code, StatusCode::OK);
    let st = join(&state).await;
    assert_eq!(
        (
            st.state.as_str(),
            st.stop_reason.as_str(),
            st.phase.as_str()
        ),
        ("stopped", "stopped", "idle"),
        "{}",
        st.error
    );
    assert!(st.iteration >= 5);
    assert_eq!(st.published_iteration, st.iteration);
    assert_eq!(st.accuracy_iteration, Some(st.iteration));
    assert!(st.preview_note.is_empty(), "{}", st.preview_note);
    assert!(st.gap_total > 0.0 && !st.publication().converged);
    // the reported gaps are the gaps of what the solver now holds
    let (solver, stop, _) = pf_session(&state).unwrap();
    let mut s = solver.lock().unwrap();
    assert_eq!(s.iteration, st.iteration);
    let (gaps, evs) = pf_measured_gaps(&mut s);
    assert_close(&st.gaps, &gaps);
    assert_close(&st.evs, &evs);
    assert_close(&[st.gap_total], &[gaps.iter().sum::<f64>()]);
    drop(s);
    // the run is over: nothing is "stopping" any more, though the flag stays up
    assert!(stop.load(Ordering::Relaxed));
    assert_eq!(http_status(&state).await["stopping"], false);
}

#[tokio::test]
async fn stop_during_a_check_keeps_that_check() {
    let state = session(serde_json::json!({"realization": "raw"}));
    // every iteration is followed by a check, so STOP lands in or right beside one
    solve_until(&state, 1, 5).await;
    post_json(&state, "/api/preflop/stop", serde_json::json!({})).await;
    let st = join(&state).await;
    assert_eq!(
        (st.state.as_str(), st.stop_reason.as_str()),
        ("stopped", "stopped"),
        "{}",
        st.error
    );
    assert_eq!(st.accuracy_iteration, Some(st.iteration));
    let (solver, _, _) = pf_session(&state).unwrap();
    let (gaps, _) = pf_measured_gaps(&mut solver.lock().unwrap());
    assert_close(&st.gaps, &gaps);
}

#[tokio::test]
async fn stop_with_learned_flop_values_measures_and_settles_at_the_final_strategies() {
    let state = session(serde_json::json!({"realization": "leafnet", "leaf_net": "v1"}));
    // a check after every iteration: the net has always just been run for the
    // current iteration count when STOP cuts the next pass short
    solve_until(&state, 1, 3).await;
    post_json(&state, "/api/preflop/stop", serde_json::json!({})).await;
    let st = join(&state).await;
    assert_eq!(
        (st.state.as_str(), st.stop_reason.as_str()),
        ("stopped", "stopped"),
        "{}",
        st.error
    );
    assert_eq!(st.accuracy_iteration, Some(st.iteration));
    let (solver, _, _) = pf_session(&state).unwrap();
    let mut s = solver.lock().unwrap();
    assert!(!s.leaf_values_stale());
    // priced with the net's output at exactly these strategies (no drift), and
    // the reported gaps are the ones that pricing gives
    let (gaps, evs, drift) = s.consistent_gaps_and_evs().expect("learned model");
    assert!(
        drift < 1e-9,
        "left priced {drift} of the pot away from the net's output"
    );
    assert_close(&st.gaps, &gaps);
    assert_close(&st.evs, &evs);
}

#[tokio::test]
async fn a_replaced_session_ends_without_the_last_check() {
    let state = session(serde_json::json!({"realization": "raw"}));
    solve_until(&state, 1_000_000, 5).await;
    let (_, _, status) = pf_session(&state).unwrap();
    pf_stop_and_join(&state).await.unwrap();
    let st = status.lock().unwrap().clone();
    assert_eq!(
        (st.state.as_str(), st.stop_reason.as_str()),
        ("stopped", "stopped")
    );
    assert!(st.accuracy_iteration.is_none() && st.gaps.is_empty());
    assert!(st.preview_note.contains("accuracy has not been measured"));
    // the next solve starts clean and its own STOP measures again
    solve_until(&state, 1_000_000, st.iteration + 3).await;
    post_json(&state, "/api/preflop/stop", serde_json::json!({})).await;
    let st = join(&state).await;
    assert_eq!(st.accuracy_iteration, Some(st.iteration));
}

#[tokio::test]
async fn status_says_a_stop_is_on_its_way_while_the_solve_is_still_running() {
    let state = session(serde_json::json!({"realization": "raw"}));
    let (_, stop, status) = pf_session(&state).unwrap();
    status.lock().unwrap().state = "running".into();
    assert_eq!(http_status(&state).await["stopping"], false);
    stop.store(true, Ordering::Relaxed);
    assert_eq!(http_status(&state).await["stopping"], true);
}
