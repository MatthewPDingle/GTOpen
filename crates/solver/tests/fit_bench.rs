//! Manual benchmarks for least-exploitable frequency locks.
//!
//! Quality (CPU, river spots): how much EV the locked player gives up against
//! a best response, versus the unconstrained solve, for the three ways of
//! locking a node to a frequency: raking (Scale), the quick fit (Least EV
//! loss) and the full fit (Least exploitable).
//!   cargo test --release -p solver --test fit_bench -- --ignored --nocapture fit_quality
//!
//! Cost (CPU, or CUDA with --features gpu): iterations and seconds to reach
//! the exploitability target with a fit running, from scratch and warm,
//! against the plain solve.
//!   cargo test --release -p solver --test fit_bench -- --ignored --nocapture fit_cost_cpu
//!   cargo test --release -p solver --features gpu --test fit_bench -- --ignored --nocapture fit_cost_gpu

use solver::fit::FIT_TOLERANCE;
use solver::game::Dealt;
use solver::query::PathStep;
use solver::tree::{parse_sizes, StreetSizing, TreeConfig};
use solver::{LockMode, Solver, Spot, SpotConfig};
use std::sync::Arc;
use std::time::Instant;

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: parse_sizes(raise).unwrap(), donk: vec![] }
}

fn act(index: usize) -> PathStep {
    PathStep::Action { index }
}

/// The locked player's chips against a best response, per pair, from the
/// river start. Zero-sum (no rake), so it is minus the opponent's BR value.
fn value_vs_br(s: &Solver, p: usize) -> f64 {
    let spot = &*s.spot;
    let o = 1 - p;
    let cfv = s.traverse_br(0, o, &spot.weights[p], Dealt::default());
    let br: f64 = spot.weights[o].iter().zip(&cfv).map(|(&w, &v)| w as f64 * v as f64).sum();
    -br / s.pair_weight_sum()
}

/// Reach-weighted action frequencies of the acting player at a node.
fn freqs_at(s: &Solver, path: &[PathStep]) -> Vec<f64> {
    let view = s.node_view(path).unwrap();
    let p = view.player.unwrap() as usize;
    let na = view.actions.len();
    let (mut tot, mut acc) = (0f64, vec![0f64; na]);
    for h in &view.players[p].hands {
        if let Some(st) = &h.strategy {
            tot += h.reach as f64;
            for a in 0..na {
                acc[a] += h.reach as f64 * st[a] as f64;
            }
        }
    }
    acc.iter().map(|x| x / tot).collect()
}

fn pct(s: &Solver) -> f64 {
    s.exploitability() / s.spot.tree.config.starting_pot * 100.0
}

fn fmt_freqs(f: &[f64]) -> String {
    f.iter().map(|x| format!("{:.0}", x * 100.0)).collect::<Vec<_>>().join("/")
}

struct Case {
    name: &'static str,
    config: SpotConfig,
    path: Vec<PathStep>,
}

fn river_cases() -> Vec<Case> {
    let polar = SpotConfig {
        board: "Ks9h5d3c2s".to_string(),
        range_oop: "AA,KK,99,AK,KQ,KJs,K9s,QJ,JT,T8s,76s,A4s,64s".to_string(),
        range_ip: "AK,KQ,KJ,KT,QQ,JJ,TT,99,A9s,98s,55".to_string(),
        tree: TreeConfig {
            starting_pot: 100.0,
            effective_stack: 100.0,
            oop: [sizing("", ""), sizing("", ""), sizing("100", "")],
            ip: [sizing("", ""), sizing("", ""), sizing("", "")],
            ..Default::default()
        },
    };
    let wide_tree = TreeConfig {
        starting_pot: 60.0,
        effective_stack: 240.0,
        oop: [sizing("", ""), sizing("", ""), sizing("33,75,150", "60")],
        ip: [sizing("", ""), sizing("", ""), sizing("50,100", "60")],
        ..Default::default()
    };
    let wide = SpotConfig {
        board: "Ks7h2d5c9s".to_string(),
        range_oop: "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o".to_string(),
        range_ip: "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo".to_string(),
        tree: wide_tree,
    };
    vec![
        Case { name: "polar river, OOP check/jam", config: polar, path: vec![] },
        Case { name: "wide river, OOP 4 options", config: wide.clone(), path: vec![] },
        Case { name: "wide river, IP after check", config: wide, path: vec![act(0)] },
    ]
}

/// Targets that a user would plausibly lock: halfway to uniform, and the
/// biggest action's frequency shifted to the passive action.
fn targets(gto: &[f64]) -> Vec<(String, Vec<f32>)> {
    let n = gto.len() as f64;
    let half: Vec<f32> = gto.iter().map(|&g| (0.5 * g + 0.5 / n) as f32).collect();
    let mut shift: Vec<f32> = gto.iter().map(|&g| g as f32).collect();
    let big = (1..gto.len()).max_by(|&a, &b| gto[a].total_cmp(&gto[b])).unwrap_or(1);
    let moved = shift[big] * 0.5;
    shift[big] -= moved;
    shift[0] += moved;
    let mut out = vec![("halfway to uniform".to_string(), half), ("half of the main bet to check".to_string(), shift)];
    if gto.len() == 2 {
        out.push(("bet 25%".to_string(), vec![0.75, 0.25]));
        out.push(("bet 75%".to_string(), vec![0.25, 0.75]));
    }
    out
}

const BASE_ITERS: u32 = 1000;
const RESOLVE_ITERS: u32 = 1000;

fn solve(config: &SpotConfig, iters: u32) -> Solver {
    let mut s = Solver::new(Arc::new(Spot::new(config.clone()).unwrap()));
    for _ in 0..iters {
        s.iterate();
    }
    s
}

#[test]
#[ignore = "manual benchmark"]
fn fit_quality() {
    println!("EV given up against a best response, % of pot, versus the unconstrained solve");
    println!("(lower is better; each lock is followed by {RESOLVE_ITERS} re-solve iterations)");
    for case in river_cases() {
        let base = solve(&case.config, BASE_ITERS);
        let p = base.node_view(&case.path).unwrap().player.unwrap() as usize;
        let pot = base.spot.tree.config.starting_pot;
        let gto = freqs_at(&base, &case.path);
        let v0 = value_vs_br(&base, p);
        println!("\n{}: solved to {:.3}% pot, node frequencies {}", case.name, pct(&base), fmt_freqs(&gto));
        for (label, target) in targets(&gto) {
            let mut row = Vec::new();
            for method in ["rake", "quick", "full"] {
                let mut s = solve(&case.config, BASE_ITERS);
                match method {
                    "rake" => drop(s.lock_node(&case.path, LockMode::Range { freqs: target.clone() }, "b".into()).unwrap()),
                    "quick" => drop(s.lock_node(&case.path, LockMode::Fit { freqs: target.clone() }, "b".into()).unwrap()),
                    _ => drop(s.add_fit(&case.path, &target, "b".into()).unwrap()),
                }
                for _ in 0..RESOLVE_ITERS {
                    s.iterate();
                }
                if method == "full" {
                    s.materialize_fits().unwrap();
                }
                let got = freqs_at(&s, &case.path);
                let off = got.iter().zip(&target).map(|(a, &b)| (a - b as f64).abs()).fold(0.0, f64::max);
                assert!(off < 1e-3, "{method} locked at {got:?}, target {target:?}");
                let loss = (v0 - value_vs_br(&s, p)) / pot * 100.0;
                row.push(format!("{method} {loss:7.3}"));
            }
            let t: Vec<f64> = target.iter().map(|&x| x as f64).collect();
            println!("  {:<32} target {:<14} {}", label, fmt_freqs(&t), row.join("   "));
        }
    }
}

/// Iterations until exploitability <= target and every fit is within
/// tolerance, checking every `every` iterations.
fn run_cpu(s: &mut Solver, target_pct: f64, every: u32, max: u32) -> (u32, f64, f64) {
    let start = Instant::now();
    let mut done = 0;
    loop {
        for _ in 0..every {
            s.iterate();
        }
        done += every;
        let x = pct(s);
        let err = if s.has_fits() { s.fit_max_error() } else { 0.0 };
        if (x <= target_pct && err <= FIT_TOLERANCE as f64) || done >= max {
            return (done, start.elapsed().as_secs_f64(), x);
        }
    }
}

#[test]
#[ignore = "manual benchmark"]
fn fit_cost_cpu() {
    let target_pct = 0.1;
    println!("Iterations to {target_pct}% pot (and fits within {:.1} pts)", FIT_TOLERANCE * 100.0);
    for case in river_cases() {
        let mut plain = Solver::new(Arc::new(Spot::new(case.config.clone()).unwrap()));
        let (n0, t0, _) = run_cpu(&mut plain, target_pct, 10, 20_000);
        let gto = freqs_at(&plain, &case.path);
        for (label, target) in targets(&gto).into_iter().take(2) {
            let mut scratch = Solver::new(Arc::new(Spot::new(case.config.clone()).unwrap()));
            scratch.add_fit(&case.path, &target, "b".into()).unwrap();
            let (n1, t1, _) = run_cpu(&mut scratch, target_pct, 10, 20_000);
            let mut warm = solve(&case.config, n0);
            warm.add_fit(&case.path, &target, "b".into()).unwrap();
            let (n2, t2, _) = run_cpu(&mut warm, target_pct, 10, 20_000);
            println!(
                "{} / {label}: plain {n0} it {t0:.2}s | fit from scratch {n1} it {t1:.2}s ({:.2}x) | fit warm +{n2} it {t2:.2}s",
                case.name,
                n1 as f64 / n0 as f64,
            );
        }
    }
}

#[cfg(feature = "gpu")]
mod gpu {
    use super::*;
    use solver::gpu::GpuSolver;

    fn bench_config(board: &str) -> SpotConfig {
        let mut cfg: SpotConfig = serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
        cfg.board = board.into();
        cfg
    }

    fn gpu_pct(gpu: &mut GpuSolver, host: &Solver) -> f64 {
        gpu.exploitability(host).unwrap() / host.spot.tree.config.starting_pot * 100.0
    }

    /// Iterate until exploitability <= target and fits converge, checking
    /// every `every` iterations the way the server does.
    fn run(gpu: &mut GpuSolver, host: &mut Solver, target_pct: f64, every: u32, max: u32) -> (u32, f64, f64, f64) {
        let start = Instant::now();
        let mut done = 0;
        loop {
            for _ in 0..every {
                gpu.iterate().unwrap();
            }
            done += every;
            let x = gpu_pct(gpu, host);
            let mut err = 0.0;
            if host.has_fits() {
                gpu.sync_fit_lines(host).unwrap();
                gpu.download_fits(host).unwrap();
                err = host.fit_max_error();
            }
            if (x <= target_pct && err <= FIT_TOLERANCE as f64) || done >= max {
                return (done, start.elapsed().as_secs_f64(), x, err);
            }
        }
    }

    fn ms_per_iteration(gpu: &mut GpuSolver) -> f64 {
        gpu.synchronize().unwrap();
        let start = Instant::now();
        for _ in 0..40 {
            gpu.iterate().unwrap();
        }
        gpu.synchronize().unwrap();
        start.elapsed().as_secs_f64() * 1000.0 / 40.0
    }

    #[test]
    #[ignore = "manual CUDA benchmark"]
    fn fit_cost_gpu() {
        let target_pct = 0.3;
        let every = 20;
        let max = 4000;
        println!("bench_spot.json, iterations to {target_pct}% pot (and fits within {:.1} pts)", FIT_TOLERANCE * 100.0);
        // root of the flop; a turn decision below the chance node; a river root
        let cases: Vec<(&str, &str, Vec<PathStep>)> = vec![
            ("flop root (OOP)", "Ks7h2d", vec![]),
            ("flop IP after check", "Ks7h2d", vec![act(0)]),
            (
                "turn OOP after check-check, 4c",
                "Ks7h2d",
                vec![act(0), act(0), PathStep::Card { card: "4c".into() }],
            ),
            ("river root (OOP)", "Ks7h2dQhTc", vec![]),
        ];
        for (name, board, path) in cases {
            let cfg = bench_config(board);
            // plain solve from scratch
            let mut plain = Solver::new(Arc::new(Spot::new(cfg.clone()).unwrap()));
            let mut gpu = GpuSolver::new(&plain).unwrap();
            let ms_plain = ms_per_iteration(&mut gpu);
            let mut gpu = GpuSolver::new(&plain).unwrap();
            let (n0, t0, x0, _) = run(&mut gpu, &mut plain, target_pct, every, max);
            gpu.sync_to_cpu(&mut plain).unwrap();
            let gto = freqs_at(&plain, &path);
            let (label, target) = targets(&gto).remove(0);

            // fit from scratch
            let mut host = Solver::new(Arc::new(Spot::new(cfg.clone()).unwrap()));
            host.add_fit(&path, &target, "b".into()).unwrap();
            host.prepare_fits();
            let mut g = GpuSolver::new(&host).unwrap();
            let ms_fit = ms_per_iteration(&mut g);
            let mut host = Solver::new(Arc::new(Spot::new(cfg.clone()).unwrap()));
            host.add_fit(&path, &target, "b".into()).unwrap();
            host.prepare_fits();
            let mut g = GpuSolver::new(&host).unwrap();
            let (n1, t1, x1, e1) = run(&mut g, &mut host, target_pct, every, max);

            // fit added to the finished plain solve, the server's order
            plain.add_fit(&path, &target, "b".into()).unwrap();
            gpu.download_fits(&mut plain).unwrap();
            let fresh = plain.prepare_fits();
            gpu.update_locks(&plain).unwrap();
            gpu.update_fits(&plain, &fresh).unwrap();
            let (n2, t2, x2, e2) = run(&mut gpu, &mut plain, target_pct, every, max);
            gpu.sync_to_cpu(&mut plain).unwrap();
            plain.materialize_fits().unwrap();
            let locked = freqs_at(&plain, &path);

            let t: Vec<f64> = target.iter().map(|&x| x as f64).collect();
            println!(
                "\n{name}: solved {} -> target {} ({label}), locked {}\n  ms/iteration plain {ms_plain:.3} fit {ms_fit:.3} ({:+.1}%)\n  plain {n0} it {t0:.2}s ({x0:.3}%) | from scratch {n1} it {t1:.2}s ({x1:.3}%, off {:.2} pts, {:.2}x) | warm +{n2} it {t2:.2}s ({x2:.3}%, off {:.2} pts)",
                fmt_freqs(&gto),
                fmt_freqs(&t),
                fmt_freqs(&locked),
                (ms_fit / ms_plain - 1.0) * 100.0,
                e1 * 100.0,
                n1 as f64 / n0 as f64,
                e2 * 100.0,
            );
        }
    }
}
