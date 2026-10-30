use solver::preflop::{
    BucketPolicy, PreflopConfig, PreflopSolver,
    equity::{EquityTable, NUM_CLASSES, class_prob},
};
use std::sync::Arc;
#[test]
fn conditional_action_values_match_closed_form_and_do_not_change_strategy() {
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions":["SB","BB"],"posts":[0.5,1.0],"stack":10.0,
        "limp":false,"open_raises":[2.0],"raise_mults":[],"max_raises":1,
        "add_allin":false,"realization":"raw","rake_pct":0.0
    }))
    .unwrap();
    let eq = Arc::new(EquityTable::build(1000));
    let mut s = PreflopSolver::new(cfg, eq.clone()).unwrap();
    let calls = BucketPolicy {
        call: vec![1.0; NUM_CLASSES],
        raise: vec![0.0; NUM_CLASSES],
        jam: vec![0.0; NUM_CLASSES],
        raise_size: "min".into(),
        raise_sizes: vec![],
        raise_multiples: vec![],
    };
    s.lock_point(&[1], Some(calls)).unwrap();
    let before = s.arena_snapshot();
    for br in [false, true] {
        let values = s.diagnostic_action_evs(&[], br).unwrap();
        let facing = s.diagnostic_action_evs(&[1], br).unwrap();
        for h in 0..NUM_CLASSES {
            let e: f64 = (0..NUM_CLASSES)
                .map(|j| eq.eq(h, j) as f64 * class_prob(j) as f64)
                .sum();
            assert!(values[0][h].abs() < 1e-6);
            assert!((values[1][h] - (4.0 * e - 1.5)).abs() < 2e-5);
            assert!(facing[0][h].abs() < 1e-6);
            assert!((facing[1][h] - (4.0 * e - 1.0)).abs() < 2e-5);
        }
    }
    assert_eq!(before, s.arena_snapshot());
    assert!(s.diagnostic_action_evs(&[999], false).is_err());
}
