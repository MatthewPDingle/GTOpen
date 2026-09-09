use solver::preflop::{BucketPolicy, PreflopConfig, PreflopSolver};
use solver::preflop::equity::EquityTable;
use std::sync::{Arc, OnceLock};

fn game(model: &str, rake: f64, cap: f64, stack: f64) -> PreflopSolver {
    static EQ: OnceLock<Arc<EquityTable>> = OnceLock::new();
    let eq = EQ.get_or_init(|| Arc::new(EquityTable::build(100))).clone();
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions":["SB","BB"],"stack":stack,"posts":[0.5,1],"limp":true,
        "open_raises":[2.5],"raise_mults":[3],"max_raises":2,"add_allin":true,
        "realization":model,"rake_pct":rake,"rake_cap":cap
    })).unwrap();
    PreflopSolver::new(cfg, eq).unwrap()
}

fn path(s: &PreflopSolver, kinds: &[&str]) -> Vec<usize> {
    let mut node = 0;
    kinds.iter().map(|kind| {
        let a = s.nodes[node].actions.iter().position(|a| a.kind == *kind).unwrap();
        node = s.child(node, a); a
    }).collect()
}

#[test]
fn calibrated_diagnostic_exposes_rake_invariance_without_changing_strategy() {
    let s = game("calibrated", 0.0, 3.0, 100.0);
    assert!(s.fit.is_some());
    let before = s.average_strategy(0);
    let line = path(&s, &["call", "check"]);
    let zero = s.node_view(&line).unwrap().continuation.unwrap();
    assert_eq!(s.average_strategy(0), before);
    assert_eq!(s.iteration, 0);
    let taxed = game("calibrated", 10.0, 3.0, 100.0)
        .node_view(&line).unwrap().continuation.unwrap();
    assert_eq!(zero.model, "calibrated");
    assert!(!taxed.requested_rake_applied);
    assert_eq!(zero.total_value_bb, taxed.total_value_bb);
    assert_eq!(taxed.rake_on_starting_pot_bb, 0.2);
    assert!((taxed.pot_bb - taxed.total_value_bb - taxed.unallocated_bb).abs() < 1e-10);
    assert!(taxed.note.contains("not an expected-rake estimate"));
}

#[test]
fn all_in_diagnostic_applies_current_rake_even_with_calibrated_config() {
    let s = game("calibrated", 0.0, 0.5, 5.0);
    let line = path(&s, &["jam", "call"]);
    let zero = s.node_view(&line).unwrap().continuation.unwrap();
    let taxed = game("calibrated", 10.0, 0.5, 5.0)
        .node_view(&line).unwrap().continuation.unwrap();
    assert_eq!(taxed.model, "all_in_equity");
    assert!(taxed.requested_rake_applied);
    assert_eq!(taxed.rake_on_starting_pot_bb, 0.5);
    assert!((taxed.total_value_bb / zero.total_value_bb - 0.95).abs() < 1e-5);
}

#[test]
fn raw_diagnostic_preserves_uncapped_rake_convention() {
    let s = game("raw", 0.0, 0.0, 100.0);
    let line = path(&s, &["call", "check"]);
    let zero = s.node_view(&line).unwrap().continuation.unwrap();
    let taxed = game("raw", 10.0, 0.0, 100.0)
        .node_view(&line).unwrap().continuation.unwrap();
    assert_eq!(taxed.model, "raw");
    assert!(taxed.requested_rake_applied);
    assert_eq!(taxed.rake_on_starting_pot_bb, 0.2);
    assert!((taxed.total_value_bb / zero.total_value_bb - 0.9).abs() < 1e-5);
}

#[test]
fn action_fold_and_unreachable_nodes_have_no_continuation_values() {
    let mut s = game("raw", 5.0, 3.0, 100.0);
    assert!(s.node_view(&[]).unwrap().continuation.is_none());
    let fold = path(&s, &["fold"]);
    assert!(s.node_view(&fold).unwrap().continuation.is_none());
    let flop = path(&s, &["call", "check"]);
    s.lock_point(&[], Some(BucketPolicy { call:vec![0.0;169], raise:vec![0.0;169],
        jam:vec![0.0;169], raise_size:"min".into(), raise_sizes:vec![] })).unwrap();
    let view = s.node_view(&flop).unwrap();
    assert!(view.strategy_note.is_some());
    assert!(view.continuation.is_none());
}

#[test]
fn folded_seat_path_mass_does_not_change_conditional_hu_values() {
    let base = game("static", 5.0, 3.0, 100.0);
    let mut cfg = base.cfg.clone();
    cfg.positions = vec!["BTN".into(), "SB".into(), "BB".into()];
    cfg.posts = vec![0.0, 0.5, 1.0];
    cfg.ante = 0.1;
    let policy = |scale: f32| BucketPolicy {
        call:(0..169).map(|h| scale*(0.2+0.6*h as f32/168.0)).collect(),
        raise:vec![0.0;169], jam:vec![0.0;169], raise_size:"min".into(), raise_sizes:vec![],
    };
    let mut a = PreflopSolver::new(cfg.clone(), base.eq.clone()).unwrap();
    let mut b = PreflopSolver::new(cfg, base.eq.clone()).unwrap();
    // Both paths arrive at the same two live ranges. The folded player's
    // hand distribution and total path mass differ, which must cancel out.
    for (s,scale) in [(&mut a, 1.0), (&mut b, 0.1)] {
        s.lock_point(&[], Some(policy(scale))).unwrap();
        let sb = path(s, &["fold"]);
        s.lock_point(&sb, Some(policy(0.7))).unwrap();
    }
    let line = path(&a, &["fold", "call", "check"]);
    let av = a.node_view(&line).unwrap().continuation.unwrap();
    let bv = b.node_view(&line).unwrap().continuation.unwrap();
    assert_eq!(av.model, "static");
    assert_eq!(av.players.len(), 2);
    assert!((av.pot_bb-2.3).abs() < 1e-9);
    assert!((av.rake_on_starting_pot_bb-0.115).abs() < 1e-9);
    for (a,b) in av.players.iter().zip(&bv.players) {
        assert!((a.value_bb-b.value_bb).abs() < 1e-5);
    }
    assert!((av.unallocated_bb-bv.unallocated_bb).abs() < 1e-5);
}
