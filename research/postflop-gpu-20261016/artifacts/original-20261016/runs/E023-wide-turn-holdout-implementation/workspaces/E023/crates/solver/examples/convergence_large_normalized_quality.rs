//! Registered large full-particle normalized-regret combined-quality screen.
use serde_json::{json, Value};
use solver::preflop::{
    convergence_research::Experiment, equity::EquityTable, gpu::PreflopGpu, PreflopSolver,
};
use std::{path::Path, sync::Arc, time::Instant};
fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 3 {
        return Err("INPUT PATHS OUTPUT".into());
    }
    let samples = 1024;
    let seed = 42;
    let normalized = true;
    let out = Path::new(&a[2]);
    if out.exists() {
        return Err("output exists".into());
    }
    let paths: Vec<Vec<usize>> =
        serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e| e.to_string())?)
            .map_err(|e| e.to_string())?;
    let mut expected = Vec::new();
    for opening in [2, 3] {
        let prefix = vec![opening, 0, 0, 0, 0];
        for suffix in [
            vec![],
            vec![0],
            vec![1],
            vec![0, 0],
            vec![1, 0],
            vec![1, 1],
            vec![2],
            vec![2, 0],
            vec![2, 1],
        ] {
            let mut p = prefix.clone();
            p.extend(suffix);
            expected.push(p);
        }
    }
    for prefix in [
        vec![1, 0, 0, 0, 0],
        vec![1, 1, 0, 0, 0],
        vec![1, 1, 1, 0, 0],
    ] {
        for suffix in [vec![], vec![0], vec![0, 0]] {
            let mut p = prefix.clone();
            p.extend(suffix);
            expected.push(p);
        }
    }
    if paths != expected {
        return Err("unregistered paths".into());
    }
    let cfg: Value = serde_json::from_slice(&std::fs::read(&a[0]).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    rayon::ThreadPoolBuilder::new()
        .num_threads(8)
        .build_global()
        .map_err(|e| e.to_string())?;
    let started = Instant::now();
    let b = std::fs::read("cache/preflop_eq169.bin").map_err(|e| e.to_string())?;
    let eq = Arc::new(EquityTable::load_or_build(
        "cache/preflop_eq169.bin",
        u32::from_le_bytes(b[..4].try_into().unwrap()),
    ));
    let mut s = PreflopSolver::new(
        serde_json::from_value(cfg.get("config").unwrap_or(&cfg).clone())
            .map_err(|e| e.to_string())?,
        eq.clone(),
    )?;
    if s.nodes.len() != 1567754
        || s.n != 8
        || s.iteration != 0
        || s.fit.is_none()
        || s.multiway_equity_model() != "coupled_deck_v1"
        || s.live_seats().iter().any(|x| !*x)
    {
        return Err("unregistered fixture".into());
    }
    for p in &paths {
        s.research_refinement_plan(p)?;
    }
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let mut g = PreflopGpu::new(&s, 20000)?;
    g.configure_research(Experiment::new("gamma15", samples, 1500, seed)?)?;
    if normalized {
        g.enable_research_normalized_regret()?;
    }
    let setup_seconds = started.elapsed().as_secs_f64();
    let mut streak = 0;
    let mut checks = Vec::new();
    let mut solve_seconds = 0.;
    for i in 1..=1500 {
        let t = Instant::now();
        g.iterate(&mut s)?;
        solve_seconds += t.elapsed().as_secs_f64();
        if i % 50 != 0 {
            continue;
        }
        let t = Instant::now();
        let (gaps, evs) = g.gaps_and_evs()?;
        let evaluation_seconds = t.elapsed().as_secs_f64();
        if gaps.len() != 8
            || evs.len() != 8
            || gaps.iter().any(|x| !x.is_finite() || *x < 0.0)
            || evs.iter().any(|x| !x.is_finite())
        {
            return Err("invalid canonical check".into());
        }
        let t = Instant::now();
        g.sync_to_cpu(&mut s)?;
        let publication_seconds = t.elapsed().as_secs_f64();
        let t = Instant::now();
        let rows: Vec<Value> = paths
            .iter()
            .map(|p| {
                s.research_conditioned_action_quality_against(&s, p)
                    .map(|q| json!({"candidate":q}))
            })
            .collect::<Result<_, _>>()?;
        let audit_seconds = t.elapsed().as_secs_f64();
        let passed = rows
            .iter()
            .filter(|r| {
                r["candidate"]["passes_local_tail_gate"] == true
                    && r["candidate"]["conditioned_before_evaluation"] == true
            })
            .count();
        let gap: f64 = gaps.iter().sum();
        streak = if gap <= 0.005 && passed == 27 {
            streak + 1
        } else {
            0
        };
        let row = json!({"iteration":i,"gaps":gaps,"evs":evs,"gap":gap,"rows":rows,"passed":passed,
            "consecutive_combined_passes":streak,"full_reference_samples":1024,"solve_seconds":solve_seconds,"elapsed_seconds":started.elapsed().as_secs_f64(),"evaluation_seconds":evaluation_seconds,"publication_seconds":publication_seconds,"audit_seconds":audit_seconds});
        let t = Instant::now();
        std::fs::write(
            out.join(format!("check-{i:04}.json")),
            serde_json::to_vec(&row).unwrap(),
        )
        .map_err(|e| e.to_string())?;
        let serialization_seconds = t.elapsed().as_secs_f64();
        println!(
            "LARGE_NORMALIZED_QUALITY {}",
            json!({"samples":samples,"seed":seed,"normalized":normalized,"iteration":i,"gap":gap,"passed":passed,"qualified":streak>=2,"elapsed_seconds":started.elapsed().as_secs_f64(),"serialization_seconds":serialization_seconds})
        );
        checks.push(row);
        if streak >= 2 {
            break;
        }
    }
    drop(g);
    let save_started = Instant::now();
    let save = out.join("final.gtop");
    s.save_game(save.to_str().ok_or("invalid save path")?)?;
    let reload = PreflopSolver::load_game(save.to_str().unwrap(), eq)?;
    if s.arena_snapshot() != reload.arena_snapshot() {
        return Err("roundtrip mismatch".into());
    }
    let result = json!({"input":a[0],"nodes":s.nodes.len(),"samples":samples,"seed":seed,"normalized":normalized,
        "schedule":"gamma15","horizon":1500,"limit":1500,"iteration":s.iteration,"checks":checks,"qualified":streak>=2,
        "setup_seconds":setup_seconds,"save_validation_seconds":save_started.elapsed().as_secs_f64(),"solve_seconds":solve_seconds,"seconds":started.elapsed().as_secs_f64(),"roundtrip_exact":true,"independent_saved_audit_pending":true,"large_game_qualified":false});
    std::fs::write(
        out.join("result.json"),
        serde_json::to_vec_pretty(&result).unwrap(),
    )
    .map_err(|e| e.to_string())
}
