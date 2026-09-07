//! Large-game correctness gate for the optional GPU equity cache.
#![cfg(feature = "gpu")]
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopConfig, PreflopSolver};
use std::sync::Arc;

#[test]
#[ignore = "manual large CUDA cached-versus-budget-fallback equivalence"]
fn tight_budget_preserves_large_game_bits() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
    let eq = Arc::new(EquityTable::load_or_build(path, 20000));
    for (n, tight_budget) in [(6, 700), (8, 1600)] {
        let mut posts = vec![0.0; n];
        posts[n - 2] = 0.5;
        posts[n - 1] = 1.0;
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
            "stack":if n == 8 {150.0} else {100.0}, "posts":posts,
            "limp":true, "open_raises":[2.5,4.0], "raise_mults":[3.0],
            "max_raises":if n == 8 {2} else {3}, "add_allin":false,
            "allin_threshold":0.85, "rake_pct":5.0, "rake_cap":3.0,
            "realization":if n == 6 {"static"} else {"calibrated"}
        })).unwrap();
        let mut expected: Option<(Vec<f32>, Vec<f32>, Vec<f64>, Vec<f64>)> = None;
        for budget in [20000, tight_budget] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            if n == 8 { assert!(s.fit.is_some(), "requires calibrated fit"); }
            // The preferred cache estimate exceeds each tight budget.
            assert!(solver::preflop::gpu::vram_estimate_mb(&s) > tight_budget as f64);
            let mut gpu = PreflopGpu::new(&s, budget).expect("requires CUDA");
            for _ in 0..65 { gpu.iterate(&mut s).unwrap(); }
            let (gaps, evs) = gpu.gaps_and_evs().unwrap();
            gpu.sync_to_cpu(&mut s).unwrap();
            let (regrets, strategy) = s.arena_snapshot();
            assert_eq!(s.iteration, 65);
            if let Some((r, t, g, e)) = &expected {
                assert_eq!(r.len(), regrets.len());
                assert_eq!(t.len(), strategy.len());
                assert!(r.iter().zip(&regrets).all(|(a,b)|a.to_bits()==b.to_bits()));
                assert!(t.iter().zip(&strategy).all(|(a,b)|a.to_bits()==b.to_bits()));
                assert_eq!(g.iter().map(|v|v.to_bits()).collect::<Vec<_>>(), gaps.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                assert_eq!(e.iter().map(|v|v.to_bits()).collect::<Vec<_>>(), evs.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                println!("METRIC_JSON {}", serde_json::json!({
                    "metrics":{}, "seats":n, "tight_budget_mb":budget,
                    "iteration":s.iteration, "all_arena_gap_ev_bits_equal":true
                }));
            } else {
                expected = Some((regrets, strategy, gaps, evs));
            }
        }
    }
}
