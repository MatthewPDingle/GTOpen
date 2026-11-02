//! Least-exploitable fits on the GPU must follow the CPU implementation:
//! same targets reached, same bounty, same locked strategy, and the GPU best
//! response must treat a running fit as its future lock like the CPU does.
//! Require an NVIDIA GPU, the `gpu` feature and libnvrtc:
//!   cargo test --release --features gpu --test gpu_fit -- --test-threads=1

#![cfg(feature = "gpu")]

use solver::gpu::GpuSolver;
use solver::query::PathStep;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig, Storage};
use std::sync::Arc;

fn sizing(bet: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: vec![], donk: vec![] }
}

const POT: f64 = 100.0;
const ROOT: &[PathStep] = &[];

fn river() -> SpotConfig {
    SpotConfig {
        board: "Ks9h5d3c2s".to_string(),
        range_oop: "AA,KK,99,AK,KQ,KJs,K9s,QJ,JT,T8s,76s,A4s,64s".to_string(),
        range_ip: "AK,KQ,KJ,KT,QQ,JJ,TT,99,A9s,98s,55".to_string(),
        tree: TreeConfig {
            starting_pot: POT,
            effective_stack: 100.0,
            oop: [sizing(""), sizing(""), sizing("100")],
            ip: [sizing(""), sizing(""), sizing("")],
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
            oop: [sizing(""), sizing("75"), sizing("75")],
            ip: [sizing(""), sizing("75"), sizing("75")],
            ..Default::default()
        },
    }
}

fn base(config: SpotConfig, storage: Storage, iso: bool, iters: u32) -> Solver {
    let mut s = Solver::with_storage(Arc::new(Spot::new(config).unwrap()), storage);
    s.use_isomorphism = iso;
    for _ in 0..iters {
        s.iterate();
    }
    s
}

fn bet_freq(s: &Solver, path: &[PathStep], action: usize) -> f64 {
    let view = s.node_view(path).unwrap();
    let p = view.player.unwrap() as usize;
    let (mut tot, mut acc) = (0f64, 0f64);
    for h in &view.players[p].hands {
        if let Some(st) = &h.strategy {
            tot += h.reach as f64;
            acc += h.reach as f64 * st[action] as f64;
        }
    }
    acc / tot
}

/// Same fit, same start: CPU and GPU land on the same bounty and lock.
#[test]
fn gpu_fit_matches_cpu_on_the_river() {
    let target = [0.25f32, 0.75];
    let mut cpu = base(river(), Storage::F32, true, 400);
    let mut host = base(river(), Storage::F32, true, 400);
    cpu.add_fit(ROOT, &target, "fit".into()).unwrap();
    host.add_fit(ROOT, &target, "fit".into()).unwrap();
    host.prepare_fits();
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..600 {
        cpu.iterate();
        gpu.iterate().unwrap();
    }
    // the GPU best response treats the fit as its future lock
    let x_gpu = gpu.exploitability(&host).unwrap() / POT * 100.0;
    gpu.sync_to_cpu(&mut host).unwrap();
    gpu.download_fits(&mut host).unwrap();
    let x_host = host.exploitability() / POT * 100.0;
    let x_cpu = cpu.exploitability() / POT * 100.0;
    let (bc, bg) = (cpu.fits_view()[0].bounty_pct_pot.clone(), host.fits_view()[0].bounty_pct_pot.clone());
    eprintln!("exploitability cpu {x_cpu:.4} gpu {x_gpu:.4} host {x_host:.4}; bounty cpu {bc:?} gpu {bg:?}");
    assert!((x_gpu - x_host).abs() < 0.01, "GPU readout {x_gpu} vs CPU on GPU arenas {x_host}");
    assert!(x_gpu < 0.05 && x_cpu < 0.05);
    for a in 0..2 {
        assert!((bc[a] - bg[a]).abs() < 0.5 + 0.1 * bc[a].abs(), "bounty {bc:?} vs {bg:?}");
    }
    assert!(host.fit_max_error() < 0.005, "{:?}", host.fits_view());
    cpu.materialize_fits().unwrap();
    host.materialize_fits().unwrap();
    let (lc, lg) = (&cpu.locks[&0], &host.locks[&0]);
    let diff = lc.iter().zip(lg).map(|(a, b)| (a - b).abs()).fold(0f32, f32::max);
    assert!(diff < 0.1, "locked strategies differ by {diff}");
}

/// Fit below a chance node with isomorphism and compressed host storage,
/// added while the GPU solve is already running.
#[test]
fn gpu_fit_added_mid_solve_below_a_chance_node() {
    let path = vec![
        PathStep::Action { index: 0 },
        PathStep::Action { index: 0 },
        PathStep::Card { card: "3s".into() },
    ];
    for storage in [Storage::F32, Storage::Compressed] {
        let mut host = base(turn(), storage, true, 50);
        let mut gpu = GpuSolver::new(&host).unwrap();
        for _ in 0..100 {
            gpu.iterate().unwrap();
        }
        gpu.sync_to_cpu(&mut host).unwrap();
        host.add_fit(&path, &[0.4, 0.6], "river fit".into()).unwrap();
        // the server's order: pull dual state, restart fresh fits, upload
        gpu.download_fits(&mut host).unwrap();
        let fresh = host.prepare_fits();
        assert_eq!(fresh.len(), 1);
        gpu.update_locks(&host).unwrap();
        gpu.update_fits(&host, &fresh).unwrap();
        for _ in 0..400 {
            gpu.iterate().unwrap();
        }
        gpu.sync_fit_lines(&mut host).unwrap();
        gpu.download_fits(&mut host).unwrap();
        let v = host.fits_view();
        eprintln!("{storage:?}: {:?}", v[0]);
        assert!(v[0].max_error < 0.01, "{storage:?}: {:?}", v[0]);
        let x = gpu.exploitability(&host).unwrap() / POT * 100.0;
        assert!(x < 0.1, "{storage:?}: exploitability {x}");
        gpu.sync_to_cpu(&mut host).unwrap();
        host.materialize_fits().unwrap();
        host.ensure_symmetric();
        let f = bet_freq(&host, &path, 1);
        assert!((f - 0.6).abs() < 1e-3, "{storage:?}: locked bet {f}");
    }
}

/// Removing every fit puts the GPU back on the plain solve: the captured
/// graphs are rebuilt without the fit kernels.
#[test]
fn gpu_fit_cancel_restores_plain_solve() {
    let mut host = base(river(), Storage::F32, true, 100);
    host.add_fit(ROOT, &[0.5, 0.5], "fit".into()).unwrap();
    host.prepare_fits();
    let mut gpu = GpuSolver::new(&host).unwrap();
    for _ in 0..50 {
        gpu.iterate().unwrap();
    }
    assert_eq!(host.clear_fits(), 1);
    gpu.update_locks(&host).unwrap();
    gpu.update_fits(&host, &[]).unwrap();
    for _ in 0..300 {
        gpu.iterate().unwrap();
    }
    let x = gpu.exploitability(&host).unwrap() / POT * 100.0;
    assert!(x < 0.05, "plain solve after cancel: {x}% pot");
}
