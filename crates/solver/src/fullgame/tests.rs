//! GPU tests: they need CUDA and run with `--features gpu`.
use super::*;
use crate::parse_sizes;

fn preflop(stack: f64) -> PreflopConfig {
    serde_json::from_value(serde_json::json!({
        "positions": ["SB", "BB"], "stack": stack, "posts": [0.5, 1.0],
        "limp": true, "open_raises": [3.0], "raise_mults": [3.0], "max_raises": 2,
        "add_allin": true, "rake_pct": 5.0, "rake_cap": 3.0, "realization": "balanced"
    }))
    .unwrap()
}

fn sizing(bet: &str) -> [StreetSizing; 3] {
    let s = StreetSizing { bet: parse_sizes(bet).unwrap(), raise: vec![], donk: vec![] };
    [s.clone(), s.clone(), s]
}

fn game(bet: &str, support: Option<SupportSeed>) -> FullGame {
    game_with(bet, support, false)
}

fn game_with(bet: &str, support: Option<SupportSeed>, f32_state: bool) -> FullGame {
    game_parked(bet, support, f32_state, None)
}

fn game_parked(bet: &str, support: Option<SupportSeed>, f32_state: bool, resident_flops: Option<usize>) -> FullGame {
    let config = FullGameConfig {
        preflop: preflop(20.0),
        // Rainbow (no flop symmetry) and two-tone (one suit swap).
        flops: vec![("Kh7d2c".into(), 2.0), ("Ks9s4d".into(), 1.0)],
        oop: if bet.is_empty() { Default::default() } else { sizing(bet) },
        ip: if bet.is_empty() { Default::default() } else { sizing(bet) },
        max_raises: 0,
        allin_threshold: 0.85,
        add_allin: false,
        f32_state,
        resident_flops,
        support,
    };
    FullGame::build(config, &mut |m| println!("{m}")).expect("test requires CUDA")
}

/// Class-symmetric pseudo-random reaches, as preflop strategies produce.
fn reaches(seed: usize) -> [Vec<f64>; 2] {
    std::array::from_fn(|p| {
        (0..N).map(|c| ((class_of_combo(c) * 37 + p * 11 + seed) % 23) as f64 / 23.0).collect()
    })
}

#[test]
fn checkdown_continuations_match_pair_tables() {
    // With no postflop bets every continuation is a pure check-down, so its
    // values must equal the panel pair tables' equity values exactly: this
    // pins the chance weights, rake and half-pot utility conversion.
    let mut g = game("", None);
    let (node, net, inv) = g.nodes.iter().enumerate()
        .find_map(|(i, n)| match n { Node::Flop { net, inv, .. } => Some((i, *net, *inv)), _ => None })
        .unwrap();
    let r = reaches(3);
    let mut worst = 0f64;
    for p in 0..2 {
        let gpu = g.cfr(p, node, &r, 1).unwrap();
        let e = PairTables::apply(&g.tables.eq, &r[1 - p]);
        let m = PairTables::apply(&g.tables.mass, &r[1 - p]);
        for c in 0..N {
            let expect = net * e[c] - inv[p] * m[c];
            worst = worst.max((gpu[c] - expect).abs() / (1.0 + expect.abs()));
        }
    }
    println!("check-down max relative error {worst:e}");
    assert!(worst < 2e-4, "check-down mismatch {worst}");
}

#[test]
fn outside_support_pairs_check_down() {
    // A leaf without continuations (no baseline support) settles every pair
    // by check-down, which must agree with the check-down continuations.
    let mut g = game("", None);
    let (node, leaf, net, inv) = g.nodes.iter().enumerate()
        .find_map(|(i, n)| match n { Node::Flop { leaf, net, inv } => Some((i, *leaf, *net, *inv)), _ => None })
        .unwrap();
    let r = reaches(5);
    let full = g.cfr(0, node, &r, 1).unwrap();
    g.leaves[leaf].conts.clear();
    let outside = g.cfr(0, node, &r, 2).unwrap();
    let e = PairTables::apply(&g.tables.eq, &r[1]);
    let m = PairTables::apply(&g.tables.mass, &r[1]);
    for c in 0..N {
        let expect = net * e[c] - inv[0] * m[c];
        assert!((outside[c] - expect).abs() < 1e-9 * (1.0 + expect.abs()));
        assert!((full[c] - expect).abs() < 2e-4 * (1.0 + expect.abs()));
    }
}

#[test]
fn small_full_game_converges_and_conserves_chips() {
    let mut g = game("50", None);
    let first = { g.iterate().unwrap(); g.evaluate().unwrap() };
    for _ in 1..300 {
        g.iterate().unwrap();
    }
    let last = g.evaluate().unwrap();
    println!("iteration 1: {first:?}\niteration 300: {last:?}");
    assert!(last.gaps.iter().all(|&x| x > -1e-6));
    assert!(last.gap_total < first.gap_total / 10.0);
    assert!(last.gap_total < 0.05, "gap {}", last.gap_total);
    // Zero-sum apart from rake, which is at most the 3bb cap.
    let total = last.evs[0] + last.evs[1];
    assert!(total <= 1e-6 && total >= -3.0, "ev sum {total}");
    assert_eq!(last.outside_support, 0.0);
}

#[test]
fn seeded_support_reports_outside_play() {
    let mut g = game("50", Some(SupportSeed { iterations: 200, min_freq: 0.05, expand_at: vec![] }));
    assert!(g.leaves.iter().any(|l| l.support[0].iter().any(|&x| !x)));
    for _ in 0..50 {
        g.iterate().unwrap();
    }
    let e = g.evaluate().unwrap();
    println!("{e:?}");
    assert!(e.outside_support > 0.0 && e.outside_support < 1.0);
    assert!(e.gaps.iter().all(|&x| x > -1e-6));
    // Growing the support to the game's own ranges covers its play again.
    let rebuilt = g.expand_support(0.05, &mut |m| println!("{m}")).unwrap();
    assert!(!rebuilt.is_empty());
    for _ in 0..50 {
        g.iterate().unwrap();
    }
    let after = g.evaluate().unwrap();
    println!("{after:?}");
    assert!(after.outside_support < e.outside_support, "{} >= {}", after.outside_support, e.outside_support);
}

#[test]
fn sixteen_bit_state_matches_f32() {
    // Same game, learning state in 16 bits versus f32: both converge and
    // agree on values and the SB's first decision.
    let run = |f32_state: bool| {
        let mut g = game_with("50", None, f32_state);
        for _ in 0..300 {
            g.iterate().unwrap();
        }
        let e = g.evaluate().unwrap();
        let (_, _, root) = g.strategy(&[]).unwrap();
        (e, root, g.device_bytes())
    };
    let (q, q_root, q_bytes) = run(false);
    let (f, f_root, f_bytes) = run(true);
    println!("16-bit {q:?} {q_bytes} B\nf32    {f:?} {f_bytes} B");
    assert!(q.gap_total < 0.01 && f.gap_total < 0.01);
    for s in 0..2 {
        assert!((q.evs[s] - f.evs[s]).abs() < 0.01, "seat {s}: {} vs {}", q.evs[s], f.evs[s]);
    }
    let worst = q_root.iter().zip(&f_root).map(|(a, b)| (a - b).abs()).fold(0.0, f64::max);
    assert!(worst < 0.1, "root strategy differs by {worst}");
    assert!(q_bytes < f_bytes);
}
#[test]
fn parked_continuations_match_resident_exactly() {
    // Streaming state through the shared slot changes where it lives, not
    // the arithmetic: results must be bit-identical.
    let run = |resident: Option<usize>| {
        let mut g = game_parked("50", None, false, resident);
        for _ in 0..40 {
            g.iterate().unwrap();
        }
        (g.evaluate().unwrap(), g.strategy(&[]).unwrap().2, g.parked())
    };
    let (a, a_root, a_parked) = run(None);
    let (b, b_root, b_parked) = run(Some(1));
    println!("resident {a:?}\nparked   {b:?} ({b_parked} parked)");
    assert_eq!(a_parked, 0);
    assert!(b_parked > 0);
    assert_eq!(a.evs, b.evs);
    assert_eq!(a.best_responses, b.best_responses);
    assert_eq!(a_root, b_root);
}
#[test]
fn flop_export_reproduces_gpu_values_on_the_cpu() {
    // Browse reads a continuation through a CPU solver: decoded state must
    // give the same average-strategy values as the GPU evaluation.
    let mut g = game_parked("50", None, false, Some(1));
    for _ in 0..30 {
        g.iterate().unwrap();
    }
    let view = g.node_view(&[]).unwrap();
    assert_eq!(view["kind"], "action");
    for (leaf, flop) in [(0usize, 0usize), (0, 1)] {
        let host = g.flop_solver(leaf, flop).unwrap();
        let reach: [Vec<f32>; 2] = std::array::from_fn(|p| host.spot.weights[p].clone());
        let gpu = {
            let FullGame { leaves, dev, .. } = &mut g;
            leaves[leaf].conts[flop].gpu.evaluate_shared(&mut dev.scratch, &mut dev.state, [&reach[0], &reach[1]]).unwrap()
        };
        for p in 0..2 {
            let cpu = host.traverse_avg(0, p, &reach[1 - p], crate::game::Dealt::default());
            let scale = gpu[p][1].iter().map(|v| v.abs()).fold(1e-9f32, f32::max);
            let worst = cpu.iter().zip(&gpu[p][1]).map(|(a, b)| (a - b).abs()).fold(0f32, f32::max) / scale;
            println!("leaf {leaf} flop {flop} player {p}: max relative difference {worst:e}");
            assert!(worst < 2e-3, "{worst}");
        }
    }
}