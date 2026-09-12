//! Offline alternating upstream/conditional GPU refinement. No live resume.
use solver::preflop::{equity::EquityTable, gpu::PreflopGpu, PreflopSolver};
use serde_json::{json, Value};
use std::{collections::HashSet, sync::Arc, time::Instant};

fn main() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 3 { return Err("INPUT PATHS OUTPUT".into()); }
    let out = std::path::Path::new(&args[2]);
    if out.exists() { return Err("output exists".into()); }
    let paths: Vec<Vec<usize>> = serde_json::from_slice(
        &std::fs::read(&args[1]).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    if paths.is_empty() || paths.len() > 64 || paths.iter().any(|p| p.is_empty() || p.len() > 64)
        || paths.iter().collect::<HashSet<_>>().len() != paths.len() {
        return Err("one to 64 distinct nonempty bounded paths required".into());
    }
    rayon::ThreadPoolBuilder::new().num_threads(8).build_global().map_err(|e| e.to_string())?;
    let bytes = std::fs::read("cache/preflop_eq169.bin").map_err(|e| e.to_string())?;
    let samples = u32::from_le_bytes(bytes.get(..4).ok_or("short equity cache")?.try_into().unwrap());
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let mut solver = PreflopSolver::load_game(&args[0], eq.clone())?;
    if solver.multiway_equity_model() != "coupled_deck_v1" { return Err("canonical model required".into()); }
    // Validate every path before creating output or changing any learning state.
    for path in &paths { solver.research_refinement_plan(path)?; }
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let started = Instant::now();
    let original_age = solver.iteration;
    let mut cycles = Vec::new();
    let mut qualified = false;
    for cycle in 0..4 {
        let upstream = solver.research_refine_ancestors_gpu(&paths, 25)?;
        println!("UPSTREAM {}", json!({"cycle":cycle,"seconds":upstream["seconds"]}));
        let mut updates = Vec::new();
        // Earlier paths precede descendants in the registered path list. Each
        // update recomputes incoming ranges from the current complete policy.
        for path in &paths {
            let quality = solver.research_conditioned_action_quality_against(&solver, path)?;
            if quality["passes_local_tail_gate"] == true { continue; }
            for iterations in [1000, 4000] {
                let result = solver.research_refine_branch_gpu(path, iterations, 4096)?;
                let quality = solver.research_conditioned_action_quality_against(&solver, path)?;
                println!("DOWNSTREAM {}", json!({"cycle":cycle,"path":path,"iterations":iterations,
                    "passes":quality["passes_local_tail_gate"],"seconds":result["seconds"]}));
                updates.push(json!({"path":path,"refinement":result,"quality":quality}));
                if quality["passes_local_tail_gate"] == true { break; }
            }
        }
        let mut gpu = PreflopGpu::new(&solver, 23000)?;
        let (gaps, evs) = gpu.gaps_and_evs()?;
        drop(gpu);
        if gaps.iter().chain(&evs).any(|x| !x.is_finite()) { return Err("nonfinite full check".into()); }
        let rows: Vec<Value> = paths.iter().map(|p| solver.research_conditioned_action_quality_against(&solver, p)
            .map(|q| json!({"candidate":q}))).collect::<Result<_,_>>()?;
        let passed = rows.iter().filter(|r| r["candidate"]["passes_local_tail_gate"] == true).count();
        let gap: f64 = gaps.iter().sum();
        qualified = gap <= 0.005 && passed == paths.len();
        if solver.iteration != original_age { return Err("global age changed".into()); }
        let save = out.join(format!("cycle-{cycle}.gtop"));
        solver.save_game(save.to_str().ok_or("invalid save path")?)?;
        let reload = PreflopSolver::load_game(save.to_str().unwrap(), eq.clone())?;
        if reload.arena_snapshot() != solver.arena_snapshot() { return Err("roundtrip mismatch".into()); }
        drop(reload);
        let result = json!({"cycle":cycle,"upstream":upstream,"updates":updates,"rows":rows,
            "global_gaps":gaps,"global_evs":evs,"passed":passed,"qualified":qualified,
            "roundtrip_exact":true,"elapsed_seconds":started.elapsed().as_secs_f64()});
        std::fs::write(out.join(format!("cycle-{cycle}.json")), serde_json::to_vec_pretty(&result).unwrap()).map_err(|e| e.to_string())?;
        println!("CYCLE {}", json!({"cycle":cycle,"gap":gap,"passed":passed,"qualified":qualified}));
        cycles.push(result);
        if qualified { break; }
    }
    solver.save_game(out.join("final.gtop").to_str().ok_or("invalid final path")?)?;
    let result = json!({"input":args[0],"cycles":cycles,"qualified":qualified,
        "normal_global_resume_supported":false,"seconds":started.elapsed().as_secs_f64(),
        "scope":"Alternating local GPU updates; full unrestricted final checks; no deployment qualification beyond registered gates"});
    std::fs::write(out.join("result.json"), serde_json::to_vec_pretty(&result).unwrap()).map_err(|e| e.to_string())
}
