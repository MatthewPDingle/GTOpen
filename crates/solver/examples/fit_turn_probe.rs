//! Probe: trace a least-exploitable fit at a turn node below the flop's
//! chance node (OOP, after check-check, 4c), on the CPU or the GPU.
//!   cargo run --release -p solver --example fit_turn_probe -- [warm] [cpu|gpu] [small|bench] [max fit iterations]
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
        "{it}: x {x:.3}% achieved {:?} current {:?} bounty%pot {:?} err {:.4}",
        f.achieved, f.current, f.bounty_pct_pot, f.max_error
    );
}

/// Per-hand picture at the fit node (average strategies, bounty excluded):
/// how far apart the two actions' EVs are, in pots, by reach mass.
fn diagnose(s: &Solver, path: &[PathStep]) {
    let v = s.node_view(path).unwrap();
    let p = v.player.unwrap() as usize;
    let pot = v.pot;
    let mut rows: Vec<(f64, f64, f64, String)> = Vec::new(); // (reach, ev gap bet-check in pots, bet freq, combo)
    for h in &v.players[p].hands {
        if let (Some(st), Some(evs)) = (&h.strategy, &h.evs) {
            if let (Some(c), Some(b)) = (evs[0], evs[evs.len() - 1]) {
                if h.reach > 0.0 {
                    rows.push((h.reach as f64, (b - c) as f64 / pot, st[st.len() - 1] as f64, h.combo.clone()));
                }
            }
        }
    }
    let tot: f64 = rows.iter().map(|r| r.0).sum();
    println!("node pot {pot}, actions {:?}, {} hands with reach", v.actions.iter().map(|a| a.label.clone()).collect::<Vec<_>>(), rows.len());
    for (lo, hi) in [(-1e9, -6.0), (-6.0, -2.0), (-2.0, -1.0), (-1.0, -0.25), (-0.25, -0.02), (-0.02, 0.02), (0.02, 0.25), (0.25, 1.0), (1.0, 1e9)] {
        let sel: Vec<_> = rows.iter().filter(|r| r.1 >= lo && r.1 < hi).collect();
        let m: f64 = sel.iter().map(|r| r.0).sum();
        let bf: f64 = sel.iter().map(|r| r.0 * r.2).sum::<f64>() / m.max(1e-30);
        println!("  gap [{lo:>6}, {hi:>6}) pots: reach share {:.3}, bet freq {:.3}", m / tot, bf);
    }
    // cumulative regrets at the node, in pot x opponent-reach units: what a
    // bounty of b pots must outweigh, at b per iteration
    let idx = s.walk_path(path).unwrap().node_idx;
    let node = &s.spot.tree.nodes[idx as usize];
    let nh = s.spot.hands[p].len();
    let omega: f64 = v.players[1 - p].hands.iter().map(|h| h.reach as f64).sum();
    let reg = match &s.regrets[p] {
        solver::store::Store::F32(b) => unsafe { b.slice(node.data_offset, 2 * nh) }.to_vec(),
        _ => vec![],
    };
    println!("  opponent reach mass {omega:.4}, iteration {}", s.iteration);
    let combos: Vec<String> = s.spot.hands[p].iter().map(|h| solver::cards::combo_to_string(h.c1, h.c2)).collect();
    rows.sort_by(|a, b| b.0.total_cmp(&a.0));
    for r in rows.iter().take(12) {
        let i = combos.iter().position(|c| *c == r.3);
        let (rc, rb) = match i {
            Some(i) if !reg.is_empty() => (reg[i] as f64 / (pot * omega), reg[nh + i] as f64 / (pot * omega)),
            _ => (f64::NAN, f64::NAN),
        };
        println!("  {} reach {:.4} gap {:+.3} pots bet {:.3} | R_check {rc:+.2} R_bet {rb:+.2} (pot-iterations)", r.3, r.0 / tot, r.1, r.2);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let warm: u32 = args.get(1).map(|a| a.parse().unwrap()).unwrap_or(0);
    let use_gpu = args.get(2).map(|a| a == "gpu").unwrap_or(false);
    let cfg = match args.get(3).map(|a| a.as_str()) {
        Some("bench") => serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap(),
        Some("deep") => {
            let mut c = small();
            c.tree.effective_stack = 970.0;
            c.tree.oop = [sz("33", "60"), sz("75", "60"), sz("75", "60")];
            c.tree.ip = [sz("33", "60"), sz("75", "60"), sz("75", "60")];
            c
        }
        _ => small(),
    };
    let path = vec![PathStep::Action { index: 0 }, PathStep::Action { index: 0 }, PathStep::Card { card: "4c".into() }];
    let target = [0.66f32, 0.34];
    let max: u32 = args.get(4).map(|a| a.parse().unwrap()).unwrap_or(2000);
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
            if it == max {
                break;
            }
        }
        diagnose(&s, &path);
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
            if it == max {
                break;
            }
        }
        gpu.sync_to_cpu(&mut s).unwrap();
        diagnose(&s, &path);
    }
    #[cfg(not(feature = "gpu"))]
    panic!("build with --features gpu");
}
