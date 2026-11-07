//! Save-header engine settings and the save-time sibling materialization.
//!
//! The header records the CFR algorithm and the isomorphism switch, because a
//! resumed solve must keep the update rule it was solved with. Saves written
//! before those fields existed keep the old defaults (dcfr, isomorphism on).
//! `save` also materializes isomorphic siblings itself: CFR traverses only
//! orbit representatives, so an unmaterialized save is a valid-looking file
//! whose non-canonical runouts hold stale arenas.

use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{permute_card, Algorithm, LockMode, PathStep, Solver, Spot, SpotConfig};
use std::path::{Path, PathBuf};
use std::sync::Arc;

const MAGIC_LEN: usize = 10; // b"GTOSOLVE2\n"

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

/// Tiny river-only clairvoyance spot: cheap to build and solve.
fn tiny_config() -> SpotConfig {
    SpotConfig {
        board: "QcJc9c3d2d".to_string(),
        range_oop: "AcKc,8h7h".to_string(),
        range_ip: "QdQh".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    }
}

/// Flop spot with exactly the c<->h suit swap (see
/// `convergence.rs::lock_after_solve_visible_on_isomorphic_branch`).
fn symmetric_flop_config() -> SpotConfig {
    SpotConfig {
        board: "KsQs2d".to_string(),
        range_oop: "TT,99,88,77,AKs,AQs,AJs,JTs,T9s,87s,AKo,KQo".to_string(),
        range_ip: "QQ,JJ,TT,AKs,KQs,QJs,T9s,98s,AQo".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    }
}

/// Unique per test, so the parallel test threads cannot collide.
fn temp_path(tag: &str) -> PathBuf {
    std::env::temp_dir().join(format!("gto_save_header_{}_{tag}.gto", std::process::id()))
}

fn solve_saved(config: SpotConfig, tag: &str, algo: Algorithm, iso: bool) -> (PathBuf, u32) {
    let path = temp_path(tag);
    let mut solver = Solver::new(Arc::new(Spot::new(config).unwrap()));
    solver.algo = algo;
    solver.use_isomorphism = iso;
    for _ in 0..20 {
        solver.iterate();
    }
    solver.save(path.to_str().unwrap()).unwrap();
    (path, solver.iteration)
}

/// Rewrite the JSON header line in place, leaving the magic and the arenas
/// byte-identical (the idiom from `save_compat.rs` / `save_locks.rs`).
fn doctor_header(path: &Path, edit: impl FnOnce(&mut serde_json::Value)) {
    let bytes = std::fs::read(path).unwrap();
    let nl = MAGIC_LEN + bytes[MAGIC_LEN..].iter().position(|&b| b == b'\n').unwrap();
    let mut header: serde_json::Value = serde_json::from_slice(&bytes[MAGIC_LEN..nl]).unwrap();
    edit(&mut header);
    let mut out = bytes[..MAGIC_LEN].to_vec();
    out.extend_from_slice(serde_json::to_string(&header).unwrap().as_bytes());
    out.extend_from_slice(&bytes[nl..]); // '\n' + arenas untouched
    std::fs::write(path, out).unwrap();
}

/// The save's JSON header as a value (magic and arenas untouched).
fn header_json(path: &Path) -> serde_json::Value {
    let bytes = std::fs::read(path).unwrap();
    let nl = MAGIC_LEN + bytes[MAGIC_LEN..].iter().position(|&b| b == b'\n').unwrap();
    serde_json::from_slice(&bytes[MAGIC_LEN..nl]).unwrap()
}

/// A resumed solve must keep the algorithm and isomorphism switch it was
/// solved with, not whatever defaults the loading process happens to have.
#[test]
fn engine_settings_round_trip() {
    let (path, iteration) =
        solve_saved(tiny_config(), "settings", Algorithm::CfrPlus, false);
    // The header grew fields; the on-disk version tag must not move.
    assert!(std::fs::read(&path).unwrap().starts_with(b"GTOSOLVE2\n"));
    let loaded = Solver::load(path.to_str().unwrap()).unwrap();
    assert_eq!(loaded.iteration, iteration);
    assert_eq!(loaded.algo, Algorithm::CfrPlus);
    assert!(!loaded.use_isomorphism);
    std::fs::remove_file(path).ok();
}

/// The recorded tag is a format value, not just a debug string: every engine's
/// canonical name must parse back to that engine, and the parser's historical
/// spellings must keep working.
#[test]
fn algorithm_tags_round_trip() {
    for algo in [Algorithm::Dcfr, Algorithm::CfrPlus, Algorithm::PcfrPlus] {
        assert_eq!(Algorithm::parse(algo.name()), Ok(algo), "tag {:?}", algo.name());
    }
    assert_eq!(Algorithm::CfrPlus.name(), "cfr+");
    assert_eq!(Algorithm::parse("CFR+"), Ok(Algorithm::CfrPlus));
    assert_eq!(Algorithm::parse("cfrplus"), Ok(Algorithm::CfrPlus));
    assert_eq!(Algorithm::parse("pcfr_plus"), Ok(Algorithm::PcfrPlus));
    assert!(Algorithm::parse("quantum").is_err());
}

/// Pre-field saves carry no engine settings; they must load with today's
/// defaults (dcfr + isomorphism), not with the loading process's choice.
#[test]
fn legacy_header_without_engine_settings_uses_defaults() {
    let (path, iteration) =
        solve_saved(tiny_config(), "legacy", Algorithm::CfrPlus, false);
    doctor_header(&path, |h| {
        let obj = h.as_object_mut().unwrap();
        obj.remove("algo");
        obj.remove("use_isomorphism");
    });
    let loaded = Solver::load(path.to_str().unwrap()).unwrap();
    assert_eq!(loaded.iteration, iteration);
    assert_eq!(loaded.algo, Algorithm::Dcfr);
    assert!(loaded.use_isomorphism);
    std::fs::remove_file(path).ok();
}

/// A corrupt tag is corruption, not a reason to silently pick a default.
#[test]
fn unknown_algorithm_tag_is_a_load_error() {
    let (path, _) = solve_saved(tiny_config(), "bad_tag", Algorithm::Dcfr, true);
    doctor_header(&path, |h| h["algo"] = serde_json::json!("quantum-cfr"));
    let err = match Solver::load(path.to_str().unwrap()) {
        Ok(_) => panic!("unknown algorithm tag must be refused"),
        Err(e) => e,
    };
    assert!(err.contains("unknown algorithm"), "unexpected error: {err}");
    std::fs::remove_file(path).ok();
}

/// Unknown header fields are ignored, so an older binary can read a save that
/// carries newer fields (and a newer one a future save); the loader must not
/// grow a strict field list by accident.
#[test]
fn unknown_header_fields_are_ignored() {
    let (path, iteration) = solve_saved(tiny_config(), "extra_field", Algorithm::Dcfr, true);
    doctor_header(&path, |h| {
        h["a_field_from_the_future"] = serde_json::json!({"nested": [1, 2, 3]});
    });
    let loaded = Solver::load(path.to_str().unwrap()).unwrap();
    assert_eq!(loaded.iteration, iteration);
    assert_eq!(loaded.algo, Algorithm::Dcfr);
    assert!(loaded.use_isomorphism);
    std::fs::remove_file(path).ok();
}

/// `save` must materialize isomorphic siblings: without it the 4h turn branch
/// would still hold the untouched (uniform) arenas while the canonical 4c
/// branch has the solved strategy.
#[test]
fn save_materializes_isomorphic_siblings() {
    let spot = Spot::new(symmetric_flop_config()).unwrap();
    assert_eq!(spot.suit_perms.len(), 2, "expected exactly the c<->h swap");
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..100 {
        solver.iterate();
    }
    let path = temp_path("siblings");
    // deliberately no ensure_symmetric here
    solver.save(path.to_str().unwrap()).unwrap();

    let mut loaded = Solver::load(path.to_str().unwrap()).unwrap();
    assert!(loaded.use_isomorphism, "header should round-trip the switch");
    // read every branch as stored: no remapping to the representative
    loaded.use_isomorphism = false;
    let runout = |card: &str| {
        vec![
            PathStep::Action { index: 0 },
            PathStep::Action { index: 0 },
            PathStep::Card { card: card.to_string() },
        ]
    };
    let (path_h, path_c) = (runout("4h"), runout("4c"));
    let view_h = loaded.node_view(&path_h).unwrap();
    let view_c = loaded.node_view(&path_c).unwrap();

    // the swap this orbit was transported with: 4h -> 4c
    let h = solver::parse_cards("4h").unwrap()[0];
    let c = solver::parse_cards("4c").unwrap()[0];
    let k = loaded
        .spot
        .suit_perms
        .iter()
        .position(|pm| permute_card(h, pm) == c)
        .expect("4h must map to 4c under a suit permutation");

    // guard: a stale sibling reads as uniform, so a uniform canonical
    // strategy would make this comparison vacuous
    let na = view_c.actions.len() as f32;
    let non_uniform = view_c
        .players
        .iter()
        .flat_map(|p| p.hands.iter())
        .filter_map(|hand| hand.strategy.as_ref())
        .any(|s| s.iter().any(|f| (f - 1.0 / na).abs() > 0.05));
    assert!(non_uniform, "canonical strategy must be non-uniform");

    let mut compared = 0;
    for p in 0..2 {
        let perm = &loaded.spot.hand_perm[p][k];
        for (i, hand) in view_h.players[p].hands.iter().enumerate() {
            let (Some(sibling), Some(canon)) = (
                hand.strategy.as_ref(),
                view_c.players[p].hands[perm[i] as usize].strategy.as_ref(),
            ) else {
                continue;
            };
            for (a, b) in sibling.iter().zip(canon.iter()) {
                assert!(
                    (a - b).abs() < 1e-6,
                    "player {p} hand {} on 4h must mirror its 4c sibling: {a} vs {b}",
                    hand.combo
                );
            }
            compared += 1;
        }
    }
    assert!(compared > 0, "no strategies were compared");

    // Regrets must be materialized too: a resumed solve reads them, so a
    // strategy-only copy would look fine here but diverge on the next update.
    let walk_h = loaded.walk_path(&path_h).unwrap();
    let walk_c = loaded.walk_path(&path_c).unwrap();
    let node_h = &loaded.spot.tree.nodes[walk_h.node_idx as usize];
    let node_c = &loaded.spot.tree.nodes[walk_c.node_idx as usize];
    assert_eq!(node_h.player, node_c.player, "mirrored runouts must act on the same seat");
    let p = node_h.player as usize;
    let na = node_h.num_children as usize;
    assert_eq!(na, node_c.num_children as usize);
    let nh = loaded.spot.hands[p].len();
    let mut regrets_h = vec![0f32; na * nh];
    let mut regrets_c = vec![0f32; na * nh];
    unsafe {
        loaded.regrets[p].read_f32(walk_h.node_idx, node_h.data_offset, na * nh, &mut regrets_h);
        loaded.regrets[p].read_f32(walk_c.node_idx, node_c.data_offset, na * nh, &mut regrets_c);
    }
    let perm = &loaded.spot.hand_perm[p][k];
    for a in 0..na {
        for i in 0..nh {
            let (sibling, canon) = (regrets_h[a * nh + i], regrets_c[a * nh + perm[i] as usize]);
            assert!(
                (sibling - canon).abs() < 1e-6,
                "player {p} hand {i} regrets on 4h must mirror 4c: {sibling} vs {canon}"
            );
        }
    }
    std::fs::remove_file(path).ok();
}

/// A solver loaded from a save this writer produced is already materialized,
/// so saving it again must reproduce the same file (header + arenas) and that
/// file must load back with the same settings. A save whose sibling branches
/// were never materialized is repaired by its first re-save.
#[test]
fn resaving_a_loaded_solver_is_stable() {
    let (first, iteration) =
        solve_saved(tiny_config(), "resave_first", Algorithm::PcfrPlus, false);
    let mut loaded = Solver::load(first.to_str().unwrap()).unwrap();
    let second = temp_path("resave_second");
    loaded.save(second.to_str().unwrap()).unwrap();
    assert_eq!(
        std::fs::read(&first).unwrap(),
        std::fs::read(&second).unwrap(),
        "re-saving a clean loaded solver should reproduce the file"
    );

    let reloaded = Solver::load(second.to_str().unwrap()).unwrap();
    assert_eq!(reloaded.iteration, iteration);
    assert_eq!(reloaded.algo, Algorithm::PcfrPlus);
    assert!(!reloaded.use_isomorphism);
    std::fs::remove_file(first).ok();
    std::fs::remove_file(second).ok();
}

/// Locks are stored in a map but written in node order: with several locks a
/// load-then-save round trip must still reproduce the file byte for byte (the
/// manual GPU state controls fingerprint these files).
#[test]
fn resaving_a_locked_solver_is_stable() {
    let spot = Spot::new(symmetric_flop_config()).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..40 {
        solver.iterate();
    }
    solver.lock_node(&[], LockMode::Freeze, "root".into()).unwrap();
    let mut locks = 1;
    for index in 0..solver.spot.tree.nodes[0].num_children as usize {
        // the first child path that lands on another action node
        if solver
            .lock_node(&[PathStep::Action { index }], LockMode::Freeze, "child".into())
            .is_ok()
        {
            locks += 1;
            break;
        }
    }
    assert_eq!(locks, 2, "expected a second action node below the root");

    let first = temp_path("resave_locks_first");
    solver.save(first.to_str().unwrap()).unwrap();
    let header = header_json(&first);
    let saved: Vec<u32> = header["locks"]
        .as_array()
        .unwrap()
        .iter()
        .map(|entry| entry[0].as_u64().unwrap() as u32)
        .collect();
    assert_eq!(saved.len(), 2);
    assert!(saved.windows(2).all(|w| w[0] < w[1]), "locks not in node order: {saved:?}");

    let mut loaded = Solver::load(first.to_str().unwrap()).unwrap();
    assert!(loaded.use_isomorphism, "header should round-trip the switch");
    assert_eq!(loaded.locks, solver.locks);
    let second = temp_path("resave_locks_second");
    loaded.save(second.to_str().unwrap()).unwrap();
    assert_eq!(
        std::fs::read(&first).unwrap(),
        std::fs::read(&second).unwrap(),
        "re-saving a locked solver should reproduce the file"
    );
    std::fs::remove_file(first).ok();
    std::fs::remove_file(second).ok();
}
