//! "Trust the read" on the GPU must follow the CPU (rnr.rs): same trust-game
//! exploitability and readouts on the same arenas, trust 0 = the unlocked
//! GPU solve, and the dial can change mid-solve.
//! Require an NVIDIA GPU, the `gpu` feature and libnvrtc:
//!   cargo test --release --features gpu --test gpu_rnr -- --test-threads=1

#![cfg(feature = "gpu")]

use solver::gpu::GpuSolver;
use solver::query::PostflopStats;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig, Storage};
use std::sync::Arc;

const POT: f64 = 100.0;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: parse_sizes(raise).unwrap(), donk: vec![] }
}

fn river() -> SpotConfig {
    SpotConfig {
        board: "Ks9h5d3c2s".to_string(),
        range_oop: "AA,KK,99,AK,KQ,KJs,K9s,QJ,JT,T8s,76s,A4s,64s".to_string(),
        range_ip: "AK,KQ,KJ,KT,QQ,JJ,TT,99,A9s,98s,55,QJs".to_string(),
        tree: TreeConfig {
            starting_pot: POT,
            effective_stack: 300.0,
            oop: [sizing("", ""), sizing("", ""), sizing("75", "100")],
            ip: [sizing("", ""), sizing("", ""), sizing("75", "100")],
            ..Default::default()
        },
    }
}

fn turn() -> SpotConfig {
    SpotConfig {
        board: "Kh9d5c2h".to_string(),
        range_oop: "AA,KK,99,AK,KQ,QJs,JTs,T8s,76s,A5s".to_string(),
        range_ip: "AK,KQ,KJ,QQ,JJ,TT,A9s,98s,55".to_string(),
        tree: TreeConfig {
            starting_pot: POT,
            effective_stack: 200.0,
            oop: [sizing("", ""), sizing("75", ""), sizing("75", "")],
            ip: [sizing("", ""), sizing("75", ""), sizing("75", "")],
            ..Default::default()
        },
    }
}

fn folder() -> PostflopStats {
    PostflopStats {
        contextual_betting: None,
        cbet: [60.0, 55.0, 50.0],
        fold_to_bet: [70.0, 70.0, 75.0],
        raise_bet: 0.0,
        donk: 30.0,
        bet_size: "min".into(),
    }
}

/// Solve `iters` on the CPU, then lock `villain` to the folding profile.
fn locked(config: SpotConfig, storage: Storage, iters: u32, villain: usize) -> Solver {
    let mut s = Solver::with_storage(Arc::new(Spot::new(config).unwrap()), storage);
    for _ in 0..iters {
        s.iterate();
    }
    s.lock_profile(villain, &folder(), None).unwrap();
    s
}

fn pct(x: f64) -> f64 {
    x / POT * 100.0
}

/// GPU and CPU solve the same trust game: the GPU's own readout matches the
/// CPU readout of the GPU arenas, and both converge to the same frontier
/// point as a CPU-only solve.
#[test]
fn gpu_trust_game_matches_cpu() {
    let cases: [(fn() -> SpotConfig, Storage, usize, u32); 4] = [
        (river, Storage::F32, 1, 600),
        (river, Storage::F32, 0, 600),
        (turn, Storage::F32, 1, 300),
        (turn, Storage::Compressed, 1, 300),
    ];
    for (config, storage, villain, iters) in cases {
        let mut cpu = locked(config(), storage, 40, villain);
        let mut host = locked(config(), storage, 40, villain);
        cpu.set_trust(Some(0.6)).unwrap();
        host.set_trust(Some(0.6)).unwrap();
        let mut gpu = GpuSolver::new(&host).unwrap();
        for _ in 0..iters {
            cpu.iterate();
            gpu.iterate().unwrap();
        }
        let g = gpu.trust_readout(&host).unwrap();
        gpu.sync_to_cpu(&mut host).unwrap();
        host.ensure_symmetric();
        let h = host.trust_readout().unwrap();
        let c = cpu.trust_readout().unwrap();
        eprintln!("{storage:?} villain {villain}:\n  gpu  {g:?}\n  host {h:?}\n  cpu  {c:?}");
        // same arenas: the GPU evaluation equals the CPU evaluation
        assert!((pct(g.exploitability) - pct(h.exploitability)).abs() < 0.01);
        for (a, b) in [
            (g.hero_ev_vs_read, h.hero_ev_vs_read),
            (g.hero_ev_vs_mixture, h.hero_ev_vs_mixture),
            (g.villain_best_response_ev, h.villain_best_response_ev),
        ] {
            assert!((a - b).abs() < 0.01, "GPU readout {g:?} vs CPU on GPU arenas {h:?}");
        }
        // independent solves land on the same point of the frontier
        assert!(pct(g.exploitability) < 0.5 && pct(c.exploitability) < 0.5);
        assert!((g.hero_ev_vs_read - c.hero_ev_vs_read).abs() < 1.0, "{g:?} vs {c:?}");
        assert!((g.villain_best_response_ev - c.villain_best_response_ev).abs() < 1.0, "{g:?} vs {c:?}");
    }
}

/// Trust 0 on the GPU is the unlocked GPU solve.
#[test]
fn gpu_trust_zero_is_the_unlocked_solve() {
    let mut host = locked(turn(), Storage::F32, 30, 1);
    host.set_trust(Some(0.0)).unwrap();
    let mut plain = Solver::new(Arc::new(Spot::new(turn()).unwrap()));
    for _ in 0..30 {
        plain.iterate();
    }
    plain.restart_averages(); // as set_trust did for `host`
    let mut ga = GpuSolver::new(&host).unwrap();
    let mut gb = GpuSolver::new(&plain).unwrap();
    for _ in 0..100 {
        ga.iterate().unwrap();
        gb.iterate().unwrap();
    }
    let (xa, xb) = (ga.exploitability(&host).unwrap(), gb.exploitability(&plain).unwrap());
    assert!((xa - xb).abs() < 1e-4 * xb.abs().max(1.0), "trust 0 {xa} vs unlocked {xb}");
    ga.sync_to_cpu(&mut host).unwrap();
    gb.sync_to_cpu(&mut plain).unwrap();
    let view = |s: &Solver| -> Vec<Option<Vec<f32>>> {
        s.node_view(&[]).unwrap().players[0].hands.iter().map(|h| h.strategy.clone()).collect()
    };
    let (va, vb) = (view(&host), view(&plain));
    for (a, b) in va.iter().zip(&vb) {
        if let (Some(a), Some(b)) = (a, b) {
            for (x, y) in a.iter().zip(b) {
                assert!((x - y).abs() < 1e-5, "root strategy {a:?} vs {b:?}");
            }
        }
    }
}

/// The dial turned on and back off during a GPU solve (update_locks after
/// set_trust, as the server does): trust 1 again reads as today's solve.
#[test]
fn gpu_dial_changes_mid_solve() {
    let mut host = locked(river(), Storage::F32, 40, 1);
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..200 {
        gpu.iterate().unwrap();
    }
    let full = gpu.trust_readout(&host).unwrap();
    assert_eq!(full.trust, 1.0);
    // the restart keeps the pre-lock average at locked nodes on the device
    let solved = |s: &Solver| -> Vec<(u32, Vec<f32>)> {
        let mut idx: Vec<u32> = s.locks.keys().copied().collect();
        idx.sort();
        idx.into_iter()
            .map(|i| {
                let node = &s.spot.tree.nodes[i as usize];
                let mut v = vec![0f32; node.num_children as usize * s.spot.hands[node.player as usize].len()];
                s.solved_strategy_into(node, &mut v);
                (i, v)
            })
            .collect()
    };
    let before = solved(&host);
    host.set_trust(Some(0.3)).unwrap();
    gpu.update_locks(&host).unwrap();
    for _ in 0..600 {
        gpu.iterate().unwrap();
    }
    let dialed = gpu.trust_readout(&host).unwrap();
    eprintln!("full {full:?}\ndialed {dialed:?}");
    assert!(pct(dialed.exploitability) < 0.5, "{dialed:?}");
    // less trust: less EV against the read, much less exploitable
    assert!(dialed.hero_ev_vs_read < full.hero_ev_vs_read);
    assert!(dialed.villain_best_response_ev < full.villain_best_response_ev - 1.0);
    host.set_trust(None).unwrap();
    gpu.update_locks(&host).unwrap();
    for _ in 0..10 {
        gpu.iterate().unwrap();
    }
    let x = gpu.exploitability(&host).unwrap();
    gpu.sync_to_cpu(&mut host).unwrap();
    assert_eq!(solved(&host), before, "locked nodes' averages survive the device restart");
    let xh = host.exploitability();
    assert!((pct(x) - pct(xh)).abs() < 0.01, "back to today's solve: gpu {x} vs cpu {xh}");
}

/// A read-reached villain node the profile leaves open: on the GPU too the
/// read and the free villain learn it apart (the free villain's own device
/// arenas), the CPU reads the same values after a sync, and the trust game
/// converges with nothing left for the read villain to gain.
#[test]
fn gpu_free_villain_has_his_own_arenas() {
    use solver::game::Dealt;
    use solver::query::PathStep;
    for storage in [Storage::F32, Storage::Compressed] {
        let mut host = locked(river(), storage, 40, 1);
        assert!(host.unlock_node(&[PathStep::Action { index: 0 }]).unwrap());
        host.set_trust(Some(0.9)).unwrap();
        let mut cpu = locked(river(), storage, 40, 1);
        assert!(cpu.unlock_node(&[PathStep::Action { index: 0 }]).unwrap());
        cpu.set_trust(Some(0.9)).unwrap();
        let mut gpu = GpuSolver::new(&host).unwrap();
        for _ in 0..600 {
            gpu.iterate().unwrap();
            cpu.iterate();
        }
        let g = gpu.trust_readout(&host).unwrap();
        gpu.sync_to_cpu(&mut host).unwrap();
        host.ensure_symmetric();
        let h = host.trust_readout().unwrap();
        let c = cpu.trust_readout().unwrap();
        eprintln!("{storage:?}:\n  gpu  {g:?}\n  host {h:?}\n  cpu  {c:?}");
        assert!((pct(g.exploitability) - pct(h.exploitability)).abs() < 0.01, "{g:?} vs {h:?}");
        assert!((g.hero_ev_vs_mixture - h.hero_ev_vs_mixture).abs() < 0.01, "{g:?} vs {h:?}");
        assert!((g.villain_best_response_ev - h.villain_best_response_ev).abs() < 0.01, "{g:?} vs {h:?}");
        assert!(pct(g.exploitability) < 0.1 && pct(c.exploitability) < 0.1, "{g:?} / {c:?}");
        assert!((g.hero_ev_vs_read - c.hero_ev_vs_read).abs() < 0.5, "{g:?} vs {c:?}");
        // nothing left for the read villain at the open node
        let w0 = &host.spot.weights[0];
        let value = |s: &Solver, cfv: &[f32]| {
            s.spot.weights[1].iter().zip(cfv).map(|(&w, &v)| w as f64 * v as f64).sum::<f64>() / s.pair_weight_sum()
        };
        let br = value(&host, &host.traverse_br_view(0, 1, w0, Dealt::default(), false));
        let avg = value(&host, &host.traverse_avg_view(0, 1, w0, Dealt::default(), false));
        assert!(br - avg < 0.1, "{storage:?}: the read villain could gain {} chips", br - avg);
    }
}
