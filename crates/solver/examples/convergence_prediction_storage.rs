//! Read-only exact-tree prediction storage inventory, without a GPU engine.
use solver::preflop::{equity::EquityTable,PreflopSolver};
use std::{sync::Arc,path::Path};
fn main()->Result<(),String> {
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()!=2 || Path::new(&a[1]).exists() {return Err("SAVED_GAME NEW_JSON".into());}
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let s=PreflopSolver::load_game(&a[0],eq)?;
    let result=s.research_prediction_storage()?;
    if s.nodes.len()!=1567754 || s.n!=8 || s.multiway_equity_model()!="coupled_deck_v1" || s.has_overrides() {
        return Err("wrong registered storage fixture".into());
    }
    println!("{}",result);
    std::fs::write(&a[1],serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
