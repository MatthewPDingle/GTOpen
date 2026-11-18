//! Print what the GPU's large-game mode would do with a Preflop Lab game.
//! No GPU needed: `cargo run --release --features gpu --example large_game_plan -- config.json [budget_mb]`
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::sync::Arc;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let config: PreflopConfig = serde_json::from_str(&std::fs::read_to_string(&args[1]).expect("config file")).expect("config json");
    let budget: u64 = args.get(2).and_then(|v| v.parse().ok()).unwrap_or(31_600);
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let data = std::fs::read(path).expect("equity table");
    let eq = Arc::new(EquityTable::load_or_build(path, u32::from_le_bytes(data[..4].try_into().unwrap())));
    use solver::preflop::gpu;
    // what the lab shows before the build (the size walk) and after it
    let est = solver::preflop::estimate_tree(&config).expect("size walk");
    let before = (gpu::minimum_need_of(&config, &est), gpu::large_need_of(&config, &est));
    let s = PreflopSolver::new(config, eq).expect("build");
    let t = std::time::Instant::now();
    let after = (gpu::minimum_need_mb(&s), gpu::large_need_mb(&s));
    eprintln!("{}", serde_json::json!({
        "normal_mb": { "size_walk": before.0, "built": after.0 },
        "large_game_mb": { "size_walk": before.1, "built": after.1 },
        "need_seconds": t.elapsed().as_secs_f64(),
    }));
    println!("{}", serde_json::to_string_pretty(&gpu::large_plan_report(&s, budget)).unwrap());
}
