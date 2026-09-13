use solver::preflop::{PreflopSolver,equity::EquityTable};
use std::sync::Arc;
fn main()->Result<(),String>{
    let a:Vec<_>=std::env::args().skip(1).collect();if a.len()!=2{return Err("INPUT OUTPUT".into());}
    if std::path::Path::new(&a[1]).exists(){return Err("output exists".into());}
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let s=PreflopSolver::load_game(&a[0],eq)?;let r=s.research_shared_cv_storage()?;
    std::fs::write(&a[1],serde_json::to_vec_pretty(&r).unwrap()).map_err(|e|e.to_string())?;
    println!("{r}");Ok(())
}
