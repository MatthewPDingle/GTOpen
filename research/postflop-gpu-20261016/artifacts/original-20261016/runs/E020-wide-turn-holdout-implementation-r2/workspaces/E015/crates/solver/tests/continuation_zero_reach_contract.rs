//! Diagnose existing update semantics; does not qualify the compact bridge.
#![cfg(feature = "preflop-research")]
use solver::{cfr::Discounts, gpu::GpuSolver, store::Store};
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

fn data(store: &Store) -> &[f32] {
    let Store::F32(a) = store else {
        panic!("F32 required")
    };
    a.as_slice()
}

fn copy_host(source: &Solver) -> Solver {
    let mut target = Solver::new(source.spot.clone());
    target.algo = source.algo;
    target.use_isomorphism = false;
    target.iteration = source.iteration;
    for (dst, src) in target
        .regrets
        .iter_mut()
        .chain(&mut target.strat)
        .zip(source.regrets.iter().chain(&source.strat))
    {
        let Store::F32(a) = dst else {
            panic!("F32 required")
        };
        a.as_mut_slice().copy_from_slice(data(src));
    }
    target
}

fn bits(s: &Solver) -> Vec<Vec<u32>> {
    s.regrets
        .iter()
        .chain(&s.strat)
        .map(|a| data(a).iter().map(|x| x.to_bits()).collect())
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

#[test]
fn zero_opponent_pruning_differs_from_unpruned_gpu_average_updates() {
    let sizing = StreetSizing {
        bet: parse_sizes("50").unwrap(),
        raise: vec![],
        donk: parse_sizes("50").unwrap(),
    };
    let sp = Arc::new(
        Spot::new(SpotConfig {
            board: "KsQh2d".into(),
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
    let mut seed = Solver::new(sp.clone());
    seed.algo = Algorithm::CfrPlus;
    seed.use_isomorphism = false;
    // Build the same nontrivial state for both zero-reach cases.
    {
        let mut warm = GpuSolver::new(&seed).unwrap();
        for t in 1..=16 {
            let pair = [weights(&sp, 0, t), weights(&sp, 1, t)];
            for p in 0..2 {
                warm.research_continuation_sweep(p, t, &pair[p], &pair[1 - p])
                    .unwrap();
            }
        }
        warm.sync_to_cpu(&mut seed).unwrap();
    }
    let before = bits(&seed);
    let root = &sp.tree.nodes[0];
    assert_eq!(root.player, 0);
    let nh = sp.hands[0].len();
    let na = root.num_children as usize;
    let off = root.data_offset as usize;
    let old_r = &data(&seed.regrets[0])[off..off + nh * na];
    let old_s = &data(&seed.strat[0])[off..off + nh * na];
    let ds = Discounts::for_iteration(Algorithm::CfrPlus, 17).strat;
    let mut failures = vec![];
    for mode in ["zero_opponent", "zero_own"] {
        let mut own = weights(&sp, 0, 17);
        let mut opponent = weights(&sp, 1, 17);
        if mode == "zero_opponent" {
            opponent.fill(0.);
        } else {
            own.fill(0.);
        }
        let mut expected = vec![0.; old_s.len()];
        for h in 0..nh {
            let sum: f32 = (0..na).map(|a| old_r[a * nh + h].max(0.)).sum();
            for a in 0..na {
                let i = a * nh + h;
                let sigma = if sum > 1e-12 {
                    old_r[i].max(0.) / sum
                } else {
                    1. / na as f32
                };
                expected[i] = old_s[i] * ds + own[h] * sigma;
            }
        }
        let mut cpu = copy_host(&seed);
        let mut gpu_host = copy_host(&seed);
        let mut gpu = GpuSolver::new(&gpu_host).unwrap();
        let cpu_cfv = cpu
            .research_continuation_sweep(0, 17, &own, &opponent)
            .unwrap();
        let gpu_cfv = gpu
            .research_continuation_sweep(0, 17, &own, &opponent)
            .unwrap();
        gpu.sync_to_cpu(&mut gpu_host).unwrap();
        let cpu_s = &data(&cpu.strat[0])[off..off + nh * na];
        let gpu_s = &data(&gpu_host.strat[0])[off..off + nh * na];
        let cfv_difference = maximum(&cpu_cfv, &gpu_cfv) / opponent.iter().sum::<f32>().max(1.);
        let gpu_formula_error = maximum(&expected, gpu_s);
        let cpu_formula_error = maximum(&expected, cpu_s);
        let cpu_unchanged = bits(&cpu) == before;
        let gpu_root_changed = maximum(old_s, gpu_s) > 1e-6;
        let zero_cfvs = cpu_cfv.iter().chain(&gpu_cfv).all(|x| *x == 0.);
        let passed = gpu_formula_error < 2e-6
            && cfv_difference < 0.002
            && if mode == "zero_opponent" {
                cpu_unchanged && gpu_root_changed && zero_cfvs
            } else {
                cpu_formula_error < 2e-6
            };
        println!(
            "ZERO_REACH {}",
            serde_json::json!({"mode":mode, "passed":passed,
            "cpu_all_arenas_unchanged":cpu_unchanged, "gpu_root_average_sums_changed":gpu_root_changed,
            "both_cfvs_zero":zero_cfvs, "same_state_cfv_difference_per_mass":cfv_difference,
            "gpu_root_formula_error":gpu_formula_error, "cpu_root_formula_error":cpu_formula_error,
            "cpu_gpu_normalized_root_difference":maximum(&cpu.average_strategy(0,root), &gpu_host.average_strategy(0,root))})
        );
        if !passed {
            failures.push(mode);
        }
    }
    assert!(
        failures.is_empty(),
        "Zero-reach diagnostic failed: {failures:?}"
    );
}
