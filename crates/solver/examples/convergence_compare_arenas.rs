//! Independent, read-only comparison of two all-learning saved histories.
use serde_json::json;
use solver::preflop::{equity::EquityTable, PreflopSolver};
use std::{path::Path, sync::Arc};

fn main() -> Result<(), String> {
    let a: Vec<_> = std::env::args().skip(1).collect();
    if a.len() != 3 || Path::new(&a[2]).exists() {
        return Err("REFERENCE CANDIDATE NEW_OUTPUT_JSON".into());
    }
    let bytes = std::fs::read("cache/preflop_eq169.bin").map_err(|e| e.to_string())?;
    let eq = Arc::new(EquityTable::load_or_build(
        "cache/preflop_eq169.bin",
        u32::from_le_bytes(bytes[..4].try_into().unwrap()),
    ));
    let reference = PreflopSolver::load_game(&a[0], eq.clone())?;
    let candidate = PreflopSolver::load_game(&a[1], eq)?;
    if reference.iteration != candidate.iteration
        || reference.nodes.len() != candidate.nodes.len()
        || reference.has_overrides()
        || candidate.has_overrides()
        || reference.hero.is_some()
        || candidate.hero.is_some()
        || reference.multiway_equity_model() != candidate.multiway_equity_model()
        || serde_json::to_value(&reference.cfg).map_err(|e| e.to_string())?
            != serde_json::to_value(&candidate.cfg).map_err(|e| e.to_string())?
    {
        return Err("incompatible saved states".into());
    }
    let (rr, ra) = reference.arena_snapshot();
    let (cr, ca) = candidate.arena_snapshot();
    let exact = |x: &[f32], y: &[f32]| {
        x.len() == y.len()
            && x.iter()
                .zip(y)
                .all(|(a, b)| a.is_finite() && b.is_finite() && a.to_bits() == b.to_bits())
    };
    let regrets_exact = exact(&rr, &cr);
    let averages_exact = exact(&ra, &ca);
    if !regrets_exact || averages_exact {
        return Err("averaging discriminator did not isolate average history".into());
    }
    std::fs::write(
        &a[2],
        serde_json::to_vec_pretty(&json!({
            "reference":a[0], "candidate":a[1], "iteration":reference.iteration,
            "nodes":reference.nodes.len(), "regret_entries":rr.len(),
            "regrets_bit_exact":regrets_exact, "averages_bit_exact":averages_exact,
            "all_learning":true, "model":reference.multiway_equity_model()
        }))
        .unwrap(),
    )
    .map_err(|e| e.to_string())
}
