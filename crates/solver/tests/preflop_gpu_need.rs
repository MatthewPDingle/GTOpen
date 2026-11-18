//! The Preflop Lab says before a build whether a game fits the graphics
//! card. That figure comes from the size walk's counts; it must equal what
//! the built game reports. Arithmetic only: no CUDA device is needed.
#![cfg(feature = "gpu")]
use solver::preflop::{
    equity::EquityTable, estimate_tree,
    gpu::{minimum_need_mb, minimum_need_of, policy_need_mb, tree_need_mb},
    PreflopConfig, PreflopSolver,
};
use std::sync::Arc;

fn games() -> Vec<serde_json::Value> {
    let six = ["UTG", "HJ", "CO", "BTN", "SB", "BB"];
    let eight = ["UTG", "UTG1", "MP", "HJ", "CO", "BTN", "SB", "BB"];
    vec![
        // learned flop values and blockers, as a new game from the form
        serde_json::json!({"positions": six, "stack": 100.0, "posts": [0, 0, 0, 0, 0.5, 1],
            "limp": false, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 4, "add_allin": false,
            "rake_pct": 5.0, "rake_cap": 3.0, "realization": "leafnet", "leaf_net": "v3", "card_removal": true}),
        // limps, two open sizes and the all-in option: all-in terminals have no flop to learn
        serde_json::json!({"positions": six, "stack": 100.0, "posts": [0, 0, 0, 0, 0.5, 1],
            "limp": true, "open_raises": [2.5, 4.0], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
            "rake_pct": 5.0, "rake_cap": 3.0, "realization": "leafnet", "leaf_net": "v3", "card_removal": true}),
        // heads-up: no multiway pots at all
        serde_json::json!({"positions": ["SB", "BB"], "stack": 100.0, "posts": [0.5, 1],
            "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 4, "add_allin": true,
            "rake_pct": 0.0, "rake_cap": 0.0, "realization": "balanced", "card_removal": true}),
        // unequal stacks with an ante: side pots and returned chips
        serde_json::json!({"positions": ["CO", "BTN", "SB", "BB"], "stack": 100.0, "stacks": [100, 40, 25, 60],
            "posts": [0, 0, 0.5, 1], "ante": 0.1, "limp": true, "open_raises": [2.5], "raise_mults": [3.0],
            "max_raises": 3, "add_allin": true, "rake_pct": 5.0, "rake_cap": 3.0,
            "realization": "leafnet", "leaf_net": "v3", "card_removal": true}),
        // an old save's model: a straddle, calibrated values, no blockers
        serde_json::json!({"positions": eight, "stack": 150.0, "posts": [2, 0, 0, 0, 0, 0, 0.5, 1],
            "utg_straddle": true, "limp": true, "open_raises": [6.0], "raise_mults": [3.0], "max_raises": 2,
            "add_allin": false, "rake_pct": 10.0, "rake_cap": 3.0, "realization": "calibrated"}),
    ]
}

#[test]
fn the_estimate_before_a_build_matches_the_built_game() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    for game in games() {
        let cfg: PreflopConfig = serde_json::from_value(game.clone()).unwrap();
        let est = estimate_tree(&cfg).unwrap();
        let before = minimum_need_of(&cfg, &est);
        let s = PreflopSolver::new(cfg, eq.clone()).unwrap();
        assert_eq!(est.nodes as usize, s.nodes.len(), "{game}");
        let built = minimum_need_mb(&s);
        assert!((before - built).abs() < 1e-6 * built, "{game}: estimated {before} MB, built {built} MB");
        // the two parts add up, and a fresh game has only the placeholder for locked strategies
        assert_eq!(built, tree_need_mb(&s) + policy_need_mb(&s));
        assert_eq!(policy_need_mb(&s), 4.0 / 1e6);
        // a GPU solve holds both big tables and more
        assert!(built > s.arena_mb(), "{game}");
    }
}

#[test]
fn a_locked_node_adds_to_the_need() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    let cfg: PreflopConfig = serde_json::from_value(games().remove(2)).unwrap();
    let mut s = PreflopSolver::new(cfg, eq).unwrap();
    let (tree, fresh) = (tree_need_mb(&s), policy_need_mb(&s));
    // lock the first decision as solved: its strategy is stored on the card
    s.iterate();
    s.lock_point(&[], None).unwrap();
    assert!(policy_need_mb(&s) > fresh);
    assert_eq!(tree_need_mb(&s), tree, "locks do not change the tree's part");
}
