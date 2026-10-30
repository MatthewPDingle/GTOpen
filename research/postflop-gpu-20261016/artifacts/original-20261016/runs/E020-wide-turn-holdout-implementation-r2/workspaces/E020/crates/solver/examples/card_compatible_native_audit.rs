//! Offline existing-engine push/fold policies for an independent chance-model audit.
#[cfg(not(feature = "gpu"))]
fn main() { panic!("Build with --features gpu"); }

#[cfg(feature = "gpu")]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use serde_json::json;
    use solver::preflop::{PreflopConfig, PreflopSolver, equity::EquityTable, gpu::PreflopGpu};
    use std::sync::Arc;
    let output = std::env::args().nth(1).expect("new output path");
    assert!(!std::path::Path::new(&output).exists(), "preserve completed evidence");
    rayon::ThreadPoolBuilder::new().num_threads(4).build_global()?;
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    let mut results = Vec::new();
    for stack in [3.0, 10.0, 50.0, 200.0] {
        let cfg: PreflopConfig = serde_json::from_value(json!({
            "positions":["SB","BB"], "posts":[1.0,2.0], "stack":stack,
            "ante":0.0,"limp":false,"open_raises":[],"raise_mults":[],
            "max_raises":1,"add_allin":true,"rake_pct":0.0,"rake_cap":0.0,
            "no_flop_no_drop":true,"realization":"balanced"
        }))?;
        let mut s = PreflopSolver::new(cfg, eq.clone())?;
        s.prune = false;
        assert_eq!(s.nodes[0].actor, 0);
        assert_eq!(s.nodes[0].actions.len(), 2);
        let jam = s.nodes[0].actions.iter().position(|a| a.kind == "jam").unwrap();
        let reply = s.child(0, jam);
        assert_eq!(s.nodes[reply].actor, 1);
        assert_eq!(s.nodes[reply].actions.len(), 2);
        let call = s.nodes[reply].actions.iter().position(|a| a.kind == "call").unwrap();
        let mut g = PreflopGpu::new(&s, 512)?;
        let start = std::time::Instant::now();
        for target in [1000, 10000] {
            while s.iteration < target { g.iterate(&mut s)?; }
            let gpu = g.gaps_and_evs()?;
            g.sync_to_cpu(&mut s)?;
            let cpu = s.gaps_and_evs();
            let x = s.average_strategy(0);
            let y = s.average_strategy(reply);
            results.push(json!({"stack":stack,"iteration":s.iteration,"config":s.cfg,
                "node_count":s.nodes.len(),"gpu_gaps":gpu.0,"gpu_evs":gpu.1,
                "cpu_gaps":cpu.0,"cpu_evs":cpu.1,"elapsed_seconds":start.elapsed().as_secs_f64(),
                "hero_jam":&x[jam*169..(jam+1)*169],"opponent_call":&y[call*169..(call+1)*169]}));
            println!("stack {stack} iteration {target} complete");
        }
    }
    std::fs::write(output, serde_json::to_vec_pretty(&json!({"results":results,
        "note":"Unmodified PreflopGpu, balanced symmetric cached equities; no production server access."}))?)?;
    Ok(())
}
