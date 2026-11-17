//! Blockers (card removal) on the GPU must price every terminal as
//! removal_terminal_value() does on the CPU: folds, heads-up pots under
//! each realization (with the learned correction), 3+ way pots, side pots
//! and the exact 3-way table.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::leafnet::constant_net;
use crate::preflop::PreflopConfig;
use crate::preflop::three_way::tests::small;

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

fn close(a: &(Vec<f64>, Vec<f64>), b: &(Vec<f64>, Vec<f64>)) -> bool {
    a.0.iter().chain(&a.1).zip(b.0.iter().chain(&b.1)).all(|(x, y)| (x - y).abs() < 5e-3)
}

fn game(n: usize, realization: &str, stacks: Option<Vec<f64>>) -> PreflopConfig {
    let mut posts = vec![0.0; n];
    posts[n - 2] = 0.5;
    posts[n - 1] = 1.0;
    let mut v = serde_json::json!({
        "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(), "stack": 30.0,
        "posts": posts, "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": true, "rake_pct": 5.0, "rake_cap": 2.0, "realization": realization,
        "card_removal": true,
    });
    if let Some(stacks) = stacks {
        v["stacks"] = serde_json::json!(stacks);
    }
    serde_json::from_value(v).unwrap()
}

#[test]
fn blockers_match_the_cpu() {
    let cases: Vec<(&str, PreflopConfig, bool)> = vec![
        ("heads-up static", game(2, "static", None), false),
        ("heads-up balanced", game(2, "balanced", None), false),
        ("heads-up learned", game(2, "leafnet", None), false),
        ("3 seats static", game(3, "static", None), false),
        ("3 seats learned", game(3, "leafnet", None), false),
        ("4 seats balanced", game(4, "balanced", None), false),
        ("4 seats, side pots", game(4, "static", Some(vec![12.0, 30.0, 6.0, 20.0])), false),
        ("3 seats, exact 3-way table", game(3, "balanced", None), true),
    ];
    let mut shared_runs = 0;
    for (name, cfg, three_way) in cases {
        let learned = cfg.realization == "leafnet";
        let mut s = PreflopSolver::new(cfg, table()).unwrap();
        if three_way {
            s.set_three_way_table(small()).unwrap();
        }
        if learned {
            let pattern: Vec<f32> = (0..2 * NUM_CLASSES).map(|k| 0.04 * (((k * 7) % 11) as f32 - 5.0) / 5.0).collect();
            s.install_leaf_net(Arc::new(constant_net(&pattern))).unwrap();
            s.set_leaf_schedule(u32::MAX, Some(0.3));
        }
        for _ in 0..20 {
            s.iterate();
        }
        if learned {
            s.refresh_leaf_values().unwrap();
        }
        // The shared plan runs 3+ seat games without side pots or the 3-way
        // table; it must agree with the normal plan at the same strategies.
        let shared = s.n > 2 && !three_way && s.nodes.iter().all(|nd| nd.side_pots.is_empty());
        {
            let (mut fast, selection) = PreflopGpu::new_throughput(&s, 8000).expect("test requires CUDA");
            eprintln!("{name}: {} ({:?})", selection.mode, selection.fallback_reason);
            assert!(shared || selection.mode == "normal_gpu", "{name}: {selection:?}");
            shared_runs += (selection.mode == "retained_cohorts") as usize;
            let fast = fast.gaps_and_evs().unwrap();
            let normal = PreflopGpu::new(&s, 2000).unwrap().gaps_and_evs().unwrap();
            assert!(fast.0.iter().chain(&fast.1).zip(normal.0.iter().chain(&normal.1)).all(|(x, y)| (x - y).abs() < 2e-4),
                "{name}: shared plan {fast:?} normal plan {normal:?}");
        }
        // the plan the server picks, then the normal plan directly
        for fast in [true, false] {
            let mut g = if fast {
                PreflopGpu::new_throughput(&s, 8000).expect("test requires CUDA").0
            } else {
                PreflopGpu::new(&s, 2000).expect("test requires CUDA")
            };
            let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
            assert!(close(&cpu, &gpu), "{name}, at build: cpu {cpu:?} gpu {gpu:?}");
            // blockers move the values (so the comparison means something)
            s.cfg.card_removal = false;
            let plain = s.gaps_and_evs();
            s.cfg.card_removal = true;
            assert!(cpu.0.iter().chain(&cpu.1).zip(plain.0.iter().chain(&plain.1)).any(|(x, y)| (x - y).abs() > 1e-4),
                "{name}: blockers change nothing");
            // learn on the device, then compare again at the new strategies
            for _ in 0..10 {
                g.iterate(&mut s).unwrap();
            }
            g.sync_to_cpu(&mut s).unwrap();
            let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
            assert!(close(&cpu, &gpu), "{name}, after learning: cpu {cpu:?} gpu {gpu:?}");
        }
    }
    assert!(shared_runs >= 2, "the shared plan ran {shared_runs} of the games it should take");
}

#[test]
fn blockers_terminal_values_match_the_cpu_class_by_class() {
    for (name, cfg) in [
        ("heads-up balanced", game(2, "balanced", None)),
        ("3 seats static", game(3, "static", None)),
        ("4 seats, side pots", game(4, "static", Some(vec![12.0, 30.0, 6.0, 20.0]))),
    ] {
        let mut s = PreflopSolver::new(cfg, table()).unwrap();
        for _ in 0..15 {
            s.iterate();
        }
        // the normal plan, then the plan the server picks (the shared one
        // for the 3-seat game)
        for fast in [false, true] {
        let mut g = if fast {
            PreflopGpu::new_throughput(&s, 8000).expect("test requires CUDA").0
        } else {
            PreflopGpu::new(&s, 2000).expect("test requires CUDA")
        };
        let np = s.n;
        for p in 0..np {
            g.down(1, p as i32).unwrap();
            g.terminals(p as i32).unwrap();
            let reach: Vec<f32> = g.stream.clone_dtoh(&g.d_reach).unwrap();
            let src: Vec<u32> = g.stream.clone_dtoh(&g.d_reach_src).unwrap();
            let slots: Vec<u32> = g.stream.clone_dtoh(&g.d_val_slot).unwrap();
            let val: Vec<f32> = g.stream.clone_dtoh(&g.d_val).unwrap();
            let mut worst = 0f32;
            for (node, nd) in s.nodes.iter().enumerate() {
                if nd.kind == KIND_ACTION {
                    continue;
                }
                let local: Vec<Vec<f32>> = (0..np)
                    .map(|q| reach[src[node * np + q] as usize * NUM_CLASSES..][..NUM_CLASSES].to_vec())
                    .collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(node, p, &local, &mut expected);
                for h in 0..NUM_CLASSES {
                    let got = val[slots[node] as usize * NUM_CLASSES + h];
                    let err = (got - expected[h]).abs() / expected[h].abs().max(1e-3);
                    worst = worst.max(err);
                    assert!(err < 2e-2 || (got - expected[h]).abs() < 1e-5,
                        "{name} seat {p} node {node} class {h}: gpu {got} cpu {}", expected[h]);
                }
            }
            eprintln!("{name} seat {p}{}: worst relative difference {worst:.2e}", if fast { ", server plan" } else { "" });
        }
        }
    }
}
