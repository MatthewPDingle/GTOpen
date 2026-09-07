//! Frozen generic-seat CUDA terminal benchmark (3/5/7/9 players). Run manually:
//! cargo test --release -p solver --features gpu --test preflop_generic_perf -- --ignored --nocapture
#![cfg(feature = "gpu")]

use solver::preflop::equity::EquityTable;
use solver::preflop::{gpu::PreflopGpu, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn config(n: usize) -> PreflopConfig {
    let mut posts = vec![0.0; n];
    posts[n - 2] = 0.5;
    posts[n - 1] = 1.0;
    PreflopConfig {
        positions: (0..n).map(|p| format!("P{p}")).collect(),
        stack: if n >= 7 { 150.0 } else { 100.0 },
        posts,
        ante: 0.0,
        limp: true,
        open_raises: vec![2.5, 4.0],
        raise_mults: vec![3.0],
        max_raises: if n >= 7 { 2 } else { 3 },
        add_allin: false,
        allin_threshold: 0.85,
        rake_pct: 5.0,
        rake_cap: 3.0,
        no_flop_no_drop: true,
        realization: if n == 6 { "static" } else { "calibrated" }.into(),
        call_only_seats: vec![],
        open_raises_by_seat: None,
        raise_mults_by_seat: None,
    }
}

fn fingerprint(values: impl IntoIterator<Item = u32>) -> u64 {
    values.into_iter().fold(0xcbf29ce484222325, |hash, bits| {
        bits.to_le_bytes().into_iter().fold(hash, |hash, byte| {
            (hash ^ byte as u64).wrapping_mul(0x100000001b3)
        })
    })
}

fn median(mut samples: Vec<f64>) -> f64 {
    samples.sort_by(f64::total_cmp);
    samples[samples.len() / 2]
}

#[test]
#[ignore = "manual CUDA performance benchmark"]
fn generic_seat_timings_and_fingerprints() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    for n in [3, 5, 7, 9] {
        let mut s = PreflopSolver::new(config(n), eq.clone()).unwrap();
        if n != 6 {
            assert!(s.fit.is_some(), "benchmark requires the calibrated fit");
        }
        let mut gpu = PreflopGpu::new(&s, 20000).expect("benchmark requires CUDA");
        for _ in 0..5 {
            gpu.iterate(&mut s).unwrap();
        }
        let mut iteration_ms = Vec::new();
        let mut check_ms = Vec::new();
        let mut sync_ms = Vec::new();
        let mut last = (Vec::new(), Vec::new());
        for _ in 0..3 {
            let start = Instant::now();
            for _ in 0..20 {
                // PreflopGpu::iterate synchronizes before returning.
                gpu.iterate(&mut s).unwrap();
            }
            iteration_ms.push(start.elapsed().as_secs_f64() * 1000.0 / 20.0);
            let start = Instant::now();
            last = gpu.gaps_and_evs().unwrap();
            check_ms.push(start.elapsed().as_secs_f64() * 1000.0);
            let start = Instant::now();
            gpu.sync_to_cpu(&mut s).unwrap();
            sync_ms.push(start.elapsed().as_secs_f64() * 1000.0);
        }
        let (regrets, strategy) = s.arena_snapshot();
        let hash = fingerprint(regrets.iter().chain(&strategy).map(|v| v.to_bits()));
        println!(
            "PERF seats={n} nodes={} iteration_ms={:.3} check_ms={:.3} sync_ms={:.3} arena_hash={hash:016x} gaps={:?} evs={:?}",
            s.nodes.len(), median(iteration_ms), median(check_ms), median(sync_ms), last.0, last.1,
        );
    }
}
