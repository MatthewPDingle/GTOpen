//! Read-only export of a tiny saved preflop tree for offline action-value audits.
use serde_json::json;
use solver::preflop::{equity::EquityTable, PreflopSolver};
use std::{path::Path, sync::Arc};

fn main() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() != 2 { return Err("holdem_action_export SAVE OUTPUT".into()); }
    if Path::new(&args[1]).exists() { return Err("Refusing to overwrite an export".into()); }
    let cache = Path::new("cache/preflop_eq169.bin");
    if !cache.exists() { return Err("Existing equity cache required".into()); }
    let eq = Arc::new(EquityTable::load_or_build(cache.to_str().unwrap(), 20000));
    let s = PreflopSolver::load_game(&args[0], eq)?;
    if s.n != 2 || s.nodes.len() > 1000 { return Err("Small heads-up game required".into()); }
    let before = s.arena_snapshot();
    let mut paths = vec![Vec::new(); s.nodes.len()];
    let mut nodes = Vec::new();
    for (i, n) in s.nodes.iter().enumerate() {
        let children: Vec<_> = (0..n.actions.len()).map(|a| {
            let child = s.child(i, a);
            paths[child] = paths[i].iter().copied().chain([a]).collect();
            child
        }).collect();
        let (walked, reaches) = s.walk(&paths[i])?;
        if walked != i { return Err("Path mismatch".into()); }
        nodes.push(json!({"id":i,"path":paths[i],"kind":n.kind,"actor":n.actor,
            "children":children,"pot":n.pot,"invested":n.invested,"live":n.live,
            "winner":n.winner,"r":n.r,"reaches":reaches,
            "actions":n.actions.iter().map(|a|json!({"label":a.label,"to":a.to})).collect::<Vec<_>>(),
            "sigma":if n.kind == 0 {s.average_strategy(i)} else {Vec::new()}}));
    }
    if before != s.arena_snapshot() { return Err("Export modified policy".into()); }
    std::fs::write(&args[1], serde_json::to_vec_pretty(&json!({
        "config":s.cfg,"iteration":s.iteration,"postflop_order":s.postflop_order(),
        "nodes":nodes,"read_only":true
    })).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
