//! An all-in over the last raise (`allin_over_last_raise`). With a raise cap
//! the last raise can never be re-raised, so it always sees a flop when
//! called and a solve raises hands it would otherwise call with. The option
//! adds one action behind every capped raise, an all-in, and nothing else.

use super::equity::EquityTable;
use super::*;
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(200))).clone()
}

fn cfg(json: serde_json::Value) -> PreflopConfig {
    serde_json::from_value(json).unwrap()
}

/// Four seats, 100 bb, open 2.5, 3-bet 7.5, 4-bet 22.5 and then the cap.
fn game(over: bool, add_allin: bool) -> PreflopConfig {
    let mut c = cfg(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0], "stack": 100.0,
        "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": add_allin, "realization": "static", "rake_pct": 5.0, "rake_cap": 2.0
    }));
    c.allin_over_last_raise = over;
    c
}

fn raising(a: &PAction) -> bool {
    a.kind == "raise" || a.kind == "jam"
}

/// Everything below `node` in the tree with the option, which the other tree
/// does not have: nobody may raise again.
fn no_raise_below(on: &PreflopSolver, node: usize) {
    let nd = &on.nodes[node];
    if nd.kind != KIND_ACTION {
        return;
    }
    for (a, act) in nd.actions.iter().enumerate() {
        assert!(!raising(act), "a raise after the all-in over the last raise: {}", act.label);
        no_raise_below(on, on.child(node, a));
    }
}

/// Walks both trees together and returns how many all-ins the option added.
fn compare(off: &PreflopSolver, on: &PreflopSolver, a: usize, b: usize) -> usize {
    let (x, y) = (&off.nodes[a], &on.nodes[b]);
    assert_eq!((x.kind, x.actor, x.raises), (y.kind, y.actor, y.raises));
    assert!((x.pot - y.pot).abs() < 1e-9);
    if x.kind != KIND_ACTION {
        return 0;
    }
    let labels = |nd: &PNode| nd.actions.iter().map(|a| a.label.clone()).collect::<Vec<_>>();
    let mut added = 0;
    if y.actions.len() != x.actions.len() {
        // the one extra action is an all-in, last, behind the capped raise
        assert_eq!(x.raises, off.cfg.max_raises, "{:?} vs {:?}", labels(x), labels(y));
        assert_eq!(y.actions.len(), x.actions.len() + 1, "{:?} vs {:?}", labels(x), labels(y));
        assert!(!x.actions.iter().any(raising));
        let extra = y.actions.last().unwrap();
        assert_eq!(extra.kind, "jam");
        assert!((extra.to - on.cfg.stack).abs() < 1e-9);
        no_raise_below(on, on.child(b, x.actions.len()));
        added += 1;
    }
    assert_eq!(labels(x)[..], labels(y)[..x.actions.len()]);
    for i in 0..x.actions.len() {
        added += compare(off, on, off.child(a, i), on.child(b, i));
    }
    added
}

#[test]
fn the_only_new_action_is_an_all_in_over_the_last_raise() {
    for add_allin in [false, true] {
        let off = PreflopSolver::new(game(false, add_allin), table()).unwrap();
        let on = PreflopSolver::new(game(true, add_allin), table()).unwrap();
        let added = compare(&off, &on, 0, 0);
        assert!(added > 0);
        assert!(on.nodes.len() > off.nodes.len());
        // the size preview counts the same tree the build makes
        let est = estimate_tree(&on.cfg).unwrap();
        assert_eq!(est.nodes as usize, on.nodes.len());
    }
}

#[test]
fn the_reply_to_the_last_raise_is_fold_call_or_all_in() {
    let on = PreflopSolver::new(game(true, false), table()).unwrap();
    let step = |node: usize, label: &str| {
        let nd = &on.nodes[node];
        let a = nd.actions.iter().position(|a| a.label.starts_with(label)).unwrap_or_else(|| {
            panic!("no {label:?} among {:?}", nd.actions.iter().map(|a| &a.label).collect::<Vec<_>>())
        });
        on.child(node, a)
    };
    // CO opens, BTN 3-bets, the blinds fold, CO 4-bets: BTN faces the last raise
    let node = ["Raise", "3-bet", "Fold", "Fold", "4-bet"].iter().fold(0, |n, l| step(n, l));
    let kinds: Vec<&str> = on.nodes[node].actions.iter().map(|a| a.kind.as_str()).collect();
    assert_eq!(kinds, ["fold", "call", "jam"]);
    // and CO, shoved on, may only fold or call
    let node = step(node, "All-in");
    let kinds: Vec<&str> = on.nodes[node].actions.iter().map(|a| a.kind.as_str()).collect();
    assert_eq!(kinds, ["fold", "call"]);
}

/// The game the option was measured with on a GPU before it existed: one
/// more raise allowed, with the threshold lowered until that raise is an
/// all-in. Where that trick works the two games are the same game.
#[test]
fn it_is_the_game_with_one_more_raise_that_can_only_be_an_all_in() {
    let mut a = PreflopSolver::new(game(true, true), table()).unwrap();
    let mut trick = game(false, true);
    trick.max_raises = 4;
    trick.allin_threshold = 0.6; // the 5-bet to 67.5 of 100; no earlier raise reaches 60
    let mut b = PreflopSolver::new(trick, table()).unwrap();
    assert_eq!(a.nodes.len(), b.nodes.len());
    for _ in 0..5 {
        a.iterate();
        b.iterate();
    }
    assert_eq!(a.arena_snapshot(), b.arena_snapshot());
}

#[test]
fn no_raise_cap_reached_means_no_new_action() {
    // heads-up push or fold: the open all-in is the last raise, and with
    // both players all-in or folded nothing can follow it
    let hu = |over: bool| {
        let mut c = cfg(serde_json::json!({
            "positions": ["SB", "BB"], "posts": [0.5, 1.0], "stack": 10.0, "limp": false,
            "open_raises": [], "raise_mults": [], "max_raises": 1, "add_allin": true, "realization": "raw"
        }));
        c.allin_over_last_raise = over;
        PreflopSolver::new(c, table()).unwrap()
    };
    assert_eq!(hu(false).nodes.len(), hu(true).nodes.len());
}

#[test]
fn saves_use_v9_and_round_trip() {
    let mut s = PreflopSolver::new(game(true, false), table()).unwrap();
    for _ in 0..3 {
        s.iterate();
    }
    let path = std::env::temp_dir().join(format!("gtopen-last-allin-save-{}.gtop", std::process::id()));
    let path = path.to_str().unwrap();
    s.save_game(path).unwrap();
    let bytes = std::fs::read(path).unwrap();
    assert_eq!(&bytes[..12], super::save::MAGIC_LAST_ALLIN);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert!(loaded.cfg.allin_over_last_raise);
    assert_eq!(loaded.arena_snapshot(), s.arena_snapshot());
    // A v9 file whose header lost the setting must not continue as another game.
    let end = 12 + bytes[12..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[12..end]).unwrap();
    header["config"].as_object_mut().unwrap().remove("allin_over_last_raise");
    let mut out = bytes[..12].to_vec();
    out.extend(serde_json::to_vec(&header).unwrap());
    out.extend_from_slice(&bytes[end..]);
    std::fs::write(path, out).unwrap();
    assert!(PreflopSolver::load_game(path, table()).err().unwrap().contains("v9"));
    // With a big blind ante as well it is still v9, and loads with both.
    let mut both = game(true, false);
    both.bb_ante = 1.0;
    let both = PreflopSolver::new(both, table()).unwrap();
    both.save_game(path).unwrap();
    assert_eq!(&std::fs::read(path).unwrap()[..12], super::save::MAGIC_LAST_ALLIN);
    let loaded = PreflopSolver::load_game(path, table()).unwrap();
    assert!(loaded.cfg.allin_over_last_raise && loaded.cfg.bb_ante == 1.0);
    // Without the option the config and the file are what they always were.
    let old = PreflopSolver::new(game(false, false), table()).unwrap();
    assert!(!serde_json::to_string(&old.cfg).unwrap().contains("allin_over_last_raise"));
    old.save_game(path).unwrap();
    assert_ne!(&std::fs::read(path).unwrap()[..12], super::save::MAGIC_LAST_ALLIN);
    std::fs::remove_file(path).unwrap();
}
