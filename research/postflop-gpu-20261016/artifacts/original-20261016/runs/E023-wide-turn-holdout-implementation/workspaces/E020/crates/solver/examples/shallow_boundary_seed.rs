//! Seed deterministic offline policies for native stack-boundary checks.
#[cfg(not(feature="preflop-research"))]
fn main() { panic!("Build with --features preflop-research"); }

#[cfg(feature="preflop-research")]
fn main() -> Result<(), String> {
    use serde_json::json;
    use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
    use std::{path::Path, sync::Arc};
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 1 { return Err("shallow_boundary_seed OUTPUT_DIRECTORY".into()); }
    let out = Path::new(&args[0]);
    if out.exists() { return Err("refusing to replace existing fixtures".into()); }
    let cache = "cache/preflop_eq169.bin";
    let bytes = std::fs::read(cache).map_err(|e| e.to_string())?;
    if bytes.len() != 4 + 169 * 169 * 4 || u32::from_le_bytes(bytes[..4].try_into().unwrap()) != 20000 {
        return Err("existing 20000-sample equity cache required".into());
    }
    let eq = Arc::new(EquityTable::load_or_build(cache, 20000));
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let mut fixtures = Vec::new();
    for (i, spr) in [0.1, 0.2-1e-7, 0.2, 0.2+1e-7, 0.75-1e-7, 0.75, 0.75+1e-7, 0.85, 1.-1e-7, 1., 1.+1e-7].into_iter().enumerate() {
        let cfg: PreflopConfig = serde_json::from_value(json!({
            "positions":["SB","BB"],"stack":22.5+45.*spr,"posts":[0.5,1.],
            "ante":0.,"limp":true,"open_raises":[2.5],"raise_mults":[3.],
            "max_raises":3,"add_allin":true,"rake_pct":0.,"rake_cap":0.,
            "no_flop_no_drop":true,"realization":"balanced"
        })).map_err(|e| e.to_string())?;
        let mut s = PreflopSolver::new(cfg, eq.clone())?;
        s.research_seed_quality_fixture_averages()?;
        let path = out.join(format!("{i}.gtop"));
        s.save_game(path.to_str().ok_or("path")?)?;
        fixtures.push(json!({"file":format!("{i}.gtop"),"target_spr":spr,"config":s.cfg,"nodes":s.nodes.len()}));
    }
    std::fs::write(out.join("fixtures.json"), serde_json::to_vec_pretty(&json!({"fixtures":fixtures,"production_enabled":false})).unwrap()).map_err(|e| e.to_string())?;
    Ok(())
}
