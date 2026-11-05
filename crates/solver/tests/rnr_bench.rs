//! Manual benchmark for "trust the read" (rnr.rs) on the bench flop:
//! iteration cost with the dial on versus the plain and the locked solve,
//! and a warm-started trust sweep (p = 1 down to 0) with its readouts.
//!   cargo test --release -p solver --features gpu --test rnr_bench -- --ignored --nocapture

#![cfg(feature = "gpu")]

use solver::gpu::GpuSolver;
use solver::query::PostflopStats;
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;
use std::time::Instant;

fn station_folder() -> PostflopStats {
    // folds too much to bets, rarely raises, c-bets a lot
    PostflopStats {
        contextual_betting: None,
        cbet: [75.0, 60.0, 50.0],
        fold_to_bet: [60.0, 60.0, 65.0],
        raise_bet: 3.0,
        donk: 10.0,
        bet_size: "min".into(),
    }
}

fn ms_per_iteration(gpu: &mut GpuSolver, n: u32) -> f64 {
    for _ in 0..3 {
        gpu.iterate().unwrap();
    }
    gpu.synchronize().unwrap();
    let t = Instant::now();
    for _ in 0..n {
        gpu.iterate().unwrap();
    }
    gpu.synchronize().unwrap();
    t.elapsed().as_secs_f64() * 1000.0 / n as f64
}

/// Iterate until the solve's exploitability is at most `target` % pot.
fn run_to(gpu: &mut GpuSolver, host: &Solver, target: f64, every: u32, max: u32) -> (u32, f64, f64) {
    let pot = host.spot.tree.config.starting_pot;
    let t = Instant::now();
    let mut done = 0;
    loop {
        for _ in 0..every {
            gpu.iterate().unwrap();
        }
        done += every;
        let x = gpu.exploitability(host).unwrap() / pot * 100.0;
        if x <= target || done >= max {
            return (done, t.elapsed().as_secs_f64(), x);
        }
    }
}

#[test]
#[ignore]
fn rnr_bench_flop() {
    let mut cfg: SpotConfig = serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
    cfg.board = "Ks7h2d".into();
    let target = 0.3;
    let mut host = Solver::new(Arc::new(Spot::new(cfg).unwrap()));
    let pot = host.spot.tree.config.starting_pot;

    let mut gpu = GpuSolver::new(&host).unwrap();
    let (n, secs, x) = run_to(&mut gpu, &host, target, 20, 4000);
    let ms_plain = ms_per_iteration(&mut gpu, 20);
    println!("plain solve: {n} iterations, {secs:.1} s, {x:.3}% pot; {ms_plain:.2} ms/iteration");

    gpu.sync_to_cpu(&mut host).unwrap();
    host.ensure_symmetric();
    let t = Instant::now();
    let summary = host.lock_profile(1, &station_folder(), Some(1)).unwrap();
    println!("profile lock on IP: {} nodes in {:.1} s", summary.locked, t.elapsed().as_secs_f64());
    gpu.update_locks(&host).unwrap();
    let ms_locked = ms_per_iteration(&mut gpu, 20);

    println!("trust, iterations, seconds, exploit % pot, hero EV vs read, villain BR EV, hero worst case (chips; pot {pot})");
    let mut ms_rnr = 0.0;
    for (k, trust) in [1.0f32, 0.9, 0.8, 0.7, 0.5, 0.25, 0.0].into_iter().enumerate() {
        host.set_trust(Some(trust)).unwrap();
        gpu.update_locks(&host).unwrap();
        if k == 1 {
            ms_rnr = ms_per_iteration(&mut gpu, 20);
        }
        let (n, secs, x) = run_to(&mut gpu, &host, target, 20, 4000);
        let t = Instant::now();
        let r = gpu.trust_readout(&host).unwrap();
        let readout_s = t.elapsed().as_secs_f64();
        println!(
            "{trust:.2}, {n}, {secs:.1}, {x:.3}, {:.3}, {:.3}, {:?} (readout {readout_s:.2} s)",
            r.hero_ev_vs_read, r.villain_best_response_ev, r.hero_worst_case_ev
        );
    }
    println!(
        "ms/iteration: plain {ms_plain:.2}, locked {ms_locked:.2}, trust 0.9 {ms_rnr:.2} ({:+.1}% vs locked)",
        (ms_rnr / ms_locked - 1.0) * 100.0
    );
}

fn bench_spot() -> Arc<Spot> {
    let mut cfg: SpotConfig = serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
    cfg.board = "Ks7h2d".into();
    Arc::new(Spot::new(cfg).unwrap())
}

/// On the bench flop, trust 0 must track the unlocked GPU solve iteration
/// for iteration, and a direct (not warm-swept) trust 0.5 solve must
/// converge; its GPU readout is checked against the CPU on the same arenas.
#[test]
#[ignore]
fn rnr_bench_trust_zero_tracks_unlocked() {
    let spot = bench_spot();
    let pot = spot.tree.config.starting_pot;
    let warm = |s: &mut Solver| {
        let mut g = GpuSolver::new(s).unwrap();
        for _ in 0..100 {
            g.iterate().unwrap();
        }
        g.sync_to_cpu(s).unwrap();
        s.ensure_symmetric();
    };
    let mut a = Solver::new(spot.clone());
    let mut b = Solver::new(spot.clone());
    warm(&mut a);
    warm(&mut b);
    a.lock_profile(1, &station_folder(), Some(1)).unwrap();
    a.set_trust(Some(0.0)).unwrap();
    b.restart_averages();
    let mut ga = GpuSolver::new(&a).unwrap();
    let mut gb = GpuSolver::new(&b).unwrap();
    println!("iterations, trust 0 exploit % pot, unlocked exploit % pot");
    for k in 1..=10 {
        for _ in 0..100 {
            ga.iterate().unwrap();
            gb.iterate().unwrap();
        }
        let xa = ga.exploitability(&a).unwrap() / pot * 100.0;
        let xb = gb.exploitability(&b).unwrap() / pot * 100.0;
        println!("{}, {xa:.4}, {xb:.4}", k * 100);
    }
    drop((ga, gb));

    for trust in [0.5f32, 0.9] {
        let mut s = Solver::new(spot.clone());
        warm(&mut s);
        s.lock_profile(1, &station_folder(), Some(1)).unwrap();
        s.set_trust(Some(trust)).unwrap();
        let mut g = GpuSolver::new(&s).unwrap();
        println!("direct trust {trust}: iterations, exploit % pot");
        for k in 1..=10 {
            for _ in 0..200 {
                g.iterate().unwrap();
            }
            println!("  {}, {:.4}", k * 200, g.exploitability(&s).unwrap() / pot * 100.0);
        }
        let gr = g.trust_readout(&s).unwrap();
        g.sync_to_cpu(&mut s).unwrap();
        s.ensure_symmetric();
        let t = Instant::now();
        let cr = s.trust_readout().unwrap();
        println!("  gpu readout {gr:?}\n  cpu readout {cr:?} ({:.1} s)", t.elapsed().as_secs_f64());
    }
}
