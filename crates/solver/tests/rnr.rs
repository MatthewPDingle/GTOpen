//! "Trust the read" (Restricted Nash Response, rnr.rs): trust = 1 must be
//! today's lock-and-re-adapt solve, trust = 0 the unlocked solve, and the
//! levels in between must trade EV against the read for safety.

use solver::game::Dealt;
use solver::query::{PathStep, PostflopStats};
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: parse_sizes(raise).unwrap(), donk: vec![] }
}

/// River spot: OOP bets 75% or checks, IP can raise or bet 75% when
/// checked to. The IP profile folds far too much to bets and never raises.
fn river() -> Spot {
    Spot::new(SpotConfig {
        board: "Ks9h5d3c2s".to_string(),
        range_oop: "AA,KK,99,AK,KQ,KJs,K9s,QJ,JT,T8s,76s,A4s,64s".to_string(),
        range_ip: "AK,KQ,KJ,KT,QQ,JJ,TT,99,A9s,98s,55,QJs".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 300.0,
            oop: [sizing("", ""), sizing("", ""), sizing("75", "100")],
            ip: [sizing("", ""), sizing("", ""), sizing("75", "100")],
            ..Default::default()
        },
    })
    .unwrap()
}

/// Turn spot (a chance layer exercises the stacked reach masking).
fn turn() -> Spot {
    Spot::new(SpotConfig {
        board: "Kh9d5c2h".to_string(),
        range_oop: "AA,KK,99,AK,KQ,QJs,JTs,T8s,76s,A5s".to_string(),
        range_ip: "AK,KQ,KJ,QQ,JJ,TT,A9s,98s,55".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 200.0,
            oop: [sizing("", ""), sizing("75", ""), sizing("75", "")],
            ip: [sizing("", ""), sizing("75", ""), sizing("75", "")],
            ..Default::default()
        },
    })
    .unwrap()
}

fn folder() -> PostflopStats {
    PostflopStats {
        contextual_betting: None,
        cbet: [60.0, 55.0, 50.0],
        fold_to_bet: [70.0, 70.0, 75.0],
        raise_bet: 0.0,
        donk: 30.0,
        bet_size: "min".into(),
    }
}

/// Solve `base` iterations, then lock IP to the folding profile.
fn locked(spot: fn() -> Spot, base: usize) -> Solver {
    let mut s = Solver::new(Arc::new(spot()));
    for _ in 0..base {
        s.iterate();
    }
    let summary = s.lock_profile(1, &folder(), None).unwrap();
    assert!(summary.locked > 0);
    s
}

fn root_strategies(s: &Solver) -> Vec<Option<Vec<f32>>> {
    s.node_view(&[]).unwrap().players[0].hands.iter().map(|h| h.strategy.clone()).collect()
}

/// A villain node below the root: OOP checks, IP to act.
const CHECKED: &[PathStep] = &[PathStep::Action { index: 0 }];

#[test]
fn trust_validation_and_inactive_cases() {
    let mut s = Solver::new(Arc::new(river()));
    assert!(s.set_trust(Some(1.5)).is_err());
    assert!(s.set_trust(Some(-0.1)).is_err());
    assert!(s.set_trust(Some(f32::NAN)).is_err());
    s.set_trust(Some(0.5)).unwrap();
    assert!(s.rnr_active().is_none(), "no profile lock: nothing to trust");
    assert!(s.trust_readout().is_err());
    let mut s = locked(river, 10);
    s.set_trust(Some(1.0)).unwrap();
    assert!(s.rnr_active().is_none(), "trust 1 is today's solve");
    s.set_trust(Some(0.7)).unwrap();
    let r = s.rnr_active().unwrap();
    assert_eq!(r.villain, 1);
    assert!((r.trust - 0.7).abs() < 1e-7);
}

#[test]
fn trust_one_is_todays_locked_solve() {
    let mut a = locked(river, 30);
    let mut b = locked(river, 30);
    b.set_trust(Some(1.0)).unwrap();
    for _ in 0..40 {
        a.iterate();
        b.iterate();
    }
    assert_eq!(root_strategies(&a), root_strategies(&b));
    assert_eq!(a.exploitability().to_bits(), b.exploitability().to_bits());
}

#[test]
fn trust_zero_is_the_unlocked_solve() {
    for spot in [river as fn() -> Spot, turn] {
        let mut a = locked(spot, 25);
        a.set_trust(Some(0.0)).unwrap();
        let mut b = Solver::new(Arc::new(spot()));
        for _ in 0..25 {
            b.iterate();
        }
        // a new trust level restarts the averages (set_trust); match it
        assert_eq!(a.iteration, 0);
        b.restart_averages();
        for _ in 0..30 {
            a.iterate();
            b.iterate();
        }
        // the hero's learning is bit-identical to the unlocked solve
        assert_eq!(root_strategies(&a), root_strategies(&b));
        // ...and so is the free villain's, read under the free view
        let w0 = &b.spot.weights[0];
        let fa = a.traverse_avg_view(0, 1, w0, Dealt::default(), true);
        let fb = b.traverse_avg(0, 1, w0, Dealt::default());
        assert_eq!(fa, fb);
        let (ea, eb) = (a.exploitability(), b.exploitability());
        assert!((ea - eb).abs() <= 1e-6 * eb.abs().max(1.0), "trust-0 exploitability {ea} vs unlocked {eb}");
    }
}

#[test]
fn trust_game_converges() {
    let mut s = locked(river, 20);
    s.set_trust(Some(0.6)).unwrap();
    for _ in 0..20 {
        s.iterate();
    }
    let early = s.exploitability();
    for _ in 0..300 {
        s.iterate();
    }
    let late = s.exploitability();
    assert!(late.is_finite() && late >= -1e-6);
    assert!(late < early, "trust-game exploitability {early} -> {late}");
    assert!(late < 0.5, "trust game should converge below 0.5% pot, got {late} chips");
}

#[test]
fn frontier_trades_ev_vs_read_for_safety() {
    let mut rows = Vec::new();
    for trust in [0.0f32, 0.5, 0.8, 1.0] {
        let mut s = locked(river, 60);
        s.set_trust(Some(trust)).unwrap();
        for _ in 0..600 {
            s.iterate();
        }
        let r = s.trust_readout().unwrap();
        assert_eq!((r.hero, r.villain), (0, 1));
        assert!(r.exploitability < 0.5, "trust {trust}: not converged ({} chips)", r.exploitability);
        // zero-sum: hero's worst case is the pot minus the best response
        let worst = r.hero_worst_case_ev.unwrap();
        assert!((worst + r.villain_best_response_ev - 100.0).abs() < 1e-6);
        assert!(worst <= r.hero_ev_vs_read + 1e-3);
        rows.push((trust, r.hero_ev_vs_read, worst));
    }
    eprintln!("trust, EV vs read, worst case: {rows:?}");
    let tol = 0.3; // chips, about the convergence level
    for w in rows.windows(2) {
        let ((t0, read0, worst0), (t1, read1, worst1)) = (w[0], w[1]);
        assert!(read1 >= read0 - tol, "EV vs read fell from trust {t0} to {t1}: {read0} -> {read1}");
        assert!(worst1 <= worst0 + tol, "worst case rose from trust {t0} to {t1}: {worst0} -> {worst1}");
    }
    let (first, last) = (rows[0], rows[rows.len() - 1]);
    assert!(last.1 > first.1 + 1.0, "the over-folding read should be worth exploiting: {rows:?}");
    assert!(last.2 < first.2 - 1.0, "full trust should be exploitable: {rows:?}");
}

#[test]
fn read_locks_still_shown_and_free_villain_differs_off_read() {
    // the read is what Browse shows at a profile node; the free villain's
    // own strategy there is visible through the free view
    let mut s = locked(river, 30);
    let read = s.node_view(CHECKED).unwrap().players[1].hands.iter().map(|h| h.strategy.clone()).collect::<Vec<_>>();
    s.set_trust(Some(0.3)).unwrap();
    for _ in 0..100 {
        s.iterate();
    }
    let after = s.node_view(CHECKED).unwrap().players[1].hands.iter().map(|h| h.strategy.clone()).collect::<Vec<_>>();
    assert_eq!(read, after, "profile locks stay the read");
}

#[test]
fn warm_started_sweep_converges_at_every_level() {
    // the server's sweep: one solver, the dial stepped down, warm-started,
    // with and without the warm regret rescale
    for keep in [None, Some(20)] {
        let mut s = locked(turn, 60);
        s.warm_regret_keep = keep;
        let pot = s.spot.tree.config.starting_pot;
        for trust in [1.0f32, 0.9, 0.7, 0.4, 0.0] {
            let epoch = s.average_epoch;
            s.set_trust(Some(trust)).unwrap();
            assert_eq!(s.average_epoch != epoch, trust != 1.0, "only a changed dial restarts");
            for _ in 0..300 {
                s.iterate();
            }
            let x = s.exploitability() / pot * 100.0;
            eprintln!("keep {keep:?} trust {trust}: {x:.3}% pot");
            assert!(x < 0.5, "keep {keep:?} trust {trust}: warm-started solve stuck at {x}% pot");
        }
    }
}

#[test]
fn read_and_free_villain_learn_apart_off_the_profile() {
    // A read-reached villain node the profile leaves open (here unlocked by
    // hand; deep raise lines in a real tree): the read re-adapts there for
    // himself and the free villain for himself. Sharing one strategy there
    // made the trust game stall at high trust.
    for trust in [0.9f32, 0.5] {
        let mut s = locked(river, 60);
        assert!(s.unlock_node(CHECKED).unwrap());
        s.set_trust(Some(trust)).unwrap();
        let mut xs = Vec::new();
        for k in 1..=600 {
            s.iterate();
            if k % 200 == 0 {
                xs.push(s.exploitability());
            }
        }
        eprintln!("trust {trust}: exploitability {xs:?} chips");
        assert!(xs[2] < 0.05, "trust {trust}: trust game stuck at {} chips", xs[2]);
        assert!(xs[2] < xs[0]);
        // the read villain best-responds at the open node too: playing it
        // like the free villain would leave him a gain there
        let w0 = &s.spot.weights[0];
        let value = |cfv: &[f32]| {
            s.spot.weights[1].iter().zip(cfv).map(|(&w, &v)| w as f64 * v as f64).sum::<f64>() / s.pair_weight_sum()
        };
        let br = value(&s.traverse_br_view(0, 1, w0, Dealt::default(), false));
        let avg = value(&s.traverse_avg_view(0, 1, w0, Dealt::default(), false));
        eprintln!("trust {trust}: read villain gain {} chips", br - avg);
        assert!(br - avg < 0.05, "trust {trust}: the read villain could gain {} chips", br - avg);
    }
}

#[test]
fn new_trust_level_keeps_the_pre_lock_average_at_locked_nodes() {
    // a re-applied profile rakes from the solved strategy at its nodes
    let mut s = locked(river, 30);
    let solved = |s: &Solver| -> Vec<(u32, Vec<f32>)> {
        let mut idx: Vec<u32> = s.locks.keys().copied().collect();
        idx.sort();
        idx.into_iter()
            .map(|i| {
                let node = &s.spot.tree.nodes[i as usize];
                let mut v = vec![0f32; node.num_children as usize * s.spot.hands[node.player as usize].len()];
                s.solved_strategy_into(node, &mut v);
                (i, v)
            })
            .collect()
    };
    let before = solved(&s);
    for trust in [0.5f32, 0.2] {
        s.set_trust(Some(trust)).unwrap();
        for _ in 0..50 {
            s.iterate();
        }
        assert_eq!(solved(&s), before, "trust {trust}");
    }
}
