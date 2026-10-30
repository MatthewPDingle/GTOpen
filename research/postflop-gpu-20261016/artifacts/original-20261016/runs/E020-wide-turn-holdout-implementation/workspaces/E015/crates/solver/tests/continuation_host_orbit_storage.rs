//! Storage-only prototype: retain explicit GPU traversal and restore every bit.
#![cfg(feature = "preflop-research")]
use solver::{
    gpu::{plan::GpuPlan, GpuSolver, SymmetricContinuationGpu},
    store::Store,
};
use solver::{parse_sizes, Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::{sync::Arc, time::Instant};

fn data(s: &Store) -> &[f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_slice()
}
fn data_mut(s: &mut Store) -> &mut [f32] {
    let Store::F32(a) = s else {
        panic!("F32 required")
    };
    a.as_mut_slice()
}
fn weights(sp: &Spot, p: usize, t: u32) -> Vec<f32> {
    sp.hands[p]
        .iter()
        .map(|h| {
            let c = solver::preflop::equity::class_index(h.c1 / 4, h.c2 / 4, h.c1 % 4 == h.c2 % 4);
            0.02 + ((c * 7 + t as usize * 3 + p * 11) % 23) as f32 / 23.
        })
        .collect()
}
fn pair(sp: &Spot, mode: &str, t: u32) -> [Vec<f32>; 2] {
    let source = t.min(100);
    let mut result = std::array::from_fn(|p| {
        if mode == "abrupt_pair" {
            weights(sp, p, source)
        } else {
            let (a, b) = (weights(sp, p, 31), weights(sp, p, 47));
            let x = (source - 1) as f32 / 99.;
            a.iter()
                .zip(&b)
                .map(|(a, b)| a * (1. - x) + b * x)
                .collect()
        }
    });
    if mode == "abrupt_pair" && t <= 100 && t % 17 == 0 {
        result[(t / 17) as usize % 2].fill(0.);
    }
    result
}

fn packed(source: &Solver, plan: &GpuPlan) -> [Vec<f32>; 4] {
    let mut result = std::array::from_fn(|k| vec![0.; plan.arena_elements[k % 2]]);
    let mut copied = [0usize; 2];
    for &i in &plan.action_nodes {
        let n = &source.spot.tree.nodes[i as usize];
        let p = n.player as usize;
        let len = n.num_children as usize * source.spot.hands[p].len();
        let src = n.data_offset as usize;
        let dst = plan.node_data_off[i as usize] as usize;
        for (k, s) in [(p, &source.regrets[p]), (p + 2, &source.strat[p])] {
            result[k][dst..dst + len].copy_from_slice(&data(s)[src..src + len]);
        }
        copied[p] += len;
    }
    assert_eq!(copied, plan.arena_elements);
    result
}

fn restore(source: &Solver, plan: &GpuPlan, packed: &[Vec<f32>; 4]) -> Solver {
    let mut restored = Solver::new(source.spot.clone());
    restored.algo = source.algo;
    restored.iteration = source.iteration;
    restored.use_isomorphism = true;
    for &i in &plan.action_nodes {
        let n = &source.spot.tree.nodes[i as usize];
        let p = n.player as usize;
        let len = n.num_children as usize * source.spot.hands[p].len();
        let dst = n.data_offset as usize;
        let src = plan.node_data_off[i as usize] as usize;
        data_mut(&mut restored.regrets[p])[dst..dst + len]
            .copy_from_slice(&packed[p][src..src + len]);
        data_mut(&mut restored.strat[p])[dst..dst + len]
            .copy_from_slice(&packed[p + 2][src..src + len]);
    }
    restored.mark_sym_dirty();
    restored.ensure_symmetric();
    restored.use_isomorphism = false;
    restored
}

fn mismatch(a: &Solver, b: &Solver) -> (usize, f64) {
    let mut count = 0;
    let mut max = 0f64;
    for (a, b) in a
        .regrets
        .iter()
        .chain(&a.strat)
        .zip(b.regrets.iter().chain(&b.strat))
    {
        assert_eq!(data(a).len(), data(b).len());
        for (a, b) in data(a).iter().zip(data(b)) {
            assert!(a.is_finite() && b.is_finite());
            count += usize::from(a.to_bits() != b.to_bits());
            max = max.max((*a as f64 - *b as f64).abs());
        }
    }
    (count, max)
}

#[test]
fn canonical_host_storage_restores_explicit_tied_state_bitwise() {
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
            let mut source = Solver::new(sp.clone());
            source.algo = Algorithm::CfrPlus;
            source.use_isomorphism = false;
            let mut gpu =
                SymmetricContinuationGpu::new_explicit_reference(&source, u64::MAX).unwrap();
            let plan = GpuPlan::build(&sp, true);
            for t in 1..=300 {
                let reaches = pair(&sp, mode, t);
                for p in 0..2 {
                    gpu.sweep(p, t, &reaches[p], &reaches[1 - p]).unwrap();
                }
                if ![1, 17, 100, 300].contains(&t) {
                    continue;
                }
                gpu.sync_to_cpu(&mut source).unwrap();
                let clock = Instant::now();
                let compact = packed(&source, &plan);
                let encode = clock.elapsed().as_secs_f64();
                let clock = Instant::now();
                let mut restored = restore(&source, &plan, &compact);
                let decode = clock.elapsed().as_secs_f64();
                let (different, max_error) = mismatch(&source, &restored);
                let mut resumed_values_exact = false;
                let mut resumed_arrays_exact = false;
                if different == 0 {
                    // Two ordinary full GPU passes from the identical states.
                    // This verifies restoration without introducing compressed chance traversal.
                    let mut a = GpuSolver::new(&source).unwrap();
                    let mut b = GpuSolver::new(&restored).unwrap();
                    let next = pair(&sp, mode, t + 1);
                    resumed_values_exact = true;
                    for p in 0..2 {
                        let va = a
                            .research_continuation_sweep(p, t + 1, &next[p], &next[1 - p])
                            .unwrap();
                        let vb = b
                            .research_continuation_sweep(p, t + 1, &next[p], &next[1 - p])
                            .unwrap();
                        resumed_values_exact &=
                            va.iter().zip(&vb).all(|(x, y)| x.to_bits() == y.to_bits());
                    }
                    let mut resumed = Solver::new(sp.clone());
                    resumed.algo = Algorithm::CfrPlus;
                    resumed.use_isomorphism = false;
                    a.sync_to_cpu(&mut resumed).unwrap();
                    b.sync_to_cpu(&mut restored).unwrap();
                    resumed_arrays_exact = mismatch(&resumed, &restored).0 == 0;
                }
                let raw = source
                    .regrets
                    .iter()
                    .chain(&source.strat)
                    .map(|s| data(s).len() * 4)
                    .sum::<usize>();
                let stored = compact.iter().map(|a| a.len() * 4).sum::<usize>();
                let passed =
                    different == 0 && resumed_values_exact && resumed_arrays_exact && stored <= raw;
                println!(
                    "HOST_ORBIT {}",
                    serde_json::json!({"mode":mode,"board":board,"iteration":t,
                    "raw_array_bytes":raw,"stored_array_bytes":stored,"encode_seconds":encode,"restore_seconds":decode,
                    "restore_differing_values":different,"restore_max_absolute_error":max_error,
                    "resumed_values_bitwise_equal":resumed_values_exact,"resumed_arrays_bitwise_equal":resumed_arrays_exact,
                    "passed":passed})
                );
                if !passed {
                    failures.push((mode, board, t));
                }
            }
        }
    }
    assert!(
        failures.is_empty(),
        "Exact host storage diagnostic failures: {failures:?}"
    );
}
