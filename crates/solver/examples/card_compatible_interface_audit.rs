//! Offline test of the pre-existing legal-pair interface against an independent LP oracle.
#[cfg(not(feature = "preflop-research"))]
fn main() { panic!("Build with --features preflop-research"); }

#[cfg(feature = "preflop-research")]
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
        let source = std::fs::read_to_string(std::env::args().nth(2).expect("kernel path"))?;
        let plan = g.enable_learned_interface_research(&s, &source, false)?;
        let optimization = g.skip_redundant_interface_work(&s)?;
        let start = std::time::Instant::now();
        for target in [1000, 10000] {
            while s.iteration < target { g.iterate(&mut s)?; }
            let gpu = g.gaps_and_evs()?;
            g.sync_to_cpu(&mut s)?;
            let cpu = s.gaps_and_evs();
            let x = s.average_strategy(0);
            let y = s.average_strategy(reply);
            results.push(json!({"stack":stack,"iteration":s.iteration,"config":s.cfg,
                "node_count":s.nodes.len(),"interface_plan":plan,"optimization":optimization,"gpu_gaps":gpu.0,"gpu_evs":gpu.1,
                "ordinary_cpu_gaps_not_this_model":cpu.0,"ordinary_cpu_evs_not_this_model":cpu.1,"elapsed_seconds":start.elapsed().as_secs_f64(),
                "hero_jam":&x[jam*169..(jam+1)*169],"opponent_call":&y[call*169..(call+1)*169]}));
            println!("stack {stack} iteration {target} complete");
        }
    }
    std::fs::write(output, serde_json::to_vec_pretty(&json!({"results":results,
        "note":"Existing research interface, learned pricing disabled, anchored compatible chance. CPU outputs retain original semantics and are not a validation oracle. No production server access or saves."}))?)?;
    Ok(())
}
