//! Owned large-native CPU research only. Never saves or merges a solver session.
//! INPUT.gtop REGISTERED_PATHS.json OUTPUT.json inspect|refine [SECONDS<=120] [ITERATIONS=100]
use solver::preflop::{PreflopSolver,equity::EquityTable};
use serde_json::{json,Value};
use std::{sync::Arc,time::Instant,io::Write};

fn main()->Result<(),String> {
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()<4 || a.len()>6 || !["inspect","refine"].contains(&a[3].as_str()) {
        return Err("INPUT.gtop REGISTERED_PATHS.json OUTPUT.json inspect|refine [SECONDS<=120] [ITERATIONS=100]".into());
    }
    let seconds:u64=a.get(4).map_or(Ok(120),|x|x.parse()).map_err(|_|"bad seconds")?;
    let iterations:u32=a.get(5).map_or(Ok(100),|x|x.parse()).map_err(|_|"bad iterations")?;
    if seconds==0 || seconds>120 || ![2,10,30,100].contains(&iterations) {return Err("invalid fixed work bounds".into());}
    let protocol:Value=serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let registered=protocol["paths"].as_array().ok_or("registered paths array required")?;
    if registered.is_empty() || registered.len()>3 {return Err("register1..3 paths".into());}
    let paths:Vec<Vec<usize>>=registered.iter().map(|r|serde_json::from_value(r["path"].clone()).map_err(|e|e.to_string())).collect::<Result<_,_>>()?;
    // Arena cap is checked again after load; allow bounded native metadata too.
    if std::fs::metadata(&a[0]).map_err(|e|e.to_string())?.len()>3*1024*1024*1024+32*1024*1024 {
        return Err("native input exceeds3GiB arenas plus32MiB metadata allowance".into());
    }
    let mut out=std::fs::OpenOptions::new().create_new(true).write(true).open(&a[2]).map_err(|e|e.to_string())?;
    let total=Instant::now();let cache=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    if cache.len()!=4+169*169*4 {return Err("malformed frozen equity cache".into());}
    let samples=u32::from_le_bytes(cache[..4].try_into().unwrap());
    if samples==0 {return Err("zero equity samples".into());}
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    if std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?!=cache {return Err("equity cache changed".into());}
    let loading=Instant::now();let mut s=PreflopSolver::load_game(&a[0],eq).map_err(|e|e.to_string())?;
    let load_seconds=loading.elapsed().as_secs_f64();
    let inspection=s.research_inspect_conditional_large(&paths)?;
    let mut rows=Vec::new();let work=Instant::now();
    if a[3]=="refine" {
        for (i,path) in paths.iter().enumerate() {
            let observed=&inspection["paths"][i];let expected=&registered[i];
            let mismatch=observed["error"].is_string() || observed["has_positive_learned_prefix_support"]!=true
                || expected["expected_actor"]!=observed["actor"] || expected["expected_live"]!=observed["live_positions"]
                || expected["expected_pot"].as_f64()!=observed["pot"].as_f64();
            if mismatch {rows.push(json!({"path":path,"status":"registered_structure_or_support_rejected","observed":observed}));continue;}
            let remaining=seconds.saturating_sub(work.elapsed().as_secs());
            if remaining==0 {rows.push(json!({"path":path,"status":"total_work_budget_exhausted"}));continue;}
            match s.research_refine_conditional_large(path,remaining,iterations) {
                Ok(row)=>rows.push(row),Err(error)=>rows.push(json!({"path":path,"error":error}))
            }
        }
    }
    if std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?!=cache {return Err("equity cache changed after work".into());}
    let result=json!({"development_only":true,"mode":a[3],"input":a[0],"registered_protocol":protocol,
        "inspection":inspection,"load_seconds":load_seconds,"elapsed_seconds":total.elapsed().as_secs_f64(),
        "cache_samples":samples,"time_cap_seconds":seconds,"max_local_iterations":iterations,"results":rows,
        "source_native_written":false,"quality_scope":"Registered development paths; no holdout claim",
        "timing_scope":"Work budget includes between-case overhead; an in-progress case also performs mandatory backup/audit/restore outside its cancellation deadline"});
    serde_json::to_writer(&mut out,&result).map_err(|e|e.to_string())?;out.flush().map_err(|e|e.to_string())?;
    println!("CONDITIONAL_LARGE {}",json!({"output":a[2],"mode":a[3],"elapsed_seconds":total.elapsed().as_secs_f64()}));
    Ok(())
}
