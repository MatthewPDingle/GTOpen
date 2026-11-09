//! The learned flop correction on the GPU must price as leaf_correction()
//! does on the CPU, before and after the host refreshes and re-uploads it.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::leafnet::constant_net;
use crate::preflop::PreflopConfig;

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

/// Different per class and per side, so a swapped seat or class shows.
fn pattern(scale: f32, tilt: f32) -> Vec<f32> {
    (0..2 * NUM_CLASSES)
        .map(|k| scale * (((k * 7) % 11) as f32 - 5.0) / 5.0 + if k < NUM_CLASSES { tilt } else { -2.0 * tilt })
        .collect()
}

fn close(a: &(Vec<f64>, Vec<f64>), b: &(Vec<f64>, Vec<f64>)) -> bool {
    a.0.iter().chain(&a.1).zip(b.0.iter().chain(&b.1)).all(|(x, y)| (x - y).abs() < 5e-3)
}

#[test]
fn learned_corrections_match_the_cpu() {
    for n in [2usize, 3] {
        // the plan the server picks (shared evaluation where it fits), then the normal plan
        for fast in [true, false] {
            let mut posts = vec![0.0; n];
            posts[n - 2] = 0.5;
            posts[n - 1] = 1.0;
            let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(), "stack": 30.0,
                "posts": posts, "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
                "add_allin": true, "rake_pct": 5.0, "rake_cap": 2.0, "realization": "leafnet",
            })).unwrap();
            let mut s = PreflopSolver::new(cfg, table()).unwrap();
            s.install_leaf_net(Arc::new(constant_net(&pattern(0.04, 0.01)))).unwrap();
            s.leaf.as_mut().unwrap().interval = u32::MAX; // refreshes driven here
            for _ in 0..20 {
                s.iterate();
            }
            s.refresh_leaf_values().unwrap();
            let (mut g, name) = if fast {
                let (g, selection) = PreflopGpu::new_throughput(&s, 2000).expect("test requires CUDA");
                (g, selection.mode)
            } else {
                (PreflopGpu::new(&s, 2000).expect("test requires CUDA"), "normal")
            };
            let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
            assert!(close(&cpu, &gpu), "{n} seats, {name} plan, uploaded at build: cpu {cpu:?} gpu {gpu:?}");
            // the corrections move the values (so the comparison means something)
            let saved = s.leaf.take();
            let plain = s.gaps_and_evs();
            s.leaf = saved;
            assert!(!close(&cpu, &plain), "{n} seats: the correction changes nothing");

            // learn on the device (captured sweeps), refresh on the host, re-upload
            for _ in 0..10 {
                g.iterate(&mut s).unwrap();
            }
            g.sync_to_cpu(&mut s).unwrap();
            s.leaf.as_mut().unwrap().net = Arc::new(constant_net(&pattern(-0.05, 0.02)));
            s.refresh_leaf_values().unwrap();
            g.upload_leaf_corr(&s).unwrap();
            let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
            assert!(close(&cpu, &gpu), "{n} seats, {name} plan, re-uploaded: cpu {cpu:?} gpu {gpu:?}");
            // and the device keeps agreeing after learning against the new values
            g.iterate(&mut s).unwrap();
            g.sync_to_cpu(&mut s).unwrap();
            let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
            assert!(close(&cpu, &gpu), "{n} seats, {name} plan, after learning: cpu {cpu:?} gpu {gpu:?}");
        }
    }
}
