//! SOURCE.gtop FULL_REFERENCE.gtop CACHE NEW_OUTPUT_DIRECTORY THREADS [PATHS.json]
//! Predeclared scales0.01/0.1/1, checkpoints50/100/500 full-model iterations.
use serde_json::{json, Value};
use solver::preflop::{
    equity::{EquityTable, NUM_CLASSES},
    PreflopSolver,
};
use std::{path::PathBuf, sync::Arc, time::Instant};

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if !(5..=6).contains(&args.len()) {
        return Err("SOURCE FULL_REFERENCE CACHE NEW_OUTPUT_DIRECTORY THREADS [PATHS.json]".into());
    }
    let threads: usize = args[4].parse().map_err(|_| "invalid threads")?;
    if !(1..=4).contains(&threads) {
        return Err("threads must be1..4".into());
    }
    for path in &args[..2] {
        if std::fs::metadata(path).map_err(|e| e.to_string())?.len() > 140 * 1024 * 1024 {
            return Err("input exceeds bounded small fixture native limit".into());
        }
    }
    let out = PathBuf::from(&args[3]);
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
        return Err("output parent must lie inside lab target/research-preview".into());
    }
    let cache = std::fs::read(&args[2]).map_err(|e| e.to_string())?;
    if cache.len() != 4 + NUM_CLASSES * NUM_CLASSES * 4 {
        return Err("invalid cache length".into());
    }
    let samples = u32::from_le_bytes(cache[..4].try_into().unwrap());
    if samples == 0 {
        return Err("zero cache samples".into());
    }
    let eq = Arc::new(EquityTable::load_or_build(&args[2], samples));
    let source = PreflopSolver::load_game(&args[0], eq.clone())?;
    let reference = PreflopSolver::load_game(&args[1], eq.clone())?;
    let paths: Vec<Vec<usize>> = if args.len() == 6 {
        serde_json::from_slice(&std::fs::read(&args[5]).map_err(|e| e.to_string())?)
            .map_err(|e| e.to_string())?
    } else {
        vec![]
    };
    if paths.len() > 8 {
        return Err("at most8 local paths".into());
    }
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .map_err(|e| e.to_string())?;
    // Validate reference/constraints before creating experiment output files.
    let source_quality = pool.install(|| source.research_policy_quality_against(&reference))?;
    std::fs::create_dir(&out).map_err(|e| e.to_string())?;
    let mut runs = Vec::new();
    for scale in [0.01f32, 0.1, 1.0] {
        let started = Instant::now();
        let (mut fresh, mut provenance) = source.research_full_policy_warmstart(scale)?;
        provenance["source_native"] = json!(args[0]);
        provenance["reference_native"] = json!(args[1]);
        provenance["source_hash_verification"] =
            json!("pin source SHA256 externally; no native rewriting or relabeling");
        let scale_name = if scale == 0.01 {
            "001"
        } else if scale == 0.1 {
            "01"
        } else {
            "1"
        };
        let provenance_path = out.join(format!("scale-{scale_name}-provenance.json"));
        std::fs::write(
            &provenance_path,
            serde_json::to_vec_pretty(&provenance).unwrap(),
        )
        .map_err(|e| e.to_string())?;
        let mut iteration_seconds = 0.0;
        let mut checkpoints = Vec::new();
        for done in 1..=500 {
            let t = Instant::now();
            if !pool.install(|| fresh.try_iterate()) {
                return Err("warmstart full iteration canceled".into());
            }
            iteration_seconds += t.elapsed().as_secs_f64();
            if ![50, 100, 500].contains(&done) {
                continue;
            }
            let quality_started = Instant::now();
            let mut quality = pool.install(|| fresh.research_policy_quality_against(&reference))?;
            let local: Result<Vec<_>, _> = pool.install(|| {
                paths
                    .iter()
                    .map(|path| fresh.research_local_action_quality_against(&reference, path))
                    .collect()
            });
            quality["selected_local_action_quality"] = json!(local?);
            let path = out.join(format!("scale-{scale_name}-full-{done:03}.gtop"));
            fresh.save_game(path.to_str().ok_or("nonUTF8 output")?)?;
            let roundtrip = PreflopSolver::load_game(path.to_str().unwrap(), eq.clone())?;
            if roundtrip.multiway_equity_model() != "coupled_deck_v1"
                || roundtrip.iteration != done
                || roundtrip.arena_snapshot() != fresh.arena_snapshot()
            {
                return Err("warmstart output roundtrip mismatch".into());
            }
            let row = json!({"scale":scale,"full_iterations":done,"full_iteration_seconds":iteration_seconds,
                "quality_and_save_seconds":quality_started.elapsed().as_secs_f64(),"elapsed_seconds":started.elapsed().as_secs_f64(),
                "native":path,"provenance":provenance_path,"roundtrip_exact":true,"quality":quality});
            println!("WARMSTART {row}");
            checkpoints.push(row);
        }
        runs.push(json!({"scale":scale,"provenance":provenance,"checkpoints":checkpoints}));
    }
    if std::fs::read(&args[2]).map_err(|e| e.to_string())? != cache {
        return Err("equity cache changed".into());
    }
    let result = json!({"schema":1,"family":"preview_average_to_fresh_full_regrets_v1","source":args[0],"reference":args[1],
        "threads":threads,"source_quality":source_quality,"runs":runs,
        "scope":"Bounded research initialization; full payoff learning starts at0; no approximate regrets/iteration transferred"});
    std::fs::write(
        out.join("run.json"),
        serde_json::to_vec_pretty(&result).unwrap(),
    )
    .map_err(|e| e.to_string())?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("preview warmstart: {e}");
        std::process::exit(1);
    }
}
