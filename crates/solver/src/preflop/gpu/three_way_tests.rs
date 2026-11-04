//! The 3-way table on the GPU must price exactly as on the CPU: single-pot
//! 3-way terminals, 3-seat side pots, and coupled-deck 4+ way pots alongside.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::PreflopConfig;
use crate::preflop::three_way::tests::small;

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

fn configs() -> Vec<PreflopConfig> {
    let equal: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0], "stack": 20.0,
        "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 2, "add_allin": true,
        "limp": true, "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    })).unwrap();
    let short: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["BTN", "SB", "BB"], "posts": [0.0, 0.5, 1.0],
        "stack": 40.0, "stacks": [40.0, 3.0, 40.0], "open_raises": [2.5],
        "raise_mults": [3.0], "max_raises": 3, "add_allin": true,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    })).unwrap();
    let four: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["CO", "BTN", "SB", "BB"], "posts": [0.0, 0.0, 0.5, 1.0],
        "stack": 40.0, "stacks": [40.0, 8.0, 20.0, 40.0], "open_raises": [2.5],
        "raise_mults": [3.0], "max_raises": 1, "add_allin": true, "limp": true,
        "rake_pct": 5.0, "rake_cap": 3.0, "realization": "raw"
    })).unwrap();
    vec![equal, short, four]
}

#[test]
fn three_way_table_terminals_match_cpu() {
    for cfg in configs() {
        let mut s = PreflopSolver::new(cfg, table()).unwrap();
        s.set_three_way_table(small()).unwrap();
        let mut gpu = PreflopGpu::new(&s, 4000).unwrap();
        assert_eq!(gpu.use_tw, 1);
        let three: Vec<usize> = (0..s.nodes.len()).filter(|&i| s.nodes[i].kind == KIND_POT_SHARE && s.nodes[i].live.count_ones() >= 3).collect();
        assert!(!three.is_empty());
        if s.n == 4 {
            assert!(gpu.use_multiway != 0, "4-way pots stay on the coupled kernels");
            assert!(three.iter().any(|&i| s.nodes[i].live.count_ones() == 3));
        }
        let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
        let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        gpu.down(1, 0).unwrap();
        let mut reaches = gpu.stream.clone_dtoh(&gpu.d_reach).unwrap();
        for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
            for (h, x) in r.iter_mut().enumerate() { *x *= 1.0 + ((h * 7 + block) % 5) as f32; }
            let mass: f32 = r.iter().sum();
            if mass > 0.0 { for x in r { *x /= mass; } }
        }
        gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
        unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
            .launch(LaunchConfig { block_dim: (128, 1, 1), ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap(); }
        // Manual reach replacement bypasses down(): refresh the HU cache too.
        if gpu.use_eq_cache != 0 {
            let (start, count) = gpu.eq_spans[s.n];
            if count > 0 {
                unsafe { gpu.stream.launch_builder(&gpu.f_equities)
                    .arg(&gpu.d_eq_work).arg(&start).arg(&gpu.d_eq_blocks).arg(&gpu.d_eq)
                    .arg(&gpu.d_reach).arg(&gpu.d_reach_mass).arg(&mut gpu.d_eq_cache)
                    .launch(PreflopGpu::cfg(count)).unwrap(); }
            }
        }
        for p in 0..s.n {
            gpu.terminals(p as i32).unwrap();
            let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
            for &t in &three {
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let base = sources[t * s.n + q] as usize * NUM_CLASSES;
                    reaches[base..base + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(t, p, &local, &mut expected);
                let base = slots[t] as usize * NUM_CLASSES;
                let tolerance = 3e-5 * (1.0 + s.nodes[t].pot as f32);
                for h in 0..NUM_CLASSES {
                    assert!((actual[base + h] - expected[h]).abs() <= tolerance,
                        "{} seats, terminal {t} (live {:b}, {} pots), p {p}, h {h}: gpu {} vs cpu {}",
                        s.n, s.nodes[t].live, s.nodes[t].side_pots.len(), actual[base + h], expected[h]);
                }
            }
        }
    }
}

#[test]
fn three_way_table_takes_the_normal_plan() {
    let mut s = PreflopSolver::new(configs().remove(0), table()).unwrap();
    s.set_three_way_table(small()).unwrap();
    assert!(PreflopGpu::new_with_cohort_mode(&s, 4000, true, false, true, false).err().unwrap().contains("3-way table"));
    let gpu = PreflopGpu::new(&s, 4000).unwrap();
    assert_eq!(gpu.use_multiway, 0, "a 3-handed game needs no coupled kernels under the table");
    assert!(!gpu.exact_reuse_compatible());
    let (_, selection) = PreflopGpu::new_throughput(&s, 4000).unwrap();
    assert_eq!(selection.mode, "normal_gpu");
}
