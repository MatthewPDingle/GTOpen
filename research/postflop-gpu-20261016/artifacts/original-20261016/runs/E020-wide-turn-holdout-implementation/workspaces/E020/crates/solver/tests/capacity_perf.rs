//! Fixed capacity and initialization controls added before reach-storage trials.
#![cfg(feature = "gpu")]
use cudarc::driver::CudaContext;
use solver::preflop::{equity::EquityTable, gpu::{PreflopGpu, vram_estimate_mb}, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

#[test]
#[ignore = "manual GPU capacity measurement"]
fn preflop_capacity() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    let ctx = CudaContext::new(0).unwrap();
    for n in [6, 8] {
        let mut posts = vec![0.0; n];
        posts[n-2] = 0.5;
        posts[n-1] = 1.0;
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
            "stack":if n==8 {150.0} else {100.0}, "posts":posts, "limp":true,
            "open_raises":[2.5,4.0], "raise_mults":[3.0], "max_raises":if n==8 {2} else {3},
            "allin_threshold":0.85, "add_allin":false, "rake_pct":5.0, "rake_cap":3.0,
            "realization":if n==6 {"static"} else {"calibrated"}
        })).unwrap();
        let start = Instant::now();
        let mut s = PreflopSolver::new(cfg, eq.clone()).unwrap();
        let build_ms = start.elapsed().as_secs_f64() * 1000.0;
        let estimate = vram_estimate_mb(&s);
        ctx.synchronize().unwrap();
        let free_before = ctx.mem_get_info().unwrap().0;
        let start = Instant::now();
        let gpu = PreflopGpu::new(&s, 20000).unwrap();
        ctx.synchronize().unwrap();
        let init_ms = start.elapsed().as_secs_f64() * 1000.0;
        let free_after = ctx.mem_get_info().unwrap().0;
        gpu.sync_to_cpu(&mut s).unwrap();
        let prefix = format!("preflop.{n}");
        println!("METRIC_JSON {}", serde_json::json!({
            "metrics":{
                format!("{prefix}.build_ms"):build_ms,
                format!("{prefix}.init_ms"):init_ms,
                format!("{prefix}.estimated_vram_mb"):estimate,
                format!("{prefix}.allocated_vram_mb"):free_before.saturating_sub(free_after) as f64 / 1e6,
                format!("{prefix}.cpu_arena_mb"):s.arena_mb()
            }, "nodes":s.nodes.len(), "seats":n,
            "note":"Allocated VRAM is device free-memory delta; estimate is the engine preflight formula."
        }));
        drop(gpu);
        ctx.synchronize().unwrap();
    }
}
