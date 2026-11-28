//! Rake types: "Full" rakes every pot (`no_flop_no_drop = false`), and GG
//! Network's rule rakes a preflop fold-out only once the line had a 3-bet or
//! more. Postflop pots are raked the same way under every type.

use super::equity::{class_prob, EquityTable, NUM_CLASSES};
use super::*;
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
}

fn cfg(json: serde_json::Value) -> PreflopConfig {
    serde_json::from_value(json).unwrap()
}

/// A 3-max game where the button opens and the small blind can 3-bet.
fn three(rake_threebet: bool, no_flop_no_drop: bool) -> PreflopConfig {
    cfg(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 30.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": false, "realization": "raw",
        "rake_pct": 5.0, "rake_cap": 2.0,
        "no_flop_no_drop": no_flop_no_drop, "rake_threebet": rake_threebet
    }))
}

fn step(s: &PreflopSolver, node: usize, label: &str) -> usize {
    let nd = &s.nodes[node];
    let a = nd.actions.iter().position(|a| a.label.starts_with(label)).unwrap_or_else(|| {
        panic!("no {label:?} among {:?}", nd.actions.iter().map(|a| &a.label).collect::<Vec<_>>())
    });
    s.child(node, a)
}

fn walk(s: &PreflopSolver, path: &[&str]) -> usize {
    path.iter().fold(0, |node, label| step(s, node, label))
}

fn weights(n: usize) -> Vec<Vec<f32>> {
    (0..n)
        .map(|p| (0..NUM_CLASSES).map(|h| class_prob(h) * ((h * 7 + p * 17) % 23 + 1) as f32 / 25.0).collect())
        .collect()
}

#[test]
fn the_three_bet_rule_rakes_only_lines_with_a_three_bet() {
    let s = PreflopSolver::new(three(true, true), table()).unwrap();
    // Unopened and single-raised pots end before a 3-bet: no rake.
    let unopened = &s.nodes[walk(&s, &["Fold", "Fold"])];
    assert_eq!(unopened.raises, 0);
    assert_eq!(s.fold_win_rake(unopened), 0.0);
    let single = &s.nodes[walk(&s, &["Raise 2.5", "Fold", "Fold"])];
    assert_eq!(single.raises, 1);
    assert_eq!(s.fold_win_rake(single), 0.0);
    // A 3-bet wins uncontested: the rake comes off the matched pot, so the
    // small blind's uncalled 5 bb is returned first.
    let threebet = &s.nodes[walk(&s, &["Raise 2.5", "3-bet 7.5", "Fold", "Fold"])];
    assert_eq!(threebet.raises, 2);
    assert_eq!((threebet.pot, threebet.invested.clone()), (11.0, vec![2.5, 7.5, 1.0]));
    assert!((s.fold_win_rake(threebet) - 0.3).abs() < 1e-12);
    assert_eq!(s.fold_win_rake(threebet), s.rake_of(threebet.pot - 5.0));
    // The same line is untouched when the rule is off, and the other types
    // leave the postflop leaves to the continuation model.
    let off = PreflopSolver::new(three(false, true), table()).unwrap();
    assert_eq!(off.fold_win_rake(&off.nodes[walk(&off, &["Raise 2.5", "3-bet 7.5", "Fold", "Fold"])]), 0.0);
    let full = PreflopSolver::new(three(false, false), table()).unwrap();
    let nd = &full.nodes[walk(&full, &["Raise 2.5", "Fold", "Fold"])];
    assert!((full.fold_win_rake(nd) - full.rake_of(nd.pot - 1.5)).abs() < 1e-12);
}

#[test]
fn payoffs_conserve_chips_under_the_three_bet_rule() {
    let mut s = PreflopSolver::new(three(true, true), table()).unwrap();
    let w = weights(3);
    let probability: f64 = w.iter().map(|w| w.iter().sum::<f32>() as f64).product();
    let (mut raked, mut free) = (0, 0);
    for (node, nd) in s.nodes.iter().enumerate() {
        if nd.kind != KIND_FOLD_WIN {
            continue;
        }
        let rake = s.fold_win_rake(nd);
        if rake > 0.0 {
            raked += 1;
        } else {
            free += 1;
        }
        let mut total = 0.0;
        for p in 0..3 {
            let mut values = [0f32; NUM_CLASSES];
            s.terminal_value(node, p, &w, &mut values);
            total += values.iter().zip(&w[p]).map(|(v, w)| *v as f64 * *w as f64).sum::<f64>();
        }
        assert!((total + probability * rake).abs() < 1e-5, "node {node}: {total} vs {}", -probability * rake);
    }
    // The tree has both kinds of fold-win: before a 3-bet and after one.
    assert!(raked > 0 && free > 0, "{raked} raked and {free} free fold terminals");
    for _ in 0..10 {
        s.iterate();
    }
    assert!(s.evs().iter().all(|v| v.is_finite()));
    assert!(s.br_gaps().iter().all(|g| g.is_finite() && *g >= -1e-6));
}

#[test]
fn saves_use_v9_and_round_trip() {
    let mut s = PreflopSolver::new(three(true, true), table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    let path = std::env::temp_dir().join(format!("gtopen-rake3bet-save-{}.gtop", std::process::id()));
    let path = path.to_str().unwrap();
    s.save_game(path).unwrap();
    let bytes = std::fs::read(path).unwrap();
    assert_eq!(&bytes[..12], super::save::MAGIC_RAKE3BET);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert!(loaded.cfg.rake_threebet);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // A v9 file whose header lost the setting must not continue as another game.
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"].as_object_mut().unwrap().remove("rake_threebet");
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table()).err().unwrap().contains("v9"));
    // Without the rule the config omits the field and the save is not v9.
    let old = PreflopSolver::new(three(false, true), table()).unwrap();
    assert!(!serde_json::to_string(&old.cfg).unwrap().contains("rake_threebet"));
    old.save_game(path).unwrap();
    assert_ne!(&std::fs::read(path).unwrap()[..12], super::save::MAGIC_RAKE3BET);
    // A pre-v9 file claiming the setting must not be read as one.
    let bytes = std::fs::read(path).unwrap();
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"]["rake_threebet"] = true.into();
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table()).err().unwrap().contains("v9"));
    // A v9 game can carry any earlier feature too: the big blind ante here.
    let mut both = three(true, true);
    both.bb_ante = 1.0;
    let mut s = PreflopSolver::new(both, table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    s.save_game(path).unwrap();
    assert_eq!(&std::fs::read(path).unwrap()[..12], super::save::MAGIC_RAKE3BET);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert!((loaded.cfg.bb_ante - 1.0).abs() < 1e-12 && loaded.cfg.rake_threebet);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // ... and action-dependent raise sizes, the other feature a v9 header skips
    // the old cross-check for.
    let mut sized = three(true, true);
    sized.limper_extra = 1.0;
    let mut s = PreflopSolver::new(sized, table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    s.save_game(path).unwrap();
    assert_eq!(&std::fs::read(path).unwrap()[..12], super::save::MAGIC_RAKE3BET);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert!((loaded.cfg.limper_extra - 1.0).abs() < 1e-12 && loaded.cfg.rake_threebet);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    std::fs::remove_file(path).unwrap();
}
