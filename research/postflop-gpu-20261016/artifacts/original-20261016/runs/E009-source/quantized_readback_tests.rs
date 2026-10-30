//! Integration oracle for optional compressed readback. The oracle downloads
//! the same untouched f32 device images and calls the pre-existing CPU writer.
//! Run serially: cargo test --release -p solver --features gpu --lib quantized_readback_tests -- --test-threads=1
use super::*;
use crate::{LockMode, PathStep, Spot, SpotConfig, Storage, StreetSizing, TreeConfig, parse_sizes};
use crate::tree::KIND_ACTION;

fn host(board: &str, storage: Storage, iso: bool) -> Solver {
    let sizing = || StreetSizing {
        bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![],
    };
    let spot = Spot::new(SpotConfig {
        board: board.into(),
        range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
        range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
        tree: TreeConfig {
            starting_pot: 10.0, effective_stack: 20.0, rake_pct: 0.05, rake_cap: 1.0,
            oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
            ..Default::default()
        },
    }).unwrap();
    let mut solver = Solver::with_storage(Arc::new(spot), storage);
    solver.use_isomorphism = iso;
    solver
}

fn copy_store(src: &Store, dst: &mut Store) {
    match (src, dst) {
        (Store::F32(a), Store::F32(b)) => b.as_mut_slice().copy_from_slice(a.as_slice()),
        (Store::I16 { q: aq, scale: ascale }, Store::I16 { q: bq, scale: bscale }) => {
            bq.as_mut_slice().copy_from_slice(aq.as_slice());
            bscale.as_mut_slice().copy_from_slice(ascale.as_slice());
        }
        (Store::U16 { q: aq, scale: ascale }, Store::U16 { q: bq, scale: bscale }) => {
            bq.as_mut_slice().copy_from_slice(aq.as_slice());
            bscale.as_mut_slice().copy_from_slice(ascale.as_slice());
        }
        _ => panic!("oracle storage mismatch"),
    }
}

fn copy_host(src: &Solver) -> Solver {
    let mut dst = Solver::with_storage(src.spot.clone(), src.storage);
    for p in 0..2 {
        copy_store(&src.regrets[p], &mut dst.regrets[p]);
        copy_store(&src.strat[p], &mut dst.strat[p]);
    }
    dst.iteration = src.iteration;
    dst.algo = src.algo;
    dst.use_isomorphism = src.use_isomorphism;
    dst.locks = src.locks.clone();
    dst.lock_labels = src.lock_labels.clone();
    dst
}

// Compare every stored byte, including gaps and scales indexed by nodes that do
// not belong to this player. f32 equality alone would miss signed zero/NaN bits.
fn store_bytes(store: &Store) -> Vec<u8> {
    let mut result = Vec::new();
    match store {
        Store::F32(values) => {
            result.push(0);
            for &value in values.as_slice() { result.extend_from_slice(&value.to_bits().to_le_bytes()); }
        }
        Store::I16 { q, scale } => {
            result.push(1);
            for &value in q.as_slice() { result.extend_from_slice(&value.to_le_bytes()); }
            for &value in scale.as_slice() { result.extend_from_slice(&value.to_bits().to_le_bytes()); }
        }
        Store::U16 { q, scale } => {
            result.push(2);
            for &value in q.as_slice() { result.extend_from_slice(&value.to_le_bytes()); }
            for &value in scale.as_slice() { result.extend_from_slice(&value.to_bits().to_le_bytes()); }
        }
    }
    result
}

fn cpu_bytes(solver: &Solver) -> Vec<Vec<u8>> {
    solver.regrets.iter().chain(&solver.strat).map(store_bytes).collect()
}

fn equal_bytes(actual: &[u8], expected: &[u8], label: &str) {
    assert_eq!(actual.len(), expected.len(), "{label} byte length");
    if let Some(index) = actual.iter().zip(expected).position(|(a, b)| a != b) {
        panic!("{label}: byte {index}, actual={:02x}, expected={:02x}", actual[index], expected[index]);
    }
}

fn equal_hosts(actual: &Solver, expected: &Solver, label: &str) {
    assert_eq!(actual.iteration, expected.iteration, "{label}: iteration");
    assert_eq!(actual.algo, expected.algo, "{label}: algorithm");
    for (index, (a, b)) in cpu_bytes(actual).iter().zip(cpu_bytes(expected)).enumerate() {
        equal_bytes(a, &b, &format!("{label}: store {index} (regret0,regret1,strategy0,strategy1)"));
    }
}

struct Images { regrets: [Vec<f32>; 2], strategy: [Vec<f32>; 2] }
fn device_images(gpu: &GpuSolver) -> Images {
    gpu.stream.synchronize().unwrap();
    let regrets = std::array::from_fn(|p| gpu.stream.clone_dtoh(&gpu.d_regrets[p]).unwrap());
    let strategy = std::array::from_fn(|p| gpu.stream.clone_dtoh(&gpu.d_strat[p]).unwrap());
    gpu.stream.synchronize().unwrap();
    Images { regrets, strategy }
}

fn equal_device(actual: &Images, expected: &Images, label: &str) {
    for (store, (a, b)) in actual.regrets.iter().chain(&actual.strategy)
        .zip(expected.regrets.iter().chain(&expected.strategy)).enumerate() {
        assert_eq!(a.len(), b.len(), "{label}: device store {store} length");
        for (i, (&a, &b)) in a.iter().zip(b).enumerate() {
            assert_eq!(a.to_bits(), b.to_bits(), "{label}: device store {store} element {i}");
        }
    }
}

fn compare_sync(gpu: &mut GpuSolver, host: &mut Solver, strategy_only: bool, label: &str) -> Solver {
    let raw = device_images(gpu);
    let mut expected = copy_host(host);
    for p in 0..2 {
        if !strategy_only { gpu.arena_layout[p].write(&expected, p, 0, &raw.regrets[p]); }
        gpu.arena_layout[p].write(&expected, p, 1, &raw.strategy[p]);
    }
    expected.iteration = gpu.iteration;
    if gpu.iso_active { expected.mark_sym_dirty(); }
    if strategy_only { gpu.sync_strategy(host).unwrap(); }
    else { gpu.sync_to_cpu(host).unwrap(); }
    equal_hosts(host, &expected, label);
    equal_device(&device_images(gpu), &raw, label);
    expected
}

fn base_budget(host: &Solver) -> u64 {
    let plan = GpuPlan::build(&host.spot, host.use_isomorphism);
    plan.staging_bytes() + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
        + 512 * 1024 * 1024
}

// Deliberately nonzero data in storage that neither active nor inactive action
// writes own. A scatter implementation must preserve these bytes on every sync.
fn seed_nonowned_compressed(host: &mut Solver) -> (usize, usize) {
    let mut gaps = 0;
    let mut unused_scales = 0;
    for p in 0..2 {
        let mut owned_q = vec![false; host.spot.tree.data_size[p] as usize];
        let mut owned_scale = vec![false; host.spot.tree.nodes.len()];
        for (i, node) in host.spot.tree.nodes.iter().enumerate() {
            if node.kind == KIND_ACTION && node.player as usize == p {
                owned_scale[i] = true;
                let off = node.data_offset as usize;
                let len = node.num_children as usize * host.spot.hands[p].len();
                owned_q[off..off + len].fill(true);
            }
        }
        gaps += owned_q.iter().filter(|&&owned| !owned).count();
        unused_scales += owned_scale.iter().filter(|&&owned| !owned).count();
        for store in [&mut host.regrets[p], &mut host.strat[p]] {
            let scales = match store {
                Store::I16 { q, scale } => {
                    for (i, value) in q.as_mut_slice().iter_mut().enumerate() {
                        if !owned_q[i] { *value = -12345; }
                    }
                    scale.as_mut_slice()
                }
                Store::U16 { q, scale } => {
                    for (i, value) in q.as_mut_slice().iter_mut().enumerate() {
                        if !owned_q[i] { *value = 54321; }
                    }
                    scale.as_mut_slice()
                }
                Store::F32(_) => unreachable!(),
            };
            for (i, value) in scales.iter_mut().enumerate() {
                if !owned_scale[i] {
                    *value = f32::from_bits([0x8000_0000, 0x7fc0_0123, 0x3fa0_0000][i % 3]);
                }
            }
        }
    }
    assert!(unused_scales > 0, "fixture must exercise nonowned scale preservation");
    (gaps, unused_scales)
}

#[test]
fn full_compressed_zero_and_solved_readback_matches_old_writer() {
    let mut host = host("KsQs2dJdTc", Storage::Compressed, false);
    let mut gpu = GpuSolver::new(&host).unwrap();
    assert!(gpu.uses_quantized_readback(), "fixture must exercise optional compressed path");
    for p in 0..2 {
        assert_eq!(gpu.d_regrets[p].len(), host.spot.tree.data_size[p] as usize,
            "river fixture should have a full arena layout");
    }
    // Seed after construction so this also covers fresh positive-zero uploads.
    seed_nonowned_compressed(&mut host);
    compare_sync(&mut gpu, &mut host, false, "full zero");
    for _ in 0..4 { gpu.iterate().unwrap(); }
    compare_sync(&mut gpu, &mut host, false, "full solved");
    compare_sync(&mut gpu, &mut host, false, "full repeated");
    for _ in 0..2 { gpu.iterate().unwrap(); }
    compare_sync(&mut gpu, &mut host, true, "full strategy only");
    compare_sync(&mut gpu, &mut host, false, "full after strategy only");
}

#[test]
fn compact_warm_readback_restores_inactive_nodes_and_survives_locks() {
    let mut host = host("KsQs2dJd", Storage::Compressed, false);
    for _ in 0..3 { host.iterate(); }
    host.use_isomorphism = true;
    let plan = GpuPlan::build(&host.spot, true);
    let mut inactive_by_player = [0usize; 2];
    for (i, node) in host.spot.tree.nodes.iter().enumerate() {
        if node.kind == KIND_ACTION && plan.node_data_off[i] == u64::MAX {
            let p = node.player as usize;
            inactive_by_player[p] += 1;
            let len = node.num_children as usize * host.spot.hands[p].len();
            // Force distinct, nonzero initial inactive snapshots. The actual
            // CPU encoder remains the only source of quantization arithmetic.
            unsafe {
                host.regrets[p].write_f32(i as u32, node.data_offset, len, &vec![-3.25; len]);
                host.strat[p].write_f32(i as u32, node.data_offset, len, &vec![7.5; len]);
            }
        }
    }
    assert!(inactive_by_player.iter().all(|&n| n > 0));
    seed_nonowned_compressed(&mut host);
    let mut gpu = GpuSolver::new(&host).unwrap();
    assert!(gpu.uses_quantized_readback());
    assert!(gpu.iso_active);
    for p in 0..2 { assert!(gpu.d_regrets[p].len() < host.spot.tree.data_size[p] as usize); }
    compare_sync(&mut gpu, &mut host, false, "compact warm initial");
    for _ in 0..4 { gpu.iterate().unwrap(); }
    let mut expected = compare_sync(&mut gpu, &mut host, false, "compact warm solved");
    let stale_siblings = cpu_bytes(&host);
    host.ensure_symmetric();
    expected.ensure_symmetric();
    equal_hosts(&host, &expected, "materialized siblings");
    assert!(cpu_bytes(&host) != stale_siblings, "fixture must actually materialize inactive data");
    compare_sync(&mut gpu, &mut host, false, "compact restores initial inactive snapshots");
    compare_sync(&mut gpu, &mut host, false, "compact repeated restore");

    host.lock_node(&[PathStep::Action { index: 0 }], LockMode::Freeze, "readback lock".into()).unwrap();
    gpu.update_locks(&host).unwrap();
    for _ in 0..3 { gpu.iterate().unwrap(); }
    compare_sync(&mut gpu, &mut host, true, "compact strategy only after lock");
    compare_sync(&mut gpu, &mut host, false, "compact full after lock");
    gpu.iterate().unwrap();
    compare_sync(&mut gpu, &mut host, false, "compact continued iteration");
}

#[test]
fn tight_budget_and_f32_fallbacks_match_old_writer() {
    for (storage, board, iso, tight) in [
        (Storage::Compressed, "KsQs2dJd", true, true),
        (Storage::F32, "KsQs2dJd", true, true),
        (Storage::F32, "KsQs2dJdTc", false, false),
    ] {
        let mut host = host(board, storage, false);
        for _ in 0..2 { host.iterate(); }
        host.use_isomorphism = iso;
        if storage == Storage::Compressed { seed_nonowned_compressed(&mut host); }
        let budget = if tight { base_budget(&host) } else { u64::MAX };
        let mut gpu = GpuSolver::new_with_budget(&host, budget).unwrap();
        assert!(!gpu.uses_quantized_readback(), "tight/F32 fixture must exercise original fallback");
        for _ in 0..3 { gpu.iterate().unwrap(); }
        let label = format!("fallback {storage:?}, iso={iso}, tight={tight}");
        let mut expected = compare_sync(&mut gpu, &mut host, false, &label);
        host.ensure_symmetric();
        expected.ensure_symmetric();
        equal_hosts(&host, &expected, &format!("{label} after materialization"));
        compare_sync(&mut gpu, &mut host, false, &format!("{label} repeated"));
        gpu.iterate().unwrap();
        compare_sync(&mut gpu, &mut host, true, &format!("{label} strategy only"));
    }
}
