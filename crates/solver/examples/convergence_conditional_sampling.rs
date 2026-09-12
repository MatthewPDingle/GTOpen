//! Offline fixed-current-policy diagnostic; no live API access or learning.
use solver::preflop::{equity::EquityTable, PreflopSolver};
use std::{path::Path, sync::Arc, time::Instant};
fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 3 {
        return Err("GAME PATHS OUTPUT".into());
    }
    if Path::new(&a[2]).exists() {
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
        return Err("unregistered path set".into());
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
    let s = PreflopSolver::load_game(&a[0], eq)?;
    if s.nodes.len() != 23038 || s.n != 6 || ![950, 1000].contains(&s.iteration) || s.fit.is_none()
    {
        return Err("unregistered fixture".into());
    }
    let mut result = s.research_conditional_sampling_gpu(&paths, 4096)?;
    result["seconds"] = serde_json::json!(started.elapsed().as_secs_f64());
    std::fs::write(&a[2], serde_json::to_vec(&result).unwrap()).map_err(|e| e.to_string())
}
