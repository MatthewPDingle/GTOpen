//! Offline root-only trust-region diagnostic. INPUT PATHS OUTPUT.
use solver::preflop::{equity::EquityTable,gpu::PreflopGpu,PreflopSolver};
use serde_json::{json,Value};
use std::{collections::HashSet,sync::Arc,time::Instant};
const NC:usize=169;

fn main()->Result<(),String> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("INPUT PATHS OUTPUT".into());}
    let out=std::path::Path::new(&args[2]);
    if out.exists(){return Err("output exists".into());}
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if paths.is_empty() || paths.len()>64 || paths.iter().any(|p|p.is_empty() || p.len()>64)
        || paths.iter().collect::<HashSet<_>>().len()!=paths.len() {return Err("distinct bounded audit paths required".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let bytes=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples=u32::from_le_bytes(bytes.get(..4).ok_or("short equity cache")?.try_into().unwrap());
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    let mut s=PreflopSolver::load_game(&args[0],eq.clone())?;
    for p in &paths {s.research_refinement_plan(p)?;}
    if s.nodes.len()>2_000_000 || s.multiway_equity_model()!="coupled_deck_v1" {return Err("bounded canonical parent required".into());}
    let age=s.iteration;let before=s.arena_snapshot();
    let started=Instant::now();
    let mut gpu=PreflopGpu::new(&s,23000)?;
    let root=gpu.research_frontier_action_values(&s,&[vec![]])?["rows"][0].clone();
    drop(gpu);
    if root["forced_or_frozen"]!=false {return Err("root must be unconstrained".into());}
    let na=root["actions"].as_array().ok_or("missing actions")?.len();
    let mut original=vec![0f32;na*NC];let mut target=vec![0f32;na*NC];
    for (h,hand) in root["hands"].as_array().ok_or("missing hands")?.iter().enumerate() {
        if h>=NC || hand["class_index"]!=json!(h) {return Err("invalid hand ordering".into());}
        let q:Vec<f64>=serde_json::from_value(hand["action_values_counterfactual_bb"].clone()).map_err(|e|e.to_string())?;
        let sigma:Vec<f32>=serde_json::from_value(hand["average_probabilities"].clone()).map_err(|e|e.to_string())?;
        if q.len()!=na || sigma.len()!=na || q.iter().any(|v|!v.is_finite()) {return Err("invalid root action values".into());}
        let best=q.iter().copied().fold(f64::NEG_INFINITY,f64::max);
        let eligible:Vec<_>=(0..na).filter(|&a|best-q[a]<=1e-8).collect();
        let mass:f64=eligible.iter().map(|&a|sigma[a] as f64).sum();
        for a in 0..na {original[a*NC+h]=sigma[a];}
        for &a in &eligible {target[a*NC+h]=if mass>1e-12 {(sigma[a] as f64/mass) as f32} else {1.0/eligible.len() as f32};}
    }
    std::fs::create_dir_all(out).map_err(|e|e.to_string())?;
    let mut candidates=Vec::new();let mut best_gap=f64::INFINITY;let mut selected=0usize;
    let mut selected_policy=original.clone();
    // Fixed grid: choose minimum unrestricted global gap, not whichever local
    // audit happens to pass. Every candidate retains all later policies.
    for alpha in [0.0,0.0625,0.125,0.25,0.5,1.0] {
        let mut policy:Vec<f32>=original.iter().zip(&target).map(|(&a,&b)|((1.0-alpha)*a as f64+alpha*b as f64) as f32).collect();
        for h in 0..NC {
            let sum:f64=(0..na).map(|a|policy[a*NC+h] as f64).sum();
            for a in 0..na {policy[a*NC+h]=(policy[a*NC+h] as f64/sum) as f32;}
        }
        if alpha!=0.0 {s.research_set_root_average(&policy)?;}
        let mut gpu=PreflopGpu::new(&s,23000)?;
        let (gaps,evs)=gpu.gaps_and_evs()?;drop(gpu);
        if gaps.len()!=s.cfg.positions.len() || evs.len()!=gaps.len() || gaps.iter().any(|g|!g.is_finite() || *g<0.0)
            || evs.iter().any(|g|!g.is_finite()) {return Err("invalid global check".into());}
        let rows:Vec<Value>=paths.iter().map(|p|s.research_conditioned_action_quality_against(&s,p).map(|v|json!({"candidate":v}))).collect::<Result<_,_>>()?;
        let passed=rows.iter().filter(|r|r["candidate"]["passes_local_tail_gate"]==true
            && r["candidate"]["conditioned_before_evaluation"]==true).count();
        let gap:f64=gaps.iter().sum();let qualified=gap<=0.005 && passed==paths.len();
        println!("CANDIDATE {}",json!({"alpha":alpha,"gap":gap,"passed":passed,"qualified":qualified}));
        if gap<best_gap {best_gap=gap;selected=candidates.len();selected_policy=policy.clone();}
        candidates.push(json!({"alpha":alpha,"global_gaps":gaps,"global_evs":evs,"rows":rows,
            "passed":passed,"qualified":qualified,"root_policy":policy}));
    }
    s.research_set_root_average(&selected_policy)?;
    let after=s.arena_snapshot();let root_len=na*NC;
    if before.0[root_len..]!=after.0[root_len..] || before.1[root_len..]!=after.1[root_len..] || s.iteration!=age {
        return Err("root repair changed later history or global age".into());
    }
    let mut gpu=PreflopGpu::new(&s,23000)?;
    let (gaps,evs)=gpu.gaps_and_evs()?;drop(gpu);
    let recorded:Vec<f64>=serde_json::from_value(candidates[selected]["global_gaps"].clone()).unwrap();
    if gaps.iter().zip(&recorded).any(|(a,b)|(a-b).abs()>1e-5) {return Err("selected policy recheck differs".into());}
    let save=out.join("final.gtop");s.save_game(save.to_str().ok_or("invalid save")?)?;
    let reload=PreflopSolver::load_game(save.to_str().unwrap(),eq)?;
    if reload.arena_snapshot()!=after {return Err("roundtrip mismatch".into());}
    let result=json!({"input":args[0],"nodes":s.nodes.len(),"global_age":age,"root_values":root,
        "candidates":candidates,"selected_index":selected,"final_global_gaps":gaps,"final_global_evs":evs,
        "nonroot_arenas_unchanged":true,"roundtrip_exact":true,"normal_global_resume_supported":false,
        "seconds":started.elapsed().as_secs_f64(),"scope":"Root-only policy mixture; selection by minimum full global gap; unchanged 27-path and global qualification gates"});
    std::fs::write(out.join("result.json"),serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
