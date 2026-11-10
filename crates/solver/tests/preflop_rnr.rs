//! "Trust the read" in Preflop Lab hero mode (preflop/rnr.rs): anchors,
//! convergence and the readout.

use solver::preflop::equity::EquityTable;
use solver::preflop::{archetypes, PreflopConfig, PreflopSolver};
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(4000))).clone()
}

/// 3-handed 20bb: BTN opens 2.5 or jams, one re-raise level.
fn config() -> PreflopConfig {
    PreflopConfig { leaf_net: None,
        utg_straddle: false,
        positions: vec!["BTN".into(), "SB".into(), "BB".into()],
        stack: 20.0,
        stacks: None,
        posts: vec![0.0, 0.5, 1.0],
        ante: 0.0,
        limp: false,
        open_raises: vec![2.5],
        raise_mults: vec![3.0],
        max_raises: 2,
        add_allin: true,
        allin_threshold: 0.85,
        rake_pct: 0.0,
        rake_cap: 0.0,
        no_flop_no_drop: true,
        realization: "raw".into(),
        call_only_seats: vec![],
        open_raises_by_seat: None,
        fourbet_mults: None,
        fourbet_mults_by_seat: None,
        raise_mults_by_seat: None,
        icm: None,
    }
}

/// Solved table, then BTN hero against the given seats playing archetype
/// profiles (the rest frozen at their solved play).
fn hero_vs(ruled: &[(usize, &str)]) -> PreflopSolver {
    let mut s = PreflopSolver::new(config(), table()).unwrap();
    s.prune = false;
    solve(&mut s, 300);
    let mut profiles = vec![None; 3];
    for &(seat, name) in ruled {
        let stats = archetypes().into_iter().find(|(n, _)| *n == name).unwrap().1;
        profiles[seat] = Some(s.generate_profile(seat, &stats, name).unwrap().0);
    }
    s.set_table(vec![false; 3], profiles).unwrap();
    // the table adapts to the profiles before the hero is picked
    solve(&mut s, 300);
    s.set_hero(Some(0)).unwrap();
    s
}

fn solve(s: &mut PreflopSolver, iterations: u32) {
    for _ in 0..iterations {
        s.iterate();
    }
}

fn hero_nodes(s: &PreflopSolver) -> Vec<usize> {
    (0..s.nodes.len()).filter(|&i| s.nodes[i].kind == 0 && s.nodes[i].actor == 0).collect()
}

#[test]
fn full_trust_is_the_max_exploit_hero_mode_solves() {
    let mut plain = hero_vs(&[(2, "Calling station")]);
    let mut dial = hero_vs(&[(2, "Calling station")]);
    dial.set_trust(Some(1.0)).unwrap();
    solve(&mut plain, 400);
    solve(&mut dial, 400);
    for node in hero_nodes(&plain) {
        let (a, b) = (plain.average_strategy(node), dial.average_strategy(node));
        let d = a.iter().zip(&b).map(|(x, y)| (x - y).abs()).fold(0f32, f32::max);
        assert!(d < 1e-5, "node {node}: hero strategies differ by {d}");
    }
    let (ga, ea) = plain.gaps_and_evs();
    let (gb, eb) = dial.gaps_and_evs();
    assert!((ea[0] - eb[0]).abs() < 1e-5, "hero EV {} vs {}", ea[0], eb[0]);
    assert!((ga[0] - gb[0]).abs() < 1e-5);
    // the free type learned a response of its own meanwhile
    let r = dial.trust_readout().unwrap();
    assert!((r.hero_ev_vs_read - r.hero_ev_vs_mixture).abs() < 1e-6);
    assert!(r.hero_ev_vs_adapting < r.hero_ev_vs_read - 0.01, "{r:?}");
    assert_eq!(r.seats, vec![2]);
    assert!(dial.free_strategy(hero_nodes(&dial)[0]).is_none(), "the hero has no free type");
}

#[test]
fn less_trust_trades_exploit_ev_for_safety_and_converges() {
    let mut s = hero_vs(&[(1, "Maniac"), (2, "Calling station")]);
    let mut readouts = Vec::new();
    for t in [1.0f32, 0.6, 0.0] {
        s.set_trust(Some(t)).unwrap();
        assert_eq!(s.iteration, 0, "a new level restarts the schedule");
        solve(&mut s, 600);
        let (gaps, _) = s.gaps_and_evs();
        let live = s.live_seats();
        assert_eq!(live, vec![true, true, true], "the hero and both free types learn");
        let total: f64 = gaps.iter().zip(&live).filter(|(_, l)| **l).map(|(g, _)| g).sum();
        assert!(total < 0.05, "trust {t}: summed gap {total} bb ({gaps:?})");
        readouts.push(s.trust_readout().unwrap());
    }
    let (full, mid, none) = (&readouts[0], &readouts[1], &readouts[2]);
    assert!(full.hero_ev_vs_read > mid.hero_ev_vs_read && mid.hero_ev_vs_read > none.hero_ev_vs_read - 1e-3,
        "EV vs the read should fall with trust: {readouts:?}");
    assert!(none.hero_ev_vs_adapting > full.hero_ev_vs_adapting + 0.01,
        "less trust should cost less against adapting seats: {readouts:?}");
    // at trust 0 the hero faces only the free types
    assert!((none.hero_ev_vs_mixture - none.hero_ev_vs_adapting).abs() < 1e-6);
    println!("readouts: {readouts:?}");
}

/// Mixing the reach is exact: the hero's EV against the mixture equals the
/// trust-weighted EV over the four type pairs of two independent ruled
/// seats (coupled-deck 3-way pots and side pots included).
#[test]
fn mixed_reach_is_the_expectation_over_independent_types() {
    let mut s = hero_vs(&[(1, "Maniac"), (2, "Calling station")]);
    s.set_trust(Some(0.7)).unwrap();
    solve(&mut s, 200);
    let ev = |a: f32, b: f32| s.hero_ev_with_types(&[a, b]).unwrap();
    for t in [0.7f32, 0.3] {
        let u = 1.0 - t;
        let expected = (t * t) as f64 * ev(1.0, 1.0)
            + (t * u) as f64 * (ev(1.0, 0.0) + ev(0.0, 1.0))
            + (u * u) as f64 * ev(0.0, 0.0);
        let got = ev(t, t);
        assert!((got - expected).abs() < 1e-4, "trust {t}: mixture {got} vs expectation {expected}");
    }
}

#[test]
fn trust_needs_hero_mode_and_a_profile_and_leaves_plain_play_alone() {
    let mut s = PreflopSolver::new(config(), table()).unwrap();
    assert!(s.set_trust(Some(1.5)).is_err());
    s.set_trust(Some(0.5)).unwrap();
    // no hero: the dial is stored but inert, plain CFR runs
    solve(&mut s, 50);
    assert!(s.trust_readout().is_err());
    assert_eq!(s.live_seats(), vec![true, true, true]);
    // hero mode without profiles: still inert
    s.set_hero(Some(0)).unwrap();
    solve(&mut s, 20);
    assert!(s.trust_readout().is_err());
    assert!(s.trust_seats().is_empty());
}

/// Side pots (a short SB) and ICM payouts: the trust game still converges.
#[test]
fn side_pot_and_icm_games_still_solve_with_the_dial() {
    let mut short = config();
    short.stacks = Some(vec![20.0, 6.0, 14.0]);
    let mut icm = short.clone();
    icm.icm = Some(solver::preflop::IcmConfig {
        payouts: vec![50.0, 30.0, 20.0], field: vec![], field_groups: vec![], stack_off: 1.0,
    });
    for (label, cfg) in [("side pots", short), ("ICM", icm)] {
        let mut s = PreflopSolver::new(cfg, table()).unwrap();
        s.prune = false;
        assert!(s.nodes.iter().any(|n| !n.side_pots.is_empty()));
        solve(&mut s, 200);
        let mut profiles = vec![None; 3];
        for (seat, name) in [(1, "Maniac"), (2, "Calling station")] {
            let stats = archetypes().into_iter().find(|(n, _)| *n == name).unwrap().1;
            profiles[seat] = Some(s.generate_profile(seat, &stats, name).unwrap().0);
        }
        s.set_table(vec![false; 3], profiles).unwrap();
        solve(&mut s, 200);
        s.set_hero(Some(0)).unwrap();
        s.set_trust(Some(0.5)).unwrap();
        solve(&mut s, 600);
        let (gaps, _) = s.gaps_and_evs();
        let total: f64 = gaps.iter().sum();
        assert!(total < 0.05, "{label}: summed gap {total} ({gaps:?})");
        let r = s.trust_readout().unwrap();
        // the mixture sits between its pure cases (under ICM free seats that
        // adapt can help the hero: prize equity is shared three ways)
        let (lo, hi) = (r.hero_ev_vs_read.min(r.hero_ev_vs_adapting), r.hero_ev_vs_read.max(r.hero_ev_vs_adapting));
        assert!(r.hero_ev_vs_mixture > lo - 1e-3 && r.hero_ev_vs_mixture < hi + 1e-3, "{label}: {r:?}");
        println!("{label}: {r:?}");
    }
}
