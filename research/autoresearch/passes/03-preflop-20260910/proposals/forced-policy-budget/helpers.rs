// Include the one-float placeholder allocated when no policies are forced.
fn forced_storage_bytes(elements: usize) -> Result<usize, String> {
    elements
        .max(1)
        .checked_mul(std::mem::size_of::<f32>())
        .ok_or_else(|| "forced strategy allocation size overflow".into())
}

// Stream one node's policy at a time: exact CPU routing, no concatenated
// forced table or tree-sized temporary allocation in the estimate.
fn forced_policy_elements(s: &PreflopSolver) -> Result<usize, String> {
    s.nodes
        .iter()
        .enumerate()
        .filter(|(_, n)| n.kind == KIND_ACTION)
        .try_fold(0usize, |total, (i, _)| {
            let count = s.forced_sigma(i).map_or(0, |p| p.len());
            total
                .checked_add(count)
                .ok_or_else(|| "forced strategy count overflow".into())
        })
}

fn reserve_forced_vram_mb(base_mb: f64, elements: usize, budget_mb: u64) -> Result<f64, String> {
    let bytes = forced_storage_bytes(elements)?;
    let need = base_mb + bytes as f64 / 1e6;
    if !need.is_finite() || need > budget_mb as f64 {
        return Err(format!("needs ~{need:.0} MB VRAM including {:.1} MB forced policies (budget {budget_mb} MB); solving on CPU", bytes as f64 / 1e6));
    }
    Ok(need)
}
