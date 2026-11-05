//! ICM terminals on the GPU must price exactly as icm_terminal_value() on
//! the CPU: fold wins, single pots under each continuation and multiway
//! model, the 3-way table, and side pots; and an ICM game must solve.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::three_way::tests::small;
use crate::preflop::{IcmConfig, PreflopConfig};

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

fn icm(mut c: PreflopConfig, payouts: &[f64], field: &[f64]) -> PreflopConfig {
    c.icm = Some(IcmConfig { payouts: payouts.to_vec(), field: field.to_vec(), field_groups: vec![], stack_off: 1.0 });
    c
}

fn configs() -> Vec<PreflopConfig> {
    let short: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "stack": 25.0, "stacks": [25.0, 4.0, 18.0], "open_raises": [2.5], "ante": 0.125,
        "raise_mults": [3.0], "max_raises": 3, "add_allin": true, "limp": true, "realization": "raw"
    })).unwrap();
    let four: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
        "stack": 30.0, "stacks": [30.0, 8.0, 15.0, 22.0], "open_raises": [2.5],
        "raise_mults": [3.0], "max_raises": 1, "add_allin": true, "limp": true, "realization": "raw"
    })).unwrap();
    let equal: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["HJ", "CO", "BTN", "SB", "BB"], "posts": [0, 0, 0, 0.5, 1],
        "stack": 20.0, "ante": 0.125, "open_raises": [2.0], "raise_mults": [2.5],
        "max_raises": 2, "add_allin": true, "limp": true, "realization": "balanced"
    })).unwrap();
    vec![
        icm(short, &[50.0, 30.0, 20.0], &[]),
        icm(four, &[40.0, 25.0, 15.0, 10.0, 10.0], &[12.0]),
        icm(equal, &[30.0, 20.0, 14.0, 10.0, 8.0, 6.0, 6.0, 6.0], &[20.0, 20.0, 20.0]),
    ]
}

#[test]
fn icm_terminals_match_cpu() {
    for cfg in configs() {
        for model in ["coupled_deck_v1", "legacy_product", "three_way_table_v1"] {
            let mut s = PreflopSolver::new(cfg.clone(), table()).unwrap();
            if model == "three_way_table_v1" {
                s.set_three_way_table(small()).unwrap();
            } else {
                s.set_multiway_equity_model(model).unwrap();
            }
            let mut gpu = PreflopGpu::new(&s, 4000).unwrap();
            assert!(gpu.icm.is_some());
            let terms: Vec<usize> = (0..s.nodes.len()).filter(|&i| s.nodes[i].kind != KIND_ACTION).collect();
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            gpu.down(1, 0).unwrap();
            // Uneven unit-mass ranges, so seats and classes differ.
            let mut reaches = gpu.stream.clone_dtoh(&gpu.d_reach).unwrap();
            for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                for (h, x) in r.iter_mut().enumerate() { *x *= 1.0 + ((h * 7 + block) % 5) as f32; }
                let mass: f32 = r.iter().sum();
                if mass > 0.0 { for x in r { *x /= mass; } }
            }
            gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
            unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                .launch(LaunchConfig { block_dim: (128, 1, 1), ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap(); }
            // Heads-up pots read cached equities of the replaced reach.
            gpu.refresh_eq_cache(s.n).unwrap();
            let mut worst = 0f32;
            // Twice through the seats: each pass must rewrite what the last left.
            for p in (0..s.n).chain(0..s.n) {
                gpu.terminals(p as i32).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                for &t in &terms {
                    let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                        let base = sources[t * s.n + q] as usize * NUM_CLASSES;
                        reaches[base..base + NUM_CLASSES].to_vec()
                    }).collect();
                    let mut expected = vec![0f32; NUM_CLASSES];
                    s.terminal_value(t, p, &local, &mut expected);
                    let base = slots[t] as usize * NUM_CLASSES;
                    let tolerance = 1e-4 * (1.0 + s.nodes[t].pot as f32);
                    for h in 0..NUM_CLASSES {
                        let err = (actual[base + h] - expected[h]).abs();
                        worst = worst.max(err);
                        assert!(err <= tolerance,
                            "{model}, {} seats, terminal {t} (live {:b}, {} pots), p {p}, h {h}: gpu {} vs cpu {}",
                            s.n, s.nodes[t].live, s.nodes[t].side_pots.len(), actual[base + h], expected[h]);
                    }
                }
            }
            eprintln!("{model}, {} seats: worst ICM terminal error {worst:e}", s.n);
        }
    }
}

#[test]
fn icm_games_take_the_normal_plan_and_solve() {
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "stack": 10.0, "stacks": [10.0, 4.0, 7.0], "ante": 0.125, "open_raises": [2.0],
        "raise_mults": [], "max_raises": 2, "add_allin": true, "realization": "raw"
    })).unwrap();
    let cfg = icm(cfg, &[50.0, 30.0, 20.0], &[]);
    let mut on_gpu = PreflopSolver::new(cfg.clone(), table()).unwrap();
    assert!(PreflopGpu::new_with_cohort_mode(&on_gpu, 2000, true, false, true, false).err().unwrap().contains("ICM"));
    let (mut gpu, selection) = PreflopGpu::new_throughput(&on_gpu, 2000).unwrap();
    assert_eq!(selection.mode, "normal_gpu");
    assert!(!selection.static_cdf);
    let mut on_cpu = PreflopSolver::new(cfg, table()).unwrap();
    for _ in 0..200 {
        gpu.iterate(&mut on_gpu).unwrap();
        on_cpu.iterate();
    }
    gpu.sync_to_cpu(&mut on_gpu).unwrap();
    // The CPU's own ICM best responses grade both strategies.
    let (g, c): (f64, f64) = (on_gpu.br_gaps().iter().sum(), on_cpu.br_gaps().iter().sum());
    eprintln!("ICM gap sums after 200 iterations: gpu {g:.5} bb, cpu {c:.5} bb");
    assert!(g.is_finite() && g <= 1.5 * c + 0.02, "gpu {g} vs cpu {c}");
}
