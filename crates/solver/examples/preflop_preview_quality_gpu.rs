//! CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE GPU_BUDGET_MB
//! Prints research JSON, never saves/relabels/resumes either native input.
use serde_json::json;
use solver::preflop::{
    equity::{EquityTable, NUM_CLASSES},
    PreflopSolver,
};
use std::sync::Arc;

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 4 {
        return Err("CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE GPU_BUDGET_MB".into());
    }
    let budget: u64 = args[3].parse().map_err(|_| "invalid GPU budget")?;
    let mut metadata = Vec::new();
    for path in &args[..2] {
        let m = std::fs::metadata(path).map_err(|e| e.to_string())?;
        if m.len() > 3 * 1024 * 1024 * 1024 {
            return Err("native input exceeds3GiB bound".into());
        }
        metadata.push((m.len(), m.modified().map_err(|e| e.to_string())?));
    }
    let bytes = std::fs::read(&args[2]).map_err(|e| e.to_string())?;
    if bytes.len() != 4 + NUM_CLASSES * NUM_CLASSES * 4 {
        return Err("invalid equity cache length".into());
    }
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    if samples == 0 {
        return Err("zero equity cache samples".into());
    }
    let eq = Arc::new(EquityTable::load_or_build(&args[2], samples));
    let candidate = PreflopSolver::load_game(&args[0], eq.clone())?;
    let reference = PreflopSolver::load_game(&args[1], eq)?;
    let mut result = candidate.research_policy_quality_gpu_against(&reference, budget)?;
    for (path, (size, modified)) in args[..2].iter().zip(&metadata) {
        let m = std::fs::metadata(path).map_err(|e| e.to_string())?;
        if m.len() != *size || m.modified().map_err(|e| e.to_string())? != *modified {
            return Err("native input changed during evaluation".into());
        }
    }
    if std::fs::read(&args[2]).map_err(|e| e.to_string())? != bytes {
        return Err("equity cache changed during evaluation".into());
    }
    result["inputs"] = json!({"candidate":args[0],"reference":args[1],"equity_cache":args[2],
        "candidate_bytes":metadata[0].0,"reference_bytes":metadata[1].0,
        "native_size_and_mtime_unchanged":true,"equity_cache_bytes_unchanged":true,
        "native_hashes":"must be pinned externally; this harness does not rehash multi-gigabyte native files"});
    println!(
        "{}",
        serde_json::to_string_pretty(&result).map_err(|e| e.to_string())?
    );
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("GPU preview quality: {e}");
        std::process::exit(1);
    }
}
