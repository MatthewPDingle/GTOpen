use solver::preflop::{PreflopConfig, PreflopSolver, RealizationFit};
use solver::preflop::equity::{EquityTable, NUM_CLASSES};
use std::sync::{Arc, OnceLock};

fn eq() -> Arc<EquityTable> {
    static EQ: OnceLock<Arc<EquityTable>> = OnceLock::new();
    EQ.get_or_init(|| Arc::new(EquityTable::build(1000))).clone()
}
fn config() -> PreflopConfig {
    serde_json::from_value(serde_json::json!({
        "positions":["SB","BB"],"posts":[0.5,1.0],"stack":100.0,
        "open_raises":[6.0],"raise_mults":[3.0],"max_raises":3,
        "limp":false,"add_allin":true,"realization":"balanced"
    })).unwrap()
}

#[test]
fn balanced_pairs_conserve_value_and_are_bounded() {
    let fit=RealizationFit::load_default().unwrap(); let eq=eq();
    for h in 0..NUM_CLASSES { for j in 0..NUM_CLASSES {
        let a=fit.balanced_share(eq.eq(h,j),h,j,true);
        let b=fit.balanced_share(eq.eq(j,h),j,h,false);
        assert!((0.0..=1.0).contains(&a));
        assert!((a+b-1.0).abs()<2e-6,"{h} {j}: {a} {b}");
    }}
}

#[test]
fn requested_rake_is_applied_once_with_asymmetric_ranges() {
    for (pct,cap) in [(0.0,0.0),(5.0,0.0),(5.0,0.25)] {
        let mut cfg=config(); cfg.rake_pct=pct; cfg.rake_cap=cap;
        let mut s=PreflopSolver::new(cfg,eq()).unwrap();s.prune=false;
        for _ in 0..12 {s.iterate();}
        // Raise 6, call: the range weights are no longer uniform or equal.
        let v=s.node_view(&[1,1]).unwrap(); let c=v.continuation.unwrap();
        assert_eq!(c.model,"balanced"); assert!(c.requested_rake_applied);
        let rake=if cap>0.0 {(12.0*pct/100.0_f64).min(cap)} else {12.0*pct/100.0};
        assert!((c.pot_bb-12.0).abs()<1e-6);
        assert!((c.total_value_bb-(12.0-rake)).abs()<2e-5,"{c:?}");
    }
}

#[test]
fn round_specific_sizes_and_saves_preserve_the_tree() {
    let mut cfg=config();cfg.raise_mults_by_seat=Some(vec![vec![],vec![4.0]]);
    cfg.fourbet_mults=Some(vec![2.0]);cfg.fourbet_mults_by_seat=Some(vec![vec![2.5],vec![]]);
    let s=PreflopSolver::new(cfg.clone(),eq()).unwrap();
    let three=s.node_view(&[1]).unwrap();
    assert!(three.actions.iter().any(|a|a.to==24.0));
    assert!(!three.actions.iter().any(|a|a.to==18.0));
    let i=three.actions.iter().position(|a|a.to==24.0).unwrap();
    let four=s.node_view(&[1,i]).unwrap();
    assert!(four.actions.iter().any(|a|a.to==60.0));
    assert!(!four.actions.iter().any(|a|a.to==72.0));
    let path=std::env::temp_dir().join(format!("gtopen-sizing-{}.gtop",std::process::id()));
    s.save_game(path.to_str().unwrap()).unwrap();
    assert!(std::fs::read(&path).unwrap().starts_with(b"GTOPREFLOP4\n"));
    let restored=PreflopSolver::load_game(path.to_str().unwrap(),eq()).unwrap();
    assert_eq!(serde_json::to_value(&restored.cfg).unwrap(),serde_json::to_value(cfg).unwrap());
    assert_eq!(restored.nodes.len(),s.nodes.len());
    std::fs::remove_file(path).unwrap();
    let mut invalid=config();invalid.fourbet_mults_by_seat=Some(vec![vec![2.0]]);
    assert!(PreflopSolver::new(invalid,eq()).is_err());
}
