//! Raise sizes that follow the action: an extra amount per limper, callers'
//! money added to a re-raise, and separate out-of-position multipliers.
use solver::preflop::equity::EquityTable;
use solver::preflop::{estimate_tree, PreflopConfig, PreflopSolver};
use std::sync::{Arc, OnceLock};

fn eq() -> Arc<EquityTable> {
    static EQ: OnceLock<Arc<EquityTable>> = OnceLock::new();
    EQ.get_or_init(|| Arc::new(EquityTable::build(100))).clone()
}

/// 6-max, 100 bb, open 3, 3-bet 3x in position.
fn plain() -> PreflopConfig {
    serde_json::from_value(serde_json::json!({
        "positions":["UTG","HJ","CO","BTN","SB","BB"],"posts":[0,0,0,0,0.5,1.0],"stack":100.0,
        "open_raises":[3.0],"raise_mults":[3.0],"fourbet_mults":[2.3],"max_raises":3,
        "limp":true,"add_allin":false,"realization":"raw"
    })).unwrap()
}

/// The same game sized the way players do: 1 bb more per limper, callers'
/// money added to a re-raise, 4x 3-bets and 2.7x 4-bets out of position.
fn realistic() -> PreflopConfig {
    let mut cfg = plain();
    cfg.limper_extra = 1.0;
    cfg.caller_extra = 1.0;
    cfg.raise_mults_oop = Some(vec![4.0]);
    cfg.fourbet_mults_oop = Some(vec![2.7]);
    cfg
}

/// Walk action kinds from the root; returns the raise TO amounts offered there.
fn raises_after(s: &PreflopSolver, path: &[&str]) -> Vec<f64> {
    let mut n = 0;
    for kind in path {
        let i = s.nodes[n].actions.iter().position(|a| a.kind == *kind)
            .unwrap_or_else(|| panic!("no {kind} at {path:?}"));
        n = s.child(n, i);
    }
    s.nodes[n].actions.iter().filter(|a| a.kind == "raise" || a.kind == "jam").map(|a| a.to).collect()
}

fn close(got: &[f64], want: &[f64]) {
    assert_eq!(got.len(), want.len(), "{got:?} vs {want:?}");
    for (g, w) in got.iter().zip(want) {
        assert!((g - w).abs() < 1e-9, "{got:?} vs {want:?}");
    }
}

#[test]
fn a_raise_over_limpers_adds_the_extra_per_limper() {
    let s = PreflopSolver::new(realistic(), eq()).unwrap();
    close(&raises_after(&s, &[]), &[3.0]);
    close(&raises_after(&s, &["call"]), &[4.0]);
    close(&raises_after(&s, &["call", "call"]), &[5.0]);
    // a fold in between is not a limper
    close(&raises_after(&s, &["call", "fold", "call"]), &[5.0]);
    // the small blind completing counts like any other limp
    close(&raises_after(&s, &["fold", "fold", "fold", "fold", "call"]), &[4.0]);
    // a seat's own open size grows the same way
    let mut cfg = realistic();
    cfg.open_raises_by_seat = Some(vec![vec![], vec![], vec![6.0], vec![], vec![], vec![]]);
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    close(&raises_after(&s, &["call", "call"]), &[8.0]);
}

#[test]
fn a_three_bet_adds_each_callers_money_and_is_bigger_out_of_position() {
    let s = PreflopSolver::new(realistic(), eq()).unwrap();
    // UTG opens 3, HJ and CO call: BTN (in position) makes it 3x3 + 3 + 3.
    close(&raises_after(&s, &["raise", "call", "call"]), &[15.0]);
    // BTN folds: SB (out of position) makes it 4x3 + 3 + 3.
    close(&raises_after(&s, &["raise", "call", "call", "fold"]), &[18.0]);
    // with nobody calling the multipliers stand alone
    close(&raises_after(&s, &["raise", "fold", "fold"]), &[9.0]);
    close(&raises_after(&s, &["raise", "fold", "fold", "fold"]), &[12.0]);
    // limpers are not callers: UTG limps, HJ raises to 4, CO 3-bets 3x4
    close(&raises_after(&s, &["call", "raise"]), &[12.0]);
    // a caller of that raise is one: BTN makes it 4 x (3 + 1)
    close(&raises_after(&s, &["call", "raise", "call"]), &[16.0]);
}

#[test]
fn four_bets_follow_position_and_callers_too() {
    let s = PreflopSolver::new(realistic(), eq()).unwrap();
    // UTG opens 3, BTN 3-bets to 9 in position: UTG's 4-bet is out of position, 2.7 x 9.
    close(&raises_after(&s, &["raise", "fold", "fold", "raise", "fold", "fold"]), &[24.3]);
    // BTN opens 3, SB 3-bets to 12 out of position: BTN's 4-bet is in position, 2.3 x 12.
    close(&raises_after(&s, &["fold", "fold", "fold", "raise", "raise", "fold"]), &[27.6]);
    // CO opens 3, BTN 3-bets 9, SB calls the 3-bet cold: CO's 4-bet (out of
    // position to the BTN) is 9 x (2.7 + 1).
    close(&raises_after(&s, &["fold", "fold", "raise", "raise", "call", "fold"]), &[33.3]);
}

#[test]
fn heads_up_the_big_blind_is_out_of_position() {
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions":["SB","BB"],"posts":[0.5,1.0],"stack":100.0,
        "open_raises":[2.5],"raise_mults":[3.0],"raise_mults_oop":[4.0],"max_raises":3,
        "limp":false,"add_allin":false,"realization":"raw"
    })).unwrap();
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    close(&raises_after(&s, &["raise"]), &[10.0]); // BB 3-bets 4 x 2.5
    close(&raises_after(&s, &["raise", "raise"]), &[30.0]); // SB 4-bets 3 x 10
}

#[test]
fn a_straddler_is_in_position_to_the_blinds_only() {
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions":["UTG","BTN","SB","BB"],"posts":[2.0,0,0.5,1.0],"utg_straddle":true,"stack":200.0,
        "open_raises":[6.0],"raise_mults":[3.0],"raise_mults_oop":[4.0],"max_raises":2,
        "limp":false,"add_allin":false,"realization":"raw"
    })).unwrap();
    assert_eq!(cfg.postflop_order(), vec![2, 3, 0, 1]);
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    // BTN opens 6: SB and BB 3-bet out of position, the straddler too.
    close(&raises_after(&s, &["raise"]), &[24.0]);
    close(&raises_after(&s, &["raise", "fold", "fold"]), &[24.0]);
    // SB opens 6, BB folds: the straddler has position on the SB.
    close(&raises_after(&s, &["fold", "raise", "fold"]), &[18.0]);
}

#[test]
fn a_seats_own_multiplier_wins_in_and_out_of_position() {
    let mut cfg = realistic();
    cfg.raise_mults_by_seat = Some(vec![vec![], vec![], vec![], vec![], vec![5.0], vec![]]);
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    // SB uses its own 5x, still adding the two callers' money: 3 x (5 + 2).
    close(&raises_after(&s, &["raise", "call", "call", "fold"]), &[21.0]);
    // BB has no list of its own: out of position 4x plus the callers.
    close(&raises_after(&s, &["raise", "call", "call", "fold", "fold"]), &[18.0]);
}

#[test]
fn settings_left_off_keep_the_old_game_and_its_save_format() {
    let off = plain();
    let text = serde_json::to_string(&off).unwrap();
    for key in ["limper_extra", "caller_extra", "raise_mults_oop", "fourbet_mults_oop"] {
        assert!(!text.contains(key), "{key} must not be written when off");
    }
    assert!(!off.situational_sizing());
    // explicit zeros are the same game as leaving the keys out
    let mut zeros = serde_json::to_value(&off).unwrap();
    zeros["limper_extra"] = 0.0.into();
    zeros["caller_extra"] = 0.0.into();
    let zeros: PreflopConfig = serde_json::from_value(zeros).unwrap();
    assert!(!zeros.situational_sizing());
    let s = PreflopSolver::new(zeros, eq()).unwrap();
    close(&raises_after(&s, &["call", "call"]), &[3.0]);
    close(&raises_after(&s, &["raise", "call", "call"]), &[9.0]);
    close(&raises_after(&s, &["raise", "call", "call", "fold"]), &[9.0]);
    let path = std::env::temp_dir().join(format!("gtopen-plain-sizing-{}.gtop", std::process::id()));
    s.save_game(path.to_str().unwrap()).unwrap();
    assert!(!std::fs::read(&path).unwrap().starts_with(b"GTOPREFLOP7\n"));
    std::fs::remove_file(path).unwrap();
}

#[test]
fn the_new_sizes_do_not_grow_the_tree() {
    for (allin, max_raises) in [(false, 3), (true, 3), (false, 4)] {
        let (mut a, mut b) = (plain(), realistic());
        for cfg in [&mut a, &mut b] {
            cfg.add_allin = allin;
            cfg.max_raises = max_raises;
        }
        let (plain, real) = (estimate_tree(&a).unwrap(), estimate_tree(&b).unwrap());
        assert!(real.nodes <= plain.nodes, "{} > {}", real.nodes, plain.nodes);
        assert!(real.arena_len <= plain.arena_len);
        // and the estimate is the tree that gets built
        if !allin && max_raises == 3 {
            let s = PreflopSolver::new(b.clone(), eq()).unwrap();
            assert_eq!(s.nodes.len() as u64, real.nodes);
        }
    }
}

#[test]
fn saves_use_their_own_format_and_restore_the_settings() {
    let mut cfg = realistic();
    cfg.max_raises = 2;
    let s = PreflopSolver::new(cfg.clone(), eq()).unwrap();
    let path = std::env::temp_dir().join(format!("gtopen-situational-sizing-{}.gtop", std::process::id()));
    s.save_game(path.to_str().unwrap()).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    assert!(bytes.starts_with(b"GTOPREFLOP7\n"));
    let restored = PreflopSolver::load_game(path.to_str().unwrap(), eq()).unwrap();
    assert_eq!(serde_json::to_value(&restored.cfg).unwrap(), serde_json::to_value(&cfg).unwrap());
    assert_eq!(restored.nodes.len(), s.nodes.len());
    close(&raises_after(&restored, &["raise", "call", "call", "fold"]), &[18.0]);
    // A file whose settings were stripped (what an older program would see)
    // is refused instead of being read as a different game.
    let newline = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..newline]).unwrap();
    for key in ["limper_extra", "caller_extra", "raise_mults_oop", "fourbet_mults_oop"] {
        header["config"].as_object_mut().unwrap().remove(key);
    }
    let mut stripped = bytes[..12].to_vec();
    stripped.extend(serde_json::to_vec(&header).unwrap());
    stripped.extend(&bytes[newline..]);
    std::fs::write(&path, stripped).unwrap();
    assert!(PreflopSolver::load_game(path.to_str().unwrap(), eq()).is_err());
    std::fs::remove_file(path).unwrap();
}

#[test]
fn bad_settings_are_refused() {
    for (key, value) in [("limper_extra", -1.0), ("caller_extra", -0.5), ("caller_extra", f64::NAN)] {
        let mut cfg = serde_json::to_value(realistic()).unwrap();
        cfg[key] = serde_json::json!(value);
        // NaN serializes as null, which serde refuses for an f64: both are errors
        let built = serde_json::from_value::<PreflopConfig>(cfg).map_err(|e| e.to_string())
            .and_then(|cfg| PreflopSolver::new(cfg, eq()).map(|_| ()));
        assert!(built.is_err(), "{key} = {value}");
    }
    let mut cfg = realistic();
    cfg.raise_mults_oop = Some(vec![0.0]);
    assert!(PreflopSolver::new(cfg, eq()).is_err());
}

#[test]
fn a_call_all_in_for_less_adds_only_what_it_put_in() {
    let mut cfg = realistic();
    cfg.stacks = Some(vec![100.0, 2.0, 100.0, 100.0, 100.0, 100.0]);
    let s = PreflopSolver::new(cfg, eq()).unwrap();
    // UTG opens 3, HJ calls all-in for 2, CO calls 3: BTN makes it 9 + 2 + 3.
    close(&raises_after(&s, &["raise", "call", "call"]), &[14.0]);
}
