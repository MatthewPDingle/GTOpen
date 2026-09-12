//! Registered normalized pair correction screen; unchanged combined quality stop.
use serde_json::{json, Value};
use solver::preflop::{
    convergence_research::Experiment, equity::EquityTable, gpu::PreflopGpu, PreflopSolver,
};
use std::{path::Path, sync::Arc, time::Instant};
fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 6 {
        return Err("INPUT PATHS SAMPLES SEED PAIR OUTPUT".into());
    }
    let samples: u32 = a[2].parse().map_err(|_| "samples")?;
    let seed: u64 = a[3].parse().map_err(|_| "seed")?;
    if ![64, 256, 1024].contains(&samples)
        || ![42, 314159].contains(&seed)
        || !["0", "1"].contains(&a[4].as_str())
        || ((samples == 1024) != (a[4] == "0"))
    {
        return Err("unregistered case".into());
    }
    let pair = a[4] == "1";
    let normalized = true;
    let out = Path::new(&a[5]);
    if out.exists() {
        return Err("output exists".into());
    }
    let paths: Vec<Vec<usize>> =
        serde_json::from_slice(&std::fs::read(&a[1]).map_err(|e| e.to_string())?)
            .map_err(|e| e.to_string())?;
    if paths
        != vec![
            vec![2, 0, 0],
            vec![2, 0, 0, 1],
            vec![2, 0, 0, 1, 1],
            vec![2, 0, 0, 0, 0],
            vec![1, 0, 0],
            vec![1, 0, 0, 0, 0],
        ]
    {
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
    if s.nodes.len() != 23038
        || s.n != 6
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
    let mut g = PreflopGpu::new(&s, 4096)?;
    g.configure_research(Experiment::new("gamma15", samples, 1000, seed)?)?;
    let pair_extra_bytes = if pair {
        g.enable_research_normalized_pair_control(1024)?
    } else {
        g.enable_research_normalized_regret()?;
        0
    };
    let mut streak = 0;
    let mut checks = Vec::new();
    let mut solve_seconds = 0.;
    for i in 1..=1000 {
        let t = Instant::now();
        g.iterate(&mut s)?;
        solve_seconds += t.elapsed().as_secs_f64();
        if i % 25 != 0 {
            continue;
        }
        let (gaps, evs) = g.gaps_and_evs()?;
        if gaps.len() != 6
            || evs.len() != 6
            || gaps.iter().any(|x| !x.is_finite() || *x < 0.0)
            || evs.iter().any(|x| !x.is_finite())
        {
            return Err("invalid canonical check".into());
        }
        g.sync_to_cpu(&mut s)?;
        let rows: Vec<Value> = paths
            .iter()
            .map(|p| {
                s.research_conditioned_action_quality_against(&s, p)
                    .map(|q| json!({"candidate":q}))
            })
            .collect::<Result<_, _>>()?;
        let passed = rows
            .iter()
            .filter(|r| {
                r["candidate"]["passes_local_tail_gate"] == true
                    && r["candidate"]["conditioned_before_evaluation"] == true
            })
            .count();
        let gap: f64 = gaps.iter().sum();
        streak = if gap <= 0.005 && passed == 6 {
            streak + 1
        } else {
            0
        };
        let row = json!({"iteration":i,"gaps":gaps,"evs":evs,"gap":gap,"rows":rows,"passed":passed,
            "consecutive_combined_passes":streak,"full_reference_samples":1024,"solve_seconds":solve_seconds,"elapsed_seconds":started.elapsed().as_secs_f64()});
        println!(
            "NORMALIZED_PAIR_QUALITY {}",
            json!({"samples":samples,"seed":seed,"normalized":normalized,"pair":pair,"iteration":i,"gap":gap,"passed":passed,"qualified":streak>=2})
        );
        checks.push(row);
        if streak >= 2 {
            break;
        }
    }
    drop(g);
    let save = out.join("final.gtop");
    s.save_game(save.to_str().ok_or("invalid save path")?)?;
    let reload = PreflopSolver::load_game(save.to_str().unwrap(), eq)?;
    if s.arena_snapshot() != reload.arena_snapshot() {
        return Err("roundtrip mismatch".into());
    }
    let result = json!({"input":a[0],"nodes":s.nodes.len(),"samples":samples,"seed":seed,"normalized":normalized,"pair":pair,
        "pair_extra_bytes":pair_extra_bytes,"schedule":"gamma15","horizon":1000,"limit":1000,"iteration":s.iteration,"checks":checks,"qualified":streak>=2,
        "solve_seconds":solve_seconds,"seconds":started.elapsed().as_secs_f64(),"roundtrip_exact":true,"large_game_qualified":false});
    std::fs::write(
        out.join("result.json"),
        serde_json::to_vec_pretty(&result).unwrap(),
    )
    .map_err(|e| e.to_string())
}
