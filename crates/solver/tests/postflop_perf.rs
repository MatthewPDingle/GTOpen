//! Manual postflop CUDA benchmark on the shared reference spot.
//! cargo test --release -p solver --features gpu --test postflop_perf -- --ignored --nocapture
#![cfg(feature = "gpu")]

use solver::gpu::GpuSolver;
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;
use std::time::Instant;

fn median(mut samples: Vec<f64>) -> f64 {
    samples.sort_by(f64::total_cmp);
    samples[samples.len() / 2]
}

#[test]
#[ignore = "manual CUDA performance benchmark"]
fn postflop_timings() {
    for (board, rake) in [("Ks7h2d", 0.0), ("Ks7s2d", 0.05), ("Ks7h2dQhTc", 0.05)] {
        let mut cfg: SpotConfig = serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
        cfg.board = board.into();
        cfg.tree.rake_pct = rake;
        cfg.tree.rake_cap = 3.0;
        let mut s = Solver::new(Arc::new(Spot::new(cfg).unwrap()));
        let start = Instant::now();
        let mut gpu = GpuSolver::new(&s).expect("benchmark requires CUDA");
        gpu.synchronize().unwrap();
        let init_ms = start.elapsed().as_secs_f64() * 1000.0;
        if std::env::var_os("POSTFLOP_PERF_CONVERGENCE").is_some() {
            let start = Instant::now();
            loop {
                gpu.iterate().unwrap();
                if gpu.iteration % 20 == 0 {
                    let pct = gpu.exploitability(&s).unwrap()
                        / s.spot.tree.config.starting_pot * 100.0;
                    println!("CONVERGENCE board={board} iteration={} pct={pct:.9}", gpu.iteration);
                    if pct <= 0.3 || gpu.iteration >= 400 {
                        println!(
                            "POSTFLOP_TARGET board={board} iteration={} seconds={:.3} pct={pct:.9}",
                            gpu.iteration, start.elapsed().as_secs_f64(),
                        );
                        assert!(pct <= 0.3, "benchmark did not converge within 400 iterations");
                        break;
                    }
                }
            }
            continue;
        }
        for _ in 0..5 {
            gpu.iterate().unwrap();
        }
        gpu.synchronize().unwrap();
        let mut iteration_ms = Vec::new();
        let mut check_ms = Vec::new();
        let mut exploit = 0.0;
        for _ in 0..3 {
            let start = Instant::now();
            for _ in 0..20 {
                gpu.iterate().unwrap();
            }
            gpu.synchronize().unwrap();
            iteration_ms.push(start.elapsed().as_secs_f64() * 1000.0 / 20.0);
            let start = Instant::now();
            exploit = gpu.exploitability(&s).unwrap();
            check_ms.push(start.elapsed().as_secs_f64() * 1000.0);
        }
        gpu.sync_to_cpu(&mut s).unwrap();
        println!(
            "POSTFLOP board={board} rake={rake} nodes={} init_ms={init_ms:.3} iteration_ms={:.3} check_ms={:.3} exploit_chips={exploit:.9}",
            s.spot.tree.nodes.len(), median(iteration_ms), median(check_ms),
        );
        // A synchronized kernel profile distinguishes launch overhead from
        // showdown work. These diagnostic iterations are outside the timings.
        let profile = gpu.iterate_profiled().unwrap();
        println!("KERNELS board={board} ms={:?}", profile.ms);
    }
}
