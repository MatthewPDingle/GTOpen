//! SOURCE.gtop CACHE NEW_OUTPUT_DIRECTORY GPU_BUDGET_MB SCALE
//! One scale per process:0.01/0.1/1, full checkpoints2/10/30/50/100, limit100.
//! Root must apply an external wall-clock guard no greater than1800 seconds.
use serde_json::json;
use solver::preflop::{
    equity::{EquityTable, NUM_CLASSES},
    gpu::PreflopGpu,
    PreflopSolver,
};
use std::{path::PathBuf, sync::Arc, time::Instant};

fn run() -> Result<(), String> {
    let started = Instant::now();
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 5 {
        return Err("SOURCE CACHE NEW_OUTPUT_DIRECTORY GPU_BUDGET_MB SCALE".into());
    }
    let budget: u64 = args[3].parse().map_err(|_| "invalid GPU budget")?;
    if !(256..=64000).contains(&budget) {
        return Err("GPU budget must be256..64000 MB".into());
    }
    let scale: f32 = args[4].parse().map_err(|_| "invalid scale")?;
    if ![0.01f32, 0.1, 1.0].contains(&scale) {
        return Err("predeclared scale must be0.01,0.1 or1".into());
    }
    let source_meta = std::fs::metadata(&args[0]).map_err(|e| e.to_string())?;
    if source_meta.len() > 3 * 1024 * 1024 * 1024 {
        return Err("source native exceeds3GiB bound".into());
    }
    let modified = source_meta.modified().map_err(|e| e.to_string())?;
    let out = PathBuf::from(&args[2]);
    if out.exists() {
        return Err("output directory must be new".into());
    }
    let allowed = std::env::current_dir()
        .map_err(|e| e.to_string())?
        .join("target/research-preview");
    std::fs::create_dir_all(&allowed).map_err(|e| e.to_string())?;
    let allowed = allowed.canonicalize().map_err(|e| e.to_string())?;
    let parent = out
        .parent()
        .ok_or("output parent required")?
        .canonicalize()
        .map_err(|e| e.to_string())?;
    if !parent.starts_with(&allowed) {
        return Err("output parent must be inside lab target/research-preview".into());
    }
    let cache = std::fs::read(&args[1]).map_err(|e| e.to_string())?;
    if cache.len() != 4 + NUM_CLASSES * NUM_CLASSES * 4 {
        return Err("invalid cache length".into());
    }
    let samples = u32::from_le_bytes(cache[..4].try_into().unwrap());
    if samples == 0 {
        return Err("zero cache samples".into());
    }
    let phase_started=Instant::now();
    let eq = Arc::new(EquityTable::load_or_build(&args[1], samples));
    let equity_load_seconds=phase_started.elapsed().as_secs_f64();
    let phase_started=Instant::now();
    let source = PreflopSolver::load_game(&args[0], eq.clone())?;
    let source_load_seconds=phase_started.elapsed().as_secs_f64();
    let source_iteration=source.iteration;
    if ![50,1000].contains(&source_iteration) {
        return Err("large protocol requires registered source iteration50 or1000".into());
    }
    let phase_started=Instant::now();
    let (mut fresh, mut provenance) = source.research_large_full_policy_warmstart(scale)?;
    let initialization_transfer_seconds=phase_started.elapsed().as_secs_f64();
    provenance["source_native"] = json!(args[0]);
    provenance["source_native_bytes"] = json!(source_meta.len());
    provenance["source_hash_verification"] =
        json!("pin SHA256 externally; harness checks size/mtime and never saves source");
    provenance["protocol"] = json!({"predeclared_scales":[0.01,0.1,1.0],"this_process_scale":scale,
        "checkpoints":[2,10,30,50,100],"max_full_iterations":100,"maximum_external_guard_seconds":1800,
        "predeclared_source_iterations":[50,1000],"this_source_iteration":source_iteration,
        "source_scope":if source_iteration==50 {"exploratory development: early setup"} else if source_iteration==1000 {"mature development source: globally tested, local quality still requires audit"} else {"not one of the registered large sources"}});
    drop(source);
    if fresh.iteration != 0 || fresh.multiway_equity_model() != "coupled_deck_v1" {
        return Err("invalid fresh full-model state".into());
    }
    let init_seconds = started.elapsed().as_secs_f64();
    std::fs::create_dir(&out).map_err(|e| e.to_string())?;
    std::fs::write(
        out.join("provenance.json"),
        serde_json::to_vec_pretty(&provenance).unwrap(),
    )
    .map_err(|e| e.to_string())?;
    let phase_started=Instant::now();
    let mut gpu = PreflopGpu::new(&fresh, budget)?;
    let gpu_initialization_seconds=phase_started.elapsed().as_secs_f64();
    let gpu_initialized_seconds = started.elapsed().as_secs_f64();
    println!(
        "WARMSTART_GPU {}",
        json!({"phase":"initialized","scale":scale,"nodes":fresh.nodes.len(),
        "model":fresh.multiway_equity_model(),"iteration":fresh.iteration,"init_seconds":init_seconds,
        "gpu_initialized_seconds":gpu_initialized_seconds,"equity_load_seconds":equity_load_seconds,
        "source_load_seconds":source_load_seconds,"initialization_transfer_seconds":initialization_transfer_seconds,
        "gpu_initialization_seconds":gpu_initialization_seconds,"provenance":provenance})
    );
    let mut iteration_seconds = 0.0;
    let mut checkpoints = Vec::new();
    for done in 1u32..=100 {
        if started.elapsed().as_secs() >= 1800 {
            return Err("1800-second research guard reached before next full iteration".into());
        }
        let t = Instant::now();
        gpu.iterate(&mut fresh)?;
        let last_seconds = t.elapsed().as_secs_f64();
        iteration_seconds += last_seconds;
        println!(
            "WARMSTART_GPU {}",
            json!({"phase":"iterate","iteration":done,"seconds":last_seconds,
            "elapsed_seconds":started.elapsed().as_secs_f64()})
        );
        if ![2, 10, 30, 50, 100].contains(&done) {
            continue;
        }
        let check = Instant::now();
        let (gaps, evs) = gpu.gaps_and_evs()?;
        if gaps.iter().chain(&evs).any(|v| !v.is_finite()) {
            return Err("nonfinite full-model checkpoint".into());
        }
        let check_seconds = check.elapsed().as_secs_f64();
        let live = fresh.live_seats();
        let gap: f64 = gaps
            .iter()
            .zip(&live)
            .filter(|(_, l)| **l)
            .map(|(g, _)| *g)
            .sum();
        let gap_published_elapsed_seconds=started.elapsed().as_secs_f64();
        println!("WARMSTART_GPU {}",json!({"phase":"gap","full_iterations":done,"scale":scale,
            "learning_gap_full_model_bb":gap,"check_seconds":check_seconds,
            "gap_published_elapsed_seconds":gap_published_elapsed_seconds,"converged_in_full_model":gap<=0.005}));
        let save_started = Instant::now();let phase_started=Instant::now();
        gpu.sync_to_cpu(&mut fresh)?;
        let sync_seconds=phase_started.elapsed().as_secs_f64();
        let path = out.join(format!("full-{done:03}.gtop"));
        let phase_started=Instant::now();
        fresh.save_game(path.to_str().ok_or("nonUTF8 output")?)?;
        let native_save_seconds=phase_started.elapsed().as_secs_f64();let phase_started=Instant::now();
        let roundtrip = PreflopSolver::load_game(path.to_str().unwrap(), eq.clone())?;
        let roundtrip_load_seconds=phase_started.elapsed().as_secs_f64();let phase_started=Instant::now();
        if !fresh.research_warmstart_roundtrip_matches(&roundtrip)? {
            return Err("full native roundtrip differs".into());
        }
        let roundtrip_verify_seconds=phase_started.elapsed().as_secs_f64();
        drop(roundtrip);
        let m = std::fs::metadata(&args[0]).map_err(|e| e.to_string())?;
        if m.len() != source_meta.len() || m.modified().map_err(|e| e.to_string())? != modified {
            return Err("source native changed".into());
        }
        let row = json!({"phase":"checkpoint","scale":scale,"full_iterations":done,"model":fresh.multiway_equity_model(),
            "learning_gap_full_model_bb":gap,"gaps_bb":gaps,"evs_bb":evs,"live_seats":live,
            "converged_in_full_model":gap<=0.005,"full_iteration_seconds":iteration_seconds,"check_seconds":check_seconds,
            "gap_published_elapsed_seconds":gap_published_elapsed_seconds,"sync_seconds":sync_seconds,
            "native_save_seconds":native_save_seconds,"roundtrip_load_seconds":roundtrip_load_seconds,
            "roundtrip_verify_seconds":roundtrip_verify_seconds,
            "sync_save_roundtrip_seconds":save_started.elapsed().as_secs_f64(),"elapsed_seconds":started.elapsed().as_secs_f64(),
            "native":path,"roundtrip_exact":true,"provenance":out.join("provenance.json"),
            "quality_not_evaluated":"Run full-reference policy and local-tail audits; own gap alone does not establish physical/local quality."});
        println!("WARMSTART_GPU {row}");
        checkpoints.push(row);
    }
    drop(gpu);
    if std::fs::read(&args[1]).map_err(|e| e.to_string())? != cache {
        return Err("equity cache changed".into());
    }
    std::fs::write(out.join("run.json"),serde_json::to_vec_pretty(&json!({"schema":1,
        "status":"fixed100_full_iterations_complete","provenance":provenance,"checkpoints":checkpoints,
        "init_seconds":init_seconds,"gpu_initialized_seconds":gpu_initialized_seconds,
        "equity_load_seconds":equity_load_seconds,"source_load_seconds":source_load_seconds,
        "initialization_transfer_seconds":initialization_transfer_seconds,"gpu_initialization_seconds":gpu_initialization_seconds,
        "scope":"Explicit fresh full-reference policy initialization; not approximate-regret resumption"})).unwrap()).map_err(|e|e.to_string())?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("GPU preview warmstart: {e}");
        std::process::exit(1);
    }
}
