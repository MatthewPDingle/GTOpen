//! Solve one preflop game with and without blockers (card removal) on the
//! CPU and compare speed, gap and how many hands each seat mixes first in.
//!
//! cargo run --release -p solver --example blockers_compare -- [GAME.json] [ITERATIONS]
//!
//! GAME.json is a PreflopConfig ("-" or nothing: a 6-max 100 bb game with
//! the static realization). Run from the repo root so `cache/` resolves.
use solver::preflop::equity::{class_label, EquityTable, NUM_CLASSES};
use solver::preflop::{PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let cfg: PreflopConfig = match args.first().filter(|path| path.as_str() != "-") {
        Some(path) => serde_json::from_slice(&std::fs::read(path).expect("read game")).expect("parse game"),
        None => serde_json::from_value(serde_json::json!({
            "positions": ["UTG", "HJ", "CO", "BTN", "SB", "BB"], "posts": [0, 0, 0, 0, 0.5, 1.0],
            "stack": 100.0, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
            "add_allin": true, "realization": "static", "rake_pct": 5.0, "rake_cap": 3.0
        })).unwrap(),
    };
    let iterations: usize = args.get(1).map_or(300, |v| v.parse().expect("iterations"));
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 2000));
    for blockers in [false, true] {
        let mut c = cfg.clone();
        c.card_removal = blockers;
        let mut s = PreflopSolver::new(c, eq.clone()).expect("game");
        let start = Instant::now();
        for _ in 0..iterations {
            s.iterate();
        }
        let secs = start.elapsed().as_secs_f64();
        let gap: f64 = s.br_gaps().iter().sum();
        println!("blockers {blockers}: {:.1} ms per iteration, gap {gap:.4} bb", 1000.0 * secs / iterations as f64);
        // The first-in seat's mixed hands (folds 5-95% of the time).
        let root = 0;
        let sigma = s.average_strategy(root);
        let na = sigma.len() / NUM_CLASSES;
        let fold = (0..na).find(|&a| s.nodes[root].actions[a].kind == "fold");
        let mixed: Vec<String> = (0..NUM_CLASSES)
            .filter(|&h| fold.is_some_and(|f| (0.05..0.95).contains(&sigma[f * NUM_CLASSES + h])))
            .map(class_label)
            .collect();
        println!("  first in mixes {} hands: {}", mixed.len(), mixed.join(" "));
    }
}
