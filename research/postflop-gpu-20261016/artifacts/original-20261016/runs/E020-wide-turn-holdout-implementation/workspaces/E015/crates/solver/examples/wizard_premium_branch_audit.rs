//! Read-only saved-policy audit of the premium-hand 4-bet/jam decision.
use serde_json::json;
use solver::preflop::{PreflopSolver, equity::{EquityTable, NUM_CLASSES, class_label}};
use std::sync::Arc;

fn main() {
    let args:Vec<_>=std::env::args().collect();
    let save=args.get(1).expect("save path");
    let output=args.get(2).expect("new output path");
    assert!(!std::path::Path::new(output).exists(),"preserve prior evidence");
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().unwrap();
    let eq=Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin",20000));
    let s=PreflopSolver::load_game(save,eq).unwrap();
    assert_eq!(s.iteration,1000);
    let before=s.arena_snapshot();
    let root=vec![1,2,0,0,0,0,0,0];
    let decision=s.node_view(&root).unwrap();
    assert_eq!(decision.actor,Some(1));
    assert_eq!(decision.actions[2].to,45.0);
    assert_eq!(decision.actions[3].to,200.0);
    let mut pending=vec![root.clone()];let mut nodes=Vec::new();
    while let Some(path)=pending.pop() {
        let view=s.node_view(&path).unwrap();
        let export=if view.exportable {Some(s.export_spot(&path).unwrap())}else{None};
        let action_values=if view.kind=="action" {
            let values=s.diagnostic_action_evs(&path,false).unwrap();
            Some((0..NUM_CLASSES).filter(|&h|["AA","KK","QQ","AKs","A5s","QJs"].contains(&class_label(h).as_str()))
                .map(|h|json!({"hand":class_label(h),"action_ev_bb":values.iter().map(|v|v[h]).collect::<Vec<_>>()})).collect::<Vec<_>>())
        }else{None};
        if view.kind=="action" {
            for a in (0..view.actions.len()).rev() {
                if path==root && a<2 {continue;}
                let mut child=path.clone();child.push(a);pending.push(child);
            }
        }
        nodes.push(json!({"path":path,"view":view,"export":export,"selected_action_values":action_values}));
        assert!(nodes.len()<100,"unexpectedly large branch");
    }
    assert_eq!(before,s.arena_snapshot());
    let result=json!({"save":save,"iteration":s.iteration,"config":s.cfg,"nodes":nodes,
        "note":"Offline saved-policy evaluation; action EVs relative to folding at each node. Independent-class preflop model; no new solve."});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
