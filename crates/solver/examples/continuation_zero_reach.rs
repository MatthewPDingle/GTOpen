//! Read-only research diagnostic. Never evaluates payoffs or changes saved arenas.
use solver::preflop::{equity::{class_prob, EquityTable}, PreflopSolver};
use serde_json::{json, Value};
use std::{io::{BufRead, BufReader}, sync::Arc};

fn normalize(values: &[f32], actions: usize) -> Vec<f32> {
    let mut out = vec![0.; values.len()];
    for h in 0..169 {
        let sum: f32 = (0..actions).map(|a| values[a*169+h].max(0.)).sum();
        for a in 0..actions { out[a*169+h] = if sum > 1e-12 { values[a*169+h].max(0.)/sum } else { 1./actions as f32 }; }
    }
    out
}

#[derive(Default)]
struct Audit {
    visited: usize, eligible: usize, current_enabled: usize, average_enabled: usize,
    current_own_zero: usize, average_own_zero: usize, flips: Vec<Value>,
    selected: Vec<Value>,
}

fn walk(s: &PreflopSolver, regrets: &[f32], node: usize, current: &mut Vec<Vec<f32>>,
        average: &mut Vec<Vec<f32>>, path: &mut Vec<usize>, selected: &[Vec<usize>], audit: &mut Audit) {
    assert!(path.len() <= 64);
    audit.visited += 1;
    let nd = &s.nodes[node];
    let masses = |r: &Vec<Vec<f32>>| r.iter().map(|v|v.iter().sum::<f32>() as f64).collect::<Vec<_>>();
    if selected.contains(path) { audit.selected.push(json!({"path":path,"current":masses(current),"average":masses(average)})); }
    if nd.kind == 0 {
        let p = nd.actor as usize;
        let na = nd.actions.len();
        let sigma = normalize(&regrets[nd.data_off..nd.data_off+na*169], na);
        let avg = s.average_strategy(node);
        let old_current = current[p].clone(); let old_average = average[p].clone();
        for a in 0..na {
            for h in 0..169 { current[p][h]=old_current[h]*sigma[a*169+h]; average[p][h]=old_average[h]*avg[a*169+h]; }
            path.push(a); walk(s,regrets,s.child(node,a),current,average,path,selected,audit); path.pop();
        }
        current[p]=old_current; average[p]=old_average;
    } else if nd.kind == 2 && nd.live.count_ones() == 2 {
        let live: Vec<usize> = (0..s.n).filter(|&p|nd.live & (1<<p)!=0).collect();
        let remaining = live.iter().map(|&p|s.cfg.stack-nd.invested[p]+s.cfg.ante).fold(f64::INFINITY,f64::min);
        let spr = (remaining/nd.pot).max(0.);
        if !(1. ..=20.).contains(&spr) { return; }
        audit.eligible += 1;
        let cm = masses(current); let am = masses(average);
        let ce = live.iter().all(|&p| cm[p]>0.); let ae = live.iter().all(|&p|am[p]>0.);
        audit.current_enabled += ce as usize; audit.average_enabled += ae as usize;
        let mut traversers = Vec::new();
        for &p in &live {
            let cp: f64 = cm.iter().enumerate().filter(|(q,_)|*q!=p).map(|(_,v)|v).product();
            let ap: f64 = am.iter().enumerate().filter(|(q,_)|*q!=p).map(|(_,v)|v).product();
            if cm[p]==0. && cp>0. { audit.current_own_zero+=1; }
            if am[p]==0. && ap>0. { audit.average_own_zero+=1; }
            if ce!=ae && (cp>0. || ap>0.) {
                traversers.push(json!({"seat":p,"position":s.cfg.positions[p],"current_counterfactual_mass":cp,"average_counterfactual_mass":ap}));
            }
        }
        if !traversers.is_empty() { audit.flips.push(json!({"node":node,"path":path,"spr":spr,"pot":nd.pot,"live":live,"current_enabled":ce,"average_enabled":ae,"current_mass":cm,"average_mass":am,"traversers":traversers})); }
    }
}

fn main() -> Result<(), String> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("INPUT.gtop PATHS.json OUTPUT.json".into());}
    if std::path::Path::new(&args[2]).exists(){return Err("refusing to overwrite output".into());}
    let mut reader=BufReader::new(std::fs::File::open(&args[0]).map_err(|e|e.to_string())?);
    let mut line=String::new(); reader.read_line(&mut line).map_err(|e|e.to_string())?;
    if !line.starts_with("GTOPREFLOP") {return Err("invalid save".into());}
    line.clear(); reader.read_line(&mut line).map_err(|e|e.to_string())?;
    let header:Value=serde_json::from_str(&line).map_err(|e|e.to_string())?;
    if !header["point_locks"].as_array().ok_or("missing locks")?.is_empty()
        || header["seat_frozen"].as_array().ok_or("missing frozen")?.iter().any(|v|v!=false)
        || header["seat_profiles"].as_array().ok_or("missing profiles")?.iter().any(|v|!v.is_null())
        || !header["hero"].is_null() { return Err("only unconstrained research saves supported".into()); }
    rayon::ThreadPoolBuilder::new().num_threads(2).build_global().map_err(|e|e.to_string())?;
    let cache=std::fs::read("cache/preflop_eq169.bin").map_err(|e|e.to_string())?;
    let samples=u32::from_le_bytes(cache.get(..4).ok_or("short cache")?.try_into().unwrap());
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",samples));
    let s=PreflopSolver::load_game(&args[0],eq)?;
    if s.nodes.len()>2_000_000 { return Err("oversized diagnostic".into()); }
    let paths:Vec<Vec<usize>>=serde_json::from_slice(&std::fs::read(&args[1]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let (regrets,sums)=s.arena_snapshot(); drop(sums);
    if regrets.iter().any(|x|!x.is_finite()) {return Err("nonfinite regrets".into());}
    let mut current=vec![(0..169).map(class_prob).collect::<Vec<_>>();s.n]; let mut average=current.clone();
    let mut audit=Audit::default();
    walk(&s,&regrets,0,&mut current,&mut average,&mut Vec::new(),&paths,&mut audit);
    if audit.visited!=s.nodes.len() || audit.selected.len()!=paths.len() {return Err("incomplete traversal".into());}
    let result=json!({"input":args[0],"iteration":s.iteration,"nodes":audit.visited,
        "eligible_hu_terminals":audit.eligible,"current_learned_enabled":audit.current_enabled,"average_learned_enabled":audit.average_enabled,
        "current_own_zero_positive_opponents":audit.current_own_zero,"average_own_zero_positive_opponents":audit.average_own_zero,
        "flips":audit.flips,"selected":audit.selected,
        "scope":"CPU f32 reach reconstruction at one checkpoint, no payoff evaluation. Model-enable flips are not an additive gap decomposition, accuracy proof or causal attribution."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}

#[cfg(test)] mod tests {
    use super::*;
    #[test] fn regret_matching_keeps_zero_actions_and_uniform_unvisited_hands() {
        let mut r=vec![0.;338]; r[0]=-1.;r[169]=3.;r[1]=1.;r[170]=3.;
        let p=normalize(&r,2);
        assert_eq!((p[0],p[169]),(0.,1.));assert_eq!((p[1],p[170]),(0.25,0.75));
        assert_eq!((p[2],p[171]),(0.5,0.5));
    }
}
