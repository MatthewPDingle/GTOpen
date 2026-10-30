//! Lock undo / redo and freezing the line to a lock: undo must restore the
//! exact earlier locks (not a rebuild from the current solve), an edit lands
//! whole or not at all, and history refuses to replay over locks changed
//! behind its back.

use solver::query::{PathStep, PostflopStats};
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{LockMode, Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

/// River spot: OOP checks or jams pot (stack = pot), IP folds or calls. Small enough
/// to solve in milliseconds, with a two-decision line (root > Bet).
fn river() -> Solver {
    let spot = Spot::new(SpotConfig {
        board: "QcJc9c3d2d".to_string(),
        range_oop: "AcKc,8h7h,AsAh".to_string(),
        range_ip: "QdQh,KdKh".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    })
    .unwrap();
    let mut s = Solver::new(Arc::new(spot));
    for _ in 0..40 {
        s.iterate();
    }
    s
}

const ROOT: &[PathStep] = &[];
fn vs_bet() -> Vec<PathStep> {
    vec![PathStep::Action { index: 1 }]
}

fn node_idx(s: &Solver, path: &[PathStep]) -> u32 {
    s.walk_path(path).unwrap().node_idx
}

/// One recorded lock_node_on_line edit, labelled the way the server does.
fn lock(s: &mut Solver, path: &[PathStep], mode: LockMode, freeze_path: bool) -> usize {
    let label = s.path_description(path).unwrap();
    s.record_lock_edit(|s| {
        let n = s.lock_node_on_line(path, mode, label.clone(), freeze_path)?;
        Ok((n, format!("Lock · {label}")))
    })
    .unwrap()
}

#[test]
fn undo_and_redo_restore_exact_locks() {
    let mut s = river();
    let at = node_idx(&s, &vs_bet());
    lock(&mut s, &vs_bet(), LockMode::Range { freqs: vec![0.7, 0.3] }, false);
    let range_lock = s.locks[&at].clone();

    // a per-hand edit on top, then keep solving: the solved base moves, so a
    // replayed range lock would no longer match the one being restored
    lock(&mut s, &vs_bet(), LockMode::Hands {
        edits: vec![
            solver::query::HandEdit { combo: "QdQh".into(), freqs: vec![1.0, 0.0] },
        ],
    }, false);
    assert_ne!(s.locks[&at], range_lock);
    let hands_lock = s.locks[&at].clone();
    for _ in 0..40 {
        s.iterate();
    }

    let h = s.lock_history();
    assert_eq!(h.undo.len(), 2);
    assert!(h.undo[0].starts_with("Lock · QcJc9c3d2d All-in 100"), "{:?}", h.undo);

    assert!(s.undo_lock_edit().unwrap().is_some());
    assert_eq!(s.locks[&at], range_lock, "undo restores the earlier sigma bit for bit");
    assert!(s.undo_lock_edit().unwrap().is_some());
    assert!(s.locks.is_empty() && s.lock_labels.is_empty());
    assert_eq!(s.undo_lock_edit().unwrap(), None, "nothing left to undo");

    let h = s.lock_history();
    assert_eq!((h.undo.len(), h.redo.len()), (0, 2));
    assert!(s.redo_lock_edit().unwrap().is_some());
    assert_eq!(s.locks[&at], range_lock);
    assert!(s.redo_lock_edit().unwrap().is_some());
    assert_eq!(s.locks[&at], hands_lock);
    assert_eq!(s.lock_history().redo.len(), 0);
}

#[test]
fn a_new_edit_clears_redo_and_noops_add_nothing() {
    let mut s = river();
    lock(&mut s, ROOT, LockMode::Freeze, false);
    s.undo_lock_edit().unwrap();
    assert_eq!(s.lock_history().redo.len(), 1);
    lock(&mut s, &vs_bet(), LockMode::Freeze, false);
    let h = s.lock_history();
    assert_eq!((h.undo.len(), h.redo.len()), (1, 0));

    // unlocking a node that isn't locked changes nothing: no entry
    s.record_lock_edit(|s| Ok((s.unlock_node(ROOT)?, "Unlock".to_string()))).unwrap();
    assert_eq!(s.lock_history().undo.len(), 1);
}

#[test]
fn freezing_the_line_locks_earlier_decisions_and_undoes_as_one() {
    let mut s = river();
    let frozen = lock(&mut s, &vs_bet(), LockMode::Range { freqs: vec![0.5, 0.5] }, true);
    assert_eq!(frozen, 1, "the root is the one earlier decision");
    let root = 0;
    assert!(s.locks.contains_key(&root));
    assert!(s.lock_labels[&root].contains("frozen on the line to"), "{}", s.lock_labels[&root]);

    // frozen = exactly the solved strategy at the time of the lock
    let node = &s.spot.tree.nodes[root as usize];
    let mut solved = vec![0f32; s.locks[&root].len()];
    s.solved_strategy_into(node, &mut solved);
    assert_eq!(s.locks[&root], solved);

    assert_eq!(s.lock_history().undo.len(), 1, "one edit for the lock and its line");
    s.undo_lock_edit().unwrap();
    assert!(s.locks.is_empty());
}

#[test]
fn freezing_the_line_keeps_existing_locks_on_it() {
    let mut s = river();
    lock(&mut s, ROOT, LockMode::Range { freqs: vec![0.2, 0.8] }, false);
    let mine = s.locks[&0].clone();
    let frozen = lock(&mut s, &vs_bet(), LockMode::Freeze, true);
    assert_eq!(frozen, 0);
    assert_eq!(s.locks[&0], mine, "an existing lock on the line is never overwritten");
}

#[test]
fn a_failed_edit_rolls_back() {
    let mut s = river();
    let before = s.lock_history().undo.len();
    let err = s.record_lock_edit::<()>(|s| {
        s.lock_node(ROOT, LockMode::Freeze, "root".into())?;
        Err("refused".into())
    });
    assert!(err.is_err());
    assert!(s.locks.is_empty(), "the partial lock is rolled back");
    assert_eq!(s.lock_history().undo.len(), before);

    // a refused target lock freezes nothing on the line
    let bad = s.record_lock_edit(|s| {
        let n = s.lock_node_on_line(&vs_bet(), LockMode::Range { freqs: vec![1.0] }, "x".into(), true)?;
        Ok((n, "x".to_string()))
    });
    assert!(bad.is_err());
    assert!(s.locks.is_empty());
}

#[test]
fn undo_refuses_after_locks_changed_outside_history() {
    let mut s = river();
    lock(&mut s, ROOT, LockMode::Freeze, false);
    // an unrecorded mutation of the same node (e.g. a script calling the
    // engine directly) breaks the history's assumption
    s.lock_node(ROOT, LockMode::Range { freqs: vec![0.9, 0.1] }, "direct".into()).unwrap();
    let changed = s.locks[&0].clone();
    assert!(s.undo_lock_edit().is_err());
    assert_eq!(s.locks[&0], changed, "a refused undo changes nothing");
    let h = s.lock_history();
    assert!(h.undo.is_empty() && h.redo.is_empty(), "history is cleared");
}

#[test]
fn path_descriptions_name_actions_and_cards() {
    let s = river();
    assert_eq!(s.path_description(ROOT).unwrap(), "QcJc9c3d2d root");
    assert_eq!(s.path_description(&vs_bet()).unwrap(), "QcJc9c3d2d All-in 100");
    assert!(s.path_description(&[PathStep::Action { index: 9 }]).is_err());
}

#[test]
fn profile_compiles_are_undoable_and_reported_per_player() {
    let s = |_p: usize| [sizing("50", "100"), sizing("50", ""), sizing("50", "")];
    let spot = Spot::new(SpotConfig {
        board: "Qs7h2d".to_string(),
        range_oop: "AA,QQ,77,AQs,KQs,T9s,A5s".to_string(),
        range_ip: "KK,JJ,88,AKs,JTs,98s,AJo".to_string(),
        tree: TreeConfig {
            starting_pot: 10.0,
            effective_stack: 40.0,
            oop: s(0),
            ip: s(1),
            ..Default::default()
        },
    })
    .unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..5 {
        solver.iterate();
    }
    lock(&mut solver, ROOT, LockMode::Freeze, false);
    let manual = solver.locks.clone();
    let stats = PostflopStats {
        contextual_betting: None,
        cbet: [80.0, 60.0, 40.0],
        fold_to_bet: [65.0, 60.0, 55.0],
        raise_bet: 8.0,
        donk: 10.0,
        bet_size: "min".into(),
    };
    let summary = solver
        .record_lock_edit(|s| Ok((s.lock_profile(1, &stats, Some(1))?, "Profile".to_string())))
        .unwrap();
    assert!(summary.locked > 1);
    let h = solver.lock_history();
    assert_eq!(h.profile_players, vec![1]);
    assert_eq!(h.locked_nodes, 1 + summary.locked);

    solver.undo_lock_edit().unwrap();
    assert_eq!(solver.locks, manual, "the whole compile undoes as one edit");
    assert!(solver.lock_history().profile_players.is_empty());

    solver.redo_lock_edit().unwrap();
    solver
        .record_lock_edit(|s| Ok((s.clear_profile_locks(), "Clear".to_string())))
        .unwrap();
    assert_eq!(solver.locks, manual);
    solver.undo_lock_edit().unwrap();
    assert_eq!(solver.lock_history().profile_players, vec![1]);
}
