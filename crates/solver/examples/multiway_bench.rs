//! Three-player postflop benchmark: solve a spot from a JSON
//! `MwSpotConfig` and report tree size, memory and per-iteration speed.
//!
//! Usage: multiway_bench <config.json> [iterations] [check_every]
//! Env: SOLVER_STORAGE=f32|i16 (default i16), SOLVER_ALGO=dcfr|cfr+|pcfr+,
//!      SOLVER_ISO=0, SOLVER_GPU=1 (with --features gpu), SOLVER_VERIFY=1
//!      (re-check the GPU result's exploitability on the CPU),
//!      SOLVER_GPU_STORAGE=f32|i16 and SOLVER_GPU_GROUP=<cards per group>
//!      (override the GPU memory plan), SOLVER_GPU_MEM_GB (device budget),
//!      SOLVER_PROFILE=1 (per-kernel times, without CUDA graphs).

use solver::multiway::{MwSolver, MwSpot, MwSpotConfig};
use solver::{Algorithm, Storage};
use std::sync::Arc;
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let cfg: MwSpotConfig =
        serde_json::from_str(&std::fs::read_to_string(&args[1]).expect("read config")).expect("parse config");
    let iters: u32 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(100);
    let check: u32 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(25);
    let storage = match std::env::var("SOLVER_STORAGE").as_deref() {
        Ok("f32") => Storage::F32,
        _ => Storage::Compressed,
    };
    let algo = std::env::var("SOLVER_ALGO").map(|s| Algorithm::parse(&s).unwrap()).unwrap_or(Algorithm::Dcfr);
    let t0 = Instant::now();
    let spot = Arc::new(MwSpot::new(cfg).expect("build spot"));
    let e: u64 = spot.tree.data_size.iter().sum();
    println!(
        "built in {:.2}s: {} nodes, {} action nodes, {} arena entries, hands {:?}, suit perms {}",
        t0.elapsed().as_secs_f64(),
        spot.tree.nodes.len(),
        spot.num_action_nodes(),
        e,
        spot.hands.iter().map(|h| h.len()).collect::<Vec<_>>(),
        spot.suit_perms.len()
    );
    println!(
        "arenas: f32 {:.2} GB, compressed {:.2} GB",
        spot.arena_bytes(Storage::F32) as f64 / 1e9,
        spot.arena_bytes(Storage::Compressed) as f64 / 1e9
    );
    #[cfg(feature = "gpu")]
    if std::env::var("SOLVER_GPU").as_deref() == Ok("1") {
        let (full, min) = solver::multiway::gpu::estimate_device_bytes(&spot, algo);
        println!("gpu estimate: {:.2} GB resident f32, {:.2} GB minimum", full as f64 / 1e9, min as f64 / 1e9);
        let opts = solver::multiway::gpu::MwGpuOptions {
            storage: match std::env::var("SOLVER_GPU_STORAGE").as_deref() {
                Ok("f32") => Some(Storage::F32),
                Ok("i16") => Some(Storage::Compressed),
                _ => None,
            },
            budget_bytes: None,
            max_cards_per_group: std::env::var("SOLVER_GPU_GROUP").ok().and_then(|s| s.parse().ok()),
        };
        let ti = Instant::now();
        let mut gpu = solver::multiway::gpu::MwGpuSolver::with_options(spot.clone(), algo, &opts).expect("gpu init");
        println!("gpu: {} (init {:.1}s)", gpu.describe(), ti.elapsed().as_secs_f64());
        let profiling = std::env::var("SOLVER_PROFILE").as_deref() == Ok("1");
        gpu.set_profiling(profiling);
        let t = Instant::now();
        let mut solve_time = 0.0;
        for it in 1..=iters {
            let ti = Instant::now();
            gpu.iterate().expect("gpu iterate");
            gpu.synchronize().expect("gpu sync");
            solve_time += ti.elapsed().as_secs_f64();
            if it == 1 {
                println!("first iteration (includes JIT): {:.1} ms", solve_time * 1e3);
            }
            if it % check == 0 || it == iters {
                let te = Instant::now();
                let pr = gpu.progress(t.elapsed().as_secs_f64()).expect("gpu exploitability");
                println!(
                    "iter {:5} {:8.2}s  {:.2} ms/iter  exploit {:.3}% pot  gaps {:?}  (eval {:.0} ms)",
                    it,
                    pr.elapsed_secs,
                    solve_time * 1e3 / it as f64,
                    pr.exploit_pct_pot,
                    pr.gaps.map(|g| (g * 1000.0).round() / 1000.0),
                    te.elapsed().as_secs_f64() * 1e3
                );
            }
        }
        if profiling {
            println!("kernel profile (iterations and evaluations):");
            for (name, secs, n) in gpu.profile() {
                println!("  {name:16} {:9.1} ms  {n:7} launches", secs * 1e3);
            }
        }
        if std::env::var("SOLVER_VERIFY").as_deref() == Ok("1") {
            let s = gpu.to_cpu().expect("download");
            let pr = s.progress(0.0);
            println!("cpu check of gpu arenas: exploit {:.3}% pot", pr.exploit_pct_pot);
        }
        return;
    }
    let mut s = MwSolver::new(spot, storage);
    s.algo = algo;
    s.use_isomorphism = std::env::var("SOLVER_ISO").as_deref() != Ok("0");
    let t = Instant::now();
    let mut solve_time = 0.0;
    for it in 1..=iters {
        let ti = Instant::now();
        s.iterate();
        solve_time += ti.elapsed().as_secs_f64();
        if it % check == 0 || it == iters {
            let pr = s.progress(t.elapsed().as_secs_f64());
            println!(
                "iter {:5} {:8.2}s  {:.1} ms/iter  exploit {:.3}% pot  gaps {:?}",
                it,
                pr.elapsed_secs,
                solve_time * 1e3 / it as f64,
                pr.exploit_pct_pot,
                pr.gaps.map(|g| (g * 1000.0).round() / 1000.0)
            );
        }
    }
}
