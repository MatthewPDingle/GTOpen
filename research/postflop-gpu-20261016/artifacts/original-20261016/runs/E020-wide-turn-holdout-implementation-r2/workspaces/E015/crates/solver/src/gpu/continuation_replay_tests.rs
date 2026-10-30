//! Diagnostic only: replay a single update from materialized compact state.
//! This leaves the prior independent-trajectory qualification gates unchanged.
use super::*;
use crate::{game::Dealt, parse_sizes, SpotConfig, StreetSizing, TreeConfig};

fn data(s: &Store) -> &[f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_slice()
}

fn weights(sp: &Spot, p: usize, t: u32) -> Vec<f32> {
    sp.hands[p]
        .iter()
        .map(|h| {
            let c = crate::preflop::equity::class_index(h.c1 / 4, h.c2 / 4, h.c1 % 4 == h.c2 % 4);
            0.02 + ((c * 7 + t as usize * 3 + p * 11) % 23) as f32 / 23.
        })
        .collect()
}

fn maximum(a: &[f32], b: &[f32]) -> f32 {
    assert_eq!(a.len(), b.len());
    assert!(a.iter().chain(b).all(|x| x.is_finite()));
    a.iter()
        .zip(b)
        .map(|(a, b)| (a - b).abs())
        .fold(0., f32::max)
}

// Test-only injection into the fully explicit bridge. Use its normal arena
// layout upload, retain its stream/context and verify all arrays on readback.
fn reset_explicit(g: &mut SymmetricContinuationGpu, source: &Solver, check: &mut Solver) {
    assert!(!g.future_card_orbits);
    let gpu = &mut g.gpu;
    gpu.stream.synchronize().unwrap();
    for p in 0..2 {
        gpu.d_regrets[p] = gpu.arena_layout[p]
            .upload(&gpu.stream, source, p, 0, gpu.h_staging.as_mut_slice())
            .unwrap();
        gpu.d_strat[p] = gpu.arena_layout[p]
            .upload(&gpu.stream, source, p, 1, gpu.h_staging.as_mut_slice())
            .unwrap();
    }
    gpu.iteration = source.iteration;
    g.sync_to_cpu(check).unwrap();
    for (a, b) in source
        .regrets
        .iter()
        .chain(&source.strat)
        .zip(check.regrets.iter().chain(&check.strat))
    {
        assert_eq!(data(a).len(), data(b).len());
        assert!(
            data(a)
                .iter()
                .zip(data(b))
                .all(|(a, b)| a.to_bits() == b.to_bits()),
            "Explicit replay did not start from identical materialized state"
        );
    }
}

#[test]
fn identical_state_gpu_replay_separates_local_updates_from_trajectory_drift() {
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
            let mut compact_host = Solver::new(sp.clone());
            compact_host.algo = Algorithm::CfrPlus;
            compact_host.use_isomorphism = true;
            let mut explicit_host = Solver::new(sp.clone());
            explicit_host.algo = Algorithm::CfrPlus;
            explicit_host.use_isomorphism = false;
            let plan = super::super::plan::GpuPlan::build(&sp, true);
            let budget = plan.staging_bytes()
                + plan.arena_elements.iter().sum::<usize>() as u64 * 8
                + 512 * 1024 * 1024
                + sp.tree.nodes.len() as u64 * 4;
            let mut compact =
                SymmetricContinuationGpu::new_with_budget(&compact_host, budget).unwrap();
            let mut replay =
                SymmetricContinuationGpu::new_explicit_reference(&explicit_host, u64::MAX).unwrap();
            for t in 1..=100 {
                let mut pair: [Vec<f32>; 2] = std::array::from_fn(|p| {
                    if mode == "abrupt_pair" {
                        weights(&sp, p, t)
                    } else {
                        let (a, b) = (weights(&sp, p, 31), weights(&sp, p, 47));
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
                    let sampled = [1, 2, 16, 17, 50, 100].contains(&t);
                    if sampled {
                        compact.sync_to_cpu(&mut compact_host).unwrap();
                        reset_explicit(&mut replay, &compact_host, &mut explicit_host);
                    }
                    let a = compact.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                    if !sampled {
                        continue;
                    }
                    let b = replay.sweep(p, t, &pair[p], &pair[1 - p]).unwrap();
                    let mass = pair[1 - p].iter().sum::<f32>();
                    let cfv = maximum(&a, &b) / mass.max(1.);
                    if mass == 0. {
                        assert!(a.iter().chain(&b).all(|x| *x == 0.));
                    }
                    compact.sync_to_cpu(&mut compact_host).unwrap();
                    replay.sync_to_cpu(&mut explicit_host).unwrap();
                    let root = &sp.tree.nodes[0];
                    let root_difference = maximum(
                        &compact_host.average_strategy(0, root),
                        &explicit_host.average_strategy(0, root),
                    );
                    let mut value_difference = 0f32;
                    // Both states evaluated through the SAME full CPU traversal.
                    compact_host.use_isomorphism = false;
                    for q in 0..2 {
                        let opp = weights(&sp, 1 - q, 777);
                        let denom = opp.iter().sum::<f32>();
                        for br in [false, true] {
                            let eval = |s: &Solver| {
                                if br {
                                    s.traverse_br(0, q, &opp, Dealt::default())
                                } else {
                                    s.traverse_avg(0, q, &opp, Dealt::default())
                                }
                            };
                            value_difference = value_difference
                                .max(maximum(&eval(&compact_host), &eval(&explicit_host)) / denom);
                        }
                    }
                    compact_host.use_isomorphism = true;
                    let passed = cfv < 0.002 && root_difference < 0.002 && value_difference < 0.002;
                    println!(
                        "GPU_REPLAY {}",
                        serde_json::json!({"mode":mode,"board":board,"iteration":t,"player":p,
                        "prestate_all_arrays_bitwise_equal":true,"same_state_cfv_per_mass":cfv,
                        "post_root_difference":root_difference,"post_avg_br_difference_per_mass":value_difference,
                        "passed":passed})
                    );
                    if !passed {
                        failures.push((mode, board, t, p));
                    }
                }
            }
        }
    }
    assert!(
        failures.is_empty(),
        "Same-state replay failures: {failures:?}"
    );
}
