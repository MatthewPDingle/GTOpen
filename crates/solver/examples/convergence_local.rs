//! Offline selected-path audit: CANDIDATE REFERENCE OUTPUT.json
use solver::preflop::{PreflopSolver,equity::EquityTable};
use std::sync::Arc;
use serde_json::json;
fn main()->Result<(),String>{
    let a:Vec<_>=std::env::args().skip(1).collect(); if a.len()!=3{return Err("CANDIDATE REFERENCE OUTPUT".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",u32::from_le_bytes(b[..4].try_into().unwrap())));
    let c=PreflopSolver::load_game(&a[0],eq.clone())?;
    let r=PreflopSolver::load_game(&a[1],eq)?;
    let independent_cpu=if c.nodes.len()<=50_000 {
        let (cg,ce)=c.gaps_and_evs(); let (rg,re)=r.gaps_and_evs();
        Some(json!({"candidate_gaps":cg,"candidate_evs":ce,"reference_gaps":rg,"reference_evs":re}))
    } else {None};
    let mut paths=Vec::new();
    // Open, earlier players fold, BTN and SB call: includes the BB cheap-call concern.
    // Also audit the same line with no callers, plus a limped line.
    for scenario in 0..3 {
        let mut path=Vec::new();
        loop {
            let mut node=0usize;
            for &act in &path {node=r.child(node,act);}
            let nd=&r.nodes[node]; if nd.actions.is_empty(){break;}
            let pos=&r.cfg.positions[nd.actor as usize];
            if pos=="BB" || (pos=="SB" && scenario==0) { if !paths.contains(&path){paths.push(path.clone());} }
            if pos=="BB" {break;}
            let desired=if path.is_empty(){if scenario==2{"Limp"}else{"Raise"}}
                else if scenario==0 && (pos=="BTN" || pos=="SB") {"Call"} else {"Fold"};
            let Some(i)=nd.actions.iter().position(|x|x.label.starts_with(desired)) else {break;};
            path.push(i);
        }
    }
    let mut rows=Vec::new();
    for p in paths {
        let candidate=c.research_local_action_quality_against(&r,&p)?;
        let baseline=r.research_local_action_quality_against(&r,&p)?;
        rows.push(json!({"candidate":candidate,"reference_self":baseline}));
    }
    if rows.is_empty(){return Err("no local paths found".into());}
    std::fs::write(&a[2],serde_json::to_vec_pretty(&json!({"candidate":a[0],"reference":a[1],"independent_cpu":independent_cpu,"rows":rows})).unwrap()).map_err(|e|e.to_string())?;
    Ok(())
}
