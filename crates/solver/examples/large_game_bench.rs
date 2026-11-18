//! Time a Preflop Lab game on the CPU, the normal GPU plan or the GPU's
//! large-game mode, and fingerprint the solve so two runs can be compared
//! bit for bit.
//!
//! cargo run --release --features gpu -p solver --example large_game_bench -- config.json MODE [iterations] [parts]
//!   MODE  cpu | auto (what the app picks) | normal | large
//!   parts pins the large-game cut (2, 3, 4, 6, 8, 12, 16, ...)
//! Env: BENCH_BUDGET_MB (default: free graphics memory less 512 MB),
//!      BENCH_PIN=batch,cache (large mode: e.g. "32,true", to match a normal run's layout).
use solver::preflop::gpu::PreflopGpu;
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn fingerprint(s: &PreflopSolver) -> String {
    let (regrets, strategy) = s.arena_snapshot();
    let hash = regrets.iter().chain(&strategy).fold(0xcbf29ce484222325u64, |h, x| {
        x.to_bits().to_le_bytes().iter().fold(h, |h, b| (h ^ *b as u64).wrapping_mul(0x100000001b3))
    });
    format!("{hash:016x}")
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("usage: large_game_bench config.json cpu|auto|normal|large [iterations] [parts]");
        std::process::exit(2);
    }
    let config: PreflopConfig = serde_json::from_str(&std::fs::read_to_string(&args[1]).expect("config file")).expect("config json");
    let mode = args[2].as_str();
    let iterations: u32 = args.get(3).and_then(|v| v.parse().ok()).unwrap_or(10);
    let parts: Option<usize> = args.get(4).and_then(|v| v.parse().ok());
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let data = std::fs::read(path).expect("equity table");
    let eq = Arc::new(EquityTable::load_or_build(path, u32::from_le_bytes(data[..4].try_into().unwrap())));
    let t = Instant::now();
    let mut s = PreflopSolver::new(config, eq).expect("build");
    println!("{}", serde_json::json!({"event": "built", "nodes": s.nodes.len(), "tables_mb": s.arena_mb(), "seconds": t.elapsed().as_secs_f64()}));

    if mode == "cpu" {
        let mut times = Vec::new();
        for _ in 0..iterations {
            let t = Instant::now();
            s.iterate();
            times.push(t.elapsed().as_secs_f64());
            println!("{}", serde_json::json!({"event": "iteration", "engine": "cpu", "iteration": s.iteration, "seconds": times.last()}));
        }
        let t = Instant::now();
        let (gaps, evs) = s.gaps_and_evs();
        println!("{}", serde_json::json!({"event": "done", "engine": "cpu", "iteration_seconds": times, "check_seconds": t.elapsed().as_secs_f64(),
            "gap_total": gaps.iter().sum::<f64>(), "gaps": gaps, "evs": evs, "fingerprint": fingerprint(&s)}));
        return;
    }

    let budget: u64 = std::env::var("BENCH_BUDGET_MB").ok().and_then(|v| v.parse().ok()).unwrap_or_else(|| {
        let (free, _) = solver::gpu::vram_info_mb().expect("no CUDA card");
        free.saturating_sub(512)
    });
    let pin: Option<(usize, bool)> = std::env::var("BENCH_PIN").ok().map(|v| {
        let (batch, cache) = v.split_once(',').expect("BENCH_PIN=batch,cache");
        (batch.trim().parse().expect("batch"), cache.trim().parse().expect("cache true|false"))
    });
    println!("{}", serde_json::json!({"event": "need", "budget_mb": budget,
        "normal_least_mb": solver::preflop::gpu::minimum_need_mb(&s), "large_least_mb": solver::preflop::gpu::large_need_mb(&s)}));
    let t = Instant::now();
    let (mut g, selection) = match mode {
        "auto" => {
            let (g, selection) = PreflopGpu::new_throughput(&s, budget).expect("gpu");
            (g, serde_json::to_value(&selection).unwrap())
        }
        "normal" => (PreflopGpu::new(&s, budget).expect("normal plan"), serde_json::json!("normal")),
        "large" => (PreflopGpu::new_large_pinned(&s, budget, parts, pin).expect("large-game mode"), serde_json::json!("large")),
        other => panic!("unknown mode {other}"),
    };
    println!("{}", serde_json::json!({"event": "engine", "selection": selection, "large_game": g.large_game(),
        "multiway_batch": g.layout().0, "hu_equity_cache": g.layout().1, "seconds": t.elapsed().as_secs_f64()}));
    let (mut times, mut refreshes) = (Vec::new(), Vec::new());
    for _ in 0..iterations {
        let t = Instant::now();
        g.iterate(&mut s).expect("iterate");
        times.push(t.elapsed().as_secs_f64());
        println!("{}", serde_json::json!({"event": "iteration", "engine": mode, "iteration": s.iteration, "seconds": times.last()}));
        // learned flop values: the host refreshes them from the device's averages, as the app does
        if s.leaf_refresh_due(s.iteration) {
            let t = Instant::now();
            g.sync_to_cpu(&mut s).expect("sync");
            s.refresh_leaf_values();
            g.upload_leaf_corr(&s).expect("upload");
            refreshes.push(t.elapsed().as_secs_f64());
        }
    }
    let t = Instant::now();
    let (gaps, evs) = g.gaps_and_evs().expect("evaluate");
    let first_check = t.elapsed().as_secs_f64();
    let t = Instant::now();
    g.gaps_and_evs().expect("evaluate");
    let check = t.elapsed().as_secs_f64();
    g.sync_to_cpu(&mut s).expect("sync");
    println!("{}", serde_json::json!({"event": "done", "engine": mode, "large_game": g.large_game(),
        "multiway_batch": g.layout().0, "hu_equity_cache": g.layout().1,
        "iteration_seconds": times, "refresh_seconds": refreshes, "first_check_seconds": first_check, "check_seconds": check,
        "gap_total": gaps.iter().sum::<f64>(), "gaps": gaps, "evs": evs, "fingerprint": fingerprint(&s)}));
}
