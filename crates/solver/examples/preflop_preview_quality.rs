//! Offline small-tree policy quality. Prints JSON; never saves or resumes learning.
//! Usage: preflop_preview_quality CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE THREADS [PATHS.json]
use solver::preflop::{equity::{EquityTable, NUM_CLASSES}, PreflopSolver};
use std::sync::Arc;

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if !(4..=5).contains(&args.len()) { return Err("usage: preflop_preview_quality CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE THREADS [PATHS.json]".into()); }
    let threads: usize = args[3].parse().map_err(|_| "invalid threads")?;
    if !(1..=16).contains(&threads) { return Err("threads must be 1..16".into()); }
    // Reject large inputs before native rebuilding/arena allocations.
    for path in &args[..2] {
        if std::fs::metadata(path).map_err(|e|e.to_string())?.len() > 140 * 1024 * 1024 {
            return Err("quality input is larger than the bounded small-tree fixture limit".into());
        }
    }
    let cache_before = std::fs::read(&args[2]).map_err(|e|e.to_string())?;
    if cache_before.len() != 4 + NUM_CLASSES * NUM_CLASSES * 4 { return Err("equity cache has invalid size".into()); }
    let samples = u32::from_le_bytes(cache_before[..4].try_into().unwrap());
    if samples == 0 { return Err("equity cache sample count is zero".into()); }
    let eq = Arc::new(EquityTable::load_or_build(&args[2], samples));
    // Native model validation remains fully active. Unknown candidate versions
    // are rejected until the actual candidate loader supports them.
    let candidate = PreflopSolver::load_game(&args[0], eq.clone())?;
    let reference = PreflopSolver::load_game(&args[1], eq)?;
    if candidate.cfg.realization == "calibrated" && (candidate.fit.is_none() || reference.fit.is_none()) {
        return Err("calibrated quality inputs require the pinned realization fit; no fallback".into());
    }
    let pool = rayon::ThreadPoolBuilder::new().num_threads(threads).build().map_err(|e|e.to_string())?;
    let mut result = pool.install(||candidate.research_policy_quality_against(&reference))?;
    if args.len() == 5 {
        let paths: Vec<Vec<usize>> = serde_json::from_slice(&std::fs::read(&args[4]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
        if paths.len() > 8 { return Err("at most eight selected local paths".into()); }
        let rows: Result<Vec<_>,_> = pool.install(||paths.iter().map(|path|candidate.research_local_action_quality_against(&reference,path)).collect());
        result["selected_local_action_quality"] = serde_json::to_value(rows?).map_err(|e|e.to_string())?;
        result["not_evaluated"] = serde_json::json!(["physical equity","unselected local action tails","speedup","preview workflow"]);
    }
    if std::fs::read(&args[2]).map_err(|e|e.to_string())? != cache_before {
        return Err("equity cache changed during quality evaluation".into());
    }
    println!("{}", serde_json::to_string_pretty(&result).map_err(|e|e.to_string())?);
    Ok(())
}
fn main() {
    if let Err(e) = run() { eprintln!("preview quality: {e}"); std::process::exit(1); }
}
