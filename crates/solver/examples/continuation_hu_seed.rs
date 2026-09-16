//! Tiny offline fixtures only. No live server, solving, or default-model changes.
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::{path::Path, sync::Arc};

fn main() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 1 { return Err("usage: continuation_hu_seed OUTPUT_DIRECTORY".into()); }
    let out = Path::new(&args[0]);
    if out.exists() { return Err("refusing to overwrite an existing fixture directory".into()); }
    let cache = "cache/preflop_eq169.bin";
    let bytes = std::fs::read(cache).map_err(|e| e.to_string())?;
    if bytes.len() != 4 + 169 * 169 * 4 || u32::from_le_bytes(bytes[..4].try_into().unwrap()) != 20000 {
        return Err("existing 20000-sample equity cache required".into());
    }
    rayon::ThreadPoolBuilder::new().num_threads(2).build_global().map_err(|e| e.to_string())?;
    let eq = Arc::new(EquityTable::load_or_build(cache, 20000));
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let mut fixtures: Vec<Value> = Vec::new();
    for stack in [40., 100.] {
        let cfg: PreflopConfig = serde_json::from_value(json!({
            "positions": ["SB", "BB"], "stack": stack, "posts": [0.5, 1.],
            "ante": 0., "limp": true, "open_raises": [2.5], "raise_mults": [3.],
            "max_raises": 3, "add_allin": true, "rake_pct": 0., "rake_cap": 0.,
            "no_flop_no_drop": true, "realization": "balanced"
        })).map_err(|e| e.to_string())?;
        let s = PreflopSolver::new(cfg, eq.clone())?;
        if s.n != 2 || s.iteration != 0 || s.postflop_order() != vec![1, 0] || s.nodes.len() > 10000 {
            return Err("unexpected heads-up fixture topology".into());
        }
        let name = format!("hu-{}.gtop", stack as u32);
        s.save_game(out.join(&name).to_str().ok_or("non-UTF8 output")?)?;
        fixtures.push(json!({"file": name, "config": s.cfg, "nodes": s.nodes.len(),
                            "postflop_order": s.postflop_order(), "iteration": s.iteration}));
    }
    std::fs::write(out.join("fixtures.json"), serde_json::to_vec_pretty(&json!({
        "fixtures": fixtures, "production_enabled": false,
        "warning": "Fresh offline fixtures. Never load experimental result saves in the ordinary app."
    })).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    Ok(())
}
