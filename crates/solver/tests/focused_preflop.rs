#[cfg(feature = "gpu")]
#[test]
fn conditional_multiway_gpu_matches_cpu() {
    use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopSolver};
    use std::sync::Arc;
    let cfg = serde_json::from_value(serde_json::json!({
        "positions":["BTN","SB","BB"], "posts":[0,0.5,1], "stack":12,
        "limp":false, "open_raises":[], "raise_mults":[], "max_raises":1,
        "add_allin":true, "rake_pct":5, "rake_cap":1, "realization":"raw"
    })).unwrap();
    let source = PreflopSolver::new(cfg, Arc::new(EquityTable::build(256))).unwrap();
    let ranges = vec!["AA,AKs".into(), "KK,QQ,AKs".into(), "QQ,AA,AKo:0.5".into()];
    let mut cpu = source.focused(&[1], &ranges).unwrap();
    let mut device = source.focused(&[1], &ranges).unwrap();
    let (mut gpu, _) = PreflopGpu::new_throughput(&device, 4096).unwrap();
    for _ in 0..100 { cpu.iterate(); gpu.iterate(&mut device).unwrap(); }
    let (gg, ge) = gpu.gaps_and_evs().unwrap();
    gpu.sync_to_cpu(&mut device).unwrap();
    let (cg, ce) = cpu.gaps_and_evs();
    for p in 0..3 {
        assert!((gg[p]-cg[p]).abs()<0.003, "gap seat {p}: {} vs {}", gg[p], cg[p]);
        assert!((ge[p]-ce[p]).abs()<0.003, "EV seat {p}: {} vs {}", ge[p], ce[p]);
    }
    assert_eq!(source.iteration, 0);
}
