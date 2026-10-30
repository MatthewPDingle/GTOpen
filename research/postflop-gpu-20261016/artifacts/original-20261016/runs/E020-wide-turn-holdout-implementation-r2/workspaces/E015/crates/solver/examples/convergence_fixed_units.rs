//! One-process fixed-unit screen. Saved outputs are read-only audit artifacts.
use solver::preflop::{equity::EquityTable,gpu::PreflopGpu,PreflopSolver};
use serde_json::{json,Value};
use std::{sync::Arc,time::Instant,path::Path};
fn audit(s:&PreflopSolver,paths:&[Vec<usize>],gaps:Vec<f64>,evs:Vec<f64>,seconds:f64)->Result<Value,String> {
    if gaps.len()!=6 || evs.len()!=6 || gaps.iter().any(|x|!x.is_finite() || *x<0.0) || evs.iter().any(|x|!x.is_finite()) {return Err("invalid native check".into());}
    let rows:Vec<_>=paths.iter().map(|p|s.research_conditioned_action_quality_against(s,p).map(|q|json!({"candidate":q}))).collect::<Result<_,_>>()?;
    let passed=rows.iter().filter(|q|q["candidate"]["passes_local_tail_gate"]==true && q["candidate"]["conditioned_before_evaluation"]==true).count();
    let total:f64=gaps.iter().sum();
    Ok(json!({"global_age":s.iteration,"global_gaps":gaps,"global_evs":evs,"gap_total":total,
        "rows":rows,"passed":passed,"passes_combined":total<=0.005 && passed==paths.len(),"elapsed_before_audit":seconds}))
}
fn main()->Result<(),String> {
    let args:Vec<_>=std::env::args().skip(1).collect();if args.len()!=4 || !["control","candidate"].contains(&args[2].as_str()) {return Err("INPUT PATHS control|candidate OUTPUT".into());}
    let out=Path::new(&args[3]);if out.exists() {return Err("output exists".into());}
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let expected=vec![vec![2,0,0],vec![2,0,0,1],vec![2,0,0,1,1],vec![2,0,0,0,0],vec![1,0,0],vec![1,0,0,0,0]];
    if paths!=expected {return Err("unregistered diagnostic paths".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let bytes=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(bytes[..4].try_into().unwrap())));
    let mut s=Box::new(PreflopSolver::load_game(&args[0],eq.clone())?);
    if s.nodes.len()!=23038 || s.n!=6 || s.iteration!=350 || s.hero.is_some() || s.seat_frozen.iter().any(|x|*x)
        || s.seat_profiles.iter().any(|x|x.is_some()) || s.multiway_equity_model()!="coupled_deck_v1" {return Err("unregistered input state".into());}
    for p in &paths {s.research_refinement_plan(p)?;}
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;let started=Instant::now();
    let mut gpu=PreflopGpu::new(&s,4096)?;let (g,e)=gpu.gaps_and_evs()?;drop(gpu);
    let initial=audit(&s,&paths,g,e,started.elapsed().as_secs_f64())?;
    let mut history=None;let mut refinement=Value::Null;
    if args[2]=="candidate" {let (state,report)=s.research_refine_with_fixed_units_gpu(&[vec![2,0,0],vec![1,0,0]],1000,2048)?;history=Some(state);refinement=report;}
    let mut checks=Vec::new();let mut consecutive=0;let mut qualified=false;
    for step in 0..=10 {
        let (gaps,evs)=if step==0 {
            let mut gpu=PreflopGpu::new(&s,4096)?;gpu.gaps_and_evs()?
        } else if let Some(state)=&mut history {
            let r=s.research_continue_fixed_units_gpu(state,25,4096)?;
            (serde_json::from_value(r["global_gaps"].clone()).unwrap(),serde_json::from_value(r["global_evs"].clone()).unwrap())
        } else {
            let mut gpu=PreflopGpu::new(&s,4096)?;for _ in 0..25 {gpu.iterate(&mut s)?;}
            let check=gpu.gaps_and_evs()?;gpu.sync_to_cpu(&mut s)?;check
        };
        let mut row=audit(&s,&paths,gaps,evs,started.elapsed().as_secs_f64())?;
        row["elapsed_seconds"]=json!(started.elapsed().as_secs_f64());
        consecutive=if row["passes_combined"]==true {consecutive+1}else{0};qualified=consecutive>=2;
        println!("FIXED_UNIT_SCREEN {}",json!({"mode":args[2],"step":step,"global_age":s.iteration,"gap":row["gap_total"],"passed":row["passed"],"qualified":qualified}));
        std::fs::write(out.join(format!("check-{step}.json")),serde_json::to_vec_pretty(&row).unwrap()).map_err(|e|e.to_string())?;
        checks.push(row);if qualified {break;}
    }
    let final_path=out.join("final.gtop");s.save_game(final_path.to_str().ok_or("invalid output path")?)?;
    let reload=PreflopSolver::load_game(final_path.to_str().unwrap(),eq)?;if reload.arena_snapshot()!=s.arena_snapshot() {return Err("roundtrip histories differ".into());}
    let result=json!({"input":args[0],"mode":args[2],"initial":initial,"refinement":refinement,"checks":checks,
        "metadata":history.as_ref().map(|h|h.metadata()),"qualified":qualified,"roundtrip_exact":true,
        "persistent_resume_supported":false,"seconds":started.elapsed().as_secs_f64()});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
