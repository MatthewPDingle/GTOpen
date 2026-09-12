//! Read-only full-parent early/neighboring decision audit. INPUT BROAD_PATHS OUTPUT.
use solver::preflop::{equity::EquityTable,gpu::PreflopGpu,PreflopSolver};
use std::{collections::BTreeSet,sync::Arc,time::Instant};
use serde_json::json;

fn node_at(s:&PreflopSolver,path:&[usize])->Result<usize,String> {
    if path.len()>64 {return Err("path too long".into());}
    let mut node=0;
    for &a in path {if a>=s.nodes[node].actions.len(){return Err("invalid path".into());}node=s.child(node,a);}
    Ok(node)
}
fn main()->Result<(),String> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("INPUT BROAD_PATHS OUTPUT".into());}
    if std::path::Path::new(&args[2]).exists(){return Err("output exists".into());}
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e|e.to_string())?;
    let b=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples=u32::from_le_bytes(b.get(..4).ok_or("short cache")?.try_into().unwrap());
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    let s=PreflopSolver::load_game(&args[0],eq)?;
    let broad:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if broad.is_empty() || broad.len()>64 {return Err("bounded registered paths required".into());}
    let mut paths=BTreeSet::new();paths.insert(vec![]);
    // All decisions through depth two, plus registered paths, their ancestors,
    // and every action-node sibling immediately below those ancestors.
    for a in 0..s.nodes[0].actions.len() {
        let child=s.child(0,a);if s.nodes[child].actions.is_empty(){continue;}
        paths.insert(vec![a]);
        for b in 0..s.nodes[child].actions.len() {if !s.nodes[s.child(child,b)].actions.is_empty(){paths.insert(vec![a,b]);}}
    }
    for path in &broad {
        node_at(&s,path)?;
        for len in 0..=path.len() {
            let prefix=path[..len].to_vec();let node=node_at(&s,&prefix)?;
            if s.nodes[node].actions.is_empty(){return Err("registered path is not an action node".into());}
            paths.insert(prefix.clone());
            if len<path.len() {for a in 0..s.nodes[node].actions.len() {
                if s.nodes[s.child(node,a)].actions.is_empty(){continue;}
                let mut sibling=prefix.clone();sibling.push(a);paths.insert(sibling);
            }}
        }
    }
    if paths.len()>256 {return Err("frontier exceeds registered 256-node cap".into());}
    let paths:Vec<_>=paths.into_iter().collect();
    let start=Instant::now();let mut gpu=PreflopGpu::new(&s,23000)?;
    let (gaps,evs)=gpu.gaps_and_evs()?;
    let mut result=gpu.research_frontier_action_values(&s,&paths)?;
    for row in result["rows"].as_array_mut().unwrap() {
        let path:Vec<usize>=serde_json::from_value(row["path"].clone()).unwrap();
        row["in_selected_subtree"]=json!(broad.iter().any(|p|path.starts_with(p)));
        row["strict_ancestor"]=json!(broad.iter().any(|p|p.len()>path.len() && p.starts_with(&path)));
    }
    result["input"]=json!(args[0]);result["global_gaps"]=json!(gaps);result["global_evs"]=json!(evs);
    result["seconds"]=json!(start.elapsed().as_secs_f64());result["path_count"]=json!(paths.len());
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())
}
