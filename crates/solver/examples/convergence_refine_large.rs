//! Large saved-game research: INPUT AUDIT ITERATIONS OUTPUT_DIRECTORY.
//! ITERATIONS=0 writes only the read-only selected-subtree plan.
use solver::preflop::{equity::{EquityTable,NUM_CLASSES},gpu::PreflopGpu,PreflopSolver};
use std::{collections::HashSet,sync::Arc,time::Instant};
use serde_json::{json,Value};
fn main()->Result<(),String>{
    let a:Vec<_>=std::env::args().skip(1).collect();
    if a.len()!=4{return Err("INPUT AUDIT ITERATIONS OUTPUT_DIRECTORY".into());}
    let iterations:u32=a[2].parse().map_err(|_|"iterations")?;
    let engine=std::env::var("CONVERGENCE_REFINE_ENGINE").unwrap_or_else(|_|"cpu".into());
    if engine!="cpu" && engine!="gpu" {return Err("unknown refinement engine".into());}
    if iterations>4000{return Err("iteration cap".into());}
    let out=std::path::Path::new(&a[3]);if out.exists(){return Err("output exists".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let started=Instant::now();
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let mut s=PreflopSolver::load_game(&a[0],eq.clone())?;
    if s.multiway_equity_model()!="coupled_deck_v1" {return Err("full coupled source required".into());}
    let audit:Value=serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let paths:Vec<Vec<usize>>=audit["rows"].as_array().ok_or("audit rows")?.iter()
        .map(|r|serde_json::from_value(r["candidate"]["path"].clone()).map_err(|e|e.to_string())).collect::<Result<_,_>>()?;
    if paths.is_empty() || paths.len()>64 || paths.iter().collect::<HashSet<_>>().len()!=paths.len() {return Err("one to 64 distinct audit paths required".into());}
    let plans:Vec<_>=paths.iter().map(|p|s.research_refinement_plan(p)).collect::<Result<_,_>>()?;
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    std::fs::write(out.join("plan.json"),serde_json::to_vec_pretty(&plans).unwrap()).map_err(|e|e.to_string())?;
    if iterations==0 {return Ok(());}
    let mutable:HashSet<usize>=plans.iter().flat_map(|p|p["learning_node_indices"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as usize)).collect();
    let before=s.arena_snapshot(); let original_iteration=s.iteration;
    let mut progress=Vec::new();
    let adaptive=std::env::var("CONVERGENCE_REFINE_ADAPTIVE").as_deref()==Ok("1");
    let rounds=if adaptive {2} else {1};
    for round in 0..rounds {
      for (path,plan) in paths.iter().zip(&plans) {
        if plan["learning_node_indices"].as_array().unwrap().is_empty(){continue;}
        if adaptive {
            let quality=s.research_conditioned_action_quality_against(&s,path)?;
            if quality["passes_local_tail_gate"]==true {continue;}
        }
        let budgets=if adaptive && iterations>1000 {vec![1000,iterations]} else {vec![iterations]};
        for budget in budgets {
            let result=if engine=="gpu" {s.research_refine_branch_gpu(path,budget,4096)?}
                else {s.research_refine_branches(&[path.clone()],budget)?};
            let quality=s.research_conditioned_action_quality_against(&s,path)?;
            println!("REFINED {}",json!({"round":round,"path":path,"iterations":budget,"seconds":result["seconds"],"passes":quality["passes_local_tail_gate"]}));
            progress.push(json!({"refinement":result,"quality":quality,"round":round}));
            if quality["passes_local_tail_gate"]==true {break;}
        }
      }
    }
    let after=s.arena_snapshot();
    for (node,nd) in s.nodes.iter().enumerate() {
        if mutable.contains(&node) {continue;}
        let span=nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES;
        if before.0[span.clone()]!=after.0[span.clone()] || before.1[span.clone()]!=after.1[span] {
            return Err(format!("unrelated or fixed arena changed at {node}"));
        }
    }
    drop(before);drop(after);
    if s.iteration!=original_iteration{return Err("global iteration changed".into());}
    let gpu_started=Instant::now();let mut gpu=PreflopGpu::new(&s,23000)?;
    let (gaps,evs)=gpu.gaps_and_evs()?;drop(gpu);
    if gaps.iter().chain(&evs).any(|x|!x.is_finite()){return Err("nonfinite full check".into());}
    let global_check_seconds=gpu_started.elapsed().as_secs_f64();
    let save=out.join("final.gtop");s.save_game(save.to_str().ok_or("path")?)?;
    let reload=PreflopSolver::load_game(save.to_str().unwrap(),eq)?;
    if reload.arena_snapshot()!=s.arena_snapshot(){return Err("roundtrip changed arenas".into());}
    let result=json!({"input":a[0],"engine":engine,"nodes":s.nodes.len(),"refinements":progress,"global_gaps":gaps,"global_evs":evs,
        "global_check_seconds":global_check_seconds,"elapsed_seconds":started.elapsed().as_secs_f64(),
        "unrelated_and_fixed_arenas_unchanged":true,"roundtrip_exact":true,"normal_global_resume_supported":false,
        "scope":"Selected conditional re-solving; full global evaluation; additional local audit required"});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
