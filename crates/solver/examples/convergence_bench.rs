//! Offline GPU learning with full-model checks. INPUT SCHEDULE SAMPLES SEED LIMIT CHECK_EVERY OUTPUT
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, convergence_research::Experiment, PreflopSolver};
use std::{sync::Arc, time::Instant};
fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 7 { return Err("INPUT SCHEDULE SAMPLES SEED LIMIT CHECK_EVERY OUTPUT".into()); }
    let target:f64=std::env::var("CONVERGENCE_TARGET").unwrap_or_else(|_|"0.005".into()).parse().map_err(|_|"target")?;
    if !target.is_finite() || target<0.0 { return Err("invalid target".into()); }
    let samples:u32=a[2].parse().map_err(|_|"samples")?;
    let seed:u64=a[3].parse().map_err(|_|"seed")?;
    let limit:u32=a[4].parse().map_err(|_|"limit")?;
    let every:u32=a[5].parse().map_err(|_|"cadence")?;
    if limit==0 || limit>5000 || every==0 { return Err("invalid limits".into()); }
    let check_policy=std::env::var("CONVERGENCE_CHECK_POLICY").unwrap_or_else(|_|"fixed".into());
    if check_policy!="fixed" && check_policy!="coarse_then_fine" {return Err("invalid check policy".into());}
    let mut fine=check_policy=="fixed";
    let mut next_check=if fine {every} else {every.saturating_mul(2)};
    let out=std::path::Path::new(&a[6]); if out.exists() { return Err("output exists".into()); }
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let started=Instant::now();
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let mut s=if a[0].ends_with(".gtop") { PreflopSolver::load_game(&a[0],eq.clone())? } else {
        let input:Value=serde_json::from_slice(&std::fs::read(&a[0]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
        PreflopSolver::new(serde_json::from_value(input.get("config").unwrap_or(&input).clone()).map_err(|e|e.to_string())?,eq.clone())?
    };
    let restart=if std::env::var("CONVERGENCE_RESTART_AVERAGE").as_deref()==Ok("1") {
        if !a[0].ends_with(".gtop") {return Err("average restart requires saved research snapshot".into());}
        Some(s.research_restart_from_average()?)
    } else {None};
    if s.iteration!=0 || s.multiway_equity_model()!="coupled_deck_v1" { return Err("requires fresh full-model game".into()); }
    if s.cfg.realization=="calibrated" && s.fit.is_none() { return Err("missing fit".into()); }
    let mut g=PreflopGpu::new(&s,23000)?;
    if a[1]!="native" { g.configure_research(Experiment::new(&a[1],samples,1000,seed)?)?; }
    let cv_refresh=std::env::var("CONVERGENCE_CV_REFRESH").ok().map(|v|v.parse::<u32>().map_err(|_|"CV refresh")).transpose()?;
    if let Some(interval)=cv_refresh { g.enable_research_control_variate(interval,4096)?; }
    let live=s.live_seats(); let mut rows=Vec::new(); let mut solve_seconds=0.0; let mut check_seconds=0.0;
    println!("CONVERGENCE {}",json!({"phase":"init","nodes":s.nodes.len(),"schedule":a[1],"samples":samples,"seed":seed,"horizon":1000,"init_seconds":started.elapsed().as_secs_f64(),"live":live}));
    let mut passes=0;
    for i in 1..=limit {
        let t=Instant::now();g.iterate(&mut s)?;let iter_seconds=t.elapsed().as_secs_f64();solve_seconds+=iter_seconds;
        if i!=next_check && i!=limit { continue; }
        let t=Instant::now();let (gaps,evs)=g.gaps_and_evs()?;check_seconds+=t.elapsed().as_secs_f64();
        if gaps.iter().chain(&evs).any(|x|!x.is_finite()) { return Err("nonfinite check".into()); }
        let gap:f64=gaps.iter().zip(&live).filter(|(_,l)|**l).map(|(x,_)|x).sum();
        passes=if gap<=target { passes+1 } else { 0 };
        if gap<=target*4.0 {fine=true;}
        next_check=i.saturating_add(if fine {every} else {every.saturating_mul(2)});
        let row=json!({"phase":"check","iteration":i,"gap":gap,"gaps":gaps,"evs":evs,"solve_seconds":solve_seconds,"check_seconds":check_seconds,"elapsed_seconds":started.elapsed().as_secs_f64(),"last_iteration_seconds":iter_seconds,"full_reference_samples":1024,"consecutive_passes":passes});
        println!("CONVERGENCE {row}"); rows.push(row);
        if passes>=2 { break; }
    }
    let cv_stats=g.research_control_variate_stats();
    g.sync_to_cpu(&mut s)?; drop(g);
    let save=out.join("final.gtop");s.save_game(save.to_str().unwrap())?;
    let reload=PreflopSolver::load_game(save.to_str().unwrap(),eq)?;
    if reload.arena_snapshot()!=s.arena_snapshot() { return Err("roundtrip mismatch".into()); }
    let independent=if s.nodes.len()<20000 {
        let (gaps,evs)=reload.gaps_and_evs(); Some(json!({"gaps":gaps,"evs":evs}))
    } else {None};
    let result=json!({"target":target,"check_policy":check_policy,"schedule":a[1],"samples":samples,"seed":seed,"input":a[0],"nodes":s.nodes.len(),"iteration":s.iteration,"converged_twice":passes>=2,"checks":rows,"total_seconds":started.elapsed().as_secs_f64(),"independent_cpu":independent,"roundtrip_exact":true});
    let mut result=result;
    result["research_restart"]=json!(restart);
    result["control_variate"]=json!({"refresh_interval":cv_refresh,"extra_bytes_and_refresh_count":cv_stats});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())?;
    println!("CONVERGENCE {}",json!({"phase":"result","converged_twice":passes>=2,"iteration":s.iteration,"total_seconds":started.elapsed().as_secs_f64()}));
    Ok(())
}
