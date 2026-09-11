//! INPUT.gtop PATHS.json OUTPUT.json [SECONDS<=120]. Development-only CPU study.
use solver::preflop::{PreflopSolver,equity::EquityTable};
use std::{sync::Arc,time::Instant,io::Write};
use serde_json::json;

fn main()->Result<(),String> {
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()<3 || a.len()>4 {return Err("INPUT.gtop PATHS.json OUTPUT.json [SECONDS<=120]".into());}
    let cap:u64=a.get(3).map_or(Ok(120),|x|x.parse()).map_err(|_|"bad seconds")?;
    if cap==0 || cap>120 {return Err("seconds must be1..120".into());}
    let started=Instant::now();
    let mut out=std::fs::OpenOptions::new().create_new(true).write(true).open(&a[2]).map_err(|e|e.to_string())?;
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if paths.is_empty() || paths.len()>3 {return Err("freeze1..3 development paths".into());}
    if std::fs::metadata(&a[0]).map_err(|e|e.to_string())?.len()>130*1024*1024 {return Err("small native snapshot required before loading".into());}
    let cache=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    if cache.len()!=4+169*169*4 {return Err("malformed equity cache".into());}
    let samples=u32::from_le_bytes(cache[..4].try_into().unwrap());
    if samples==0 {return Err("zero equity samples".into());}
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    if std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())? != cache {return Err("equity cache changed on load".into());}
    let mut s=PreflopSolver::load_game(&a[0],eq).map_err(|e|e.to_string())?;
    let mut rows=Vec::new();
    for path in paths {
        let remaining=cap.saturating_sub(started.elapsed().as_secs());
        if remaining==0 {rows.push(json!({"path":path,"status":"total_budget_exhausted"}));continue;}
        match s.research_refine_conditional(&path,remaining,100) {
            Ok(row)=>rows.push(row),Err(error)=>rows.push(json!({"path":path,"error":error}))
        }
    }
    let result=json!({"development_only":true,"input":a[0],"paths_file":a[1],"cache_samples":samples,
        "time_cap_seconds":cap,"elapsed_seconds":started.elapsed().as_secs_f64(),"results":rows,
        "source_native_written":false,"quality_scope":"Registered previously failed development paths, not holdout"});
    serde_json::to_writer(&mut out,&result).map_err(|e|e.to_string())?;out.flush().map_err(|e|e.to_string())?;
    println!("CONDITIONAL {}",json!({"elapsed_seconds":started.elapsed().as_secs_f64(),"output":a[2],"cases":rows.len()}));
    Ok(())
}
