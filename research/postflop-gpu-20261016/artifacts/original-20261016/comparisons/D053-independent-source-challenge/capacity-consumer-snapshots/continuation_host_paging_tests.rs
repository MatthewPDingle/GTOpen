//! Storage-only prototype: retain explicit GPU traversal and restore every bit.

use crate::{
    gpu::{plan::GpuPlan, GpuSolver, SymmetricContinuationGpu},
    store::Store,
};
use crate::{parse_sizes, Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::sync::Arc;

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
            let c = crate::preflop::equity::class_index(h.c1 / 4, h.c2 / 4, h.c1 % 4 == h.c2 % 4);
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
    if !plan.iso_active {
        return std::array::from_fn(|k| {
            data(if k < 2 {
                &source.regrets[k]
            } else {
                &source.strat[k - 2]
            })
            .to_vec()
        });
    }
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

fn restore(spot: &Arc<Spot>, iteration: u32, plan: &GpuPlan, packed: &[Vec<f32>; 4]) -> Solver {
    let mut restored = Solver::new(spot.clone());
    restored.algo = Algorithm::CfrPlus;
    restored.iteration = iteration;
    restored.use_isomorphism = true;
    if !plan.iso_active {
        for p in 0..2 {
            data_mut(&mut restored.regrets[p]).copy_from_slice(&packed[p]);
            data_mut(&mut restored.strat[p]).copy_from_slice(&packed[p + 2]);
        }
        restored.use_isomorphism = false;
        return restored;
    }
    for &i in &plan.action_nodes {
        let n = &spot.tree.nodes[i as usize];
        let p = n.player as usize;
        let len = n.num_children as usize * spot.hands[p].len();
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

use cudarc::driver::CudaSlice;

fn take(g: &mut GpuSolver) -> [CudaSlice<f32>; 7] {
    g.stream.synchronize().unwrap();
    let mut small: Vec<_> = (0..7)
        .map(|_| g.stream.alloc_zeros::<f32>(1).unwrap())
        .collect();
    let mut result = Vec::new();
    for old in g
        .d_regrets
        .iter_mut()
        .chain(&mut g.d_strat)
        .chain(&mut g.d_reach)
        .chain(std::iter::once(&mut g.d_cfv))
    {
        result.push(std::mem::replace(old, small.pop().unwrap()));
    }
    result.try_into().unwrap()
}

fn swap(g: &mut GpuSolver, workspace: &mut [CudaSlice<f32>; 7]) {
    for (a, b) in g
        .d_regrets
        .iter_mut()
        .chain(&mut g.d_strat)
        .chain(&mut g.d_reach)
        .chain(std::iter::once(&mut g.d_cfv))
        .zip(workspace)
    {
        std::mem::swap(a, b);
    }
}

struct Parked {
    spot: Arc<Spot>,
    plan: GpuPlan,
    arrays: [Vec<f32>; 4],
    iteration: u32,
    candidate: SymmetricContinuationGpu,
    reference: SymmetricContinuationGpu,
}

#[test]
fn parked_host_orbits_and_shared_gpu_workspace_preserve_720_passes() {
    let mut entries = Vec::new();
    let mut workspace: Option<[CudaSlice<f32>; 7]> = None;
    for board in ["KsQs2d", "KsQs2s", "KsQh2d"] {
        for (pot, stack) in [(39.5, 80.), (93.5, 155.)] {
            let z = StreetSizing {
                bet: parse_sizes("50").unwrap(),
                raise: vec![],
                donk: parse_sizes("50").unwrap(),
            };
            let spot = Arc::new(
                Spot::new(SpotConfig {
                    board: board.into(),
                    range_oop: "AA,KK,AQs,KQo,88,76s".into(),
                    range_ip: "AA,QQ,AKo,QJs,99".into(),
                    tree: TreeConfig {
                        starting_pot: pot,
                        effective_stack: stack,
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
            let mut host = Solver::new(spot.clone());
            host.algo = Algorithm::CfrPlus;
            host.use_isomorphism = false;
            let reference =
                SymmetricContinuationGpu::new_explicit_reference(&host, u64::MAX).unwrap();
            let mut candidate =
                SymmetricContinuationGpu::new_explicit_reference(&host, u64::MAX).unwrap();
            let buffers = take(&mut candidate.gpu);
            if let Some(current) = &mut workspace {
                for (old, new) in current.iter_mut().zip(buffers) {
                    if new.len() > old.len() {
                        *old = new;
                    }
                }
            } else {
                workspace = Some(buffers);
            }
            let plan = GpuPlan::build(&spot, true);
            let arrays = packed(&host, &plan);
            entries.push(Parked {
                spot,
                plan,
                arrays,
                iteration: 0,
                candidate,
                reference,
            });
        }
    }
    let mut workspace = workspace.unwrap();
    let workspace_bytes: usize = workspace.iter().map(|a| a.len() * 4).sum();
    let raw_bytes: usize = entries
        .iter()
        .map(|a| a.spot.tree.data_size.iter().sum::<u64>() as usize * 8)
        .sum();
    let packed_bytes: usize = entries
        .iter()
        .flat_map(|a| a.arrays.iter())
        .map(|a| a.len() * 4)
        .sum();
    let mut failures = Vec::new();
    for t in 1..=60 {
        for p in 0..2 {
            let mut order: Vec<usize> = (0..entries.len()).collect();
            if (t + p as u32) % 2 == 0 {
                order.reverse();
            }
            order.rotate_left((t as usize + p) % entries.len());
            for index in order {
                let entry = &mut entries[index];
                let reaches = pair(&entry.spot, "abrupt_pair", t);
                let expected = entry
                    .reference
                    .sweep(p, t, &reaches[p], &reaches[1 - p])
                    .unwrap();
                let mut expected_host = Solver::new(entry.spot.clone());
                expected_host.algo = Algorithm::CfrPlus;
                expected_host.use_isomorphism = false;
                entry.reference.sync_to_cpu(&mut expected_host).unwrap();
                let mut host = restore(&entry.spot, entry.iteration, &entry.plan, &entry.arrays);
                swap(&mut entry.candidate.gpu, &mut workspace);
                {
                    let g = &mut entry.candidate.gpu;
                    for q in 0..2 {
                        let r = data(&host.regrets[q]);
                        let s = data(&host.strat[q]);
                        g.stream
                            .memcpy_htod(r, &mut g.d_regrets[q].slice_mut(0..r.len()))
                            .unwrap();
                        g.stream
                            .memcpy_htod(s, &mut g.d_strat[q].slice_mut(0..s.len()))
                            .unwrap();
                    }
                }
                let actual = entry
                    .candidate
                    .sweep(p, t, &reaches[p], &reaches[1 - p])
                    .unwrap();
                {
                    let g = &mut entry.candidate.gpu;
                    for q in 0..2 {
                        let r = data_mut(&mut host.regrets[q]);
                        let n = r.len();
                        g.stream
                            .memcpy_dtoh(&g.d_regrets[q].slice(0..n), r)
                            .unwrap();
                        let s = data_mut(&mut host.strat[q]);
                        let n = s.len();
                        g.stream.memcpy_dtoh(&g.d_strat[q].slice(0..n), s).unwrap();
                    }
                    g.stream.synchronize().unwrap();
                }
                swap(&mut entry.candidate.gpu, &mut workspace);
                host.iteration = t;
                let values_exact = expected.len() == actual.len()
                    && expected
                        .iter()
                        .zip(&actual)
                        .all(|(a, b)| a.to_bits() == b.to_bits());
                let arrays_exact = mismatch(&host, &expected_host).0 == 0;
                entry.arrays = packed(&host, &entry.plan);
                entry.iteration = t;
                let restored = restore(&entry.spot, t, &entry.plan, &entry.arrays);
                let roundtrip_exact = mismatch(&host, &restored).0 == 0;
                let passed = values_exact && arrays_exact && roundtrip_exact;
                println!(
                    "HOST_PAGING {}",
                    serde_json::json!({"entry":index,"iteration":t,"player":p,
                    "values_bitwise_equal":values_exact,"arrays_bitwise_equal":arrays_exact,
                    "park_restore_bitwise_equal":roundtrip_exact,"passed":passed})
                );
                if !passed {
                    failures.push((index, t, p));
                }
            }
        }
    }
    println!(
        "HOST_PAGING_SUMMARY {}",
        serde_json::json!({"entries":entries.len(),"passes":720,
        "raw_array_bytes":raw_bytes,"parked_array_bytes":packed_bytes,"shared_workspace_bytes":workspace_bytes,
        "failures":failures.len(),"production_ready":false})
    );
    assert!(
        failures.is_empty(),
        "Parked host/shared workspace parity failed: {failures:?}"
    );
}
