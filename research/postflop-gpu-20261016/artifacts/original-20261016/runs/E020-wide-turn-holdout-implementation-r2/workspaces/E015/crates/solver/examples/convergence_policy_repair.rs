//! Bounded non-root average-policy repair. INPUT PATHS OUTPUT.
use solver::preflop::{equity::EquityTable,gpu::PreflopGpu,PreflopSolver,
    convergence_policy_repair::{best_response_target,mix_policy}};
use serde_json::{json,Value};
use std::{sync::Arc,time::Instant};
const NC:usize=169;
fn write(path:impl AsRef<std::path::Path>,value:&Value)->Result<(),String>{
    std::fs::write(path,serde_json::to_vec_pretty(value).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
fn global(s:&PreflopSolver)->Result<(Vec<f64>,Vec<f64>),String>{
    let mut gpu=PreflopGpu::new(s,23000)?;let (gaps,evs)=gpu.gaps_and_evs()?;
    if gaps.len()!=s.cfg.positions.len() || evs.len()!=gaps.len()
        || gaps.iter().any(|g|!g.is_finite() || *g<0.0) || evs.iter().any(|v|!v.is_finite()) {
        return Err("invalid full-game GPU evaluation".into());
    }
    Ok((gaps,evs))
}
fn evaluate(s:&PreflopSolver,paths:&[Vec<usize>],count:usize)->Result<Value,String>{
    let (gaps,evs)=global(s)?;
    let rows:Vec<Value>=paths.iter().map(|p|s.research_conditioned_action_quality_against(s,p)
        .map(|v|json!({"candidate":v}))).collect::<Result<_,_>>()?;
    let reachable=rows.iter().all(|r|r["candidate"]["status"]=="evaluated");
    let objective=if reachable {Some(rows[..count].iter().map(|r|r["candidate"]["weighted_action_loss_bb"].as_f64().unwrap()).sum::<f64>())}else{None};
    let passed=rows.iter().filter(|r|r["candidate"]["passes_local_tail_gate"]==true
        && r["candidate"]["conditioned_before_evaluation"]==true
        && r["candidate"]["forced_or_frozen"]==false).count();
    let gap:f64=gaps.iter().sum();
    Ok(json!({"global_gaps":gaps,"global_evs":evs,"gap":gap,"rows":rows,
        "reachable":reachable,"objective":objective,"passed":passed,
        "qualified":gap<=0.005 && passed==paths.len() && reachable}))
}
fn policies(rows:&[Value])->Result<Vec<Vec<f32>>,String>{
    rows.iter().map(|row|{
        let c=&row["candidate"];if c["status"]!="evaluated"{return Err("target node unreachable".into());}
        let na=c["actions"].as_array().ok_or("missing actions")?.len();
        let mut p=vec![0f32;na*NC];
        let hands=c["hands"].as_array().ok_or("missing hands")?;
        if hands.len()!=NC {return Err("missing hand coverage".into());}
        for (h,hand) in hands.iter().enumerate(){
            if hand["class_index"]!=json!(h){return Err("invalid class order".into());}
            let v=hand["candidate_probabilities"].as_array().ok_or("missing policy")?;
            if v.len()!=na{return Err("invalid action shape".into());}
            for a in 0..na{p[a*NC+h]=v[a].as_f64().ok_or("invalid probability")? as f32;}
        }
        Ok(p)
    }).collect()
}
fn protected(trial:&Value,anchor:&Value,count:usize)->bool{
    if trial["reachable"]!=true || trial["gap"].as_f64().unwrap()>0.005{return false;}
    trial["rows"].as_array().unwrap()[count..].iter().zip(&anchor["rows"].as_array().unwrap()[count..]).all(|(t,a)|{
        let (t,a)=(&t["candidate"],&a["candidate"]);
        t["weighted_action_loss_bb"].as_f64().unwrap()<=a["weighted_action_loss_bb"].as_f64().unwrap()+1e-5
            && (a["passes_local_tail_gate"]!=true || t["passes_local_tail_gate"]==true)
    })
}
fn main()->Result<(),String>{
    let started=Instant::now();let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3{return Err("INPUT PATHS OUTPUT".into());}
    let out=std::path::Path::new(&args[2]);if out.exists(){return Err("output exists".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let bytes=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples=u32::from_le_bytes(bytes.get(..4).ok_or("short cache")?.try_into().unwrap());
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    let mut s=PreflopSolver::load_game(&args[0],eq.clone())?;
    if s.nodes.len()!=1_567_754 || s.cfg.positions.len()!=8 || s.iteration!=1050
        || s.multiway_equity_model()!="coupled_deck_v1"{return Err("registered original large anchor required".into());}
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if paths.len()!=27{return Err("registered 27 paths required".into());}
    let count=paths.len();let plan=s.research_nonroot_policy_plan(&paths,12)?;
    let heldout:Vec<Vec<usize>>=serde_json::from_value(plan["heldout_paths"].clone()).unwrap();
    let all_paths:Vec<_>=paths.iter().chain(&heldout).cloned().collect();
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    write(out.join("plan.json"),&plan)?;write(out.join("all-paths.json"),&json!(all_paths))?;
    let before=s.arena_snapshot();let age=s.iteration;let (original_gaps,original_evs)=global(&s)?;
    if original_gaps.iter().sum::<f64>()>0.005{return Err("anchor does not pass global gate".into());}
    let original:Vec<Vec<f32>>=plan["selected"].as_array().unwrap().iter().map(|r|serde_json::from_value(r["policy"].clone()).unwrap()).collect();
    s.research_set_nonroot_averages(&paths,&original)?;
    let mut anchor=evaluate(&s,&all_paths,count)?;
    if anchor["reachable"]!=true || original_gaps.iter().zip(anchor["global_gaps"].as_array().unwrap()).any(|(a,b)|(a-b.as_f64().unwrap()).abs()>1e-5){
        return Err("normalization changed evaluation or anchor paths unreachable".into());
    }
    anchor["policies"]=json!(original);
    let mut current=anchor.clone();let mut cycles=Vec::new();
    println!("ANCHOR {}",json!({"gap":anchor["gap"],"passed":anchor["passed"],"objective":anchor["objective"]}));
    for cycle in 0..3{
        if current["qualified"]==true {break;}
        let baseline=current.clone();let source_rows=&baseline["rows"].as_array().unwrap()[..count];
        let source=policies(source_rows)?;let mut targets=Vec::new();
        for (row,p) in source_rows.iter().zip(&source){
            let mut q=vec![0f64;p.len()];let na=p.len()/NC;
            for (h,hand) in row["candidate"]["hands"].as_array().unwrap().iter().enumerate(){
                for a in 0..na{q[a*NC+h]=hand["action_values_bb"][a].as_f64().ok_or("invalid action value")?;}
            }
            targets.push(best_response_target(p,&q)?);
        }
        let mut best=baseline["objective"].as_f64().unwrap();let mut selected=None;
        let mut selected_policy:Vec<Vec<f32>>=serde_json::from_value(baseline["policies"].clone()).unwrap();let mut candidates=Vec::new();
        for alpha in [0.125,0.25,0.5,0.875,1.0]{
            let mixed:Vec<_>=source.iter().zip(&targets).map(|(p,t)|mix_policy(p,t,alpha)).collect::<Result<_,_>>()?;
            s.research_set_nonroot_averages(&paths,&mixed)?;
            let mut trial=evaluate(&s,&all_paths,count)?;let eligible=protected(&trial,&anchor,count);
            trial["alpha"]=json!(alpha);trial["eligible"]=json!(eligible);trial["policies"]=json!(mixed);
            println!("CANDIDATE {}",json!({"cycle":cycle,"alpha":alpha,"gap":trial["gap"],"passed":trial["passed"],"objective":trial["objective"],"eligible":eligible}));
            if eligible && trial["objective"].as_f64().unwrap()<best{
                best=trial["objective"].as_f64().unwrap();selected=Some(candidates.len());selected_policy=mixed;
            }
            candidates.push(trial);
        }
        if best>=baseline["objective"].as_f64().unwrap()-1e-6 {
            selected=None;selected_policy=serde_json::from_value(baseline["policies"].clone()).unwrap();
        }
        s.research_set_nonroot_averages(&paths,&selected_policy)?;
        current=if let Some(i)=selected{candidates[i].clone()}else{baseline.clone()};
        cycles.push(json!({"baseline":baseline,"targets":targets,"candidates":candidates,"selected_index":selected}));
        if selected.is_none(){break;}
    }
    let final_check=evaluate(&s,&all_paths,count)?;let second_check=evaluate(&s,&all_paths,count)?;
    for check in [&final_check,&second_check]{
        if check["global_gaps"]!=current["global_gaps"] || check["rows"]!=current["rows"]{
            return Err("selected policy full recheck differs".into());
        }
    }
    let after=s.arena_snapshot();let spans:Vec<_>=plan["selected"].as_array().unwrap().iter().map(|r|
        r["start"].as_u64().unwrap() as usize..r["end"].as_u64().unwrap() as usize).collect();
    if s.iteration!=age || before.0.iter().zip(&after.0).any(|(a,b)|a.to_bits()!=b.to_bits())
        || before.1.iter().zip(&after.1).enumerate().any(|(i,(a,b))|!spans.iter().any(|r|r.contains(&i)) && a.to_bits()!=b.to_bits()){
        return Err("unselected history changed".into());
    }
    let save=out.join("final.gtop");s.save_game(save.to_str().unwrap())?;
    let reload=PreflopSolver::load_game(save.to_str().unwrap(),eq)?;
    if reload.arena_snapshot()!=after || reload.iteration!=age{return Err("saved history roundtrip differs".into());}
    write(out.join("result.json"),&json!({"input":args[0],"nodes":s.nodes.len(),"global_age":age,
        "plan":plan,"original_global_gaps":original_gaps,"original_global_evs":original_evs,"anchor":anchor,"cycles":cycles,
        "final_check":final_check,"second_check":second_check,"regrets_unchanged":true,"unselected_averages_unchanged":true,
        "roundtrip_exact":true,"normal_global_resume_supported":false,"seconds":started.elapsed().as_secs_f64()}))
}
