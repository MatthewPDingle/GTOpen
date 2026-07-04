//! Preflop solver validation: CFR vs an independent push/fold oracle,
//! structural sanity of the action grammar, and model invariants.

use solver::preflop::equity::{class_prob, EquityTable, NUM_CLASSES};
use solver::preflop::{PreflopConfig, PreflopSolver};
use std::sync::{Arc, OnceLock};

fn table() -> Arc<EquityTable> {
    static T: OnceLock<Arc<EquityTable>> = OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(4000))).clone()
}

fn hu_push_fold_config(stack: f64) -> PreflopConfig {
    PreflopConfig {
        positions: vec!["SB".into(), "BB".into()],
        stack,
        posts: vec![0.5, 1.0],
        ante: 0.0,
        limp: false,
        open_raises: vec![],
        raise_mults: vec![],
        max_raises: 1,
        add_allin: true,
        allin_threshold: 0.85,
        rake_pct: 0.0,
        rake_cap: 0.0,
        no_flop_no_drop: true,
        realization: "raw".into(),
    }
}

/// Independent Nash oracle for heads-up jam/fold at `stack` bb, using the
/// SAME equity table and the same mean-field assumptions as the solver.
/// Fictitious play (best response vs the opponent's AVERAGED strategy),
/// which converges in two-player zero-sum games — pure alternating best
/// responses cycle around the indifference boundary. Returns the averaged
/// (jam, call) frequencies plus each class's final decision margin in bb
/// against the averaged opponent strategy.
fn push_fold_oracle(eq: &EquityTable, stack: f64) -> (Vec<f32>, Vec<f32>, Vec<f64>, Vec<f64>) {
    let prob: Vec<f64> = (0..NUM_CLASSES).map(|h| class_prob(h) as f64).collect();
    let total: f64 = prob.iter().sum();
    let mut jam_mix = vec![1f64; NUM_CLASSES];
    let mut call_mix = vec![0f64; NUM_CLASSES];
    let (mut jam_margin, mut call_margin) = (vec![0f64; NUM_CLASSES], vec![0f64; NUM_CLASSES]);
    for t in 1..=4000u32 {
        // BB best response vs averaged jam range: call risks (stack-1) more
        // to win 2*stack total; folding loses the posted blind.
        let mut dist: Vec<f32> = (0..NUM_CLASSES)
            .map(|j| (prob[j] * jam_mix[j]) as f32)
            .collect();
        let s: f32 = dist.iter().sum();
        if s > 0.0 {
            dist.iter_mut().for_each(|d| *d /= s);
        }
        let mut call_br = vec![0f64; NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let e = eq.eq_vs_dist(h, &dist) as f64;
            call_margin[h] = (e * 2.0 * stack - stack) - (-1.0);
            call_br[h] = if call_margin[h] > 0.0 { 1.0 } else { 0.0 };
        }
        // SB best response vs averaged call range.
        let p_call: f64 = (0..NUM_CLASSES)
            .map(|j| prob[j] * call_mix[j])
            .sum::<f64>()
            / total;
        let mut cdist: Vec<f32> = (0..NUM_CLASSES)
            .map(|j| (prob[j] * call_mix[j]) as f32)
            .collect();
        let cs: f32 = cdist.iter().sum();
        if cs > 0.0 {
            cdist.iter_mut().for_each(|d| *d /= cs);
        }
        let mut jam_br = vec![0f64; NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            let e = eq.eq_vs_dist(h, &cdist) as f64;
            let ev_jam = (1.0 - p_call) * 1.0 + p_call * (e * 2.0 * stack - stack);
            jam_margin[h] = ev_jam - (-0.5);
            jam_br[h] = if jam_margin[h] > 0.0 { 1.0 } else { 0.0 };
        }
        // fictitious-play averaging
        let w = 1.0 / t as f64;
        for h in 0..NUM_CLASSES {
            call_mix[h] += w * (call_br[h] - call_mix[h]);
            jam_mix[h] += w * (jam_br[h] - jam_mix[h]);
        }
    }
    (
        jam_mix.iter().map(|&x| x as f32).collect(),
        call_mix.iter().map(|&x| x as f32).collect(),
        jam_margin,
        call_margin,
    )
}

/// CFR must reproduce the oracle's push/fold equilibrium for every class
/// whose decision margin is clear (mixing at the indifference boundary is
/// expected and excluded).
#[test]
fn hu_push_fold_matches_oracle() {
    let eq = table();
    let stack = 10.0;
    let mut s = PreflopSolver::new(hu_push_fold_config(stack), eq.clone()).unwrap();
    // tree: SB [Fold, All-in] -> BB [Fold, Call]
    assert_eq!(s.nodes[0].actions.len(), 2, "SB should have fold/jam");
    for _ in 0..4000 {
        s.iterate();
    }

    let (jam, call, jam_margin, call_margin) = push_fold_oracle(&eq, stack);
    let sb = s.average_strategy(0);
    let sb_jam = s.nodes[0]
        .actions
        .iter()
        .position(|a| a.kind == "jam")
        .unwrap();
    let bb_idx = s.child(0, sb_jam);
    let bb = s.average_strategy(bb_idx);
    let bb_call_a = s.nodes[bb_idx]
        .actions
        .iter()
        .position(|a| a.kind == "call")
        .unwrap();
    let sb_jam_a = s.nodes[0]
        .actions
        .iter()
        .position(|a| a.kind == "jam")
        .unwrap();

    let (mut checked, mut skipped) = (0, 0);
    for h in 0..NUM_CLASSES {
        // SB decision
        if jam_margin[h].abs() > 0.10 {
            let f = sb[sb_jam_a * NUM_CLASSES + h];
            let want = jam[h] > 0.5;
            assert!(
                if want { f > 0.85 } else { f < 0.15 },
                "SB class {} ({}): oracle jam={} margin={:.3}bb, CFR jam freq={:.3}",
                h,
                solver::preflop::equity::class_label(h),
                want,
                jam_margin[h],
                f
            );
            checked += 1;
        } else {
            skipped += 1;
        }
        // BB decision
        if call_margin[h].abs() > 0.10 {
            let f = bb[bb_call_a * NUM_CLASSES + h];
            let want = call[h] > 0.5;
            assert!(
                if want { f > 0.85 } else { f < 0.15 },
                "BB class {} ({}): oracle call={} margin={:.3}bb, CFR call freq={:.3}",
                h,
                solver::preflop::equity::class_label(h),
                want,
                call_margin[h],
                f
            );
        }
    }
    assert!(
        checked > 120,
        "oracle should give clear answers for most classes, got {checked} (skipped {skipped})"
    );

    // sanity anchors: at 10bb, AA always jams and always calls; 72o folds to a jam
    let aa = solver::preflop::equity::class_index(12, 12, false);
    let seven_deuce = solver::preflop::equity::class_index(5, 0, false);
    assert!(sb[sb_jam_a * NUM_CLASSES + aa] > 0.99);
    assert!(bb[bb_call_a * NUM_CLASSES + aa] > 0.99);
    assert!(bb[bb_call_a * NUM_CLASSES + seven_deuce] < 0.05);

    // zero-sum (no rake): total EV across players ~ 0
    let evs = s.evs();
    let total: f64 = evs.iter().sum();
    assert!(total.abs() < 0.01, "EVs should sum to ~0, got {total}");

    // convergence: BR gaps small
    let gaps = s.br_gaps();
    for (p, g) in gaps.iter().enumerate() {
        assert!(*g < 0.02, "BR gap for player {p} too big: {g} bb");
    }
}

/// Full grammar: 6-max with limps, an open size and a 3-bet builds a legal
/// tree, converges in the model, and conserves chips (minus rake when on).
#[test]
fn six_max_limp_tree_sanity() {
    let eq = table();
    let cfg = PreflopConfig {
        positions: vec![
            "UTG".into(),
            "HJ".into(),
            "CO".into(),
            "BTN".into(),
            "SB".into(),
            "BB".into(),
        ],
        stack: 100.0,
        posts: vec![0.0, 0.0, 0.0, 0.0, 0.5, 1.0],
        ante: 0.0,
        limp: true,
        open_raises: vec![2.5],
        raise_mults: vec![3.0],
        max_raises: 3,
        add_allin: false,
        allin_threshold: 0.85,
        rake_pct: 0.0,
        rake_cap: 0.0,
        no_flop_no_drop: true,
        realization: "static".into(),
    };
    let mut s = PreflopSolver::new(cfg, eq.clone()).unwrap();
    let action_nodes = s.nodes.iter().filter(|n| n.kind == 0).count();
    assert!(action_nodes > 100, "tree suspiciously small: {action_nodes}");

    // UTG's root actions must include limp (limp=true), a raise and fold
    let kinds: Vec<&str> = s.nodes[0].actions.iter().map(|a| a.kind.as_str()).collect();
    assert!(kinds.contains(&"fold") && kinds.contains(&"call") && kinds.contains(&"raise"));

    for _ in 0..100 {
        s.iterate();
    }
    let evs = s.evs();
    let total: f64 = evs.iter().sum();
    assert!(
        total.abs() < 0.06,
        "chips should be conserved without rake, got sum {total} ({evs:?})"
    );
    let g1: f64 = s.br_gaps().iter().sum();
    for _ in 0..200 {
        s.iterate();
    }
    let g2: f64 = s.br_gaps().iter().sum();
    assert!(g2 < g1, "BR gap should shrink with iterations: {g1} -> {g2}");
}

/// Rake drains EV: with rake on, total EV goes negative (and not absurdly).
#[test]
fn rake_drains_total_ev() {
    let eq = table();
    let mut cfg = hu_push_fold_config(20.0);
    cfg.open_raises = vec![2.5];
    cfg.max_raises = 2;
    cfg.limp = true;
    cfg.rake_pct = 5.0;
    cfg.rake_cap = 3.0;
    cfg.no_flop_no_drop = true;
    let mut s = PreflopSolver::new(cfg, eq).unwrap();
    for _ in 0..400 {
        s.iterate();
    }
    let total: f64 = s.evs().iter().sum();
    assert!(total < 0.0, "rake should make the game net negative, got {total}");
    assert!(total > -1.0, "rake drain implausibly large: {total}");
}

/// The size estimator must agree exactly with what the builder builds —
/// they share the enumeration logic, and this pins that they stay shared.
#[test]
fn estimate_matches_build() {
    let eq = table();
    let mut cfgs = vec![hu_push_fold_config(10.0)];
    let mut six = hu_push_fold_config(100.0);
    six.positions = vec![
        "UTG".into(), "HJ".into(), "CO".into(), "BTN".into(), "SB".into(), "BB".into(),
    ];
    six.posts = vec![0.0, 0.0, 0.0, 0.0, 0.5, 1.0];
    six.limp = true;
    six.open_raises = vec![2.5];
    six.raise_mults = vec![3.0];
    six.max_raises = 2;
    six.add_allin = false;
    cfgs.push(six);
    for cfg in cfgs {
        let est = solver::preflop::estimate_tree(&cfg).unwrap();
        let s = PreflopSolver::new(cfg, eq.clone()).unwrap();
        assert!(!est.truncated);
        assert_eq!(est.nodes as usize, s.nodes.len(), "node count mismatch");
        assert_eq!(
            est.action_nodes as usize,
            s.nodes.iter().filter(|n| n.kind == 0).count(),
            "action node mismatch"
        );
        assert!((est.arena_len as f64 * 8.0 / 1e6 - s.arena_mb()).abs() < 1e-6);
    }
}
