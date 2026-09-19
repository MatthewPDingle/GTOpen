//! Additional diagnostics only. Does not replace continuation_symmetry's
//! deliberately failing abrupt independent-input regression.
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
fn maximum(a: &[f32], b: &[f32]) -> f32 {
    assert_eq!(a.len(), b.len());
    assert!(
        a.iter().chain(b).all(|x| x.is_finite()),
        "non-finite comparison input"
    );
    a.iter()
        .zip(b)
        .map(|(x, y)| (x - y).abs())
        .fold(0., f32::max)
}

#[test]
fn coherent_range_pairs_compare_full_and_compact_without_replacing_old_gate() {
    let mut failures = vec![];
    for mode in ["abrupt_pair", "smooth_pair"] {
        for board in ["KsQs2d", "KsQs2s", "KsQh2d"] {
            let sizing = StreetSizing {
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
                        oop: [sizing.clone(), sizing.clone(), sizing.clone()],
                        ip: [sizing.clone(), sizing.clone(), sizing],
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
            let mut replay = Solver::new(sp.clone());
            replay.algo = Algorithm::CfrPlus;
            let plan = GpuPlan::build(&sp, true);
            let budget = plan.staging_bytes()
                + plan.arena_elements.iter().sum::<usize>() as u64 * 8
                + 512 * 1024 * 1024
                + sp.tree.nodes.len() as u64 * 4;
            let mut compact = SymmetricContinuationGpu::new_with_budget(&small, budget).unwrap();
            let mut explicit =
                SymmetricContinuationGpu::new_explicit_reference(&large, u64::MAX).unwrap();
            let (mut same_state, mut immediate_root, mut trajectory) = (0f32, 0f32, 0f32);
            for t in 1..=100 {
                // ONE pair per iteration, used consistently in both passes.
                let mut pair: [Vec<f32>; 2] = std::array::from_fn(|p| {
                    if mode == "abrupt_pair" {
                        weights(&sp, p, t)
                    } else {
                        let a = weights(&sp, p, 31);
                        let b = weights(&sp, p, 47);
                        let alpha = (t - 1) as f32 / 99.;
                        a.iter()
                            .zip(&b)
                            .map(|(a, b)| a * (1. - alpha) + b * alpha)
                            .collect()
                    }
                });
                if mode == "abrupt_pair" && t % 17 == 0 {
                    pair[(t / 17) as usize % 2].fill(0.);
                }
                for p in 0..2 {
                    replay.use_isomorphism = true;
                    compact.sync_to_cpu(&mut replay).unwrap();
                    replay.use_isomorphism = false;
                    let a = replay
                        .research_continuation_sweep(p, t, &pair[p], &pair[1 - p])
                        .unwrap();
                    let b = compact.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                    let c = explicit.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                    let mass = pair[1 - p].iter().sum::<f32>();
                    if mass == 0. {
                        assert!(a.iter().chain(&b).chain(&c).all(|x| *x == 0.));
                    }
                    same_state = same_state.max(maximum(&a, &b) / mass.max(1.));
                    trajectory = trajectory.max(maximum(&b, &c) / mass.max(1.));
                    if p == 0 {
                        compact.sync_to_cpu(&mut small).unwrap();
                        immediate_root = immediate_root.max(maximum(
                            &replay.average_strategy(0, &sp.tree.nodes[0]),
                            &small.average_strategy(0, &sp.tree.nodes[0]),
                        ));
                    }
                }
            }
            compact.sync_to_cpu(&mut small).unwrap();
            explicit.sync_to_cpu(&mut large).unwrap();
            let drift = maximum(
                &small.average_strategy(0, &sp.tree.nodes[0]),
                &large.average_strategy(0, &sp.tree.nodes[0]),
            );
            let (mut evaluation, mut same_policy) = (0f32, 0f32);
            for p in 0..2 {
                let opp = weights(&sp, 1 - p, 777);
                let mass = opp.iter().sum::<f32>();
                for br in [false, true] {
                    let eval = |s: &Solver| {
                        if br {
                            s.traverse_br(0, p, &opp, Dealt::default())
                        } else {
                            s.traverse_avg(0, p, &opp, Dealt::default())
                        }
                    };
                    let quotient = eval(&small);
                    let full = eval(&large);
                    evaluation = evaluation.max(maximum(&quotient, &full) / mass);
                    small.use_isomorphism = false;
                    same_policy = same_policy.max(maximum(&quotient, &eval(&small)) / mass);
                    small.use_isomorphism = true;
                }
            }
            let passed = same_state < 0.002
                && immediate_root < 0.002
                && drift < 0.01
                && evaluation < 0.002
                && same_policy < 0.0001;
            println!(
                "COHERENT {}",
                serde_json::json!({"mode":mode,"board":board,"passed":passed,
                "same_state_cfv":same_state,"immediate_root":immediate_root,"trajectory_cfv":trajectory,
                "root_drift":drift,"avg_br_difference":evaluation,"same_policy_quotient_difference":same_policy})
            );
            if !passed {
                failures.push((mode, board));
            }
        }
    }
    assert!(
        failures.is_empty(),
        "Additional coherent-pair diagnostic gates failed: {failures:?}"
    );
}
