// Reference arithmetic grouping is a compatibility constraint, separate from
// physical scratch layout. This reproduces the original union CDF planner
// after the common forced-policy accounting correction, without allocating it.
#[derive(Debug, PartialEq, Eq)]
struct ReferenceMultiwayPlan { batch: usize, use_eq_cache: bool }
fn reference_multiway_plan(
    budget_mb: u64, base_mb: f64, fixed_bytes: usize, union_slots: usize,
    eq_cache_bytes: usize, has_eq_cache: bool,
) -> Result<Option<ReferenceMultiwayPlan>, String> {
    if !base_mb.is_finite() || base_mb < 0.0 { return Err("invalid multiway base allocation".into()); }
    if union_slots == 0 { return Err("reference multiway cache requires slots".into()); }
    let one_particle = union_slots.checked_mul((NUM_CLASSES + 1) * 4)
        .ok_or_else(|| "reference CDF allocation overflow".to_string())?;
    // Preserve the original floating-point MB-to-byte calculation and floor.
    let remaining = (budget_mb as f64 * 1e6 - base_mb * 1e6 - fixed_bytes as f64).max(0.0) as usize;
    let batch = (remaining / one_particle).min(32).min(super::multiway::SAMPLES);
    if batch == 0 { return Ok(None); }
    let cdf_bytes = one_particle.checked_mul(batch).ok_or_else(|| "reference CDF allocation overflow".to_string())?;
    let fixed_and_cdf = fixed_bytes.checked_add(cdf_bytes).ok_or_else(|| "reference allocation overflow".to_string())?;
    let need = base_mb + fixed_and_cdf as f64 / 1e6;
    let use_eq_cache = has_eq_cache && need + eq_cache_bytes as f64 / 1e6 <= budget_mb as f64;
    Ok(Some(ReferenceMultiwayPlan { batch, use_eq_cache }))
}

#[derive(Debug, PartialEq, Eq)]
struct CompatibleMultiwayPlan {
    storage: MultiwayBatchPlan,
    // None: old union scratch could not fit even one particle. The optimized
    // capacity extension has no old same-budget GPU grouping to preserve.
    reference: Option<ReferenceMultiwayPlan>,
}
fn compatible_multiway_plan(
    budget_mb: u64, base_mb: f64, reference_fixed_bytes: usize,
    optimized_fixed_bytes: usize, union_slots: usize, physical_slots: usize,
    eq_cache_bytes: usize, has_eq_cache: bool,
) -> Result<Option<CompatibleMultiwayPlan>, String> {
    let reference = reference_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        union_slots, eq_cache_bytes, has_eq_cache)?;
    if physical_slots == 0 { return Err("physical multiway cache requires slots".into()); }
    let available = (budget_mb as f64 * 1e6 - base_mb * 1e6 - optimized_fixed_bytes as f64).max(0.0) as usize;
    let Some(ref target) = reference else {
        // Preserve the existing bounded capacity-extension/direct minimum-fit
        // behavior only when no original same-budget GPU batch exists.
        return Ok(multiway_batch_plan(available, physical_slots)?.map(|storage|
            CompatibleMultiwayPlan { storage, reference: None }));
    };
    let cache_len = physical_slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n| n.checked_mul(target.batch)).ok_or_else(|| "compatible CDF allocation overflow".to_string())?;
    let cdf_bytes = cache_len.checked_mul(4).ok_or_else(|| "compatible CDF allocation overflow".to_string())?;
    let eq_reserve = if target.use_eq_cache { eq_cache_bytes } else { 0 };
    let required = cdf_bytes.checked_add(eq_reserve).ok_or_else(|| "compatible allocation overflow".to_string())?;
    if available < required {
        return Err(format!("optimized multiway metadata cannot retain original {}-particle grouping and HU-cache={} within {budget_mb} MB; compatibility layout unsupported, solving on CPU",
            target.batch, target.use_eq_cache));
    }
    let preferred_normalized = physical_slots.checked_mul(NUM_CLASSES * 4)
        .ok_or_else(|| "compatible normalized allocation overflow".to_string())?;
    // The required reference batch/cache wins over optional normalization.
    // Direct division is the exact arithmetic alternative already supported.
    let mut normalized_bytes = if available - required >= preferred_normalized { preferred_normalized } else { 0 };
    let planned_need = |normalized: usize| -> Result<f64, String> {
        let bytes = optimized_fixed_bytes.checked_add(cdf_bytes).and_then(|n|n.checked_add(normalized))
            .ok_or_else(|| "compatible total allocation overflow".to_string())?;
        Ok(base_mb + bytes as f64 / 1e6 + eq_reserve as f64 / 1e6)
    };
    // Keep the final MB check authoritative at sub-byte/f64 boundaries too.
    if normalized_bytes != 0 && planned_need(normalized_bytes)? > budget_mb as f64 { normalized_bytes = 0; }
    if planned_need(normalized_bytes)? > budget_mb as f64 {
        return Err("reference multiway grouping/cache does not fit the optimized physical allocation".into());
    }
    Ok(Some(CompatibleMultiwayPlan {
        storage: MultiwayBatchPlan { batch: target.batch, cache_len, normalized_bytes }, reference,
    }))
}

