//! Read-only export of one complete two-live-player subtree from a frozen save.
use serde_json::{json, Value};
use solver::preflop::{PreflopSolver, equity::EquityTable};
use std::sync::Arc;

fn collect(s: &PreflopSolver, i: usize, path: Vec<usize>, nodes: &mut Vec<Value>) -> usize {
    let local = nodes.len();
    nodes.push(Value::Null);
    let n = &s.nodes[i];
    assert!(n.live & !6 == 0);
    if n.kind == 0 { assert!([1, 2].contains(&n.actor)); }
    let children: Vec<usize> = (0..n.actions.len()).map(|a| {
        let mut next = path.clone(); next.push(a);
        collect(s, s.child(i,a), next, nodes)
    }).collect();
    nodes[local] = json!({"original_node":i,"path":path,"kind":n.kind,
        "original_actor":n.actor,"actor":if n.actor==1 {0} else {1},
        "children":children,"strategy":if n.kind==0 {s.average_strategy(i)} else {vec![]},
        "pot":n.pot,"invested":[n.invested[1],n.invested[2]],
        "original_invested":n.invested,"original_live":n.live,
        "winner":if n.winner==1 {0} else {1},"original_winner":n.winner,
        "r":[n.r.get(1),n.r.get(2)],
        "actions":n.actions.iter().map(|a|json!({"kind":a.kind,"to":a.to,"label":a.label})).collect::<Vec<_>>()});
    local
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();
    assert_eq!(args.len(),2,"SAVE OUTPUT");
    assert!(!std::path::Path::new(&args[1]).exists(),"preserve evidence");
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global()?;
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let s=PreflopSolver::load_game(&args[0],eq)?;
    assert_eq!(s.iteration,1000);assert_eq!(s.cfg.realization,"balanced");
    let before=s.arena_snapshot();
    let path=vec![1,2,0,0,0,0,0,0];let (root,reaches)=s.walk(&path)?;
    assert_eq!(s.nodes[root].live,6);
    let mut nodes=Vec::new();collect(&s,root,path.clone(),&mut nodes);
    let order:Vec<_>=s.postflop_order().into_iter().filter(|p|[1,2].contains(p)).collect();
    assert_eq!(order,vec![1,2]);
    let out=json!({"save":args[0],"iteration":s.iteration,"config":s.cfg,
        "root_path":path,"original_seats":[1,2],"postflop_order":[0,1],
        "incoming_class_mass":[reaches[1],reaches[2]],
        "class_base":s.fit.as_ref().map(|f|f.class_base()),"nodes":nodes});
    assert_eq!(before,s.arena_snapshot());
    std::fs::write(&args[1],serde_json::to_vec_pretty(&out)?)?;
    println!("Exported {} nodes without changing the saved strategy",nodes.len());
    Ok(())
}
