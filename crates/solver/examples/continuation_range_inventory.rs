//! Offline saved-game range inventory. Reads a save; never solves or contacts the app.
use serde_json::{json, Value};
use solver::preflop::{PreflopSolver, equity::{EquityTable,class_prob,NUM_CLASSES}};
use std::{collections::BTreeMap, sync::Arc};

#[derive(Clone)]
struct Candidate { path:Vec<usize>, probability:f64, raises:u8, oop:usize, ip:usize }

fn walk(s:&PreflopSolver,node:usize,path:&mut Vec<usize>,reach:&mut [Vec<f32>],mass:&mut [f64],
        buckets:&mut BTreeMap<(u8,bool,bool),Vec<Candidate>>) {
    let probability:f64=mass.iter().product();
    if probability<1e-9 {return;}
    let nd=&s.nodes[node];
    if nd.kind!=0 {
        if nd.kind!=2 || nd.live.count_ones()!=2 {return;}
        let seats:Vec<_>=s.postflop_order().into_iter().filter(|&p|nd.live&(1<<p)!=0).collect();
        let (oop,ip)=(seats[0],seats[1]);
        let remaining=(s.cfg.stack-nd.invested[oop]+s.cfg.ante).min(s.cfg.stack-nd.invested[ip]+s.cfg.ante);
        if nd.pot<=0. || !(1.0..=20.0).contains(&(remaining/nd.pot)) {return;}
        let key=(nd.raises.min(3),nd.aggressor as usize==oop,oop>=s.n-2 || ip>=s.n-2);
        let bucket=buckets.entry(key).or_default();
        bucket.push(Candidate{path:path.clone(),probability,raises:nd.raises,oop,ip});
        bucket.sort_by(|a,b|b.probability.total_cmp(&a.probability));
        bucket.truncate(24);
        return;
    }
    let actor=nd.actor as usize;let old=reach[actor].clone();let old_mass=mass[actor];
    let sigma=s.average_strategy(node);
    for a in 0..nd.actions.len() {
        for h in 0..NUM_CLASSES {reach[actor][h]=old[h]*sigma[a*NUM_CLASSES+h];}
        mass[actor]=reach[actor].iter().map(|&v|v as f64).sum();
        path.push(a);walk(s,s.child(node,a),path,reach,mass,buckets);path.pop();
    }
    reach[actor]=old;mass[actor]=old_mass;
}

fn main()->Result<(),String> {
    let args:Vec<_>=std::env::args().collect();
    if args.len()!=3 {return Err("continuation_range_inventory SAVE OUTPUT".into());}
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let s=PreflopSolver::load_game(&args[1],eq)?;
    let mut reach=vec![(0..NUM_CLASSES).map(class_prob).collect::<Vec<_>>();s.n];
    let mut buckets=BTreeMap::new();
    walk(&s,0,&mut vec![],&mut reach,&mut vec![1.;s.n],&mut buckets);
    let mut rows=Vec::new();let mut skipped=0;
    for c in buckets.values().flatten() {
        let v=s.node_view(&c.path)?;
        if v.strategy_note.is_some() || v.history.iter().any(|h|h.strategy_note.is_some()) {skipped+=1;continue;}
        assert!(v.exportable);
        assert!((v.branch_probability-c.probability).abs()<1e-9);
        let remaining=(s.cfg.stack-v.invested[c.oop]+s.cfg.ante).min(s.cfg.stack-v.invested[c.ip]+s.cfg.ante);
        let row:Value=json!({"path":c.path,"branch_probability":c.probability,"raises":c.raises,
            "oop":c.oop,"ip":c.ip,"oop_position":s.cfg.positions[c.oop],"ip_position":s.cfg.positions[c.ip],
            "pot":v.pot,"stack":remaining,"weights":[v.reaches_all[c.oop],v.reaches_all[c.ip]],"history":v.history});
        rows.push(row);
    }
    let result=json!({"source":args[1],"iteration":s.iteration,"config":s.cfg,"candidates":rows,
        "skipped_unavailable":skipped,"selection":"Top 24 independent-reach branches per raise-depth/aggressor/blind bucket; HU SPR 1-20, branch probability >=1e-9. Inputs only, not reference payoff labels."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result).unwrap()).map_err(|e|e.to_string())?;
    eprintln!("Exported {} candidates; skipped {} unavailable",rows.len(),skipped);
    Ok(())
}
