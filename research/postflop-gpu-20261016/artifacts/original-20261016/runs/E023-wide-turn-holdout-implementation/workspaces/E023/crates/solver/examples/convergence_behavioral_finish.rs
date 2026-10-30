//! Registered native finish from an offline behavioral warm-start initializer.
use serde_json::{json, Value};
use solver::preflop::{
    convergence_research::Experiment, equity::EquityTable, gpu::PreflopGpu, PreflopSolver,
};
use std::{path::Path, sync::Arc, time::Instant};
fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len()!=5{return Err("INPUT PATHS MODE PRETRAIN_RESULT OUTPUT".into())}
    let reset=match a[2].as_str(){"keep"=>false,"reset"=>true,_=>return Err("mode".into())};
    let out=Path::new(&a[4]);
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
    let pretrain:Value=serde_json::from_slice(&std::fs::read(&a[3]).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let pretrain_seconds=pretrain["seconds"].as_f64().ok_or("pretrain time")?;
    let epsilon=pretrain["epsilon_label"].as_str().ok_or("pretrain epsilon")?;
    if !["0","0.01","0.05"].contains(&epsilon) || (!reset && epsilon!="0")
        || pretrain["iteration"]!=1000 || pretrain["samples"]!=1024 || pretrain["seed"]!=42
        || !pretrain_seconds.is_finite() || pretrain_seconds<=0.0{return Err("unregistered pretraining".into())}
    let mut s=PreflopSolver::load_game(&a[0],eq.clone())?;
    if s.nodes.len()!=23038 || s.n!=6 || s.iteration!=1000 || s.fit.is_none()
        || s.multiway_equity_model()!="coupled_deck_v1" || s.live_seats().iter().any(|x|!*x){return Err("unregistered input".into())}
    let before=s.arena_snapshot();let original_age=s.iteration;
    let preparation=if reset{s.research_reset_learning_averages()?}else{json!({"reset_learning_nodes":0,"reset_entries":0})};
    let after=s.arena_snapshot();
    if before.0!=after.0 || s.iteration!=original_age || (if reset{after.1.iter().any(|v|*v!=0.0) || preparation["reset_entries"]!=after.1.len()}else{before.1!=after.1}){return Err("initializer preservation mismatch".into())}
    drop(before);drop(after);
    for p in &paths {
        s.research_refinement_plan(p)?;
    }
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let mut g = PreflopGpu::new(&s, 4096)?;
    g.configure_research(Experiment::new("gamma15",1024,1000,42)?)?;
    if g.research_behavioral_constrained_gaps().is_ok(){return Err("behavioral state leaked".into())}
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
        let row = json!({"iteration":s.iteration,"finishing_iteration":i,"gaps":gaps,"evs":evs,"gap":gap,"rows":rows,"passed":passed,
            "consecutive_combined_passes":streak,"full_reference_samples":1024,"solve_seconds":solve_seconds,"elapsed_seconds":started.elapsed().as_secs_f64()});
        println!(
            "BEHAVIORAL_FINISH {}",
            json!({"epsilon":epsilon,"reset":reset,"iteration":s.iteration,"finishing_iteration":i,"gap":gap,"passed":passed,"qualified":streak>=2})
        );
        checks.push(row);
        if streak>=2{break;}

    }
    drop(g);
    let save = out.join("final.gtop");
    s.save_game(save.to_str().ok_or("invalid save path")?)?;
    let reload = PreflopSolver::load_game(save.to_str().unwrap(), eq)?;
    if s.arena_snapshot() != reload.arena_snapshot() {
        return Err("roundtrip mismatch".into());
    }
    let mut audit=PreflopGpu::new(&reload,4096)?;
    audit.configure_research(Experiment::new("gamma15",1024,1000,42)?)?;
    let (gaps,evs)=audit.gaps_and_evs()?;
    let last=checks.last().ok_or("missing checks")?;
    if json!(gaps)!=last["gaps"] || json!(evs)!=last["evs"]{return Err("fresh saved evaluation mismatch".into())}
    let finishing_seconds=started.elapsed().as_secs_f64();
    let result=json!({"input":a[0],"nodes":s.nodes.len(),"samples":1024,"seed":42,"epsilon_label":epsilon,"reset":reset,
        "preparation":preparation,"retained_regrets_exact":true,"initialization_exact":true,"native_only":true,
        "original_iteration":original_age,"schedule":"gamma15","horizon":1000,"limit":1000,"iteration":s.iteration,"checks":checks,
        "qualified":streak>=2,"solve_seconds":solve_seconds,"finishing_seconds":finishing_seconds,"pretrain_seconds":pretrain_seconds,
        "total_seconds":pretrain_seconds+finishing_seconds,"roundtrip_exact":true,"fresh_saved_evaluation_exact":true,
        "large_game_qualified":false,"normal_global_resume_supported":false,"scope":"Warm-start native finish; not exact historical regret conversion"});
    std::fs::write(
        out.join("result.json"),
        serde_json::to_vec_pretty(&result).unwrap(),
    )
    .map_err(|e| e.to_string())
}
