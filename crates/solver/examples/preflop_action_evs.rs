//! Evaluate a saved game without changing it or running further iterations.
use solver::preflop::{
    PreflopSolver,
    equity::{EquityTable, NUM_CLASSES, class_label},
};
use std::sync::Arc;
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let save = args.get(1).expect("save path");
    let output = args.get(2).expect("output JSON path");
    let path: Vec<usize> = args.get(3).map_or(vec![1], |s| {
        s.split(',')
            .filter(|s| !s.is_empty())
            .map(|s| s.parse().unwrap())
            .collect()
    });
    let br = args.get(4).is_some_and(|v| v == "br");
    rayon::ThreadPoolBuilder::new()
        .num_threads(16)
        .build_global()
        .unwrap();
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let s = PreflopSolver::load_game(save, eq).unwrap();
    let before = s.arena_snapshot();
    let view = s.node_view(&path).unwrap();
    eprintln!("Evaluating {:?}, iteration {}", path, s.iteration);
    let t = std::time::Instant::now();
    let values = s.diagnostic_action_evs(&path, br).unwrap();
    assert_eq!(
        before,
        s.arena_snapshot(),
        "evaluation changed the saved strategy"
    );
    let sigma = view.strategy.as_ref().unwrap();
    let hands:Vec<_>=(0..NUM_CLASSES).map(|h|serde_json::json!({
        "hand":class_label(h),"actions":view.actions.iter().enumerate().map(|(a,x)|
            serde_json::json!({"label":x.label,"frequency":sigma[a*NUM_CLASSES+h],"ev_bb":values[a][h]})).collect::<Vec<_>>()
    })).collect();
    std::fs::write(output,serde_json::to_vec_pretty(&serde_json::json!({
        "config":s.cfg,"iteration":s.iteration,"path":path,"actor":view.actor_pos,
        "seconds":t.elapsed().as_secs_f64(),"units":"original bb relative to folding here",
        "evaluation":if br {"one action then hero best response against saved opponents"} else {"one action then saved average policies; no further solving"}, "hands":hands
    })).unwrap()).unwrap();
    eprintln!("Done in {:.2}s", t.elapsed().as_secs_f64());
}
