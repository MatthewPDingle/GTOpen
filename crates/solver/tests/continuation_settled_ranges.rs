//! Diagnostic continuation of the failed coherent-range trajectories.
//! Fixed tails do not replace or relax the original changing-range gates.
#![cfg(feature = "preflop-research")]
use solver::{
    game::Dealt,
    gpu::{plan::GpuPlan, SymmetricContinuationGpu},
};
use solver::{parse_sizes, Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::sync::Arc;

fn weights(sp: &Spot, p: usize, t: u32) -> Vec<f32> {
    sp.hands[p]
        .iter()
        .map(|h| {
            let c = solver::preflop::equity::class_index(h.c1 / 4, h.c2 / 4, h.c1 % 4 == h.c2 % 4);
            0.02 + ((c * 7 + t as usize * 3 + p * 11) % 23) as f32 / 23.
        })
        .collect()
}

fn maximum(a: &[f32], b: &[f32]) -> f64 {
    assert_eq!(a.len(), b.len());
    assert!(a.iter().chain(b).all(|x| x.is_finite()));
    a.iter()
        .zip(b)
        .map(|(a, b)| (*a as f64 - *b as f64).abs())
        .fold(0., f64::max)
}

fn joint_mass(sp: &Spot, pair: &[Vec<f32>; 2]) -> f64 {
    let mut z = 0.;
    for (i, a) in sp.hands[0].iter().enumerate() {
        for (j, b) in sp.hands[1].iter().enumerate() {
            if a.mask & b.mask == 0 {
                z += pair[0][i] as f64 * pair[1][j] as f64;
            }
        }
    }
    assert!(z.is_finite() && z > 0.);
    z
}

#[test]
fn fixed_tail_measures_convergence_without_replacing_changing_range_gates() {
    let mut failures = vec![];
    for mode in ["abrupt_pair", "smooth_pair"] {
        for board in ["KsQs2d", "KsQs2s", "KsQh2d"] {
            let z = StreetSizing {
                bet: parse_sizes("50").unwrap(),
                raise: vec![],
                donk: parse_sizes("50").unwrap(),
            };
            let sp = Arc::new(
                Spot::new(SpotConfig {
                    board: board.into(),
                    range_oop: "AA,KK,AQs,KQo,88,76s".into(),
                    range_ip: "AA,QQ,AKo,QJs,99".into(),
                    tree: TreeConfig {
                        starting_pot: 39.5,
                        effective_stack: 80.,
                        rake_pct: 0.04,
                        rake_cap: 6.,
                        max_raises: 0,
                        oop: [z.clone(), z.clone(), z.clone()],
                        ip: [z.clone(), z.clone(), z],
                        ..Default::default()
                    },
                })
                .unwrap(),
            );
            let mut small = Solver::new(sp.clone());
            small.algo = Algorithm::CfrPlus;
            small.use_isomorphism = true;
            let mut large = Solver::new(sp.clone());
            large.algo = Algorithm::CfrPlus;
            large.use_isomorphism = false;
            let plan = GpuPlan::build(&sp, true);
            let budget = plan.staging_bytes()
                + plan.arena_elements.iter().sum::<usize>() as u64 * 8
                + 512 * 1024 * 1024
                + sp.tree.nodes.len() as u64 * 4;
            let mut compact = SymmetricContinuationGpu::new_with_budget(&small, budget).unwrap();
            let mut explicit =
                SymmetricContinuationGpu::new_explicit_reference(&large, u64::MAX).unwrap();
            for t in 1..=2000 {
                let source_t = t.min(100);
                let mut pair: [Vec<f32>; 2] = std::array::from_fn(|p| {
                    if mode == "abrupt_pair" {
                        weights(&sp, p, source_t)
                    } else {
                        let (a, b) = (weights(&sp, p, 31), weights(&sp, p, 47));
                        let alpha = (source_t - 1) as f32 / 99.;
                        a.iter()
                            .zip(&b)
                            .map(|(a, b)| a * (1. - alpha) + b * alpha)
                            .collect()
                    }
                });
                if mode == "abrupt_pair" && t <= 100 && t % 17 == 0 {
                    pair[(t / 17) as usize % 2].fill(0.);
                }
                for p in 0..2 {
                    compact.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                    explicit.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                }
                if ![100, 500, 1000, 2000].contains(&t) {
                    continue;
                }
                compact.sync_to_cpu(&mut small).unwrap();
                explicit.sync_to_cpu(&mut large).unwrap();
                // Use identical full CPU evaluation paths for both saved states.
                small.use_isomorphism = false;
                let root_difference = maximum(
                    &small.average_strategy(0, &sp.tree.nodes[0]),
                    &large.average_strategy(0, &sp.tree.nodes[0]),
                );
                let mass = joint_mass(&sp, &pair);
                let mut ev = [[0f64; 2]; 2];
                let mut gaps = [[0f64; 2]; 2];
                let mut hand_difference = 0f64;
                let mut old_probe_difference = 0f64;
                for p in 0..2 {
                    let mut values = vec![];
                    for (j, s) in [&small, &large].iter().enumerate() {
                        let a = s.traverse_avg(0, p, &pair[1 - p], Dealt::default());
                        let b = s.traverse_br(0, p, &pair[1 - p], Dealt::default());
                        assert!(a.iter().chain(&b).all(|x| x.is_finite()));
                        ev[j][p] = a
                            .iter()
                            .zip(&pair[p])
                            .map(|(v, w)| *v as f64 * *w as f64)
                            .sum::<f64>()
                            / mass;
                        gaps[j][p] = a
                            .iter()
                            .zip(&b)
                            .zip(&pair[p])
                            .map(|((a, b), w)| (*b as f64 - *a as f64) * *w as f64)
                            .sum::<f64>()
                            / mass;
                        values.push((a, b));
                    }
                    let denom = pair[1 - p].iter().map(|x| *x as f64).sum::<f64>();
                    hand_difference = hand_difference
                        .max(maximum(&values[0].0, &values[1].0) / denom)
                        .max(maximum(&values[0].1, &values[1].1) / denom);
                    // Retain the old off-distribution probe as a separate measure.
                    let probe = weights(&sp, 1 - p, 777);
                    let denom = probe.iter().map(|x| *x as f64).sum::<f64>();
                    for br in [false, true] {
                        let eval = |s: &Solver| {
                            if br {
                                s.traverse_br(0, p, &probe, Dealt::default())
                            } else {
                                s.traverse_avg(0, p, &probe, Dealt::default())
                            }
                        };
                        old_probe_difference =
                            old_probe_difference.max(maximum(&eval(&small), &eval(&large)) / denom);
                    }
                }
                small.use_isomorphism = true;
                let total = [gaps[0].iter().sum::<f64>(), gaps[1].iter().sum::<f64>()];
                let ev_difference = ev[0]
                    .iter()
                    .zip(ev[1])
                    .map(|(a, b)| (a - b).abs())
                    .fold(0., f64::max);
                let passed = total.iter().all(|g| *g >= -1e-6 && *g < 0.01)
                    && gaps.iter().flatten().all(|g| *g >= -1e-6)
                    && ev_difference < 0.002
                    && root_difference < 0.01
                    && hand_difference < 0.002;
                println!(
                    "SETTLED {}",
                    serde_json::json!({"mode":mode,"board":board,"iteration":t,
                    "normalizer":mass,"centered_ev":ev,"gaps":gaps,"combined_gap":total,
                    "max_ev_difference_bb":ev_difference,"root_difference":root_difference,
                    "current_range_avg_br_difference_per_mass":hand_difference,
                    "old_probe_avg_br_difference_per_mass":old_probe_difference,"settled_diagnostic_passed":passed})
                );
                if t == 2000 && !passed {
                    failures.push((mode, board));
                }
            }
        }
    }
    assert!(
        failures.is_empty(),
        "Fixed-tail diagnostic failures: {failures:?}"
    );
}
