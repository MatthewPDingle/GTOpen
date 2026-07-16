//! End-to-end solver correctness tests against known game-theory results.

use solver::cards::*;
use solver::evaluator::evaluate7;
use solver::game::Dealt;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Algorithm, LockMode, Solver, Spot, SpotConfig, Storage};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

fn hand_index(spot: &Spot, p: usize, combo: &str) -> usize {
    let cards = parse_cards(combo).unwrap();
    spot.hands[p]
        .iter()
        .position(|h| {
            (h.c1 == cards[0] && h.c2 == cards[1]) || (h.c1 == cards[1] && h.c2 == cards[0])
        })
        .unwrap_or_else(|| panic!("combo {combo} not found for player {p}"))
}

/// Classic clairvoyance game: polarized OOP (nuts + air) vs a bluff-catcher,
/// pot-sized bet only. Theory: OOP bets all nuts plus half the air (bluff
/// ratio 1/3 of betting range), IP calls 50%.
#[test]
fn clairvoyance_game_converges_to_theory() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..3000 {
        solver.iterate();
    }

    let exploit = solver.exploitability();
    let exploit_pct = exploit / 100.0 * 100.0;
    assert!(
        exploit_pct < 0.10,
        "exploitability too high: {exploit_pct}% pot"
    );

    // Root: OOP action node with [Check, Bet 100].
    let root = &solver.spot.tree.nodes[0];
    assert_eq!(root.num_children, 2);
    let sigma = solver.average_strategy(0, root);
    let nh = solver.spot.hands[0].len();
    let nuts = hand_index(&solver.spot, 0, "AcKc");
    let air = hand_index(&solver.spot, 0, "8h7h");
    let bet_nuts = sigma[nh + nuts];
    let bet_air = sigma[nh + air];
    assert!(bet_nuts > 0.97, "nuts should always bet, got {bet_nuts}");
    assert!(
        (bet_air - 0.5).abs() < 0.05,
        "air should bluff ~50%, got {bet_air}"
    );

    // IP node after bet: [Fold, Call].
    let bet_child = solver.spot.tree.children[root.children_start as usize + 1];
    let ip_node = &solver.spot.tree.nodes[bet_child as usize];
    assert_eq!(ip_node.kind, solver::tree::KIND_ACTION);
    assert_eq!(ip_node.player, 1);
    let sigma_ip = solver.average_strategy(bet_child, ip_node);
    let nh_ip = solver.spot.hands[1].len();
    let qq = hand_index(&solver.spot, 1, "QdQh");
    let call_freq = sigma_ip[nh_ip + qq];
    assert!(
        (call_freq - 0.5).abs() < 0.07,
        "bluff-catcher should call ~50%, got {call_freq}"
    );

    // EVs in pot-share convention via the query API.
    let view = solver.node_view(&[]).unwrap();
    let oop = &view.players[0];
    let nuts_ev = oop.hands[nuts].ev.unwrap();
    let air_ev = oop.hands[air].ev.unwrap();
    assert!(
        (nuts_ev - 150.0).abs() < 3.0,
        "nuts EV should be ~150, got {nuts_ev}"
    );
    assert!(air_ev.abs() < 2.0, "air EV should be ~0, got {air_ev}");

    // Zero-sum sanity: both players' total EVs sum to the pot.
    let ip_ev = view.players[1].hands[qq].ev.unwrap();
    let total = nuts_ev * 0.5 + air_ev * 0.5 + ip_ev;
    assert!(
        (total - 100.0).abs() < 3.0,
        "EVs should sum to pot, got {total}"
    );
}

/// A small full flop->river spot must converge (exploitability decreasing
/// and reaching < 1% pot).
#[test]
fn small_flop_spot_converges() {
    let config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));

    for _ in 0..20 {
        solver.iterate();
    }
    let e1 = solver.exploitability() / 60.0 * 100.0;
    for _ in 0..180 {
        solver.iterate();
    }
    let e2 = solver.exploitability() / 60.0 * 100.0;
    assert!(e2 < e1, "exploitability should decrease: {e1} -> {e2}");
    assert!(e2 < 1.0, "exploitability should reach < 1% pot, got {e2}%");
}

/// Equity from the solver's sweep must match brute-force enumeration.
#[test]
fn equity_matches_brute_force() {
    let config = SpotConfig {
        board: "AsKh7d".to_string(),
        range_oop: "AhAd".to_string(),
        range_ip: "KsKc".to_string(),
        tree: TreeConfig {
            starting_pot: 10.0,
            effective_stack: 100.0,
            oop: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    let spot = Spot::new(config).unwrap();
    let solver = Solver::new(Arc::new(spot));

    let eq = solver.equity(0, &solver.spot.weights[1], Dealt::default());
    let i = hand_index(&solver.spot, 0, "AhAd");

    // Brute force.
    let board = parse_cards("AsKh7d").unwrap();
    let h0 = parse_cards("AhAd").unwrap();
    let h1 = parse_cards("KsKc").unwrap();
    let mut used = 0u64;
    for &c in board.iter().chain(h0.iter()).chain(h1.iter()) {
        used |= card_mask(c);
    }
    let (mut win, mut tie, mut total) = (0f64, 0f64, 0f64);
    for t in 0..52u8 {
        if used & card_mask(t) != 0 {
            continue;
        }
        for r in (t + 1)..52 {
            if used & card_mask(r) != 0 {
                continue;
            }
            let mut c7a = [board[0], board[1], board[2], t, r, h0[0], h0[1]];
            let v0 = evaluate7(&c7a);
            c7a[5] = h1[0];
            c7a[6] = h1[1];
            let v1 = evaluate7(&c7a);
            total += 1.0;
            if v0 > v1 {
                win += 1.0;
            } else if v0 == v1 {
                tie += 1.0;
            }
        }
    }
    let expected = ((win + tie / 2.0) / total) as f32;
    assert!(
        (eq[i] - expected).abs() < 1e-4,
        "equity mismatch: solver {} vs brute force {}",
        eq[i],
        expected
    );
}

/// Node locking: if the bluff-catcher is locked to always call, the
/// polarized player must stop bluffing (and keep value betting).
#[test]
fn locked_always_call_kills_bluffs() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    // Pre-solve so the lock has a strategy to scale, then lock IP's
    // fold/call node to "always call" and re-solve.
    for _ in 0..200 {
        solver.iterate();
    }
    let path = vec![solver::PathStep::Action { index: 1 }]; // after OOP bet
    // range mode: 0% fold, 100% call -> every bluff-catcher calls
    solver
        .lock_node(
            &path,
            LockMode::Range { freqs: vec![0.0, 1.0] },
            "ip always calls".to_string(),
        )
        .unwrap();
    for _ in 0..2000 {
        solver.iterate();
    }

    let root = &solver.spot.tree.nodes[0];
    let sigma = solver.average_strategy(0, root);
    let nh = solver.spot.hands[0].len();
    let nuts = hand_index(&solver.spot, 0, "AcKc");
    let air = hand_index(&solver.spot, 0, "8h7h");
    assert!(
        sigma[nh + nuts] > 0.97,
        "nuts should still bet vs station, got {}",
        sigma[nh + nuts]
    );
    assert!(
        sigma[nh + air] < 0.05,
        "air should never bluff vs station, got {}",
        sigma[nh + air]
    );

    // And the lock itself holds in queries.
    let view = solver.node_view(&path).unwrap();
    assert!(view.locked);
    let qq = hand_index(&solver.spot, 1, "QdQh");
    let st = view.players[1].hands[qq].strategy.as_ref().unwrap();
    assert!(st[1] > 0.999, "locked call freq should be 1.0, got {}", st[1]);
}

/// Lock modes: range targeting is idempotent (re-applying the same target
/// gives the same result — no multiplier compounding), the aggregate matches
/// the requested frequency, and per-hand edits set exact values.
#[test]
fn lock_modes_clean_and_idempotent() {
    let config = SpotConfig {
        board: "Ks7h2d".to_string(),
        range_oop: "AA,KK,QQ,JJ,TT,AKs,AQs,AJs,KQs,JTs,T9s,87s,76s,A5s".to_string(),
        range_ip: "KK,QQ,JJ,TT,99,AQs,AJs,KQs,QJs,JTs,T9s,98s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("75", ""), sizing("75", ""), sizing("75", "")],
            ip: [sizing("75", ""), sizing("75", ""), sizing("75", "")],
            ..Default::default()
        },
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..300 {
        solver.iterate();
    }

    // root OOP, actions [Check, Bet 75%]
    let root_path: Vec<solver::PathStep> = vec![];
    let na = solver.spot.tree.nodes[0].num_children as usize;
    assert_eq!(na, 2);

    // reach-weighted aggregate bet frequency at the root for OOP
    let agg_bet = |s: &Solver| {
        let v = s.node_view(&[]).unwrap();
        let hs = &v.players[0].hands;
        let (mut n, mut d) = (0f64, 0f64);
        for h in hs {
            if let Some(st) = &h.strategy {
                n += st[1] as f64 * h.reach as f64;
                d += h.reach as f64;
            }
        }
        n / d
    };

    // target 30% bet / 70% check
    solver
        .lock_node(&root_path, LockMode::Range { freqs: vec![0.70, 0.30] }, "r".into())
        .unwrap();
    let a1 = agg_bet(&solver);
    assert!((a1 - 0.30).abs() < 0.02, "aggregate bet should be ~30%, got {a1}");

    // re-apply the SAME target: must not compound (idempotent)
    solver
        .lock_node(&root_path, LockMode::Range { freqs: vec![0.70, 0.30] }, "r".into())
        .unwrap();
    let a2 = agg_bet(&solver);
    assert!((a2 - a1).abs() < 1e-3, "re-locking same target compounded: {a1} -> {a2}");

    // change the target up to 65% bet, still from the solved base (not compounded)
    solver
        .lock_node(&root_path, LockMode::Range { freqs: vec![0.35, 0.65] }, "r".into())
        .unwrap();
    let a3 = agg_bet(&solver);
    assert!((a3 - 0.65).abs() < 0.02, "aggregate bet should retarget to ~65%, got {a3}");

    // per-hand edit: force AA to check 100% (action 0), others keep current
    solver
        .lock_node(
            &root_path,
            LockMode::Hands { edits: vec![solver::query::HandEdit {
                combo: "AcAd".into(),
                freqs: vec![1.0, 0.0],
            }] },
            "h".into(),
        )
        .unwrap();
    let v = solver.node_view(&[]).unwrap();
    let aa = hand_index(&solver.spot, 0, "AcAd");
    let st = v.players[0].hands[aa].strategy.as_ref().unwrap();
    assert!(st[0] > 0.999, "AcAd should be locked to 100% check, got {}", st[0]);
}

/// Suit isomorphism must (a) detect the c<->h symmetry on a two-tone board,
/// (b) converge equivalently to the non-isomorphic solver, and (c) produce
/// exactly mirrored strategies on isomorphic runouts after symmetrize.
#[test]
fn suit_isomorphism_equivalence() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config.clone()).unwrap();
    assert_eq!(
        spot.suit_perms.len(),
        2,
        "KsQs2d with symmetric ranges should have exactly the c<->h swap"
    );
    let mut iso = Solver::new(Arc::new(spot));
    let mut plain = Solver::new(Arc::new(Spot::new(config).unwrap()));
    plain.use_isomorphism = false;

    for _ in 0..100 {
        iso.iterate();
        plain.iterate();
    }
    let e_iso = iso.exploitability() / 60.0 * 100.0;
    let e_plain = plain.exploitability() / 60.0 * 100.0;
    assert!(e_iso < 2.0, "iso solver should converge, got {e_iso}%");
    assert!(e_plain < 2.0, "plain solver should converge, got {e_plain}%");
    assert!(
        (e_iso - e_plain).abs() < 0.6,
        "iso and plain exploitability should agree: {e_iso}% vs {e_plain}%"
    );

    // Root EVs agree between the two solvers.
    iso.ensure_symmetric();
    let va = iso.node_view(&[]).unwrap();
    let vb = plain.node_view(&[]).unwrap();
    for p in 0..2 {
        let avg = |v: &solver::NodeView| {
            let hs = &v.players[p].hands;
            let (mut n, mut d) = (0f64, 0f64);
            for h in hs {
                if let Some(ev) = h.ev {
                    n += ev as f64 * h.reach as f64;
                    d += h.reach as f64;
                }
            }
            n / d
        };
        let (a, b) = (avg(&va), avg(&vb));
        assert!(
            (a - b).abs() < 1.2,
            "player {p} root EV should agree: iso {a} vs plain {b}"
        );
    }

    // Isomorphic turn branches (4c vs 4h after check/check) must mirror
    // exactly once symmetrized.
    use solver::PathStep;
    let path = |card: &str| {
        vec![
            PathStep::Action { index: 0 },
            PathStep::Action { index: 0 },
            PathStep::Card { card: card.to_string() },
        ]
    };
    let vc = iso.node_view(&path("4c")).unwrap();
    let vh = iso.node_view(&path("4h")).unwrap();
    let agg_freq = |v: &solver::NodeView| {
        let hs = &v.players[0].hands;
        let (mut n, mut d) = (0f64, 0f64);
        for h in hs {
            if let Some(s) = &h.strategy {
                n += s[0] as f64 * h.reach as f64;
                d += h.reach as f64;
            }
        }
        n / d
    };
    let (fc, fh) = (agg_freq(&vc), agg_freq(&vh));
    assert!(
        (fc - fh).abs() < 1e-4,
        "isomorphic turn strategies should mirror: {fc} vs {fh}"
    );
}

fn small_flop_config() -> SpotConfig {
    SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    }
}

/// The i16/u16 compressed solver must match the f32 solver: exploitability
/// within 0.1% pot after the same number of iterations, and root EVs agree.
#[test]
fn compressed_matches_f32_within_tenth_pct_pot() {
    let config = small_flop_config();
    let mut plain = Solver::new(Arc::new(Spot::new(config.clone()).unwrap()));
    let mut comp =
        Solver::with_storage(Arc::new(Spot::new(config).unwrap()), Storage::Compressed);
    for _ in 0..200 {
        plain.iterate();
        comp.iterate();
    }
    let ef = plain.exploitability() / 60.0 * 100.0;
    let ec = comp.exploitability() / 60.0 * 100.0;
    assert!(ef < 1.0, "f32 solver should converge, got {ef}% pot");
    assert!(ec < 1.0, "compressed solver should converge, got {ec}% pot");
    assert!(
        (ef - ec).abs() < 0.1,
        "compressed exploitability must match f32 within 0.1% pot: {ec}% vs {ef}%"
    );

    // Root EVs (reach-weighted average) agree within 1% of pot.
    let va = plain.node_view(&[]).unwrap();
    let vb = comp.node_view(&[]).unwrap();
    for p in 0..2 {
        let avg = |v: &solver::NodeView| {
            let (mut n, mut d) = (0f64, 0f64);
            for h in &v.players[p].hands {
                if let Some(ev) = h.ev {
                    n += ev as f64 * h.reach as f64;
                    d += h.reach as f64;
                }
            }
            n / d
        };
        let (a, b) = (avg(&va), avg(&vb));
        assert!(
            (a - b).abs() < 0.6,
            "player {p} root EV should agree: f32 {a} vs compressed {b}"
        );
    }

    // Compressed arenas actually use less memory. (This tiny spot has very
    // short hand lists, so the per-node scale arrays weigh in at ~10% extra;
    // realistic spots sit at ~50%.)
    assert!(
        comp.arena_bytes() < plain.arena_bytes() * 7 / 10,
        "compressed arenas should be roughly half: {} vs {}",
        comp.arena_bytes(),
        plain.arena_bytes()
    );
}

/// PCFR+ must converge, in both storage modes.
#[test]
fn pcfr_plus_converges() {
    let config = small_flop_config();
    let mut s = Solver::new(Arc::new(Spot::new(config.clone()).unwrap()));
    s.algo = Algorithm::PcfrPlus;
    for _ in 0..200 {
        s.iterate();
    }
    let e = s.exploitability() / 60.0 * 100.0;
    assert!(e < 1.0, "PCFR+ (f32) should converge below 1% pot, got {e}%");

    let mut c = Solver::with_storage(Arc::new(Spot::new(config).unwrap()), Storage::Compressed);
    c.algo = Algorithm::PcfrPlus;
    for _ in 0..200 {
        c.iterate();
    }
    let e = c.exploitability() / 60.0 * 100.0;
    assert!(
        e < 1.0,
        "PCFR+ (compressed) should converge below 1% pot, got {e}%"
    );
}

/// Save/load roundtrip is exact for the compressed solver, in both directions
/// (compressed -> compressed and compressed -> f32: the on-disk format is f32).
#[test]
fn save_load_roundtrip_compressed() {
    let config = small_flop_config();
    let mut solver =
        Solver::with_storage(Arc::new(Spot::new(config).unwrap()), Storage::Compressed);
    for _ in 0..50 {
        solver.iterate();
    }
    let e_before = solver.exploitability();
    let path = std::env::temp_dir().join("gto_test_save_compressed.bin");
    let path_str = path.to_str().unwrap();
    solver.save(path_str).unwrap();

    let loaded = Solver::load_with_storage(path_str, Storage::Compressed).unwrap();
    assert_eq!(loaded.iteration, solver.iteration);
    let e_comp = loaded.exploitability();
    assert!(
        (e_before - e_comp).abs() < 1e-9,
        "compressed roundtrip changed exploitability: {e_before} vs {e_comp}"
    );

    // Loading into f32 normalizes strategies from the decoded floats rather
    // than the raw quants, so summation order differs at f32 epsilon level.
    let loaded_f32 = Solver::load_with_storage(path_str, Storage::F32).unwrap();
    let e_f32 = loaded_f32.exploitability();
    assert!(
        (e_before - e_f32).abs() < 1e-4,
        "compressed->f32 load changed exploitability: {e_before} vs {e_f32}"
    );
    std::fs::remove_file(path).ok();
}

/// Save/load roundtrip preserves the solution.
#[test]
fn save_load_roundtrip() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..200 {
        solver.iterate();
    }
    let e_before = solver.exploitability();
    let path = std::env::temp_dir().join("gto_test_save.bin");
    let path_str = path.to_str().unwrap();
    solver.save(path_str).unwrap();
    let loaded = Solver::load(path_str).unwrap();
    let e_after = loaded.exploitability();
    assert_eq!(loaded.iteration, solver.iteration);
    assert!(
        (e_before - e_after).abs() < 1e-9,
        "exploitability changed after roundtrip: {e_before} vs {e_after}"
    );
    std::fs::remove_file(path).ok();
}

/// A per-hand lock applied while browsing a non-representative isomorphic
/// runout must land on the suit-mapped combo of the representative branch,
/// so the browsed view shows the edit on exactly the combo the user picked.
#[test]
fn hands_lock_respects_suit_isomorphism() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    assert_eq!(spot.suit_perms.len(), 2, "expected exactly the c<->h swap");
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..100 {
        solver.iterate();
    }
    use solver::PathStep;
    let path = vec![
        PathStep::Action { index: 0 },
        PathStep::Action { index: 0 },
        PathStep::Card { card: "4h".to_string() },
    ];
    // sanity: 4c is the representative, so browsing 4h exercises the remap
    let canon = solver.canonical_path(&path);
    assert!(
        matches!(&canon[2], PathStep::Card { card } if card == "4c"),
        "4c should be the orbit representative of the 4h turn"
    );
    solver
        .lock_node(
            &path,
            LockMode::Hands {
                edits: vec![solver::query::HandEdit {
                    combo: "AhJh".into(),
                    freqs: vec![0.37, 0.63],
                }],
            },
            "iso hand lock".into(),
        )
        .unwrap();
    for _ in 0..50 {
        solver.iterate();
    }
    solver.ensure_symmetric();
    let v = solver.node_view(&path).unwrap();
    let idx = hand_index(&solver.spot, 0, "AhJh");
    let st = v.players[0].hands[idx].strategy.as_ref().unwrap();
    assert!(
        (st[0] - 0.37).abs() < 5e-3,
        "AhJh on the browsed 4h branch should show its own lock (37% check), got {}",
        st[0]
    );
}

/// Node locks must survive save/load: the lock list, the locked flag and the
/// displayed strategy all round-trip; pre-lock save files (no lock fields in
/// the header) still load, with empty locks.
#[test]
fn save_load_preserves_locks() {
    let config = small_flop_config();
    let mut solver = Solver::new(Arc::new(Spot::new(config).unwrap()));
    for _ in 0..50 {
        solver.iterate();
    }
    solver
        .lock_node(&[], LockMode::Range { freqs: vec![0.7, 0.3] }, "root 30% bet".into())
        .unwrap();
    let v_before = solver.node_view(&[]).unwrap();
    let path = std::env::temp_dir().join("gto_test_save_locks.bin");
    let path_str = path.to_str().unwrap();
    solver.save(path_str).unwrap();

    let loaded = Solver::load(path_str).unwrap();
    assert_eq!(loaded.list_locks(), vec!["root 30% bet".to_string()]);
    assert_eq!(loaded.locks.len(), 1);
    let v_after = loaded.node_view(&[]).unwrap();
    assert!(v_after.locked, "locked flag must survive the round-trip");
    for (a, b) in v_before.players[0]
        .hands
        .iter()
        .zip(v_after.players[0].hands.iter())
    {
        let (sa, sb) = (a.strategy.as_ref().unwrap(), b.strategy.as_ref().unwrap());
        for (x, y) in sa.iter().zip(sb.iter()) {
            assert!(
                (x - y).abs() < 1e-6,
                "{}: locked strategy changed after load: {x} vs {y}",
                a.combo
            );
        }
    }

    // pre-lock format: strip the lock fields from the header and reload
    let bytes = std::fs::read(path_str).unwrap();
    let nl = 10 + bytes[10..].iter().position(|&b| b == b'\n').unwrap();
    let mut hdr: serde_json::Value = serde_json::from_slice(&bytes[10..nl]).unwrap();
    hdr.as_object_mut().unwrap().remove("locks");
    hdr.as_object_mut().unwrap().remove("lock_labels");
    let mut old = bytes[..10].to_vec();
    old.extend_from_slice(serde_json::to_string(&hdr).unwrap().as_bytes());
    old.extend_from_slice(&bytes[nl..]);
    std::fs::write(path_str, old).unwrap();
    let legacy = Solver::load(path_str).unwrap();
    assert!(legacy.locks.is_empty() && legacy.list_locks().is_empty());
    assert_eq!(legacy.iteration, solver.iteration);
    std::fs::remove_file(path).ok();
}

/// A lock applied after a finished solve (symmetry cache clean) must show on
/// isomorphic sibling runouts immediately: lock mutations mark the cache
/// dirty, so the next ensure_symmetric materializes them.
#[test]
fn lock_after_solve_visible_on_isomorphic_branch() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    assert_eq!(spot.suit_perms.len(), 2, "expected exactly the c<->h swap");
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..100 {
        solver.iterate();
    }
    solver.ensure_symmetric(); // the solve worker leaves the cache clean

    use solver::PathStep;
    let path = vec![
        PathStep::Action { index: 0 },
        PathStep::Action { index: 0 },
        PathStep::Card { card: "4h".to_string() },
    ];
    // sanity: 4c is the representative, so browsing 4h reads the sibling copy
    let canon = solver.canonical_path(&path);
    assert!(
        matches!(&canon[2], PathStep::Card { card } if card == "4c"),
        "4c should be the orbit representative of the 4h turn"
    );
    // lock to always-bet: the solved strategy here is check-heavy, so any
    // stale (pre-lock or post-unlock) branch copy is unmistakable
    solver
        .lock_node(&path, LockMode::Range { freqs: vec![0.0, 1.0] }, "always bet".into())
        .unwrap();
    solver.ensure_symmetric(); // what the server does before every node_view
    let v = solver.node_view(&path).unwrap();
    assert!(v.locked);
    for h in &v.players[0].hands {
        let st = h.strategy.as_ref().unwrap();
        assert!(
            st[1] > 0.999,
            "{} on the browsed 4h branch must show the lock (bet 100%), got {}",
            h.combo,
            st[1]
        );
    }

    // unlock must un-materialize the sibling copy the same way
    assert!(solver.unlock_node(&path).unwrap());
    solver.ensure_symmetric();
    let vh = solver.node_view(&path).unwrap();
    assert!(!vh.locked);
    let vc = solver.node_view(&solver.canonical_path(&path)).unwrap();
    let agg_check = |v: &solver::NodeView| {
        let (mut n, mut d) = (0f64, 0f64);
        for h in &v.players[0].hands {
            if let Some(s) = &h.strategy {
                n += s[0] as f64 * h.reach as f64;
                d += h.reach as f64;
            }
        }
        n / d
    };
    let (fh, fc) = (agg_check(&vh), agg_check(&vc));
    assert!(
        (fh - fc).abs() < 1e-4,
        "after unlock the sibling must mirror the canonical branch: {fh} vs {fc}"
    );
    assert!(
        fc > 0.5,
        "solved strategy should be check-heavy here, got check freq {fc}"
    );
}

/// Range-average EVs must satisfy EV_OOP + EV_IP = pot when weighted by
/// reach x valid (each hand's EV is normalized by its own valid mass, so
/// only the pair mass aggregates consistently). Reach-only weighting breaks
/// the identity whenever card removal skews valid across hands, most
/// visibly far from convergence.
#[test]
fn range_average_ev_sums_to_pot() {
    let config = small_flop_config();
    let mut solver = Solver::new(Arc::new(Spot::new(config).unwrap()));
    for _ in 0..10 {
        solver.iterate();
    }
    let v = solver.node_view(&[]).unwrap();
    let mean = |p: usize, pair_mass: bool| {
        let (mut n, mut d) = (0f64, 0f64);
        for h in &v.players[p].hands {
            if let Some(ev) = h.ev {
                let w = h.reach as f64 * if pair_mass { h.valid as f64 } else { 1.0 };
                n += w * ev as f64;
                d += w;
            }
        }
        n / d
    };
    let sum = mean(0, true) + mean(1, true);
    let naive = mean(0, false) + mean(1, false);
    assert!(
        (sum - v.pot).abs() < v.pot * 1e-3,
        "pair-mass weighted EVs must sum to pot: {sum} vs {}",
        v.pot
    );
    assert!(
        (naive - v.pot).abs() > v.pot * 1e-3,
        "reach-only weighting should violate the identity here (else this \
         test is vacuous): {naive} vs {}",
        v.pot
    );

    // the runouts report means (reach x valid weighted) obey it on every card
    use solver::PathStep;
    let rep = solver
        .runouts(&[PathStep::Action { index: 0 }, PathStep::Action { index: 0 }])
        .unwrap();
    assert!(!rep.rows.is_empty());
    for row in &rep.rows {
        if let (Some(a), Some(b)) = (row.ev[0], row.ev[1]) {
            assert!(
                ((a + b) as f64 - rep.pot).abs() < rep.pot * 1e-3,
                "runout {}: EVs must sum to pot: {a} + {b} vs {}",
                row.card,
                rep.pot
            );
        }
    }
}

/// Runouts-report action labels must match the browse action bar: a bet that
/// puts the actor all-in is labeled "All-in", not "Bet".
#[test]
fn runouts_labels_allin_bets() {
    let config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT".to_string(),
        range_ip: "AA,KK".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 60.0,
            oop: [sizing("", ""), sizing("60", ""), sizing("", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    };
    let solver = Solver::new(Arc::new(Spot::new(config).unwrap()));
    use solver::PathStep;
    let chance = vec![PathStep::Action { index: 0 }, PathStep::Action { index: 0 }];
    let rep = solver.runouts(&chance).unwrap();
    let mut node_path = chance.clone();
    node_path.push(PathStep::Card { card: rep.rows[0].card.clone() });
    let view = solver.node_view(&node_path).unwrap();
    let browse: Vec<String> = view.actions.iter().map(|a| a.label.clone()).collect();
    let report: Vec<String> = rep.actions.iter().map(|a| a.label.clone()).collect();
    assert_eq!(report, browse, "report labels must match the browse action bar");
    assert!(
        report.iter().any(|l| l.starts_with("All-in")),
        "the stack-sized turn bet should be labeled all-in: {report:?}"
    );
}

/// Exploit view: the best response against a locked always-caller bets the
/// nuts, never bluffs the air, and per-hand BR EV dominates the current
/// strategy's EV (with a strictly positive average gain, since the solved
/// strategy still bluffs at the equilibrium frequency).
#[test]
fn exploit_view_vs_locked_station() {
    let config = SpotConfig {
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
    };
    let spot = Spot::new(config).unwrap();
    let mut solver = Solver::new(Arc::new(spot));
    for _ in 0..500 {
        solver.iterate();
    }
    // lock IP to always-call the bet
    let bet_path = vec![solver::PathStep::Action { index: 1 }];
    solver
        .lock_node(
            &bet_path,
            LockMode::Range { freqs: vec![0.0, 1.0] },
            "station".into(),
        )
        .unwrap();

    let v = solver.exploit_view(&[], 0).unwrap();
    assert_eq!(v.exploiter, 0);
    let nuts = hand_index(&solver.spot, 0, "AcKc");
    let air = hand_index(&solver.spot, 0, "8h7h");
    let st_nuts = v.hands[nuts].br_strategy.as_ref().unwrap();
    let st_air = v.hands[air].br_strategy.as_ref().unwrap();
    assert!(st_nuts[1] > 0.999, "BR must always bet the nuts, got {:?}", st_nuts);
    assert!(st_air[0] > 0.999, "BR must never bluff vs a station, got {:?}", st_air);
    for h in &v.hands {
        if let (Some(b), Some(c)) = (h.br_ev, h.cur_ev) {
            assert!(b >= c - 1e-3, "BR EV must dominate: {} vs {} ({})", b, c, h.combo);
        }
    }
    let gain = v.avg_gain.expect("avg gain");
    assert!(gain > 0.5, "exploiting a station should gain plainly, got {gain}");
}
