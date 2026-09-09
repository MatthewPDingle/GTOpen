//! Small, reproducible continuation-value audit, isolated from app sessions.
//! Run from repository root: cargo run --release -p solver --example continuation_audit
//! Optional environment: AUDIT_CASE, AUDIT_BOARD, AUDIT_MAX_ITERATIONS (default 250).
use serde_json::{json, Value};
use solver::preflop::equity::{class_index, EquityTable, NUM_CLASSES};
use solver::preflop::RealizationFit;
use solver::{combo_index, parse_sizes, rank, suit, Range, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;

const OUT: &str = "research/preflop-evolution/continuation/results.json";

fn distribution(text: &str) -> Vec<f32> {
    let range = Range::parse(text).unwrap();
    let mut weights = vec![0.0; NUM_CLASSES];
    for a in 0..52u8 { for b in a + 1..52u8 {
        weights[class_index(rank(a), rank(b), suit(a) == suit(b))] += range.weights[combo_index(a, b)];
    }}
    let total: f32 = weights.iter().sum();
    assert!(total > 0.0);
    weights.iter_mut().for_each(|v| *v /= total);
    weights
}

// Mirrors the current HU POT_SHARE formula in preflop/mod.rs. Deliberately
// retains its independent class-marginal aggregation; do not silently replace
// that with the exact compatible-pair weighting used by the reference below.
fn leaf_prices(ranges: [&str; 2], pot: f64, stack: f64, rake_pct: f64, cap: f64,
               eq: &EquityTable, fit: &RealizationFit) -> Value {
    let distributions = ranges.map(distribution);
    let rake = if cap > 0.0 { (pot * rake_pct / 100.0).min(cap) } else { pot * rake_pct / 100.0 };
    let mut raw = [0.0; 2];
    let mut positional = [0.0; 2];
    let mut calibrated = [0.0; 2];
    let mut equities = [0.0; 2];
    for p in 0..2 {
        let posw = (1.0 + 0.16 * (p as f64 - 0.5) * ((stack / pot).min(8.0) / 8.0)) as f32 as f64;
        let values: Vec<f32> = (0..NUM_CLASSES).map(|k| eq.eq_vs_dist(k, &distributions[1-p])).collect();
        for k in 0..NUM_CLASSES {
            let weight = distributions[p][k] as f64;
            let equity = values[k] as f64;
            equities[p] += weight * equity;
            raw[p] += weight * (pot-rake) * equity;
            positional[p] += weight * ((pot-rake) * equity * posw).min(pot-rake);
            calibrated[p] += weight * pot * equity * fit.class_r(k, posw);
        }
    }
    // Cached diagonal matchups are finite Monte Carlo estimates, so even
    // symmetric ranges can differ very slightly from an exact half share.
    assert!((raw.iter().sum::<f64>() - (pot-rake)).abs() < 0.01 * pot);
    json!({"equity": equities, "raw_bb": raw, "static_bb": positional,
           "calibrated_bb": calibrated, "rake_on_starting_pot_bb": rake})
}

fn sizing() -> StreetSizing {
    StreetSizing {bet: parse_sizes("50").unwrap(), raise: parse_sizes("100").unwrap(), donk: vec![]}
}

fn write_progress(records: &[Value], complete: bool) {
    std::fs::create_dir_all(Path::new(OUT).parent().unwrap()).unwrap();
    let result = json!({"schema": 1, "complete": complete, "engine": "CPU DCFR f32",
        "threads": 4, "units": "bb, gross-pot-share convention; preflop sunk investment not subtracted",
        "design": "Two fixed reaching-range fixtures, three purposively selected flops, paired 0%/5% capped rake. Not an all-flop EV estimator.",
        "postflop_weighting": "Each hand weighted by reach * valid opponent mass; all turn/river runouts enumerated within the configured betting abstraction.",
        "preflop_weighting": "Current engine independent class marginals with its cached 20,000-sample-per-matchup equity table.",
        "records": records});
    std::fs::write(OUT, serde_json::to_string_pretty(&result).unwrap()).unwrap();
}

fn main() {
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    // Refuse to regenerate/overwrite the user's cached equity table implicitly.
    let eq_path = "cache/preflop_eq169.bin";
    let bytes = std::fs::read(eq_path).expect("run from repository root with existing equity cache");
    assert_eq!(bytes.len(), 4 + NUM_CLASSES * NUM_CLASSES * 4);
    assert_eq!(u32::from_le_bytes(bytes[..4].try_into().unwrap()), 20_000);
    let eq = EquityTable::load_or_build(eq_path, 20_000);
    let fit = RealizationFit::load_default().expect("calibrated fit is required, no silent fallback");
    let cases = [
        ("symmetric", "88+,ATs+,KQs,AQo+", "88+,ATs+,KQs,AQo+"),
        ("caller_vs_raiser", "22-JJ,A2s-AQs,KTs+,QTs+,JTs,T9s,98s,87s,AJo-AQo,KQo", "88+,ATs+,KQs,AQo+"),
    ];
    let max_iterations = std::env::var("AUDIT_MAX_ITERATIONS").ok().map(|s| s.parse::<u32>().unwrap()).unwrap_or(250);
    let mut records = Vec::new();
    for (case, oop, ip) in cases {
        if std::env::var("AUDIT_CASE").is_ok_and(|value| value != case) {continue;}
        for board in ["As7h2d", "Ts9s8d", "7s7h2d"] {
            if std::env::var("AUDIT_BOARD").is_ok_and(|value| value != board) {continue;}
            for rake in [0.0, 5.0] {
                let pot = 20.0;
                let stack = 80.0;
                let cap = 3.0;
                let leaf = leaf_prices([oop, ip], pot, stack, rake, cap, &eq, &fit);
                let cfg = SpotConfig {board: board.into(), range_oop: oop.into(), range_ip: ip.into(), tree: TreeConfig {
                    starting_pot: pot, effective_stack: stack, rake_pct: rake/100.0, rake_cap: cap,
                    oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
                    max_raises: 1, add_allin: false, ..Default::default()
                }};
                eprintln!("building {case} {board} rake {rake}%");
                let started = Instant::now();
                let mut solver = Solver::new(Arc::new(Spot::new(cfg.clone()).unwrap()));
                let build_seconds = started.elapsed().as_secs_f64();
                let arena_bytes = solver.arena_bytes();
                let tree_bytes = solver.spot.tree_bytes();
                let solve_start = Instant::now();
                let mut convergence = Vec::new();
                let mut gap_pct = f64::INFINITY;
                while solver.iteration < max_iterations {
                    solver.iterate();
                    if solver.iteration % 25 == 0 || solver.iteration == max_iterations {
                        gap_pct = solver.exploitability()/pot*100.0;
                        eprintln!("{case} {board} rake {rake}% iteration {} gap {gap_pct:.5}% elapsed {:.1}s", solver.iteration, solve_start.elapsed().as_secs_f64());
                        convergence.push(json!({"iteration": solver.iteration, "gap_pct_pot": gap_pct, "seconds": solve_start.elapsed().as_secs_f64()}));
                        if gap_pct <= 0.3 {break;}
                    }
                }
                let solve_seconds = solve_start.elapsed().as_secs_f64();
                let query_start = Instant::now();
                let view = solver.node_view(&[]).unwrap();
                let mut ev = [0.0; 2];
                let mut equity = [0.0; 2];
                let mut pair_mass = [0.0; 2];
                for p in 0..2 {for hand in &view.players[p].hands {
                    let weight = hand.reach as f64 * hand.valid as f64;
                    if weight <= 0.0 {continue;}
                    pair_mass[p] += weight;
                    ev[p] += weight * hand.ev.unwrap() as f64;
                    equity[p] += weight * hand.eq.unwrap() as f64;
                }
                    ev[p] /= pair_mass[p]; equity[p] /= pair_mass[p];
                }
                assert!((pair_mass[0] - pair_mass[1]).abs() < 1e-4);
                assert!((equity.iter().sum::<f64>() - 1.0).abs() < 1e-4);
                let expected_rake = pot - ev.iter().sum::<f64>();
                assert!(expected_rake >= -1e-3 && expected_rake <= cap + 1e-3);
                if rake == 0.0 {assert!(expected_rake.abs() < 1e-3);}
                records.push(json!({"case": case, "board": board, "rake_pct": rake,
                    "config": cfg, "preflop_leaf": leaf, "reference_ev_bb": ev,
                    "reference_equity": equity, "compatible_pair_mass": pair_mass[0],
                    "reference_expected_rake_bb": expected_rake,
                    "iterations": solver.iteration, "gap_pct_pot": gap_pct, "target_met": gap_pct <= 0.3,
                    "build_seconds": build_seconds, "solve_seconds": solve_seconds,
                    "query_seconds": query_start.elapsed().as_secs_f64(),
                    "arena_bytes": arena_bytes, "tree_bytes": tree_bytes,
                    "nodes": solver.spot.tree.nodes.len(), "convergence": convergence}));
                write_progress(&records, false);
            }
        }
    }
    write_progress(&records, true);
}
