//! GPU solver correctness tests. Require an NVIDIA GPU, the `gpu` feature,
//! and libnvrtc on LD_LIBRARY_PATH:
//!   cargo test --release --features gpu --test gpu

#![cfg(feature = "gpu")]

use solver::gpu::GpuSolver;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{LockMode, Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing {
        bet: parse_sizes(bet).unwrap(),
        raise: parse_sizes(raise).unwrap(),
        donk: vec![],
    }
}

fn hand_index(spot: &Spot, p: usize, combo: &str) -> usize {
    let cards = solver::cards::parse_cards(combo).unwrap();
    spot.hands[p]
        .iter()
        .position(|h| {
            (h.c1 == cards[0] && h.c2 == cards[1]) || (h.c1 == cards[1] && h.c2 == cards[0])
        })
        .unwrap_or_else(|| panic!("combo {combo} not found for player {p}"))
}

/// Full flop tree: the GPU solve must converge, with exploitability measured
/// by the CPU best-response on the downloaded arenas, and match the CPU
/// solver's convergence quality at the same iteration count.
#[test]
fn gpu_converges_and_matches_cpu() {
    let config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };

    let mut cpu = Solver::new(Arc::new(Spot::new(config.clone()).unwrap()));
    cpu.use_isomorphism = false;
    for _ in 0..200 {
        cpu.iterate();
    }
    let e_cpu = cpu.exploitability() / 60.0 * 100.0;

    let mut host = Solver::new(Arc::new(Spot::new(config).unwrap()));
    host.use_isomorphism = false;
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..200 {
        gpu.iterate().unwrap();
    }
    gpu.sync_to_cpu(&mut host).unwrap();
    assert_eq!(host.iteration, 200);
    let e_gpu = host.exploitability() / 60.0 * 100.0;

    assert!(e_cpu < 0.6, "CPU should converge, got {e_cpu}% pot");
    assert!(e_gpu < 0.6, "GPU should converge, got {e_gpu}% pot");
    // Trajectories legitimately differ (the CPU skips discounting in
    // zero-reach-pruned subtrees; in practice the GPU converges a bit faster
    // per iteration). The GPU must never be meaningfully worse.
    assert!(
        e_gpu < e_cpu + 0.1,
        "GPU exploitability should not lag CPU: {e_gpu}% vs {e_cpu}%"
    );
}

/// Node locking on the GPU: lock the bluff-catcher to always-call, continue
/// solving on the GPU, and the polarized player must stop bluffing.
#[test]
fn gpu_locked_always_call_kills_bluffs() {
    let config = SpotConfig {
        board: "QcJc9c3d2d".to_string(),
        range_oop: "AcKc,8h7h".to_string(),
        range_ip: "QdQh".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    };
    let mut host = Solver::new(Arc::new(Spot::new(config).unwrap()));
    host.use_isomorphism = false;
    // pre-solve so the lock has a strategy to scale
    for _ in 0..200 {
        host.iterate();
    }
    let path = vec![solver::PathStep::Action { index: 1 }]; // after OOP bet
    host.lock_node(&path, LockMode::Range { freqs: vec![0.0, 1.0] }, "ip always calls".to_string())
        .unwrap();

    let mut gpu = GpuSolver::new(&host).unwrap(); // picks up the lock table
    for _ in 0..2000 {
        gpu.iterate().unwrap();
    }
    gpu.sync_to_cpu(&mut host).unwrap();

    let root = &host.spot.tree.nodes[0];
    let sigma = host.average_strategy(0, root);
    let nh = host.spot.hands[0].len();
    let nuts = hand_index(&host.spot, 0, "AcKc");
    let air = hand_index(&host.spot, 0, "8h7h");
    assert!(
        sigma[nh + nuts] > 0.97,
        "nuts should still bet vs station, got {}",
        sigma[nh + nuts]
    );
    assert!(
        sigma[nh + air] < 0.05,
        "air should never bluff vs station, got {}",
        sigma[nh + air]
    );
    // the lock itself holds in queries
    let view = host.node_view(&path).unwrap();
    assert!(view.locked);
    let qq = hand_index(&host.spot, 1, "QdQh");
    let st = view.players[1].hands[qq].strategy.as_ref().unwrap();
    assert!(st[1] > 0.999, "locked call freq should be 1.0, got {}", st[1]);
}

/// GPU exploitability (best response in VRAM) must match the CPU's number
/// on identical data — including the rake-adjusted formula.
#[test]
fn gpu_exploitability_matches_cpu() {
    let mut config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    for raked in [false, true] {
        config.tree.rake_pct = if raked { 0.05 } else { 0.0 };
        config.tree.rake_cap = if raked { 3.0 } else { 0.0 };
        let mut host = Solver::new(Arc::new(Spot::new(config.clone()).unwrap()));
        host.use_isomorphism = false;
        let mut gpu = GpuSolver::new(&host).unwrap();
        for _ in 0..100 {
            gpu.iterate().unwrap();
        }
        gpu.sync_to_cpu(&mut host).unwrap();
        let e_cpu = host.exploitability();
        let e_gpu = gpu.exploitability(&host).unwrap();
        let diff_pct = (e_cpu - e_gpu).abs() / 60.0 * 100.0;
        assert!(
            diff_pct < 0.02,
            "GPU exploitability should match CPU (rake={raked}): {e_gpu} vs {e_cpu} ({diff_pct}% pot apart)"
        );
    }
}

/// Compressed CPU storage works through the GPU path: arenas decode on
/// upload and re-encode on sync.
#[test]
fn gpu_with_compressed_cpu_storage() {
    let config = SpotConfig {
        board: "Th9h2c".to_string(),
        range_oop: "QQ,JJ,TT,99,AhKh,AsKs,87s".to_string(),
        range_ip: "AA,KK,AQs,JTs,T9s".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", "60"), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    let mut host = Solver::with_storage(
        Arc::new(Spot::new(config).unwrap()),
        solver::Storage::Compressed,
    );
    host.use_isomorphism = false;
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..200 {
        gpu.iterate().unwrap();
    }
    gpu.sync_to_cpu(&mut host).unwrap();
    let e = host.exploitability() / 60.0 * 100.0;
    assert!(
        e < 0.7,
        "GPU + compressed CPU storage should converge, got {e}% pot"
    );
}

/// Suit isomorphism on the GPU: a two-tone board with symmetric ranges must
/// (a) converge equivalently to the non-isomorphic GPU solver, (b) agree
/// with GPU exploitability, and (c) produce exactly mirrored strategies on
/// isomorphic runouts after sync + symmetrize.
#[test]
fn gpu_suit_isomorphism_equivalence() {
    let config = SpotConfig {
        board: "KsQs2d".to_string(),
        range_oop: "TT,99,88,77,AKs,AQs,AJs,JTs,T9s,87s,AKo,KQo".to_string(),
        range_ip: "QQ,JJ,TT,AKs,KQs,QJs,T9s,98s,AQo".to_string(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 200.0,
            oop: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ip: [sizing("50", ""), sizing("50", ""), sizing("50", "")],
            ..Default::default()
        },
    };
    let spot = Spot::new(config.clone()).unwrap();
    assert_eq!(spot.suit_perms.len(), 2, "KsQs2d should have the c<->h swap");

    let mut host_iso = Solver::new(Arc::new(spot)); // use_isomorphism = true
    let mut gpu_iso = GpuSolver::new(&host_iso).unwrap();
    let mut host_plain = Solver::new(Arc::new(Spot::new(config).unwrap()));
    host_plain.use_isomorphism = false;
    let mut gpu_plain = GpuSolver::new(&host_plain).unwrap();
    for _ in 0..100 {
        gpu_iso.iterate().unwrap();
        gpu_plain.iterate().unwrap();
    }
    let e_iso = gpu_iso.exploitability(&host_iso).unwrap() / 60.0 * 100.0;
    let e_plain = gpu_plain.exploitability(&host_plain).unwrap() / 60.0 * 100.0;
    assert!(e_iso < 2.0, "iso GPU should converge, got {e_iso}%");
    assert!(e_plain < 2.0, "plain GPU should converge, got {e_plain}%");
    assert!(
        (e_iso - e_plain).abs() < 0.6,
        "iso and plain GPU exploitability should agree: {e_iso}% vs {e_plain}%"
    );

    // CPU-side exploitability on synced data agrees with the GPU's number.
    gpu_iso.sync_to_cpu(&mut host_iso).unwrap();
    let e_cpu = host_iso.exploitability() / 60.0 * 100.0;
    assert!(
        (e_cpu - e_iso).abs() < 0.02,
        "CPU exploitability on synced iso data should match GPU: {e_cpu}% vs {e_iso}%"
    );

    // Isomorphic turn branches (4c vs 4h after check/check) mirror exactly
    // once the CPU materializes the sibling branches.
    host_iso.ensure_symmetric();
    use solver::PathStep;
    let path = |card: &str| {
        vec![
            PathStep::Action { index: 0 },
            PathStep::Action { index: 0 },
            PathStep::Card {
                card: card.to_string(),
            },
        ]
    };
    let vc = host_iso.node_view(&path("4c")).unwrap();
    let vh = host_iso.node_view(&path("4h")).unwrap();
    let agg_freq = |v: &solver::NodeView| {
        let (mut n, mut d) = (0f64, 0f64);
        for h in &v.players[0].hands {
            if let Some(s) = &h.strategy {
                n += s[0] as f64 * h.reach as f64;
                d += h.reach as f64;
            }
        }
        n / d
    };
    let (fc, fh) = (agg_freq(&vc), agg_freq(&vh));
    assert!(
        (fc - fh).abs() < 1e-4,
        "isomorphic turn strategies should mirror: {fc} vs {fh}"
    );
}

/// The clairvoyance game has a closed-form solution; the GPU must find it
/// (exercises fold + showdown kernels and the update path end to end).
#[test]
fn gpu_clairvoyance_closed_form() {
    let config = SpotConfig {
        board: "QcJc9c3d2d".to_string(),
        range_oop: "AcKc,8h7h".to_string(),
        range_ip: "QdQh".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    };
    let mut host = Solver::new(Arc::new(Spot::new(config).unwrap()));
    host.use_isomorphism = false;
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..3000 {
        gpu.iterate().unwrap();
    }
    gpu.sync_to_cpu(&mut host).unwrap();

    let exploit_pct = host.exploitability() / 100.0 * 100.0;
    assert!(
        exploit_pct < 0.10,
        "exploitability too high: {exploit_pct}% pot"
    );

    let root = &host.spot.tree.nodes[0];
    let sigma = host.average_strategy(0, root);
    let nh = host.spot.hands[0].len();
    let nuts = hand_index(&host.spot, 0, "AcKc");
    let air = hand_index(&host.spot, 0, "8h7h");
    assert!(
        sigma[nh + nuts] > 0.97,
        "nuts should always bet, got {}",
        sigma[nh + nuts]
    );
    assert!(
        (sigma[nh + air] - 0.5).abs() < 0.05,
        "air should bluff ~50%, got {}",
        sigma[nh + air]
    );

    let bet_child = host.spot.tree.children[root.children_start as usize + 1];
    let ip_node = &host.spot.tree.nodes[bet_child as usize];
    let sigma_ip = host.average_strategy(bet_child, ip_node);
    let nh_ip = host.spot.hands[1].len();
    let qq = hand_index(&host.spot, 1, "QdQh");
    assert!(
        (sigma_ip[nh_ip + qq] - 0.5).abs() < 0.07,
        "bluff-catcher should call ~50%, got {}",
        sigma_ip[nh_ip + qq]
    );
}
