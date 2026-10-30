//! Read-only conditional audit for an explicit, preregistered path list.
use solver::preflop::{equity::EquityTable,PreflopSolver};
use std::sync::Arc;
use serde_json::{json,Value};
fn main()->Result<(),String>{
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()!=3{return Err("INPUT PATHS_JSON OUTPUT_JSON".into());}
    if std::path::Path::new(&a[2]).exists(){return Err("output exists".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let s=PreflopSolver::load_game(&a[0],eq)?;
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if paths.is_empty() || paths.len()>64 {return Err("one to 64 explicit paths required".into());}
    let mut rows=Vec::new();
    for path in paths {
        let started=std::time::Instant::now();
        let quality=s.research_conditioned_action_quality_against(&s,&path);
        let row:Value=match quality {
            Ok(q)=>json!({"candidate":q,"seconds":started.elapsed().as_secs_f64()}),
            Err(error)=>json!({"candidate":{"path":path,"status":"error","error":error},"seconds":started.elapsed().as_secs_f64()})
        };
        println!("AUDIT {}",json!({"path":row["candidate"]["path"],"status":row["candidate"]["status"],"passes":row["candidate"]["passes_local_tail_gate"]}));
        rows.push(row);
    }
    std::fs::write(&a[2],serde_json::to_vec_pretty(&json!({"input":a[0],"rows":rows})).unwrap()).map_err(|e|e.to_string())
}
