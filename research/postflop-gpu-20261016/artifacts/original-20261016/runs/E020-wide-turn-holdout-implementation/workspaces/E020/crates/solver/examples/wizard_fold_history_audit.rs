//! Export only the saved action probabilities needed for a folded-card audit.
use serde_json::json;
use solver::preflop::{PreflopSolver, equity::EquityTable};
use std::sync::Arc;

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let save = args.get(1).expect("save path");
    let output = args.get(2).expect("new output path");
    assert!(!std::path::Path::new(output).exists(), "preserve prior evidence");
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global().unwrap();
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let s = PreflopSolver::load_game(save, eq).unwrap();
    assert_eq!(s.iteration, 1000);
    let before = s.arena_snapshot();
    let path = vec![1, 2, 0, 0, 0, 0, 0, 0];
    let mut actions = Vec::new();
    for depth in 0..path.len() {
        let prefix = &path[..depth];
        let view = s.node_view(prefix).unwrap();
        let chosen = path[depth];
        let sigma = view.strategy.as_ref().unwrap();
        actions.push(json!({"prefix":prefix,"actor":view.actor,"position":view.actor_pos,
            "chosen":chosen,"label":view.actions[chosen].label,
            "probabilities":sigma[chosen*169..(chosen+1)*169]}));
    }
    assert_eq!(before, s.arena_snapshot());
    let result = json!({"save":save,"iteration":s.iteration,"config":s.cfg,"path":path,"actions":actions,
        "note":"Read-only saved average strategy along the observed history. No solving or production access."});
    std::fs::write(output, serde_json::to_vec_pretty(&result).unwrap()).unwrap();
}
