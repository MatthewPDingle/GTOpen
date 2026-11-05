//! "Trust the read" over HTTP: the dial endpoint, the trust sweep on
//! /api/solve, and the trust option of vs-villain reports.
use super::*;
use axum::body::{to_bytes, Body};
use axum::http::Request;
use tower::ServiceExt;

/// A small river spot (fast on the CPU) with ranges wide enough for a
/// profile to matter.
fn spot_body() -> serde_json::Value {
    serde_json::json!({
        "board": "Ks7h2d3c4s",
        "range_oop": "QQ,JJ,TT,99,AhKh,AsKs,87s,A5s",
        "range_ip": "AA,KK,AQs,JTs,T9s,65s",
        "starting_pot": 60.0,
        "effective_stack": 300.0,
        "oop": [
            {"bet": "75", "raise": "100", "donk": ""},
            {"bet": "75", "raise": "100", "donk": ""},
            {"bet": "75", "raise": "100", "donk": ""}
        ],
        "ip": [
            {"bet": "75", "raise": "100", "donk": ""},
            {"bet": "75", "raise": "100", "donk": ""},
            {"bet": "75", "raise": "100", "donk": ""}
        ]
    })
}

/// A villain who barrels too much and folds too much.
fn stats() -> serde_json::Value {
    serde_json::json!({
        "cbet": [80.0, 70.0, 70.0], "fold_to_bet": [70.0, 70.0, 70.0],
        "raise_bet": 5.0, "donk": 5.0, "bet_size": "min"
    })
}

fn app(state: &Arc<AppState>) -> Router {
    Router::new()
        .route("/api/spot", post(build_spot))
        .route("/api/solve", post(start_solve))
        .route("/api/trust", post(set_trust))
        .route("/api/profile_locks", post(profile_locks).delete(profile_locks_clear))
        .route("/api/reports/run", post(report_run))
        .with_state(state.clone())
}

async fn post_json(app: Router, path: &str, body: serde_json::Value) -> (StatusCode, serde_json::Value) {
    let response = app
        .oneshot(
            Request::post(path)
                .header("content-type", "application/json")
                .body(Body::from(body.to_string()))
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let body = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let text = String::from_utf8(body.to_vec()).unwrap();
    (status, serde_json::from_str(&text).unwrap_or(serde_json::Value::String(text)))
}

/// Start a solve and wait for its worker to finish.
async fn solve(state: &Arc<AppState>, body: serde_json::Value) -> StatusInfo {
    let (status, out) = post_json(app(state), "/api/solve", body).await;
    assert_eq!(status, StatusCode::OK, "{out}");
    let handle = lock_unpoisoned(&state.session).as_mut().unwrap().worker.take().unwrap();
    tokio::task::spawn_blocking(move || handle.join().unwrap()).await.unwrap();
    let st = lock_unpoisoned(&state.status).clone();
    assert_eq!(st.state, "done", "{}", st.error);
    st
}

async fn locked_session() -> Arc<AppState> {
    let state = Arc::new(AppState::default());
    let (status, out) = post_json(app(&state), "/api/spot", spot_body()).await;
    assert_eq!(status, StatusCode::OK, "{out}");
    solve(&state, serde_json::json!({"max_iterations": 200, "target_exploit_pct": 0.05})).await;
    let (status, out) = post_json(
        app(&state),
        "/api/profile_locks",
        serde_json::json!({"player": 1, "stats": stats(), "aggressor": 1, "name": "Barreler"}),
    )
    .await;
    assert_eq!(status, StatusCode::OK, "{out}");
    assert!(out["locked"].as_u64().unwrap() > 0, "{out}");
    state
}

#[tokio::test]
async fn trust_sweep_records_one_readout_per_level() {
    let state = locked_session().await;
    let st = solve(
        &state,
        serde_json::json!({"max_iterations": 400, "target_exploit_pct": 0.05, "sweep": [1.0, 0.5, 0.0]}),
    )
    .await;
    let sweep = st.trust_sweep.expect("sweep in the status");
    assert!(!sweep.running);
    assert_eq!(sweep.current, 3);
    let trusts: Vec<f64> = sweep.points.iter().map(|p| p.readout.trust).collect();
    assert_eq!(trusts, vec![1.0, 0.5, 0.0]);
    assert_eq!(st.trust, Some(0.0));
    for p in &sweep.points {
        assert!(p.iterations > 0 && p.iterations <= 400, "{}", p.iterations);
        assert_eq!(p.readout.villain, 1);
    }
    // less trust: less EV against the read, less for a best-responding villain
    let (full, none) = (&sweep.points[0].readout, &sweep.points[2].readout);
    assert!(full.hero_ev_vs_read > none.hero_ev_vs_read + 0.1, "{} vs {}", full.hero_ev_vs_read, none.hero_ev_vs_read);
    assert!(
        full.villain_best_response_ev > none.villain_best_response_ev + 0.1,
        "{} vs {}",
        full.villain_best_response_ev,
        none.villain_best_response_ev
    );
    // the status readout is the last level's
    assert_eq!(st.trust_readout.unwrap().trust, 0.0);
    // and the solver ends at the last level
    let s = lock_unpoisoned(&state.session).as_ref().unwrap().solver.clone();
    assert_eq!(lock_unpoisoned(&s).trust(), Some(0.0));
    // a plain solve keeps the curve (pick a level, then RE-SOLVE) ...
    let st = solve(&state, serde_json::json!({"max_iterations": 400, "target_exploit_pct": 0.05, "trust": 0.5})).await;
    assert_eq!(st.trust_sweep.unwrap().points.len(), 3);
    // ... and a lock edit drops it: it described the old read
    let response = app(&state)
        .oneshot(Request::delete("/api/profile_locks").body(Body::empty()).unwrap())
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    assert!(lock_unpoisoned(&state.status).trust_sweep.is_none());
}

#[tokio::test]
async fn trust_dial_endpoint_sets_validates_and_resolves() {
    let state = locked_session().await;
    for bad in [serde_json::json!(1.5), serde_json::json!(-0.1)] {
        let (status, out) = post_json(app(&state), "/api/trust", serde_json::json!({"trust": bad})).await;
        assert_eq!(status, StatusCode::BAD_REQUEST, "{out}");
    }
    let (status, out) = post_json(app(&state), "/api/trust", serde_json::json!({"trust": 0.8})).await;
    assert_eq!(status, StatusCode::OK, "{out}");
    assert_eq!(out["villain"], 1);
    assert_eq!(lock_unpoisoned(&state.status).trust, Some(0.8));
    let st = solve(&state, serde_json::json!({"max_iterations": 400, "target_exploit_pct": 0.05})).await;
    let r = st.trust_readout.expect("readout after a solve with a read");
    assert!((r.trust - 0.8).abs() < 1e-6);
    assert!(r.hero_worst_case_ev.is_some(), "no rake: zero-sum");
    // a trust on the solve request wins over the dial
    let st = solve(&state, serde_json::json!({"max_iterations": 400, "target_exploit_pct": 0.05, "trust": 0.3})).await;
    assert!((st.trust_readout.unwrap().trust - 0.3).abs() < 1e-6);
    assert_eq!(st.trust, Some(0.3));
    // unset: full trust again
    let (status, _) = post_json(app(&state), "/api/trust", serde_json::json!({"trust": null})).await;
    assert_eq!(status, StatusCode::OK);
    let st = solve(&state, serde_json::json!({"max_iterations": 400, "target_exploit_pct": 0.05})).await;
    assert_eq!(st.trust_readout.unwrap().trust, 1.0);
    // locks changing under the readout clear it
    let response = app(&state)
        .oneshot(Request::delete("/api/profile_locks").body(Body::empty()).unwrap())
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    assert!(lock_unpoisoned(&state.status).trust_readout.is_none());
}

#[tokio::test]
async fn trust_sweep_needs_a_profile_and_valid_levels() {
    let state = Arc::new(AppState::default());
    let (status, _) = post_json(app(&state), "/api/spot", spot_body()).await;
    assert_eq!(status, StatusCode::OK);
    let (status, out) = post_json(app(&state), "/api/solve", serde_json::json!({"sweep": []})).await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
    assert!(out.as_str().unwrap().contains("profile"), "{out}");
    let state = locked_session().await;
    let (status, out) = post_json(app(&state), "/api/solve", serde_json::json!({"sweep": [1.0, 2.0]})).await;
    assert_eq!(status, StatusCode::BAD_REQUEST, "{out}");
    assert!(lock_unpoisoned(&state.status).trust_sweep.is_none());
}

#[tokio::test]
async fn report_villain_trust_is_validated() {
    let state = Arc::new(AppState::default());
    let villain = serde_json::json!({"player": 1, "name": "Barreler", "stats": stats(), "trust": 1.5});
    let (status, out) = post_json(
        app(&state),
        "/api/reports/run",
        serde_json::json!({"name": "unit-trust-check", "spot": spot_body(), "villain": villain}),
    )
    .await;
    assert_eq!(status, StatusCode::BAD_REQUEST, "{out}");
    assert!(out.as_str().unwrap().contains("trust"), "{out}");
    assert!(!lock_unpoisoned(&state.report).running);
}

#[test]
fn report_villain_trust_round_trips_and_stays_optional() {
    let v: ReportVillain =
        serde_json::from_value(serde_json::json!({"player": 1, "name": "X", "stats": stats()})).unwrap();
    assert!(v.trust.is_none());
    assert!(serde_json::to_value(&v).unwrap().get("trust").is_none(), "old reports keep their shape");
    let v: ReportVillain =
        serde_json::from_value(serde_json::json!({"player": 1, "name": "X", "stats": stats(), "trust": 0.7})).unwrap();
    assert_eq!(serde_json::to_value(&v).unwrap()["trust"], serde_json::json!(0.7f32));
}

#[test]
fn board_solve_reports_what_the_dial_bought() {
    let spot: SpotRequest = serde_json::from_value(spot_body()).unwrap();
    let villain: ReportVillain = serde_json::from_value(
        serde_json::json!({"player": 1, "name": "X", "stats": stats(), "aggressor": 1, "trust": 0.5}),
    )
    .unwrap();
    let stop = AtomicBool::new(false);
    let b = solve_board(&stop, &spot, "Ks7h2d3c4s", Some(&villain), 400, 0.05, Storage::F32, 4000.0, None)
        .unwrap_or_else(|_| panic!("board solve failed"));
    let t = &b.villain_lock["trust"];
    assert_eq!(t["trust"], 0.5);
    assert!(t["hero_ev_vs_read"].as_f64().is_some(), "{t}");
}
