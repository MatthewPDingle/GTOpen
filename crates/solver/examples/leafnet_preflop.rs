//! Solve a preflop game under "balanced" and "leafnet" and compare.
//!
//!     cargo run --release --example leafnet_preflop -- GAME.json ITERATIONS [EVERY] [leaf-only]
//!
//! GAME.json is a PreflopConfig (its realization is ignored). EVERY is the
//! refresh interval (default 50). Prints each
//! leaf refresh, the time it took, and the open/defend frequencies that
//! moved most at the root's first decisions.
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 3 {
        return Err("usage: leafnet_preflop GAME.json ITERATIONS".into());
    }
    let text = std::fs::read_to_string(&a[1]).map_err(|e| e.to_string())?;
    let iterations: u32 = a[2].parse().map_err(|_| "ITERATIONS must be a number")?;
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let every: u32 = a.get(3).and_then(|v| v.parse().ok()).unwrap_or(50);
    let leaf_only = a.get(4).map_or(false, |v| v == "leaf-only");
    let mut solved = Vec::new();
    for realization in ["balanced", "leafnet"] {
        if leaf_only && realization == "balanced" {
            continue;
        }
        let mut cfg: PreflopConfig = serde_json::from_str(&text).map_err(|e| e.to_string())?;
        cfg.realization = realization.into();
        let mut s = PreflopSolver::new(cfg, eq.clone())?;
        std::env::set_var("PREFLOP_LEAF_REFRESH", u32::MAX.to_string()); // refreshes driven here
        let t0 = Instant::now();
        let mut leaf_secs = 0f64;
        for i in 1..=iterations {
            s.iterate();
            if realization == "leafnet" && i % every == 0 {
                let t = Instant::now();
                let r = s.refresh_leaf_values().unwrap();
                leaf_secs += t.elapsed().as_secs_f64();
                println!("it {i}: refreshed {}/{} terminals in {:.2}s, mean |corr| {:.4}, max {:.3}, pot added {:+.4}",
                         r.priced, r.terminals, t.elapsed().as_secs_f64(), r.mean_abs, r.max_abs, r.mean_excess);
            }
        }
        let (gaps, evs) = s.gaps_and_evs();
        println!("{realization}: {iterations} iterations in {:.1}s (leaf {:.1}s), gaps {:?}, evs {:?}",
                 t0.elapsed().as_secs_f64(), leaf_secs,
                 gaps.iter().map(|g| (g * 1000.0).round() / 1000.0).collect::<Vec<_>>(),
                 evs.iter().map(|g| (g * 1000.0).round() / 1000.0).collect::<Vec<_>>());
        solved.push(s);
    }
    if solved.len() < 2 {
        return Ok(());
    }
    // root decision and the first response to each root action
    let mut paths: Vec<Vec<usize>> = vec![vec![]];
    let root = solved[0].node_view(&[])?;
    for (i, _) in root.actions.iter().enumerate() {
        paths.push(vec![i]);
    }
    for path in paths {
        let (Ok(b), Ok(l)) = (solved[0].node_view(&path), solved[1].node_view(&path)) else { continue };
        if b.actions.is_empty() {
            continue;
        }
        let acts: Vec<String> = b.actions.iter().zip(&l.actions)
            .map(|(x, y)| format!("{} {:.1}% -> {:.1}%", x.label, 100.0 * x.freq, 100.0 * y.freq)).collect();
        println!("{:?} {}: {}", path, b.actor_pos.clone().unwrap_or_default(), acts.join(", "));
    }
    Ok(())
}
