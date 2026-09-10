//! Separate frozen budget-control harness derived from pass3; never calls the app API.
//! Usage: preflop_budget_control INPUT ITERATIONS BUDGET_MB [--legacy]
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopConfig, PreflopSolver};
use std::{sync::Arc, time::Instant};

fn hash(values: impl Iterator<Item = u32>) -> String {
    let v = values.fold(0xcbf29ce484222325u64, |h, bits| {
        bits.to_le_bytes().iter().fold(h, |h, b| (h ^ *b as u64).wrapping_mul(0x100000001b3))
    });
    format!("{v:016x}")
}
fn memory_probe(context: &Option<Arc<cudarc::driver::CudaContext>>, stage: &str) {
    if let Some(ctx) = context {
        match ctx.mem_get_info() {
            Ok((free, total)) => println!("GPU_MEMORY {}", json!({
                "stage":stage,"free_bytes":free,"total_bytes":total,
                "used_bytes":total.saturating_sub(free),
                "scope":"CUDA driver free/total snapshot, not an OS residency or eviction measurement"
            })),
            Err(err) => println!("GPU_MEMORY {}", json!({"stage":stage,"query_error":format!("{err:?}")})),
        }
    }
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    assert!(args.len() >= 4, "usage: INPUT ITERATIONS BUDGET_MB [--legacy]");
    let input = &args[1];
    let count: u32 = args[2].parse().unwrap();
    assert!((1..=8).contains(&count), "bounded control requires 1..8 iterations");
    let budget: u64 = args[3].parse().unwrap();
    assert!([19000,21000,23000].contains(&budget), "control budget must be 19000,21000,23000 decimal MB");
    let memory_ctx = if std::env::var("PREFLOP_GPU_MEMORY_PROBE").as_deref() == Ok("1") {
        let t = Instant::now();
        let ctx = cudarc::driver::CudaContext::new(0).unwrap();
        println!("GPU_MEMORY {}",json!({"stage":"probe_context_created","ms":t.elapsed().as_secs_f64()*1000.0}));
        Some(ctx)
    } else { None };
    let roundtrip = format!("target/research-budget-control-roundtrip-{budget}.gtop");
    let bytes = std::fs::read("cache/preflop_eq169.bin").unwrap();
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let t = Instant::now();
    let mut s = if input.ends_with(".gtop") {
        PreflopSolver::load_game(input, eq.clone()).unwrap()
    } else {
        let v: Value = serde_json::from_slice(&std::fs::read(input).unwrap()).unwrap();
        let cfg: PreflopConfig = serde_json::from_value(v.get("config").unwrap_or(&v).clone()).unwrap();
        PreflopSolver::new(cfg, eq.clone()).unwrap()
    };
    if args.iter().any(|a| a == "--legacy") {
        s.set_multiway_equity_model("legacy_product").unwrap();
    }
    let build_ms = t.elapsed().as_secs_f64() * 1000.;
    if s.cfg.realization == "calibrated" { assert!(s.fit.is_some()); }
    memory_probe(&memory_ctx,"before_gpu_constructor");
    let t = Instant::now();
    let mut g = PreflopGpu::new(&s, budget).unwrap();
    let init_ms = t.elapsed().as_secs_f64() * 1000.;
    memory_probe(&memory_ctx,"after_gpu_constructor");
    println!("BENCH {}", json!({"phase":"init","budget_mb":budget,"harness":"budget-control-v1","memory_probe":memory_ctx.is_some(),"nodes":s.nodes.len(),"start_iteration":s.iteration,"model":s.multiway_equity_model(),"build_ms":build_ms,"init_ms":init_ms}));
    let mut times = Vec::new();
    for _ in 0..count {
        let t = Instant::now();
        g.iterate(&mut s).unwrap();
        let ms = t.elapsed().as_secs_f64() * 1000.;
        times.push(ms);
        println!("BENCH {}", json!({"phase":"iterate","iteration":s.iteration,"ms":ms}));
    }
    memory_probe(&memory_ctx,"after_iterations");
    let t = Instant::now();
    let (gaps, evs) = g.gaps_and_evs().unwrap();
    let check_ms = t.elapsed().as_secs_f64() * 1000.;
    memory_probe(&memory_ctx,"after_check");
    let t = Instant::now();
    g.sync_to_cpu(&mut s).unwrap();
    let sync_ms = t.elapsed().as_secs_f64() * 1000.;
    let (regret, strategy) = s.arena_snapshot();
    let fingerprint = hash(regret.iter().chain(&strategy).map(|v|v.to_bits()));
    drop(regret); drop(strategy); drop(g);
    memory_probe(&memory_ctx,"after_gpu_drop");
    let t = Instant::now();
    s.save_game(&roundtrip).unwrap();
    let save_ms = t.elapsed().as_secs_f64()*1000.;
    let save_bytes = std::fs::metadata(&roundtrip).unwrap().len();
    drop(s);
    let t = Instant::now();
    let loaded = PreflopSolver::load_game(&roundtrip,eq).unwrap();
    let load_ms = t.elapsed().as_secs_f64()*1000.;
    let (r, s) = loaded.arena_snapshot();
    assert_eq!(fingerprint, hash(r.iter().chain(&s).map(|v|v.to_bits())), "save roundtrip");
    println!("BENCH {}",json!({"phase":"result","budget_mb":budget,"harness":"budget-control-v1","iteration":loaded.iteration,"times_ms":times,"check_ms":check_ms,"sync_ms":sync_ms,"save_ms":save_ms,"load_ms":load_ms,"save_bytes":save_bytes,"arena_hash":fingerprint,"gaps":gaps,"evs":evs}));
}
