//! Times CPU iterations of an 8-handed tournament tree under chip EV and
//! under ICM payouts. `cargo run --release -p solver --example icm_cpu_bench -- [stack] [iters]`
use solver::preflop::{equity::EquityTable, IcmConfig, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let stack: f64 = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(25.0);
    let iters: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(50);
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["UTG", "UTG1", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
        "posts": [0, 0, 0, 0, 0, 0, 0.5, 1], "stack": stack, "ante": 0.125,
        "open_raises": [2.0], "raise_mults": [2.5], "max_raises": 3, "add_allin": true,
        "realization": "balanced"
    }))
    .unwrap();
    // A standard-looking 8-player final table.
    let payouts = vec![30.0, 20.0, 14.0, 10.5, 8.0, 6.5, 5.5, 5.5];
    let only = args.get(3).cloned().unwrap_or_default();
    for (label, icm) in [("chip EV", None), ("ICM", Some(IcmConfig { payouts: payouts.clone(), field: vec![], field_groups: vec![] }))] {
        if !only.is_empty() && !label.to_lowercase().starts_with(&only) {
            continue;
        }
        let mut c = cfg.clone();
        c.icm = icm;
        let t = Instant::now();
        let mut s = PreflopSolver::new(c, eq.clone()).unwrap();
        let build = t.elapsed().as_secs_f64();
        println!("{label}: built {} nodes in {build:.2}s", s.nodes.len());
        let t = Instant::now();
        for _ in 0..iters {
            s.iterate();
        }
        let per = t.elapsed().as_secs_f64() / iters as f64;
        println!("{label}: {} nodes, build {build:.2}s, {:.1} ms/iteration", s.nodes.len(), per * 1e3);
    }
}
