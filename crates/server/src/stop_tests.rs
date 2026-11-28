//! Postflop STOP: the exploitability shown for a stopped solve is measured on
//! the strategies it stops with, not carried over from an earlier check.
use super::*;

fn session() -> (Arc<AppState>, Arc<Mutex<Solver>>) {
    let config: SpotConfig = serde_json::from_str(r#"{
        "board":"QcJc9c3d2d", "range_oop":"AA,KK,QQ,JJ,AcKc,8h7h,7s6s", "range_ip":"QQ,TT,99,AdKd,KhTh,6d5d",
        "tree":{"starting_pot":100.0,"effective_stack":100.0,
            "oop":[{},{},{"bet":[{"PotPct":50.0},{"PotPct":100.0}]}],"ip":[{},{},{"bet":[{"PotPct":75.0}]}]}
    }"#).unwrap();
    let solver = Arc::new(Mutex::new(Solver::new(Arc::new(
        Spot::new(config).unwrap(),
    ))));
    let state = Arc::new(AppState::default());
    install_session(
        &state,
        Session {
            solver: solver.clone(),
            stop: Arc::new(AtomicBool::new(false)),
            worker: None,
            lock_gen: Arc::new(std::sync::atomic::AtomicU64::new(0)),
        },
        StatusInfo {
            state: "ready".into(),
            ..Default::default()
        },
    );
    // installing replaced nothing that was running; a real solve start clears this too
    state.discard_solve.store(false, Ordering::Relaxed);
    (state, solver)
}

/// Start a solve that never ends by itself (no check ever comes due) and wait for some iterations.
async fn solve_until(state: &Arc<AppState>, iterations: u32) {
    let req = SolveRequest {
        max_iterations: 100_000_000,
        target_exploit_pct: 0.0,
        check_every: 100_000_000,
        algorithm: None,
        trust: None,
        sweep: None,
    };
    let _ = start_solve(State(state.clone()), Json(req)).await.unwrap();
    while lock_unpoisoned(&state.status).iteration < iterations {
        tokio::time::sleep(std::time::Duration::from_millis(1)).await;
    }
}

#[tokio::test]
async fn stop_measures_what_the_solve_leaves() {
    let (state, solver) = session();
    solve_until(&state, 20).await;
    assert!(
        lock_unpoisoned(&state.status).history.is_empty(),
        "no check has run"
    );
    let _ = stop_solve(State(state.clone())).await;
    let st = lock_unpoisoned(&state.status).clone();
    assert_eq!(st.state, "stopped", "{}", st.error);
    let s = lock_unpoisoned(&solver);
    assert!(s.iteration >= 20);
    assert_eq!(st.iteration, s.iteration);
    let last = st.history.last().expect("measured at the stop");
    assert_eq!(last.iteration, s.iteration);
    let e = s.exploitability();
    assert!(e > 0.0);
    // a graphics card measures in single precision
    let tolerance = if cfg!(feature = "gpu") {
        1e-3 * e.max(1.0)
    } else {
        1e-9
    };
    assert!(
        (st.exploit_chips - e).abs() < tolerance,
        "{} vs {e}",
        st.exploit_chips
    );
    assert!(
        (st.exploit_pct - st.exploit_chips / 100.0 * 100.0).abs() < 1e-9,
        "percent of the 100 pot"
    );
    assert!((last.exploit_pct - st.exploit_pct).abs() < 1e-12);
}

#[test]
fn no_last_measurement_when_it_would_be_wasted() {
    let (state, _) = session();
    assert!(!measure_at_stop(&state, 0), "nothing solved");
    assert!(measure_at_stop(&state, 37));
    // the number on show already belongs to this iteration
    lock_unpoisoned(&state.status).history.push(HistoryPoint {
        iteration: 37,
        exploit_pct: 1.5,
    });
    assert!(!measure_at_stop(&state, 37));
    assert!(measure_at_stop(&state, 41));
    // the session is being replaced: nobody will read it
    state.discard_solve.store(true, Ordering::Relaxed);
    assert!(!measure_at_stop(&state, 41));
}

#[tokio::test]
async fn replacing_the_session_marks_the_solve_as_discarded() {
    let (state, _) = session();
    solve_until(&state, 5).await;
    assert!(!state.discard_solve.load(Ordering::Relaxed));
    let st = state.clone();
    tokio::task::spawn_blocking(move || stop_current(&st, true))
        .await
        .unwrap();
    assert!(state.discard_solve.load(Ordering::Relaxed));
    assert!(lock_unpoisoned(&state.session).is_none());
}
