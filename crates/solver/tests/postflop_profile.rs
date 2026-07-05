//! Postflop player profiles: HUD stats compile into Range-style locks over
//! the villain's whole tree (equilibrium distortion, never hand-blind).

use solver::game::Dealt;
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

/// Small but full three-street spot: OOP checks or bets 50%, IP c-bets 50%,
/// one raise size on the flop so raise-facing nodes exist.
fn spot() -> Spot {
    let s = |_p: usize| {
        [
            sizing("50", "100"),
            sizing("50", ""),
            sizing("50", ""),
        ]
    };
    Spot::new(SpotConfig {
        board: "Qs7h2d".to_string(),
        range_oop: "AA,KK,QQ,99,77,55,AQs,KQs,QJs,T9s,87s,AQo,KQo,A5s".to_string(),
        range_ip: "AA,KK,QQ,JJ,TT,88,66,AKs,AQs,KQs,JTs,98s,76s,AKo,AJo".to_string(),
        tree: TreeConfig {
            starting_pot: 10.0,
            effective_stack: 40.0,
            oop: s(0),
            ip: s(1),
            ..Default::default()
        },
    })
    .unwrap()
}

fn solve(iters: usize) -> Solver {
    let mut solver = Solver::new(Arc::new(spot()));
    for _ in 0..iters {
        solver.iterate();
    }
    solver
}

fn stats() -> PostflopStats {
    PostflopStats {
        cbet: [80.0, 60.0, 40.0],
        fold_to_bet: [65.0, 60.0, 55.0],
        raise_bet: 8.0,
        donk: 10.0,
        bet_size: "min".into(),
    }
}

/// Reach-weighted aggregate frequency of the given action kind at the node
/// reached by `path`, for that node's actor.
fn agg_freq(s: &Solver, path: &[PathStep], kind: &str) -> f64 {
    let view = s.node_view(path).unwrap();
    let p = view.player.expect("action node") as usize;
    let (mut num, mut den) = (0f64, 0f64);
    for h in &view.players[p].hands {
        let strat = h.strategy.as_ref().expect("actor node has strategies");
        den += h.reach as f64;
        for (a, f) in strat.iter().enumerate() {
            if view.actions[a].kind == kind {
                num += h.reach as f64 * *f as f64;
            }
        }
    }
    num / den.max(1e-12)
}

#[test]
fn profile_locks_hit_targets_and_expose_the_fish() {
    let mut s = solve(600);

    // hero (OOP) max-exploit EV against the EQUILIBRIUM villain
    let w_ip: Vec<f32> = s.spot.weights[1].clone();
    let w_oop: Vec<f32> = s.spot.weights[0].clone();
    let br0 = s.traverse_br(0, 0, &w_ip, Dealt::default());
    let base_ev: f64 = w_oop.iter().zip(&br0).map(|(&w, &v)| w as f64 * v as f64).sum();

    // manual point-lock first: it must survive profile application
    s.lock_node(
        &[PathStep::Action { index: 0 }],
        LockMode::Freeze,
        "my read".into(),
    )
    .unwrap();

    let summary = s.lock_profile(1, &stats(), Some(1)).unwrap();
    assert!(summary.locked > 10, "should lock many nodes, got {}", summary.locked);
    let row = |label: &str| {
        summary
            .rows
            .iter()
            .find(|r| r.label == label)
            .unwrap_or_else(|| panic!("missing summary row {label}: {:?}", summary.rows))
    };
    // rake hits aggregate targets closely at reached situations
    for (label, target) in [
        ("flop fold vs bet", 65.0),
        ("turn fold vs bet", 60.0),
    ] {
        let r = row(label);
        assert!(
            (r.achieved - target).abs() < 8.0,
            "{label}: target {target} achieved {}",
            r.achieved
        );
    }
    let cb = row("turn bet (initiative)");
    assert!(
        (cb.achieved - 60.0).abs() < 10.0,
        "turn barrel: target 60 achieved {}",
        cb.achieved
    );

    // the manually locked node kept its label (point read > profile)
    assert!(
        s.list_locks().iter().any(|l| l.contains("my read")),
        "manual lock should survive: {:?}",
        s.list_locks()
    );

    // spot-check a live node: IP facing the flop 50% bet folds ~65%
    let f = agg_freq(&s, &[PathStep::Action { index: 1 }], "fold");
    assert!(
        (f - 0.65).abs() < 0.08,
        "IP facing flop bet should fold ~65%, got {f}"
    );

    // hero's max-exploit EV vs the honest-folding villain must beat
    // equilibrium — the whole point of modeling the player
    let br0_after = s.traverse_br(0, 0, &w_ip, Dealt::default());
    let ev_after: f64 =
        w_oop.iter().zip(&br0_after).map(|(&w, &v)| w as f64 * v as f64).sum();
    assert!(
        ev_after > base_ev + 0.1,
        "exploit EV should grow vs a 65% folder: {base_ev:.3} -> {ev_after:.3}"
    );

    // idempotent re-apply: same lock count, no compounding
    let again = s.lock_profile(1, &stats(), Some(1)).unwrap();
    assert_eq!(summary.locked, again.locked);
    for (a, b) in summary.rows.iter().zip(again.rows.iter()) {
        assert!(
            (a.achieved - b.achieved).abs() < 0.5,
            "re-apply drifted: {} {} -> {}",
            a.label,
            a.achieved,
            b.achieved
        );
    }

    // clear removes profile locks but not the manual one
    let cleared = s.clear_profile_locks();
    assert_eq!(cleared, again.locked);
    assert_eq!(s.list_locks().len(), 1, "manual lock remains");
}
