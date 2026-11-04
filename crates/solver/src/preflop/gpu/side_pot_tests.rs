//! Side-pot terminals (unequal stacks) on the GPU must price exactly as
//! side_pot_value() on the CPU, under both multiway equity models.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::PreflopConfig;

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    // A small sample keeps the table visibly asymmetric, which is what the
    // symmetrized heads-up pots must correct for.
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

fn configs() -> Vec<PreflopConfig> {
    let three: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "stack": 40.0, "stacks": [40.0, 3.0, 40.0], "open_raises": [2.5],
        "raise_mults": [3.0], "max_raises": 3, "add_allin": true,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    })).unwrap();
    let four: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
        "stack": 40.0, "stacks": [40.0, 8.0, 20.0, 40.0], "open_raises": [2.5],
        "raise_mults": [3.0], "max_raises": 1, "add_allin": true, "limp": false,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    })).unwrap();
    vec![three, four]
}

#[test]
fn side_pot_terminals_match_cpu() {
    for cfg in configs() {
        for model in ["coupled_deck_v1", "legacy_product"] {
            let mut s = PreflopSolver::new(cfg.clone(), table()).unwrap();
            s.set_multiway_equity_model(model).unwrap();
            let side: Vec<usize> = (0..s.nodes.len()).filter(|&i| !s.nodes[i].side_pots.is_empty()).collect();
            assert!(side.iter().any(|&i| s.nodes[i].side_pots.iter().any(|&(_, m)| m.count_ones() >= 3)));
            assert!(side.iter().any(|&i| s.nodes[i].side_pots.iter().any(|&(_, m)| m.count_ones() == 2)));
            if s.n == 3 {
                // Dead money above the short stack that only one live seat can win.
                assert!(side.iter().any(|&i| s.nodes[i].side_pots.iter().any(|&(_, m)| m.count_ones() == 1)));
            }
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert_eq!(gpu.sp_nterms as usize, side.len());
            assert_eq!(gpu.use_multiway != 0, model == "coupled_deck_v1");
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            gpu.down(1, 0).unwrap();
            // Unit masses keep an absolute tolerance meaningful.
            let mut reaches = gpu.stream.clone_dtoh(&gpu.d_reach).unwrap();
            for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                // Uneven ranges, so equities differ by class and seat.
                for (h, x) in r.iter_mut().enumerate() { *x *= 1.0 + ((h * 7 + block) % 5) as f32; }
                let mass: f32 = r.iter().sum();
                if mass > 0.0 { for x in r { *x /= mass; } }
            }
            gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
            unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                .launch(LaunchConfig { block_dim: (128, 1, 1), ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap(); }
            let batches: &[u32] = if gpu.use_multiway != 0 { &[32, 7] } else { &[0] };
            for &batch in batches {
                if batch != 0 { gpu.mw_batch = batch; }
                for p in 0..s.n {
                    gpu.terminals(p as i32).unwrap();
                    let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                    for &t in &side {
                        let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                            let base = sources[t * s.n + q] as usize * NUM_CLASSES;
                            reaches[base..base + NUM_CLASSES].to_vec()
                        }).collect();
                        let mut expected = vec![0f32; NUM_CLASSES];
                        s.terminal_value(t, p, &local, &mut expected);
                        let base = slots[t] as usize * NUM_CLASSES;
                        let tolerance = 2e-5 * (1.0 + s.nodes[t].pot as f32);
                        for h in 0..NUM_CLASSES {
                            assert!((actual[base + h] - expected[h]).abs() <= tolerance,
                                "{model}, {} seats, batch {batch}, terminal {t}, p {p}, h {h}: gpu {} vs cpu {}",
                                s.n, actual[base + h], expected[h]);
                        }
                    }
                }
            }
        }
    }
}

#[test]
fn side_pot_trees_take_the_normal_plan() {
    let s = PreflopSolver::new(configs().remove(0), table()).unwrap();
    assert!(PreflopGpu::new_with_cohort_mode(&s, 2000, true, false, true, false).err().unwrap().contains("side pots"));
    let gpu = PreflopGpu::new(&s, 2000).unwrap();
    assert!(gpu.sp_nterms > 0 && !gpu.exact_reuse_compatible());
    let (_, selection) = PreflopGpu::new_throughput(&s, 2000).unwrap();
    assert_eq!(selection.mode, "normal_gpu");
    assert!(!selection.static_cdf);
}

#[test]
fn equal_stacks_have_no_side_pot_work() {
    let mut cfg = configs().remove(0);
    cfg.stacks = None;
    let s = PreflopSolver::new(cfg, table()).unwrap();
    let gpu = PreflopGpu::new(&s, 2000).unwrap();
    assert_eq!((gpu.sp_nterms, gpu.sp_ncoupled), (0, 0));
    let mw = s.nodes.iter().filter(|n| n.kind == KIND_POT_SHARE && n.live.count_ones() >= 3).count();
    assert_eq!(gpu.mw_nterms as usize, mw);
}
