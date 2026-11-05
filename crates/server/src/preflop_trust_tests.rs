//! Preflop Lab hero mode's "trust the read" dial over HTTP: the dial
//! endpoint, the status mirror and the readout measured with the gaps.
use super::*;
use axum::body::{to_bytes, Body};
use axum::http::Request;
use tower::ServiceExt;

fn app(state: &Arc<AppState>) -> Router {
    Router::new()
        .route("/api/preflop/solve", post(pf_solve))
        .route("/api/preflop/hero", post(pf_hero))
        .route("/api/preflop/trust", post(pf_trust))
        .with_state(state.clone())
}

async fn post_json(state: &Arc<AppState>, path: &str, body: serde_json::Value) -> (StatusCode, serde_json::Value) {
    let response = app(state)
        .oneshot(Request::post(path).header("content-type", "application/json").body(Body::from(body.to_string())).unwrap())
        .await
        .unwrap();
    let status = response.status();
    let text = String::from_utf8(to_bytes(response.into_body(), usize::MAX).await.unwrap().to_vec()).unwrap();
    (status, serde_json::from_str(&text).unwrap_or(serde_json::Value::String(text)))
}

/// 3-handed 20bb table, solved, SB a maniac and BB a calling station, BTN hero.
fn hero_session() -> Arc<AppState> {
    static EQ: std::sync::OnceLock<Arc<solver::preflop::equity::EquityTable>> = std::sync::OnceLock::new();
    let eq = EQ.get_or_init(|| Arc::new(solver::preflop::equity::EquityTable::build(1000))).clone();
    let cfg = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 20.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "limp": false, "realization": "raw"
    }))
    .unwrap();
    let mut s = solver::preflop::PreflopSolver::new(cfg, eq).unwrap();
    for _ in 0..150 {
        s.iterate();
    }
    let mut profiles = vec![None; 3];
    for (seat, name) in [(1, "Maniac"), (2, "Calling station")] {
        let stats = solver::preflop::archetypes().into_iter().find(|(n, _)| *n == name).unwrap().1;
        profiles[seat] = Some(s.generate_profile(seat, &stats, name).unwrap().0);
    }
    s.set_table(vec![false; 3], profiles).unwrap();
    for _ in 0..150 {
        s.iterate();
    }
    s.set_hero(Some(0)).unwrap();
    let mut status = PreflopStatus { state: "idle".into(), ..Default::default() };
    status.hero = s.hero;
    status.frozen = s.seat_frozen.clone();
    let state = Arc::new(AppState::default());
    *state.preflop.lock().unwrap() = Some(PreflopSession {
        solver: Arc::new(Mutex::new(s)),
        stop: Arc::new(AtomicBool::new(false)),
        status: Arc::new(Mutex::new(status)),
        worker: None,
    });
    state
}

async fn solve(state: &Arc<AppState>) -> PreflopStatus {
    let (code, out) = post_json(state, "/api/preflop/solve", serde_json::json!({"iterations": 300, "check_every": 100, "target_gap": 0.0})).await;
    assert_eq!(code, StatusCode::OK, "{out}");
    let handle = state.preflop.lock().unwrap().as_mut().unwrap().worker.take().unwrap();
    tokio::task::spawn_blocking(move || handle.join().unwrap()).await.unwrap();
    let (_, _, status) = pf_session(state).unwrap();
    let st = status.lock().unwrap().clone();
    assert_eq!(st.state, "done", "{}", st.error);
    st
}

fn status(state: &Arc<AppState>) -> PreflopStatus {
    pf_session(state).unwrap().2.lock().unwrap().clone()
}

#[tokio::test]
async fn preflop_trust_dial_sets_validates_and_reports() {
    let state = hero_session();
    for bad in [serde_json::json!(1.5), serde_json::json!(-0.2)] {
        let (code, out) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": bad})).await;
        assert_eq!(code, StatusCode::BAD_REQUEST, "{out}");
    }
    let (code, out) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": 0.5})).await;
    assert_eq!(code, StatusCode::OK, "{out}");
    assert_eq!(out["seats"], serde_json::json!([1, 2]));
    let st = status(&state);
    assert_eq!((st.trust, st.trust_seats.clone()), (Some(0.5), vec![1, 2]));
    let st = solve(&state).await;
    let r = st.trust_readout.expect("readout measured with the gaps");
    assert_eq!(r.trust, 0.5);
    assert_eq!(r.seats, vec![1, 2]);
    assert!(r.hero_ev_vs_mixture.is_finite() && r.hero_ev_vs_read.is_finite() && r.hero_ev_vs_adapting.is_finite());
    assert_eq!(st.gaps.len(), 3);
    // a new level restarts the hero's average and drops the old readout
    let (code, _) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": 0.8})).await;
    assert_eq!(code, StatusCode::OK);
    let st = status(&state);
    assert!(st.trust_readout.is_none() && st.accuracy_iteration.is_none());
    assert_eq!(pf_session(&state).unwrap().0.lock().unwrap().iteration, 0);
    // unset: plain hero mode, no readout after a solve
    let (code, _) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": null})).await;
    assert_eq!(code, StatusCode::OK);
    let st = solve(&state).await;
    assert!(st.trust.is_none() && st.trust_readout.is_none());
    // hero off: the dial has nothing to act on
    let (code, _) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": 0.5})).await;
    assert_eq!(code, StatusCode::OK);
    let (code, out) = post_json(&state, "/api/preflop/hero", serde_json::json!({"seat": null})).await;
    assert_eq!(code, StatusCode::OK, "{out}");
    let st = status(&state);
    assert_eq!(st.trust, Some(0.5));
    assert!(st.trust_seats.is_empty());
}

#[tokio::test]
async fn preflop_trust_dial_is_refused_mid_solve() {
    let state = hero_session();
    pf_session(&state).unwrap().2.lock().unwrap().state = "running".into();
    let (code, _) = post_json(&state, "/api/preflop/trust", serde_json::json!({"trust": 0.5})).await;
    assert_eq!(code, StatusCode::CONFLICT);
    assert!(status(&state).trust.is_none());
}
