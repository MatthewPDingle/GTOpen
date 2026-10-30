//! Inspect current/average learning state at paths from a saved local audit.
use solver::preflop::{equity::EquityTable, PreflopSolver};
use std::sync::Arc;

fn main() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 3 { return Err("INPUT.gtop LOCAL_AUDIT.json OUTPUT.json".into()); }
    let cache = std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples = u32::from_le_bytes(cache.get(..4).ok_or("short equity cache")?.try_into().unwrap());
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let solver = PreflopSolver::load_game(&args[0], eq)?;
    let audit: serde_json::Value = serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?)
        .map_err(|e|e.to_string())?;
    let rows = audit["rows"].as_array().ok_or("missing audit rows")?;
    if rows.is_empty() || rows.len() > 64 { return Err("expected 1..64 completed audit paths".into()); }
    let mut diagnostics = Vec::new();
    for row in rows {
        let path: Vec<usize> = serde_json::from_value(row["candidate"]["path"].clone()).map_err(|e|e.to_string())?;
        diagnostics.push(solver.research_node_learning_diagnostics(&path)?);
    }
    let result = serde_json::json!({"input":args[0],"audit":args[1],"nodes":diagnostics,
        "static_terminal_reuse":solver.research_static_terminal_reuse()?,
        "scope":"Read-only current/average prefix and arena-scale inspection; no convergence claim"});
    std::fs::write(&args[2], serde_json::to_vec_pretty(&result).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
