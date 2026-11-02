//! Probe: trace a least-exploitable fit at a turn node below the flop's
//! chance node (OOP, after check-check, 4c), on the CPU or the GPU.
//!   cargo run --release -p solver --example fit_turn_probe -- [warm] [cpu|gpu] [small|bench]
//! (gpu needs --features gpu)
use solver::query::PathStep;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{Solver, Spot, SpotConfig};
use std::sync::Arc;

fn sz(b: &str, r: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(b).unwrap(), raise: parse_sizes(r).unwrap(), donk: vec![] }
}

fn small() -> SpotConfig {
    SpotConfig {
        board: "Ks7h2d".into(),
        range_oop: "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,98s,87s,76s,65s,54s,AJo-A8o,KTo-K9o,QJo,JTo".into(),
        range_ip: "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo".into(),
        tree: TreeConfig {
            starting_pot: 60.0,
            effective_stack: 300.0,
            oop: [sz("33", ""), sz("75", ""), sz("75", "")],
            ip: [sz("33", ""), sz("75", ""), sz("75", "")],
            ..Default::default()
        },
    }
}

fn line(it: u32, s: &Solver, x: f64) {
    let f = &s.fits_view()[0];
    println!(
        "{it}: x {x:.3}% achieved {:?} bounty%pot {:?} err {:.4}",
        f.achieved, f.bounty_pct_pot, f.max_error
    );
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let warm: u32 = args.get(1).map(|a| a.parse().unwrap()).unwrap_or(0);
    let use_gpu = args.get(2).map(|a| a == "gpu").unwrap_or(false);
    let cfg = if args.get(3).map(|a| a == "bench").unwrap_or(false) {
        serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap()
    } else {
        small()
    };
    let path = vec![PathStep::Action { index: 0 }, PathStep::Action { index: 0 }, PathStep::Card { card: "4c".into() }];
    let target = [0.66f32, 0.34];
    let mut s = Solver::new(Arc::new(Spot::new(cfg).unwrap()));
    let pot = s.spot.tree.config.starting_pot;
    println!("nodes {} warm {warm} {}", s.spot.tree.nodes.len(), if use_gpu { "gpu" } else { "cpu" });
    if !use_gpu {
        for _ in 0..warm {
            s.iterate();
        }
        s.add_fit(&path, &target, "t".into()).unwrap();
        for it in 1..=2000 {
            s.iterate();
            if it % 20 == 0 {
                let x = s.exploitability() / pot * 100.0;
                line(it, &s, x);
                if (s.fit_max_error() as f64) <= solver::fit::FIT_TOLERANCE && x < 0.3 {
                    break;
                }
            }
        }
        return;
    }
    #[cfg(feature = "gpu")]
    {
        use solver::gpu::GpuSolver;
        let mut gpu = GpuSolver::new(&s).unwrap();
        for _ in 0..warm {
            gpu.iterate().unwrap();
        }
        if warm > 0 {
            gpu.sync_to_cpu(&mut s).unwrap();
        }
        s.add_fit(&path, &target, "t".into()).unwrap();
        gpu.download_fits(&mut s).unwrap();
        let fresh = s.prepare_fits();
        gpu.update_locks(&s).unwrap();
        gpu.update_fits(&s, &fresh).unwrap();
        for it in 1..=2000 {
            gpu.iterate().unwrap();
            if it % 20 == 0 {
                let x = gpu.exploitability(&s).unwrap() / pot * 100.0;
                gpu.sync_fit_lines(&mut s).unwrap();
                gpu.download_fits(&mut s).unwrap();
                line(it, &s, x);
                if (s.fit_max_error() as f64) <= solver::fit::FIT_TOLERANCE && x < 0.3 {
                    break;
                }
            }
        }
    }
    #[cfg(not(feature = "gpu"))]
    panic!("build with --features gpu");
}
