//! In-process save/resume checks: no listener, server process, or GPU.
use super::*;

// Keep the RAM-cap override private to a child test process rather than
// mutating the environment under concurrently running server tests.
#[test]
fn loaded_pcfr_checks_ram_cap_without_algorithm_override() {
    let out = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "save_resume_tests::loaded_pcfr_cap_child",
            "--ignored",
            "--nocapture",
        ])
        .env("GTO_PCFR_CAP_CHILD", "1")
        .env("SOLVER_MEM_MB", "0.000001")
        .env("SOLVER_GPU", "0")
        .output()
        .unwrap();
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(out.status.success(), "{}\n{}", stdout, String::from_utf8_lossy(&out.stderr));
    assert!(stdout.contains("test result: ok. 1 passed;"),
        "the isolated child must execute exactly one regression: {stdout}");
}

#[tokio::test]
#[ignore = "invoked by loaded_pcfr_checks_ram_cap_without_algorithm_override"]
async fn loaded_pcfr_cap_child() {
    if std::env::var("GTO_PCFR_CAP_CHILD").as_deref() != Ok("1") {
        return;
    }
    let config: SpotConfig = serde_json::from_str(r#"{
        "board":"QcJc9c3d2d", "range_oop":"AcKc,8h7h", "range_ip":"QdQh",
        "tree":{"starting_pot":100.0,"effective_stack":100.0,
            "oop":[{},{},{"bet":[{"PotPct":100.0}]}],"ip":[{},{},{}]}
    }"#).unwrap();
    let mut saved = Solver::new(Arc::new(Spot::new(config).unwrap()));
    saved.algo = Algorithm::PcfrPlus;
    saved.iterate();
    let path = std::env::temp_dir().join(format!("gtopen-pcfr-cap-{}.gto", std::process::id()));
    saved.save(path.to_str().unwrap()).unwrap();
    let loaded = Solver::load(path.to_str().unwrap()).unwrap();
    std::fs::remove_file(path).unwrap();
    assert_eq!(loaded.algo, Algorithm::PcfrPlus);
    assert!(!loaded.has_preds());
    let solver = Arc::new(Mutex::new(loaded));
    let state = Arc::new(AppState::default());
    install_session(&state, Session {
        solver: solver.clone(),
        stop: Arc::new(AtomicBool::new(false)),
        worker: None,
        lock_gen: Arc::new(std::sync::atomic::AtomicU64::new(0)),
    }, StatusInfo { state: "done".into(), ..Default::default() });

    for algorithm in [None, Some("pcfr+".to_string())] {
        // Invalid trust is a sentinel: even a regressed cap check must fail
        // before it can launch a worker or allocate prediction arenas.
        let req = SolveRequest {
            max_iterations: 1, target_exploit_pct: 0.0, check_every: 1,
            algorithm, trust: Some(-1.0), sweep: None,
        };
        let err = start_solve(State(state.clone()), Json(req)).await.unwrap_err();
        assert_eq!(err.0, StatusCode::BAD_REQUEST);
        assert!(err.1.contains("prediction arenas"), "RAM gate was bypassed: {}", err.1);
        let current = lock_unpoisoned(&solver);
        assert_eq!(current.iteration, 1);
        assert_eq!(current.algo, Algorithm::PcfrPlus);
        assert!(!current.has_preds());
        assert!(lock_unpoisoned(&state.session).as_ref().unwrap().worker.is_none());
        assert_eq!(lock_unpoisoned(&state.status).state, "done");
    }

    // An explicit switch away must not be charged for predictions it will
    // not allocate. The invalid-trust sentinel still prevents worker launch.
    let req = SolveRequest {
        max_iterations: 1, target_exploit_pct: 0.0, check_every: 1,
        algorithm: Some("dcfr".into()), trust: Some(-1.0), sweep: None,
    };
    let err = start_solve(State(state.clone()), Json(req)).await.unwrap_err();
    assert!(err.1.contains("trust must be between"), "{}", err.1);
    assert_eq!(lock_unpoisoned(&solver).algo, Algorithm::Dcfr);
    assert!(!lock_unpoisoned(&solver).has_preds());
}

fn assert_bad_header_rejected_before_load(tag: &str, edit: impl FnOnce(&mut serde_json::Value)) {
    let config: SpotConfig = serde_json::from_str(r#"{
        "board":"QcJc9c3d2d", "range_oop":"AcKc,8h7h", "range_ip":"QdQh",
        "tree":{"starting_pot":100.0,"effective_stack":100.0,
            "oop":[{},{},{"bet":[{"PotPct":100.0}]}],"ip":[{},{},{}]}
    }"#).unwrap();
    let mut solver = Solver::new(Arc::new(Spot::new(config).unwrap()));
    let path = std::env::temp_dir().join(format!("gtopen-header-{tag}-{}.gto", std::process::id()));
    solver.save(path.to_str().unwrap()).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    let end = 10 + bytes[10..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[10..end]).unwrap();
    edit(&mut header);
    let mut bad = bytes[..10].to_vec();
    bad.extend_from_slice(serde_json::to_string(&header).unwrap().as_bytes());
    bad.extend_from_slice(&bytes[end..]);
    std::fs::write(&path, bad).unwrap();
    let load = Solver::load(path.to_str().unwrap());
    let peek = peek_save(path.to_str().unwrap(), 1000.0, Storage::F32);
    std::fs::remove_file(path).unwrap();
    assert!(matches!(load, Err(ref e) if e.starts_with("bad header:")));
    assert!(matches!(peek, Err(ref e) if e.starts_with("bad header:")),
        "preflight must reject {tag} before the live session can be discarded");
}

#[test]
fn peek_rejects_missing_iteration() {
    assert_bad_header_rejected_before_load("missing-iteration", |h| {
        h.as_object_mut().unwrap().remove("iteration");
    });
}

#[test]
fn peek_rejects_malformed_lock_labels() {
    assert_bad_header_rejected_before_load("bad-labels", |h| {
        h["lock_labels"] = serde_json::json!([[0, {"not": "a label string"}]]);
    });
}
