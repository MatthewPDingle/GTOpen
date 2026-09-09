//! CUDA report continuation tests and a manual adaptation benchmark.
use super::*;
use solver::gpu::GpuSolver;
use solver::query::PostflopStats;

fn reference(board: &str, small: bool, storage: Storage) -> Solver {
    let mut cfg: SpotConfig = serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
    cfg.board = board.into();
    cfg.tree.rake_pct = 0.05;
    cfg.tree.rake_cap = 3.0;
    if small {
        cfg.range_oop = "QQ,JJ,TT,99,AhKh,AsKs,87s".into();
        cfg.range_ip = "AA,KK,AQs,JTs,T9s".into();
    }
    Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()), storage)
}

fn warm_and_lock(s: &mut Solver, iterations: u32) {
    let mut gpu = GpuSolver::new(s).expect("test requires CUDA");
    for _ in 0..iterations {
        gpu.iterate().unwrap();
    }
    gpu.sync_to_cpu(s).unwrap();
    drop(gpu);
    let profile = PostflopStats {
        cbet: [80.0, 60.0, 40.0],
        fold_to_bet: [65.0, 60.0, 55.0],
        raise_bet: 8.0,
        donk: 10.0,
        bet_size: "min".into(),
        contextual_betting: None,
    };
    assert!(s.lock_profile(1, &profile, Some(1)).unwrap().locked > 0);
}

#[test]
fn report_gpu_continuation_uses_additional_budget_and_keeps_locks() {
    for storage in [Storage::F32, Storage::Compressed] {
        let mut s = reference("Ks7h2dQh", true, storage);
        warm_and_lock(&mut s, 40);
        let locks = s.locks.clone();
        let stop = AtomicBool::new(false);
        let (iterations, pct, engine) = report_solve(&mut s, 21, 0.0, &stop);
        assert_eq!(engine, "gpu", "test requires CUDA and SOLVER_GPU != 0");
        assert_eq!(iterations, 61);
        assert_eq!(s.iteration, 61);
        assert_eq!(locks, s.locks);
        let cpu_pct = s.exploitability() / s.spot.tree.config.starting_pot * 100.0;
        assert!((cpu_pct - pct).abs() < 0.02, "CPU {cpu_pct} vs GPU {pct}");

        // A generous target must still check at 20 ADDITIONAL iterations,
        // not at the next absolute multiple of 20 or the first iteration.
        let (iterations, _, engine) = report_solve(&mut s, 30, f64::MAX, &stop);
        assert_eq!(engine, "gpu");
        assert_eq!(iterations, 81);

        stop.store(true, Ordering::Relaxed);
        let (iterations, pct, _) = report_solve(&mut s, 30, 0.0, &stop);
        assert_eq!(iterations, 81);
        assert_eq!(pct, -1.0, "stopped boards must be discarded");
        assert_eq!(locks, s.locks);
    }
}

#[test]
#[ignore = "manual CUDA report performance benchmark"]
fn report_adaptation_benchmark() {
    let mut s = reference("Ks7h2d", false, Storage::Compressed);
    warm_and_lock(&mut s, 40);
    let stop = AtomicBool::new(false);
    let start = std::time::Instant::now();
    let (iterations, exploit, engine) = report_solve(&mut s, 40, 0.0, &stop);
    let seconds = start.elapsed().as_secs_f64();
    assert_eq!(iterations, 80);
    println!(
        "REPORT_ADAPT engine={engine} nodes={} seconds={seconds:.3} iterations={iterations} exploit_pct={exploit:.9}",
        s.spot.tree.nodes.len(),
    );
}
