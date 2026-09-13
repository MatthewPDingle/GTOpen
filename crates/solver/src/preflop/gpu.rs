//! CUDA engine for the preflop solver: level-synchronous CFR mirroring the
//! CPU traversal exactly (validated by tests/preflop_gpu.rs on a GPU
//! machine). Built blind on a laptop â€” every deviation from the CPU math is
//! a bug by definition; keep the two in lockstep.
//!
//! Falls back cleanly: `PreflopGpu::new` errors when the game exceeds the
//! VRAM budget or CUDA is unavailable, and the server then solves on the
//! CPU + system RAM instead.

use super::{PreflopSolver, KIND_ACTION, KIND_POT_SHARE};
use crate::preflop::equity::{class_prob, NUM_CLASSES};
use crate::gpu::PinnedBuf;
use cudarc::driver::{sys, CudaContext, CudaFunction, CudaGraph, CudaSlice, CudaStream, LaunchConfig, PushKernelArg};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

const BLOCK: u32 = 256; // narrow per-node launches; reach totals always use 128 threads
const MAX_NA: usize = 16;

#[cfg(feature = "preflop-research")]
mod cv_research;
#[cfg(feature = "preflop-research")]
mod exact_reuse;
#[cfg(all(test, feature = "preflop-research"))]
mod exact_reuse_inventory;
#[cfg(feature = "preflop-research")]
mod frontier_research;
#[cfg(feature = "preflop-research")]
mod conditional_sampling;
#[cfg(feature = "preflop-research")]
mod normalized_regret;
#[cfg(feature = "preflop-research")]
mod rm_plus;
#[cfg(feature = "preflop-research")]
mod predictive;
#[cfg(feature = "preflop-research")]
mod pair_control;
#[cfg(feature = "preflop-research")]
mod exploration;
#[cfg(feature = "preflop-research")]
mod behavioral;
#[cfg(feature = "preflop-research")]
mod average_opponents;
#[cfg(feature = "preflop-research")]
mod fixed_history_units;
#[cfg(all(feature = "preflop-research", test))]
mod history_units;

fn e(err: impl std::fmt::Debug) -> String {
    format!("cuda: {err:?}")
}

pub struct PreflopGpu {
    _ctx: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    f_init: CudaFunction,
    f_down: CudaFunction,
    f_terminal: CudaFunction,
    f_reach_mass: CudaFunction,
    f_equities: CudaFunction,
    f_multiway_cdf: CudaFunction,
    f_multiway_normalize: CudaFunction,
    f_multiway_clear_active: CudaFunction,
    f_multiway_prepare: CudaFunction,
    f_multiway_terminal: CudaFunction,
    f_up: CudaFunction,
    f_discount: CudaFunction,
    // tree (immutable)
    d_kind: CudaSlice<i32>,
    d_actor: CudaSlice<i32>,
    d_na: CudaSlice<i32>,
    d_off: CudaSlice<u32>,
    d_cstart: CudaSlice<u32>,
    d_children: CudaSlice<u32>,
    d_live: CudaSlice<i32>,
    d_winner: CudaSlice<i32>,
    d_potf: CudaSlice<f32>,
    d_pots: CudaSlice<f32>,
    d_inv: CudaSlice<f32>,
    d_rw: CudaSlice<f32>,
    // calibrated realization: gross pot, per-terminal "use the fit" flag,
    // the 169-class measured base and its clip (see RealizationFit)
    d_potg: CudaSlice<f32>,
    d_calib: CudaSlice<i32>,
    d_cbase: CudaSlice<f32>,
    clip_lo: f32,
    clip_hi: f32,
    d_eq: CudaSlice<f32>,
    d_eq_slots: CudaSlice<u32>,
    d_eq_blocks: CudaSlice<u32>,
    d_eq_work: CudaSlice<u32>,
    d_eq_cache: CudaSlice<f32>,
    eq_spans: Vec<(u32, u32)>,
    use_eq_cache: i32,
    // A bounded particle batch avoids a 1024 x 170 CDF allocation for every
    // distinct reach vector. All batches still contribute to the same model.
    d_mw_order: CudaSlice<u32>,
    #[cfg(feature = "preflop-research")]
    research: Option<super::convergence_research::Experiment>,
    #[cfg(feature = "preflop-research")]
    research_samples: u32,
    #[cfg(feature = "preflop-research")]
    research_cv: Option<cv_research::ControlVariate>,
    #[cfg(feature = "preflop-research")]
    research_normalized_regret: Option<CudaFunction>,
    #[cfg(feature = "preflop-research")]
    research_rm_plus: Option<CudaFunction>,
    #[cfg(feature = "preflop-research")]
    research_predictive: Option<predictive::Predictive>,
    #[cfg(feature = "preflop-research")]
    research_rm_plus_fresh: bool,
    #[cfg(feature = "preflop-research")]
    research_pair_control: Option<pair_control::PairControl>,
    #[cfg(feature = "preflop-research")]
    research_exploration: Option<exploration::Exploration>,
    #[cfg(feature = "preflop-research")]
    research_behavioral: Option<behavioral::Behavioral>,
    #[cfg(feature = "preflop-research")]
    research_exact_reuse: Option<exact_reuse::ExactReuse>,
    #[cfg(feature = "preflop-research")]
    research_average_opponents: Option<CudaFunction>,
    #[cfg(feature = "preflop-research")]
    research_history_units: Option<fixed_history_units::FixedHistoryUnits>,
    #[cfg(feature = "preflop-research")]
    research_root_ranges: Option<(Vec<Vec<f32>>, CudaSlice<f32>)>,
    #[cfg(feature = "preflop-research")]
    research_learning_mask: bool,
    #[cfg(feature = "preflop-research")]
    research_discount_nodes: Option<CudaSlice<u32>>,
    #[cfg(feature = "preflop-research")]
    research_unit_probability: bool,
    #[cfg(feature = "preflop-research")]
    research_unit_fill: Option<CudaFunction>,
    d_mw_lower: CudaSlice<u32>,
    d_mw_upper: CudaSlice<u32>,
    d_mw_slots: CudaSlice<u32>,
    d_mw_blocks: CudaSlice<u32>,
    d_mw_work: CudaSlice<u32>,
    d_mw_cdf: CudaSlice<f32>,
    // One f32 division per needed slot/hand per traverser, reused by all particles.
    d_mw_normalized: CudaSlice<f32>,
    use_mw_normalized: bool,
    use_mw_prepared: bool,
    d_mw_compact: CudaSlice<u32>,
    mw_union_slots: u32,
    use_mw_compact: i32,
    d_mw_terms: CudaSlice<u32>,
    // One flag per CDF slot and one counterfactual probability per terminal.
    // Rebuilt on device for every traverser, including average/BR evaluation.
    d_mw_active: CudaSlice<u32>,
    d_mw_prob: CudaSlice<f32>,
    mw_spans: Vec<(u32, u32)>,
    mw_batch: u32,
    mw_nterms: u32,
    use_multiway: i32,
    d_cprob: CudaSlice<f32>,
    d_act_nodes: CudaSlice<u32>,
    d_terms: CudaSlice<u32>,
    // seat modes / locks: per node 0 = learning, 1 = frozen actor (plays
    // its strategy sums, never updated or discounted), 2 = forced sigma
    // (point lock or profile bucket) at d_forced[d_foff[node]..]
    d_src: CudaSlice<i32>,
    d_foff: CudaSlice<u32>,
    d_forced: CudaSlice<f32>,
    /// Seats whose own update pass writes nothing (frozen / fully ruled):
    /// skipped outright, like the CPU's seat_static.
    static_seats: Vec<bool>,
    constrained_br: Vec<bool>,
    n_act: u32,
    // mutable state
    d_regrets: CudaSlice<f32>,
    d_strat: CudaSlice<f32>,
    d_reach_src: CudaSlice<u32>,
    d_reach: CudaSlice<f32>,
    d_reach_mass: CudaSlice<f32>,
    d_val_slot: CudaSlice<u32>,
    d_val: CudaSlice<f32>,
    d_eval_roots: CudaSlice<f32>,
    eval_graph: Option<CudaGraph>,
    eval_warmed: bool,
    // level spans into d_act_nodes: (start, count) top-down
    spans: Vec<(u32, u32)>,
    nterms: u32,
    np: i32,
    arena_len: usize,
    learning_graphs: Vec<Option<CudaGraph>>,
    warmed: bool,
    h_snapshot: Mutex<Option<PinnedBuf>>,
    #[cfg(test)]
    phase_trace: Option<PhaseEventTrace>,
}

// Terminal values remain live across BR/average passes. Action values are
// consumed only by the preceding level, so alternate levels share scratch.
struct ValuePlan {
    slots: Vec<u32>,
    blocks: usize,
    action_nodes: Vec<u32>,
    spans: Vec<(u32, u32)>,
}
impl ValuePlan {
    fn build(s: &PreflopSolver) -> Self {
        let n = s.nodes.len();
        let mut depth = vec![0usize; n];
        let mut max_depth = 0;
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            for a in 0..node.actions.len() {
                let d = depth[i] + 1;
                depth[s.child(i, a)] = d;
                max_depth = max_depth.max(d);
            }
        }
        let mut levels = vec![Vec::new(); max_depth + 1];
        let mut slots = vec![0u32; n];
        let mut next = 1usize; // root always occupies block zero
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind == KIND_ACTION {
                levels[depth[i]].push(i as u32);
            } else if i != 0 {
                slots[i] = next as u32;
                next += 1;
            }
        }
        let mut widths = [0usize; 2];
        for (d, level) in levels.iter().enumerate() {
            let count = level.iter().filter(|&&node| node != 0).count();
            widths[d % 2] = widths[d % 2].max(count);
        }
        let bases = [next, next + widths[0]];
        let mut action_nodes = Vec::new();
        let mut spans = Vec::new();
        for (d, level) in levels.iter().enumerate() {
            let start = action_nodes.len() as u32;
            let mut offset = 0;
            for &node in level {
                if node != 0 {
                    slots[node as usize] = (bases[d % 2] + offset) as u32;
                    offset += 1;
                }
                action_nodes.push(node);
            }
            spans.push((start, level.len() as u32));
        }
        Self { slots, blocks: next + widths[0] + widths[1], action_nodes, spans }
    }
}

fn minimum_vram_mb(s: &PreflopSolver, value_blocks: usize) -> f64 {
    let n = s.nodes.len() as f64;
    let np = s.n as f64;
    let nc = NUM_CLASSES as f64;
    let arena = s.arena_len as f64;
    // One root reach per seat, then one actor reach per action edge.
    // Other seats alias their nearest written ancestor through reach_src.
    ((n + np - 1.0) * (nc + 1.0) * 4.0 + value_blocks as f64 * nc * 4.0 + 2.0 * arena * 4.0
        + n * (np * 12.0 + 44.0)) / 1e6 + 64.0
}

fn reach_sources(s: &PreflopSolver) -> Vec<u32> {
    let np = s.n;
    let mut sources = vec![0u32; s.nodes.len() * np];
    for q in 0..np { sources[q] = q as u32; }
    for (i, node) in s.nodes.iter().enumerate() {
        if node.kind != KIND_ACTION { continue; }
        for a in 0..node.actions.len() {
            let c = s.child(i, a);
            sources.copy_within(i * np..(i + 1) * np, c * np);
            sources[c * np + node.actor as usize] = (np + c - 1) as u32;
        }
    }
    sources
}

struct EquityCachePlan {
    slots: Vec<u32>,
    blocks: Vec<u32>,
    work: Vec<u32>,
    spans: Vec<(u32, u32)>,
}
impl EquityCachePlan {
    fn build(s: &PreflopSolver, sources: &[u32]) -> Self {
        Self::build_for(s, sources, false)
    }
    fn multiway(s: &PreflopSolver, sources: &[u32]) -> Self {
        Self::build_for(s, sources, true)
    }
    fn build_for(s: &PreflopSolver, sources: &[u32], multiway: bool) -> Self {
        let nblocks = s.nodes.len() + s.n - 1;
        let mut needed = vec![vec![false; nblocks]; s.n];
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind != KIND_POT_SHARE { continue; }
            let coupled = s.multiway.is_some() && node.live.count_ones() >= 3;
            if coupled != multiway { continue; }
            for p in 0..s.n {
                if (node.live >> p) & 1 == 0 { continue; }
                for q in 0..s.n {
                    if q != p && (node.live >> q) & 1 != 0 {
                        needed[p][sources[i * s.n + q] as usize] = true;
                    }
                }
            }
        }
        let mut slots = vec![u32::MAX; nblocks];
        let mut blocks = Vec::new();
        for block in 0..nblocks {
            if needed.iter().any(|p| p[block]) {
                slots[block] = blocks.len() as u32;
                blocks.push(block as u32);
            }
        }
        let mut work = Vec::new();
        let mut spans = Vec::new();
        // Learning needs only this traverser's opponents. Shared average
        // evaluation needs the union once for every seat's BR and EV.
        for p in 0..=s.n {
            let start = work.len() as u32;
            for (slot, &block) in blocks.iter().enumerate() {
                if p == s.n || needed[p][block as usize] {
                    work.push(slot as u32);
                }
            }
            spans.push((start, work.len() as u32 - start));
        }
        let plan = Self { slots, blocks, work, spans };
        // Opt-in planning-only instrumentation: no CUDA allocation/launch,
        // strategy mutation, or altered cache layout. Also works via the CPU
        // caller of vram_estimate_mb before GPU construction.
        if multiway && std::env::var_os("PREFLOP_MW_SLOT_STATS").is_some() {
            let counts: Vec<usize> = plan.spans[..s.n].iter().map(|&(_, count)| count as usize).collect();
            let union = plan.blocks.len();
            let max_seat = counts.iter().copied().max().unwrap_or(0);
            let layouts: Vec<_> = [1usize, 7, 32].into_iter().map(|batch| {
                let per_slot = (NUM_CLASSES + 1) * batch * 4;
                let normalization = NUM_CLASSES * 4;
                // Both remapping approaches retain the existing union maps,
                // work spans and active flags; only these additions/savings differ.
                let static_map = s.n * union * 4;
                let dynamic_map = union * 4;
                let saved_direct = (union - max_seat) * per_slot;
                let saved_normalized = (union - max_seat) * (per_slot + normalization);
                serde_json::json!({
                    "batch": batch,
                    "current_cdf_bytes": union * per_slot,
                    "compact_cdf_bytes": max_seat * per_slot,
                    "current_normalized_bytes": union * normalization,
                    "compact_normalized_bytes": max_seat * normalization,
                    "static_map_bytes": static_map,
                    "dynamic_map_bytes": dynamic_map,
                    "net_saved_static_direct_bytes": saved_direct as i128 - static_map as i128,
                    "net_saved_static_normalized_bytes": saved_normalized as i128 - static_map as i128,
                    "net_saved_dynamic_direct_bytes": saved_direct as i128 - dynamic_map as i128,
                    "net_saved_dynamic_normalized_bytes": saved_normalized as i128 - dynamic_map as i128,
                })
            }).collect();
            println!("preflop mw slot stats: {}", serde_json::json!({
                "positions": &s.cfg.positions,
                "union_slots": union,
                "per_traverser_slots": counts,
                "max_traverser_slots": max_seat,
                "max_union_ratio": if union == 0 { 0.0 } else { max_seat as f64 / union as f64 },
                "layouts": layouts,
            }));
        }
        plan
    }
    fn bytes(&self) -> usize {
        (self.slots.len() + self.blocks.len() + self.work.len()
            + self.blocks.len() * NUM_CLASSES) * 4
    }
    fn metadata_bytes(&self) -> usize {
        (self.slots.len() + self.blocks.len() + self.work.len()) * 4
    }
    fn disabled(np: usize) -> Self {
        Self { slots: vec![0], blocks: vec![0], work: vec![0], spans: vec![(0, 0); np + 1] }
    }
}

// Compact only if its immutable map plus one CDF particle is no larger
// than the union's minimum cache. This also saves at every larger batch size.
struct MultiwayCompactPlan {
    capacity: usize,
    map: Vec<u32>,
    bytes: usize,
    enabled: bool,
}
impl MultiwayCompactPlan {
    fn union(slots: usize) -> Self {
        Self { capacity: slots, map: vec![0], bytes: 0, enabled: false }
    }
    fn build(plan: &EquityCachePlan, np: usize) -> Result<Self, String> {
        let union = plan.blocks.len();
        if union == 0 { return Ok(Self::union(0)); }
        let capacity = plan.spans[..np].iter().map(|&(_, n)| n as usize).max().unwrap_or(0);
        if capacity == 0 { return Err("multiway compact plan has no traverser slots".into()); }
        let len = union.checked_mul(np).ok_or_else(|| "multiway compact map overflow".to_string())?;
        let bytes = len.checked_mul(4).ok_or_else(|| "multiway compact map overflow".to_string())?;
        let saved_minimum = (union - capacity).checked_mul((NUM_CLASSES + 1) * 4)
            .ok_or_else(|| "multiway compact cache overflow".to_string())?;
        if bytes >= saved_minimum { return Ok(Self::union(union)); }
        let mut map = vec![u32::MAX; len];
        for p in 0..np {
            let (start, count) = plan.spans[p];
            for local in 0..count as usize {
                let global = plan.work[start as usize + local] as usize;
                map[p * union + global] = local as u32;
            }
        }
        Ok(Self { capacity, map, bytes, enabled: true })
    }
}

// Pure byte-budget planner; no CUDA context or allocation is needed to test
// the boundary. Optional normalization must not remove the one-particle path.
#[derive(Debug, PartialEq, Eq)]
struct MultiwayBatchPlan {
    batch: usize,
    cache_len: usize,
    normalized_bytes: usize,
}
fn multiway_batch_plan(available_bytes: usize, slots: usize) -> Result<Option<MultiwayBatchPlan>, String> {
    if slots == 0 { return Err("multiway cache requires at least one slot".into()); }
    let one_particle = slots.checked_mul((NUM_CLASSES + 1) * 4)
        .ok_or_else(|| "multiway CDF scratch size overflow".to_string())?;
    if available_bytes < one_particle { return Ok(None); }
    let preferred_normalized = slots.checked_mul(NUM_CLASSES * 4)
        .ok_or_else(|| "multiway normalized reach size overflow".to_string())?;
    // Retain the preferred normalized path even if direct division could fit
    // a larger batch. Fall back only if normalized+one particle cannot fit.
    let normalized_bytes = if available_bytes - one_particle >= preferred_normalized {
        preferred_normalized
    } else { 0 };
    let batch = ((available_bytes - normalized_bytes) / one_particle)
        .min(32).min(super::multiway::SAMPLES);
    let cache_len = slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n| n.checked_mul(batch))
        .ok_or_else(|| "multiway CDF scratch size overflow".to_string())?;
    Ok(Some(MultiwayBatchPlan { batch, cache_len, normalized_bytes }))
}

// Reference arithmetic grouping is a compatibility constraint, separate from
// physical scratch layout. Reproduce the original union CDF planner for the
// explicitly supplied literal or corrected base, without allocating its scratch.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
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
    minimal_metadata: bool,
    // None: old union scratch could not fit even one particle. The optimized
    // capacity extension has no old same-budget GPU grouping to preserve.
    reference: Option<ReferenceMultiwayPlan>,
}
#[cfg(test)]
fn compatible_multiway_plan(
    budget_mb: u64, base_mb: f64, reference_fixed_bytes: usize,
    optimized_fixed_bytes: usize, union_slots: usize, physical_slots: usize,
    eq_cache_bytes: usize, has_eq_cache: bool,
) -> Result<Option<CompatibleMultiwayPlan>, String> {
    let reference = reference_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        union_slots, eq_cache_bytes, has_eq_cache)?;
    fit_compatible_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        optimized_fixed_bytes, union_slots, physical_slots, eq_cache_bytes, reference)
}

// Physical fit is independent of how the numerical reference was chosen.
// An unsupported target returns None; allocation overflow remains an error.
fn fit_compatible_multiway_plan(
    budget_mb:u64, base_mb:f64, reference_fixed_bytes:usize, optimized_fixed_bytes:usize,
    union_slots:usize, physical_slots:usize, eq_cache_bytes:usize,
    reference:Option<ReferenceMultiwayPlan>,
) -> Result<Option<CompatibleMultiwayPlan>,String> {
    if physical_slots == 0 { return Err("physical multiway cache requires slots".into()); }
    let available = (budget_mb as f64 * 1e6 - base_mb * 1e6 - optimized_fixed_bytes as f64).max(0.0) as usize;
    let Some(ref target) = reference else {
        // Preserve the existing bounded capacity-extension/direct minimum-fit
        // behavior only when no original same-budget GPU batch exists.
        return Ok(multiway_batch_plan(available, physical_slots)?.map(|storage|
            CompatibleMultiwayPlan { storage, reference: None, minimal_metadata: false }));
    };
    let cache_len = physical_slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n| n.checked_mul(target.batch)).ok_or_else(|| "compatible CDF allocation overflow".to_string())?;
    let cdf_bytes = cache_len.checked_mul(4).ok_or_else(|| "compatible CDF allocation overflow".to_string())?;
    let eq_reserve = if target.use_eq_cache { eq_cache_bytes } else { 0 };
    let required = cdf_bytes.checked_add(eq_reserve).ok_or_else(|| "compatible allocation overflow".to_string())?;
    if available < required {
        return original_layout_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
            union_slots, eq_cache_bytes, reference);
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
        return original_layout_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
            union_slots, eq_cache_bytes, reference);
    }
    Ok(Some(CompatibleMultiwayPlan {
        storage: MultiwayBatchPlan { batch: target.batch, cache_len, normalized_bytes }, reference,
        minimal_metadata: false,
    }))
}

// Exact original union/direct layout: no active flags, probability table,
// normalized reaches or compact map. Preserve reference batch AND HU cache.
fn original_layout_multiway_plan(
    budget_mb: u64, base_mb: f64, reference_fixed_bytes: usize, union_slots: usize,
    eq_cache_bytes: usize, reference: Option<ReferenceMultiwayPlan>,
) -> Result<Option<CompatibleMultiwayPlan>, String> {
    let Some(target) = reference else { return Ok(None); };
    let cache_len = union_slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n|n.checked_mul(target.batch)).ok_or_else(|| "original CDF allocation overflow".to_string())?;
    let bytes = cache_len.checked_mul(4).and_then(|n|n.checked_add(reference_fixed_bytes))
        .ok_or_else(|| "original total allocation overflow".to_string())?;
    let need = base_mb + bytes as f64 / 1e6
        + if target.use_eq_cache {eq_cache_bytes as f64 / 1e6} else {0.0};
    if need > budget_mb as f64 { return Ok(None); }
    Ok(Some(CompatibleMultiwayPlan {
        storage: MultiwayBatchPlan {batch:target.batch,cache_len,normalized_bytes:0},
        reference:Some(target),minimal_metadata:true,
    }))
}

struct DeployedCompatibilityPlan {
    plan: CompatibleMultiwayPlan,
    reference_source: &'static str,
    literal_reference: Option<ReferenceMultiwayPlan>,
}

// Literal pre-pass grouping is a numerical target, never a memory allowance.
// Accurate base includes forced policies; literal base is captured beforehand,
// not recovered by subtracting bytes from an already-rounded f64 total.
fn deployed_compatible_multiway_plan(
    budget_mb:u64, accurate_base_mb:f64, literal_base_mb:f64,
    reference_fixed_bytes:usize, optimized_fixed_bytes:usize,
    union_slots:usize, physical_slots:usize, eq_cache_bytes:usize, has_eq_cache:bool,
    force_minimal:bool,
) -> Result<Option<DeployedCompatibilityPlan>,String> {
    if !accurate_base_mb.is_finite() || accurate_base_mb < literal_base_mb {
        return Err("invalid accurately accounted multiway base".into());
    }
    let literal = reference_multiway_plan(budget_mb,literal_base_mb,reference_fixed_bytes,
        union_slots,eq_cache_bytes,has_eq_cache)?;
    let fit = |target:Option<ReferenceMultiwayPlan>| {
        if force_minimal {
            original_layout_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
                union_slots,eq_cache_bytes,target)
        } else {
            fit_compatible_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
                optimized_fixed_bytes,union_slots,physical_slots,eq_cache_bytes,target)
        }
    };
    // None means no original GPU grouping, not permission to prefer an
    // arbitrary capacity-extension batch before trying a corrected reference.
    if literal.is_some() {
        if let Some(plan)=fit(literal)? {
            return Ok(Some(DeployedCompatibilityPlan {
                plan,reference_source:"deployed_prepass",literal_reference:literal,
            }));
        }
    }
    let corrected=reference_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
        union_slots,eq_cache_bytes,has_eq_cache)?;
    Ok(fit(corrected)?.map(|plan| DeployedCompatibilityPlan {
        reference_source:if plan.reference.is_some() {"corrected_budget_fallback"} else {"capacity_extension"},
        plan,literal_reference:literal,
    }))
}

// Include the one-float placeholder allocated when no policies are forced.
fn forced_storage_bytes(elements: usize) -> Result<usize, String> {
    elements.max(1).checked_mul(std::mem::size_of::<f32>())
        .ok_or_else(|| "forced strategy allocation size overflow".into())
}

// Stream one node's policy at a time: exact CPU routing, no concatenated
// forced table or tree-sized temporary allocation in the estimate.
fn forced_policy_elements(s: &PreflopSolver) -> Result<usize, String> {
    s.nodes.iter().enumerate().filter(|(_, n)| n.kind == KIND_ACTION)
        .try_fold(0usize, |total, (i, _)| {
            let count = s.forced_sigma(i).map_or(0, |p| p.len());
            total.checked_add(count).ok_or_else(|| "forced strategy count overflow".into())
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

/// Preferred VRAM including the exact-equity cache, in MB. The constructor
/// can omit that optional cache to fit a smaller budget without changing results.
pub fn vram_estimate_mb(s: &PreflopSolver) -> f64 {
    let sources = reach_sources(s);
    let mw = EquityCachePlan::multiway(s, &sources);
    let mw_bytes = if mw.blocks.is_empty() { 0 } else {
        let compact = MultiwayCompactPlan::build(&mw, s.n).unwrap_or_else(|_| MultiwayCompactPlan::union(mw.blocks.len()));
        mw.metadata_bytes() + compact.bytes + compact.capacity * (NUM_CLASSES + 1) * 32 * 4
            + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + s.nodes.len() * 8
            + mw.blocks.len() * 4 + compact.capacity * NUM_CLASSES * 4
    };
    let forced_bytes = match forced_policy_elements(s).and_then(forced_storage_bytes) {
        Ok(bytes) => bytes,
        Err(_) => return f64::INFINITY,
    };
    minimum_vram_mb(s, ValuePlan::build(s).blocks)
        + (EquityCachePlan::build(s, &sources).bytes() + mw_bytes + forced_bytes) as f64 / 1e6
}

// Host-only, opt-in diagnostic. Does not modify source layouts, reaches, arenas,
// GPU allocations or launches. All temporary records are dropped before return.
fn multiway_terminal_key_stats(s: &PreflopSolver, sources: &[u32], terms: &[u32]) {
    use std::collections::BTreeMap;
    use std::time::Instant;
    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct Key { len: u8, ordered_sources: [u32; 8] }
    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct Record { key: Key, seat: u8, node: u32 }
    #[derive(Default)]
    struct Counts {
        tasks: usize,
        groups: usize,
        duplicate_groups: usize,
        max_multiplicity: usize,
        histogram: BTreeMap<usize, usize>,
        // opponent count -> [tasks, groups, duplicate groups]
        by_opponents: BTreeMap<usize, [usize; 3]>,
        examples: Vec<serde_json::Value>,
    }
    impl Counts {
        fn add(&mut self, multiplicity: usize, opponents: usize) {
            self.tasks += multiplicity;
            self.groups += 1;
            self.duplicate_groups += usize::from(multiplicity > 1);
            self.max_multiplicity = self.max_multiplicity.max(multiplicity);
            *self.histogram.entry(multiplicity).or_default() += 1;
            let by = self.by_opponents.entry(opponents).or_default();
            by[0] += multiplicity;
            by[1] += 1;
            by[2] += usize::from(multiplicity > 1);
        }
        fn report(&self) -> serde_json::Value {
            let bytes = self.duplicate_groups.checked_mul(NUM_CLASSES).and_then(|n| n.checked_mul(4));
            let layouts: Vec<_> = [1usize, 7, 32].into_iter().map(|batch| {
                serde_json::json!({
                    "particle_batch": batch,
                    "batch_count": super::multiway::SAMPLES.div_ceil(batch),
                    "one_batch_duplicate_sum_cache_bytes": bytes,
                    "all_batches_duplicate_sum_cache_bytes": bytes.and_then(|n| n.checked_mul(super::multiway::SAMPLES.div_ceil(batch))),
                })
            }).collect();
            serde_json::json!({
                "live_tasks": self.tasks,
                "unique_keys": self.groups,
                "duplicate_groups": self.duplicate_groups,
                "duplicate_tasks_avoided": self.tasks - self.groups,
                "duplicate_task_fraction": if self.tasks == 0 { 0.0 } else { (self.tasks-self.groups) as f64/self.tasks as f64 },
                "max_multiplicity": self.max_multiplicity,
                "group_multiplicity_histogram": self.histogram,
                "opponent_count_tasks_groups_duplicate_groups": self.by_opponents,
                "cache_layout_estimates": layouts,
                "duplicate_examples": self.examples,
            })
        }
    }

    let start = Instant::now();
    if s.n > 9 || sources.len() != s.nodes.len().saturating_mul(s.n) {
        eprintln!("preflop mw key stats: skipped invalid diagnostic source dimensions");
        return;
    }
    let Some(tasks) = terms.iter().try_fold(0usize, |total, &nd| {
        total.checked_add(s.nodes[nd as usize].live.count_ones() as usize)
    }) else {
        eprintln!("preflop mw key stats: skipped task count overflow");
        return;
    };
    let Some(requested_bytes) = tasks.checked_mul(std::mem::size_of::<Record>()) else {
        eprintln!("preflop mw key stats: skipped record size overflow");
        return;
    };
    let mut records = Vec::<Record>::new();
    if let Err(err) = records.try_reserve_exact(tasks) {
        eprintln!("preflop mw key stats: skipped {requested_bytes}-byte host diagnostic allocation: {err}");
        return;
    }
    for &node in terms {
        let live = s.nodes[node as usize].live;
        for p in 0..s.n {
            if (live >> p) & 1 == 0 { continue; }
            let mut key = Key { len: 0, ordered_sources: [0; 8] };
            for q in 0..s.n {
                if q == p || (live >> q) & 1 == 0 { continue; }
                key.ordered_sources[key.len as usize] = sources[node as usize * s.n + q];
                key.len += 1;
            }
            records.push(Record { key, seat: p as u8, node });
        }
    }
    let collect_ms = start.elapsed().as_secs_f64() * 1000.0;
    let before_sort = Instant::now();
    // This orders records by their complete key; it does NOT reorder sources
    // inside a key or alter the opponent multiplication order in the solver.
    records.sort_unstable();
    let sort_ms = before_sort.elapsed().as_secs_f64() * 1000.0;
    let before_count = Instant::now();
    let mut seats: Vec<Counts> = (0..s.n).map(|_| Counts::default()).collect();
    let mut union = Counts::default();
    let mut cross_seat = Counts::default();
    let mut cross_seat_count_histogram = BTreeMap::<usize, usize>::new();
    let mut at = 0;
    while at < records.len() {
        let key = records[at].key;
        let mut end = at + 1;
        while end < records.len() && records[end].key == key { end += 1; }
        let group = &records[at..end];
        union.add(group.len(), key.len as usize);
        let mut distinct_seats = 0usize;
        let mut seat_at = 0;
        while seat_at < group.len() {
            let p = group[seat_at].seat as usize;
            let mut seat_end = seat_at + 1;
            while seat_end < group.len() && group[seat_end].seat as usize == p { seat_end += 1; }
            distinct_seats += 1;
            let count = seat_end - seat_at;
            seats[p].add(count, key.len as usize);
            if count > 1 && seats[p].examples.len() < 3 {
                seats[p].examples.push(serde_json::json!({
                    "ordered_sources": &key.ordered_sources[..key.len as usize],
                    "node_examples": group[seat_at..seat_end].iter().take(8).map(|r| r.node).collect::<Vec<_>>(),
                    "multiplicity": count,
                }));
            }
            seat_at = seat_end;
        }
        *cross_seat_count_histogram.entry(distinct_seats).or_default() += 1;
        if distinct_seats > 1 {
            cross_seat.add(group.len(), key.len as usize);
            if cross_seat.examples.len() < 5 {
                cross_seat.examples.push(serde_json::json!({
                    "ordered_sources": &key.ordered_sources[..key.len as usize],
                    "task_examples": group.iter().take(12).map(|r| serde_json::json!({"seat":r.seat,"node":r.node})).collect::<Vec<_>>(),
                    "tasks": group.len(), "distinct_seats": distinct_seats,
                }));
            }
        }
        at = end;
    }
    let count_ms = before_count.elapsed().as_secs_f64() * 1000.0;
    let per_seat_unique_sum: usize = seats.iter().map(|s| s.groups).sum();
    let record_capacity = records.capacity();
    let record_payload_bytes = record_capacity.checked_mul(std::mem::size_of::<Record>());
    let per_seat: Vec<_> = seats.iter().enumerate().map(|(p,c)| serde_json::json!({
        "seat": p, "position": &s.cfg.positions[p], "counts": c.report(),
    })).collect();
    println!("preflop mw key stats: {}", serde_json::json!({
        "diagnostic_only": true,
        "model": s.multiway_equity_model(),
        "particles": super::multiway::SAMPLES,
        "multiway_terminals": terms.len(),
        "per_traverser": per_seat,
        "average_check_union": union.report(),
        "cross_seat_groups_only": cross_seat.report(),
        "union_group_distinct_seats_histogram": cross_seat_count_histogram,
        "within_traverser_duplicate_tasks": tasks - per_seat_unique_sum,
        "additional_frozen_cross_seat_duplicate_tasks": per_seat_unique_sum - union.groups,
        "timing_ms": {"collect":collect_ms,"sort":sort_ms,"count":count_ms,"total_before_print":start.elapsed().as_secs_f64()*1000.0},
        "host_memory_estimate": {
            "record_bytes":std::mem::size_of::<Record>(), "record_capacity":record_capacity,
            "dominant_record_payload_bytes":record_payload_bytes,
            "note":"Payload estimate, not measured RSS: excludes allocator overhead, small histograms/examples/JSON. In-place unstable sort adds no second record array. All diagnostic storage drops on return."
        },
        "interpretation":"Static source identity only, not active-reach savings or a speedup measurement. Cross-seat reuse requires one frozen average-check reach snapshot; learning sweeps invalidate it. Cache bytes exclude maps, activity flags and scatter work. Null byte estimates mean arithmetic overflow."
    }));
}

impl PreflopGpu {
    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        Self::new_with_layout(s, budget_mb, true)
    }

    // The private switch permits same-batch union/compact regression tests.
    // Public construction always chooses the minimum-fit-safe layout.
    fn new_with_layout(s: &PreflopSolver, budget_mb: u64, allow_compact: bool) -> Result<Self, String> {
        Self::new_with_layout_mode(s, budget_mb, allow_compact, false)
    }

    // The true value is used only by internal parity tests. Public construction
    // selects minimal metadata solely when the normal compatible plan needs it.
    fn new_with_layout_mode(s: &PreflopSolver, budget_mb: u64, allow_compact: bool, force_minimal: bool) -> Result<Self, String> {
        let reach_blocks = s.nodes.len().checked_add(s.n - 1)
            .filter(|&len| len <= u32::MAX as usize)
            .ok_or_else(|| "reach table beyond 32-bit block indexing; solving on CPU".to_string())?;
        let values = ValuePlan::build(s);
        let mut need = minimum_vram_mb(s, values.blocks);
        if need > budget_mb as f64 {
            return Err(format!(
                "needs ~{need:.0} MB VRAM (budget {budget_mb} MB)"
            ));
        }
        if s.nodes.iter().any(|nd| nd.actions.len() > MAX_NA) {
            return Err("a node has more than 16 actions".into());
        }
        // Per-node reach blocks are indexed with 64-bit math in the kernels,
        // but arena offsets/lengths cross the launch boundary as u32: a tree
        // whose arenas exceed 2^32 entries would silently alias wrapped
        // indices inside the buffers (no CUDA error, garbage strategies).
        if s.arena_len > u32::MAX as usize {
            return Err(format!(
                "arenas have {} entries â€” beyond the GPU engine's 32-bit arena indexing; solving on CPU",
                s.arena_len
            ));
        }

        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
        unsafe { ctx.disable_event_tracking() };

        // Compile the PTX for the device we actually found: hardcoded
        // compute_86 refuses to load on an A100 (8.0) and makes newer cards
        // JIT from stale PTX. (&'static is what cudarc's CompileOptions
        // wants; one tiny leak per process is fine.)
        let (cc_maj, cc_min) = ctx.compute_capability().map_err(e)?;
        let arch: &'static str =
            Box::leak(format!("compute_{cc_maj}{cc_min}").into_boxed_str());
        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> =
            std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("kernels.cu"),
                    cudarc::nvrtc::CompileOptions {
                        arch: Some(arch),
                        ..Default::default()
                    },
                )
                .map_err(e)
            })
            .clone()?;
        let module = ctx.load_module(ptx).map_err(e)?;
        let func = |name: &str| module.load_function(name).map_err(e);

        let n = s.nodes.len();
        let np = s.n;

        // flatten the tree (SoA)
        let mut kind = vec![0i32; n];
        let mut actor = vec![0i32; n];
        let mut na = vec![0i32; n];
        let mut off = vec![0u32; n];
        let mut cstart = vec![0u32; n];
        let mut live = vec![0i32; n];
        let mut winner = vec![0i32; n];
        let mut potf = vec![0f32; n];
        let mut pots = vec![0f32; n];
        let mut inv = vec![0f32; n * np];
        let mut rw = vec![0f32; n * np];
        let mut potg = vec![0f32; n];
        let mut calib = vec![0i32; n];
        let mut terms: Vec<u32> = Vec::new();
        for (i, nd) in s.nodes.iter().enumerate() {
            kind[i] = nd.kind as i32;
            actor[i] = nd.actor as i32;
            na[i] = nd.actions.len() as i32;
            off[i] = nd.data_off as u32;
            cstart[i] = nd.child_start;
            live[i] = nd.live as i32;
            winner[i] = nd.winner as i32;
            let rake = s.rake_of(nd.pot); // cap 0 = uncapped, same as the CPU
            // fold-win: matched pot only is raked (uncalled chips return)
            potf[i] = (nd.pot - s.fold_win_rake(nd)) as f32;
            pots[i] = (nd.pot - rake) as f32;
            potg[i] = nd.pot as f32;
            for q in 0..np {
                inv[i * np + q] = nd.invested[q] as f32;
                rw[i * np + q] = if nd.r.is_empty() { 0.0 } else { nd.r[q] };
            }
            if nd.kind != KIND_ACTION {
                terms.push(i as u32);
            }
            // Calibrated R applies exactly where terminal_value() applies it:
            // pot-share terminals, heads-up, with chips behind (spr > 0).
            // The fit was measured net-of-rake over the GROSS pot, so those
            // terminals price on potg with no rake deduction and no pot cap.
            if s.fit.is_some() && nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 2 {
                let mut min_left = f64::MAX;
                for q in 0..np {
                    if nd.live & (1 << q) != 0 {
                        min_left = min_left.min(s.cfg.stack - nd.invested[q] + s.cfg.ante);
                    }
                }
                let spr = (min_left / nd.pot).max(0.0);
                if spr > 1e-9 {
                    calib[i] = 1;
                }
            }
        }
        let (cbase, (clip_lo, clip_hi)) = match s.fit.as_ref() {
            Some(fit) => (fit.class_base().to_vec(), fit.clip()),
            None => (vec![1f32; NUM_CLASSES], (0.0, f32::MAX)),
        };

        // seat modes and locks, resolved on the host exactly as the CPU
        // traversal resolves them (forced_sigma: point lock > profile,
        // hero exempt from its own profile; frozen seats play their sums)
        let mut src = vec![0i32; n];
        let mut foff = vec![0u32; n];
        let mut forced: Vec<f32> = Vec::new();
        for (i, nd) in s.nodes.iter().enumerate() {
            if nd.kind != KIND_ACTION {
                continue;
            }
            if let Some(f) = s.forced_sigma(i) {
                src[i] = 2;
                foff[i] = forced.len() as u32;
                forced.extend_from_slice(&f);
            } else if s.seat_frozen[nd.actor as usize] {
                src[i] = 1;
            }
        }
        if forced.len() > u32::MAX as usize {
            return Err("forced-strategy table beyond 32-bit indexing; solving on CPU".into());
        }
        // Reserve actual forced allocation before CDF and optional caches,
        // including the legacy path without CDF storage.
        let literal_reference_base_mb = need;
        need = reserve_forced_vram_mb(need, forced.len(), budget_mb)?;
        let static_seats: Vec<bool> = (0..np).map(|p| s.seat_static(p)).collect();
        let n_forced = src.iter().filter(|&&x| x == 2).count();
        let n_frozen = src.iter().filter(|&&x| x == 1).count();

        let reach_src = reach_sources(s);
        let act_nodes = &values.action_nodes;
        let spans = values.spans.clone();

        let mut eq_plan = EquityCachePlan::build(s, &reach_src);
        let mut mw_plan = EquityCachePlan::multiway(s, &reach_src);
        let mw_terms: Vec<u32> = s.nodes.iter().enumerate()
            .filter(|(_, nd)| s.multiway.is_some() && nd.kind == KIND_POT_SHARE && nd.live.count_ones() >= 3)
            .map(|(i, _)| i as u32).collect();
        let use_multiway = !mw_terms.is_empty();
        if use_multiway && std::env::var("PREFLOP_MW_KEY_STATS").as_deref() == Ok("1") {
            multiway_terminal_key_stats(s, &reach_src, &mw_terms);
        }
        let mut compact = if use_multiway && allow_compact {
            MultiwayCompactPlan::build(&mw_plan, np)?
        } else { MultiwayCompactPlan::union(mw_plan.blocks.len()) };
        let mut mw_batch = 0usize;
        let mut mw_cache_len = 1usize;
        let mut mw_normalized_len = 1usize;
        let mut use_mw_normalized = false;
        let mut use_mw_prepared = true;
        let mut mw_reference = None;
        let mut mw_reference_source = "not_applicable";
        let mut mw_literal_reference = None;
        if use_multiway {
            let mut fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + compact.bytes;
            let reference_fixed = mw_plan.metadata_bytes() + mw_terms.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4;
            let selected = deployed_compatible_multiway_plan(budget_mb, need, literal_reference_base_mb,
                reference_fixed, fixed, mw_plan.blocks.len(), compact.capacity,
                eq_plan.bytes(), !eq_plan.blocks.is_empty(), force_minimal)?;
            let Some(selected) = selected else {
                let one_particle = compact.capacity * (NUM_CLASSES + 1) * 4;
                return Err(format!("coupled multiway model needs at least ~{:.0} MB VRAM (budget {budget_mb} MB); solving the same model on CPU",
                    need + (fixed + one_particle) as f64 / 1e6));
            };
            mw_reference_source = selected.reference_source;
            mw_literal_reference = selected.literal_reference;
            let selected = selected.plan;
            use_mw_prepared = !selected.minimal_metadata;
            if selected.minimal_metadata {
                compact = MultiwayCompactPlan::union(mw_plan.blocks.len());
                fixed = reference_fixed;
            }
            mw_reference = selected.reference;
            let plan = selected.storage;
            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;
            use_mw_normalized = plan.normalized_bytes != 0;
            mw_normalized_len = (plan.normalized_bytes / 4).max(1);
            need += (fixed + plan.normalized_bytes + mw_cache_len * 4) as f64 / 1e6;
        } else {
            mw_plan = EquityCachePlan::disabled(np);
        }
        let eq_cache_fits = !eq_plan.blocks.is_empty()
            && need + eq_plan.bytes() as f64 / 1e6 <= budget_mb as f64;
        let use_eq_cache = mw_reference.as_ref().map_or(eq_cache_fits, |r| r.use_eq_cache);
        if use_eq_cache && !eq_cache_fits {
            return Err("reference HU equity cache does not fit the optimized layout; solving on CPU".into());
        }
        if use_eq_cache {
            need += eq_plan.bytes() as f64 / 1e6;
        } else {
            eq_plan = EquityCachePlan::disabled(np);
        }
        let eq_cache_len = if use_eq_cache { eq_plan.blocks.len() * NUM_CLASSES } else { 1 };

        // Threads in a warp evaluate consecutive hero classes. Transpose so
        // they read consecutive equities at each opponent-class step; the
        // dot product keeps the same values and accumulation order.
        let mut eq = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for i in 0..NUM_CLASSES {
            for j in 0..NUM_CLASSES {
                eq[j * NUM_CLASSES + i] = s.eq.eq(i, j);
            }
        }
        let cprob: Vec<f32> = (0..NUM_CLASSES).map(class_prob).collect();

        let arena_len = s.arena_len;
        // SAFETY: exclusive access (no solve is running while we construct)
        let (regs, strat) = unsafe { (s.regrets.slice(), s.strat_sum.slice()) };

        let ncalib = calib.iter().filter(|&&c| c != 0).count();
        if use_multiway {
            println!("preflop gpu: coupled multiway, {} particles, {} reach CDFs, {}-particle batches, {:.0} MB CDF scratch",
                super::multiway::SAMPLES, mw_plan.blocks.len(), mw_batch, mw_cache_len as f64 * 4.0 / 1e6);
            if compact.enabled {
                println!("preflop gpu: compact CDF slots {} of {}, {:.1} MB immutable map", compact.capacity, mw_plan.blocks.len(), compact.bytes as f64 / 1e6);
            }
            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve reference grouping or minimum-VRAM fit");
            }
            if !use_mw_prepared {
                println!("preflop gpu: original union/direct metadata fallback, no active/probability scratch");
            }
            if let Some(reference) = &mw_reference {
                println!("preflop gpu: {} reference, {}-particle grouping and HU-cache={} with accurately budgeted storage",
                    mw_reference_source, reference.batch, reference.use_eq_cache);
                if mw_reference_source == "corrected_budget_fallback" {
                    println!("preflop gpu: deployed grouping could not fit safely; using corrected-budget grouping");
                }
            } else {
                println!("preflop gpu: optimized capacity extension; no safely fitting reference grouping");
            }
        }
        println!(
            "preflop gpu: {n} nodes, {} levels, {} terminals ({ncalib} calibrated), \
             {n_forced} forced + {n_frozen} frozen nodes, ~{need:.0} MB VRAM",
            spans.len(),
            terms.len()
        );

        if std::env::var("PREFLOP_GPU_LAYOUT_STATS").as_deref() == Ok("1") {
            println!("preflop gpu layout: {}", serde_json::json!({
                "baseline": "optimized_8e7e4b0",
                "model": s.multiway_equity_model(), "nodes": n, "seats": np,
                "budget_mb": budget_mb, "planned_need_mb": need,
                "forced_nodes": n_forced, "frozen_nodes": n_frozen,
                "forced_elements": forced.len(), "forced_bytes": forced_storage_bytes(forced.len())?,
                "multiway_enabled": use_multiway, "multiway_batch": mw_batch,
                "multiway_particles": super::multiway::SAMPLES,
                "cdf_slots": if use_multiway { compact.capacity } else { 0 },
                "cdf_allocated_bytes": mw_cache_len * std::mem::size_of::<f32>(),
                "compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized,
                "minimal_multiway_metadata": use_multiway && !use_mw_prepared,
                "batch_policy": mw_reference_source,
                "literal_reference_multiway_batch": mw_literal_reference.map(|r|r.batch),
                "literal_reference_hu_cache_enabled": mw_literal_reference.map(|r|r.use_eq_cache),
                "reference_multiway_batch": mw_reference.as_ref().map(|r| r.batch),
                "reference_hu_cache_enabled": mw_reference.as_ref().map(|r| r.use_eq_cache),
                "hu_equity_cache_enabled": use_eq_cache,
                "hu_equity_cache_slots": if use_eq_cache { eq_plan.blocks.len() } else { 0 },
                "hu_equity_cache_allocated_bytes": eq_cache_len * std::mem::size_of::<f32>(),
            }));
        }

        Ok(PreflopGpu {
            f_init: func("pf_init_root")?,
            f_down: func("pf_down")?,
            // Separate entry points keep the generic table-size fallback's
            // register/local-memory budget independent of specialized kernels.
            f_terminal: func(match s.n {
                2 => "pf_terminal_2", 6 => "pf_terminal_6", 8 => "pf_terminal_8",
                _ => "pf_terminal",
            })?,
            f_reach_mass: func("pf_reach_mass")?,
            f_equities: func("pf_equities")?,
            f_multiway_cdf: func(if use_mw_normalized { "pf_multiway_cdf" } else { "pf_multiway_cdf_direct" })?,
            f_multiway_normalize: func("pf_multiway_normalize")?,
            f_multiway_clear_active: func("pf_multiway_clear_active")?,
            f_multiway_prepare: func("pf_multiway_prepare")?,
            f_multiway_terminal: func(if use_mw_prepared { "pf_multiway_terminal" } else { "pf_multiway_terminal_minimal" })?,
            f_up: func("pf_up")?,
            f_discount: func("pf_discount_nodes")?,
            d_kind: stream.clone_htod(&kind).map_err(e)?,
            d_actor: stream.clone_htod(&actor).map_err(e)?,
            d_na: stream.clone_htod(&na).map_err(e)?,
            d_off: stream.clone_htod(&off).map_err(e)?,
            d_cstart: stream.clone_htod(&cstart).map_err(e)?,
            d_children: stream.clone_htod(&s.children).map_err(e)?,
            d_live: stream.clone_htod(&live).map_err(e)?,
            d_winner: stream.clone_htod(&winner).map_err(e)?,
            d_potf: stream.clone_htod(&potf).map_err(e)?,
            d_pots: stream.clone_htod(&pots).map_err(e)?,
            d_inv: stream.clone_htod(&inv).map_err(e)?,
            d_rw: stream.clone_htod(&rw).map_err(e)?,
            d_potg: stream.clone_htod(&potg).map_err(e)?,
            d_calib: stream.clone_htod(&calib).map_err(e)?,
            d_cbase: stream.clone_htod(&cbase).map_err(e)?,
            clip_lo,
            clip_hi,
            d_eq: stream.clone_htod(&eq).map_err(e)?,
            d_eq_slots: stream.clone_htod(&eq_plan.slots).map_err(e)?,
            d_eq_blocks: stream.clone_htod(&eq_plan.blocks).map_err(e)?,
            d_eq_work: stream.clone_htod(&eq_plan.work).map_err(e)?,
            d_eq_cache: stream.alloc_zeros::<f32>(eq_cache_len).map_err(e)?,
            eq_spans: eq_plan.spans,
            use_eq_cache: use_eq_cache as i32,
            d_mw_order: stream.clone_htod(s.multiway.as_ref().map(|m| m.order.as_slice()).unwrap_or(&[0])).map_err(e)?,
            #[cfg(feature = "preflop-research")]
            research: None,
            #[cfg(feature = "preflop-research")]
            research_samples: super::multiway::SAMPLES as u32,
            #[cfg(feature = "preflop-research")]
            research_cv: None,
            #[cfg(feature = "preflop-research")]
            research_normalized_regret: None,
            #[cfg(feature = "preflop-research")]
            research_rm_plus: None,
            #[cfg(feature = "preflop-research")]
            research_predictive: None,
            #[cfg(feature = "preflop-research")]
            research_rm_plus_fresh: s.iteration == 0 && s.nodes.iter().enumerate().all(|(i, nd)| {
                src[i] != 0 || (nd.data_off..nd.data_off + nd.actions.len()*NUM_CLASSES)
                    .all(|ix| regs[ix] == 0.0 && strat[ix] == 0.0)
            }),
            #[cfg(feature = "preflop-research")]
            research_pair_control: None,
            #[cfg(feature = "preflop-research")]
            research_exploration: None,
            #[cfg(feature = "preflop-research")]
            research_behavioral: None,
            #[cfg(feature = "preflop-research")]
            research_exact_reuse: None,
            #[cfg(feature = "preflop-research")]
            research_average_opponents: None,
            #[cfg(feature = "preflop-research")]
            research_history_units: None,
            #[cfg(feature = "preflop-research")]
            research_root_ranges: None,
            #[cfg(feature = "preflop-research")]
            research_learning_mask: false,
            #[cfg(feature = "preflop-research")]
            research_discount_nodes: None,
            #[cfg(feature = "preflop-research")]
            research_unit_probability: false,
            #[cfg(feature = "preflop-research")]
            research_unit_fill: None,
            d_mw_lower: stream.clone_htod(s.multiway.as_ref().map(|m| m.lower.as_slice()).unwrap_or(&[0])).map_err(e)?,
            d_mw_upper: stream.clone_htod(s.multiway.as_ref().map(|m| m.upper.as_slice()).unwrap_or(&[0])).map_err(e)?,
            d_mw_slots: stream.clone_htod(&mw_plan.slots).map_err(e)?,
            d_mw_blocks: stream.clone_htod(&mw_plan.blocks).map_err(e)?,
            d_mw_work: stream.clone_htod(&mw_plan.work).map_err(e)?,
            d_mw_cdf: stream.alloc_zeros::<f32>(mw_cache_len).map_err(e)?,
            d_mw_normalized: if use_mw_prepared { stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)? } else { stream.null::<f32>().map_err(e)? },
            use_mw_normalized,
            use_mw_prepared,
            d_mw_compact: if use_mw_prepared { stream.clone_htod(&compact.map).map_err(e)? } else { stream.null::<u32>().map_err(e)? },
            mw_union_slots: mw_plan.blocks.len() as u32,
            use_mw_compact: compact.enabled as i32,
            d_mw_terms: stream.clone_htod(if mw_terms.is_empty() { &[0u32][..] } else { mw_terms.as_slice() }).map_err(e)?,
            d_mw_active: if use_mw_prepared { stream.alloc_zeros::<u32>(mw_plan.blocks.len()).map_err(e)? } else { stream.null::<u32>().map_err(e)? },
            d_mw_prob: if use_mw_prepared { stream.alloc_zeros::<f32>(mw_terms.len().max(1)).map_err(e)? } else { stream.null::<f32>().map_err(e)? },
            mw_spans: mw_plan.spans,
            mw_batch: mw_batch as u32,
            mw_nterms: mw_terms.len() as u32,
            use_multiway: use_multiway as i32,
            d_cprob: stream.clone_htod(&cprob).map_err(e)?,
            n_act: act_nodes.len() as u32,
            d_act_nodes: stream.clone_htod(act_nodes).map_err(e)?,
            d_terms: stream.clone_htod(&terms).map_err(e)?,
            d_src: stream.clone_htod(&src).map_err(e)?,
            d_foff: stream.clone_htod(&foff).map_err(e)?,
            d_forced: if forced.is_empty() {
                stream.alloc_zeros::<f32>(1).map_err(e)?
            } else {
                stream.clone_htod(&forced).map_err(e)?
            },
            static_seats,
            constrained_br: (0..np).map(|p| s.constrained_br(p)).collect(),
            d_regrets: stream.clone_htod(regs).map_err(e)?,
            d_strat: stream.clone_htod(strat).map_err(e)?,
            d_reach_src: stream.clone_htod(&reach_src).map_err(e)?,
            d_reach: stream
                .alloc_zeros::<f32>(reach_blocks * NUM_CLASSES)
                .map_err(e)?,
            d_reach_mass: stream.alloc_zeros::<f32>(reach_blocks).map_err(e)?,
            d_val_slot: stream.clone_htod(&values.slots).map_err(e)?,
            d_val: stream.alloc_zeros::<f32>(values.blocks * NUM_CLASSES).map_err(e)?,
            spans,
            nterms: terms.len() as u32,
            np: np as i32,
            arena_len,
            d_eval_roots: stream.alloc_zeros::<f32>(2 * np * NUM_CLASSES).map_err(e)?,
            eval_graph: None,
            eval_warmed: false,
            learning_graphs: (0..np).map(|_| None).collect(),
            warmed: false,
            h_snapshot: Mutex::new(None),
            #[cfg(test)]
            phase_trace: None,
            _ctx: ctx,
            stream,
        })
    }

    /// Isolated research only. Must be configured before any learning/graph capture.
    #[cfg(feature = "preflop-research")]
    pub fn configure_research(&mut self, experiment: super::convergence_research::Experiment) -> Result<(), String> {
        if self.research_cv.is_some() || self.research_behavioral.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.warmed || self.eval_warmed || self.research_history_units.is_some() || self.research_root_ranges.is_some() { return Err("configure research before learning or evaluation; compact roots require full particles".into()); }
        self.research = Some(experiment);
        Ok(())
    }

    #[cfg(feature = "preflop-research")]
    fn research_tables(&mut self, learning: bool) -> Result<(), String> {
        self.research_tables_select(learning, learning)
    }

    #[cfg(feature = "preflop-research")]
    fn research_tables_select(&mut self, learning: bool, advance: bool) -> Result<(), String> {
        if let Some(control)=&mut self.research_pair_control {control.learning=learning;}
        let Some(r) = &mut self.research else { return Ok(()); };
        self.research_samples = if learning { r.samples } else { super::multiway::SAMPLES as u32 };
        if r.samples == super::multiway::SAMPLES as u32 || self.use_multiway == 0 { return Ok(()); }
        let shift = if learning { if advance {r.next_offset()} else {r.offset} } else { 0 };
        // All three tables retain their allocation/address, so captured CUDA
        // graphs see the current sample set. Full checks restore canonical order.
        let rotate = |v: &[u32]| {
            let split = shift * NUM_CLASSES;
            v[split..].iter().chain(&v[..split]).copied().collect::<Vec<_>>()
        };
        self.stream.memcpy_htod(&rotate(&r.deck.order), &mut self.d_mw_order).map_err(e)?;
        self.stream.memcpy_htod(&rotate(&r.deck.lower), &mut self.d_mw_lower).map_err(e)?;
        self.stream.memcpy_htod(&rotate(&r.deck.upper), &mut self.d_mw_upper).map_err(e)?;
        self.stream.synchronize().map_err(e)?;
        Ok(())
    }

    fn cfg(blocks: u32) -> LaunchConfig {
        LaunchConfig {
            grid_dim: (blocks.max(1), 1, 1),
            // Narrow levels need more lanes per node; wide levels favor more resident nodes.
            block_dim: (if blocks < 256 { BLOCK } else { 64 }, 1, 1),
            shared_mem_bytes: 0,
        }
    }

    /// One full pass for traverser `p`. mode 0 updates regrets/strategy;
    /// 1 evaluates the average strategy; 2 is best response vs average.
    fn sweep(&mut self, p: i32, mode: i32) -> Result<(), String> {
        #[cfg(feature = "preflop-research")]
        if self.research_predictive_sweep(p, mode)? { return Ok(()); }
        self.down(mode, p)?;
        self.terminals(p)?;
        self.up(p, mode)?;
        #[cfg(feature = "preflop-research")]
        if mode == 0 { self.research_rm_plus_clip(p)?; }
        Ok(())
    }

    #[cfg(feature = "preflop-research")]
    pub(crate) fn research_set_root_ranges(&mut self,ranges:Vec<Vec<f32>>)->Result<(),String> {
        if self.research_cv.is_some() || self.research_behavioral.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.warmed || self.eval_warmed || self.research.is_some() || self.research_root_ranges.is_some() || self.research_pair_control.is_some() || self.research_exploration.is_some() || self.research_history_units.is_some()
            || ranges.len()!=self.np as usize || ranges.iter().any(|r|r.len()!=NUM_CLASSES
                || r.iter().any(|x|!x.is_finite() || *x<0.0)
                || (r.iter().map(|&x|x as f64).sum::<f64>()-1.0).abs()>1e-5) {
            return Err("research roots require a fresh full-particle GPU and normalized seat ranges".into());
        }
        let flat:Vec<f32>=ranges.iter().flatten().copied().collect();
        let device=self.stream.clone_htod(&flat).map_err(e)?;
        self.research_root_ranges=Some((ranges,device));
        Ok(())
    }

    /// Restrict offline learning without changing the saved model's constraints.
    /// A fresh unmasked engine must perform final best-response evaluation.
    #[cfg(feature = "preflop-research")]
    pub(crate) fn research_restrict_learning(&mut self,s:&PreflopSolver,allowed:&std::collections::HashSet<usize>)->Result<(),String> {
        if self.research_cv.is_some() || self.research_behavioral.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.warmed || self.eval_warmed || self.research_learning_mask || self.research_normalized_regret.is_some() || self.research_pair_control.is_some() || self.research_exploration.is_some() || self.research_history_units.is_some() || allowed.is_empty()
            || allowed.iter().any(|&i|i>=s.nodes.len() || s.nodes[i].kind!=KIND_ACTION) {
            return Err("fresh engine and nonempty action-node mask required".into());
        }
        let mut src=self.stream.clone_dtoh(&self.d_src).map_err(e)?;
        if src.len()!=s.nodes.len() {return Err("learning mask topology mismatch".into());}
        let mut static_seats=vec![true;s.n];
        let mut discount_nodes=Vec::new();
        for (i,nd) in s.nodes.iter().enumerate() {
            if nd.kind!=KIND_ACTION || src[i]!=0 {continue;}
            if allowed.contains(&i) {static_seats[nd.actor as usize]=false;discount_nodes.push(i as u32);} else {src[i]=1;}
        }
        if static_seats.iter().all(|x|*x) {return Err("mask contains no learning decisions".into());}
        self.d_src=self.stream.clone_htod(&src).map_err(e)?;
        self.research_discount_nodes=Some(self.stream.clone_htod(&discount_nodes).map_err(e)?);
        self.static_seats=static_seats;
        self.research_learning_mask=true;
        Ok(())
    }

    /// Reach and sigma depend on the strategy source, not the traverser.
    /// Evaluation modes 1 and 2 both use the same average strategy.
    fn down(&mut self, mode: i32, p: i32) -> Result<(), String> {
        #[cfg(test)]
        self.phase_mark("down", p)?;
        unsafe {
            self.stream
                .launch_builder(&self.f_init)
                .arg(&self.d_cprob)
                .arg(&mut self.d_reach)
                .arg(&self.np)
                .launch(Self::cfg(4))
                .map_err(e)?;
        }
        #[cfg(feature = "preflop-research")]
        if let Some((_,ranges))=&self.research_root_ranges {
            let mut root=self.d_reach.slice_mut(0..self.np as usize*NUM_CLASSES);
            self.stream.memcpy_dtod(ranges,&mut root).map_err(e)?;
        }
        for li in 0..self.spans.len() {
            let (start, count) = self.spans[li];
            if count == 0 {
                continue;
            }
            let (start, count) = (start as i32, count as i32);
            let policy = &self.d_regrets;
            #[cfg(feature = "preflop-research")]
            let policy = if mode == 0 { self.research_predictive.as_ref().map_or(policy, |r| &r.policy) } else { policy };
            unsafe {
                self.stream
                    .launch_builder(&self.f_down)
                    .arg(&self.d_act_nodes)
                    .arg(&start)
                    .arg(&count)
                    .arg(&self.d_actor)
                    .arg(&self.d_na)
                    .arg(&self.d_off)
                    .arg(&self.d_cstart)
                    .arg(&self.d_children)
                    .arg(policy)
                    .arg(&self.d_strat)
                    .arg(&self.d_src)
                    .arg(&self.d_foff)
                    .arg(&self.d_forced)
                    .arg(&self.d_reach_src)
                    .arg(&mut self.d_reach)
                    .arg(&self.np)
                    .arg(&mode)
                    .launch(Self::cfg(count as u32))
                    .map_err(e)?;
            }
            #[cfg(feature = "preflop-research")]
            self.research_explore_reach(start,count,p,mode)?;
            #[cfg(feature = "preflop-research")]
            self.research_behavioral_reach(start,count,mode)?;
            #[cfg(feature = "preflop-research")]
            self.research_average_opponent_reach(start,count,p,mode)?;
        }
        let blocks = self.d_reach_mass.len() as u32;
        unsafe {
            self.stream.launch_builder(&self.f_reach_mass)
                .arg(&self.d_reach)
                .arg(&mut self.d_reach_mass)
                .launch(LaunchConfig { block_dim: (128, 1, 1), ..Self::cfg(blocks) })
                .map_err(e)?;
        }
        if self.use_eq_cache != 0 {
            let which = if mode == 0 { p as usize } else { self.np as usize };
            let (start, count) = self.eq_spans[which];
            if count > 0 {
                unsafe {
                    self.stream.launch_builder(&self.f_equities)
                        .arg(&self.d_eq_work).arg(&start)
                        .arg(&self.d_eq_blocks).arg(&self.d_eq)
                        .arg(&self.d_reach).arg(&self.d_reach_mass)
                        .arg(&mut self.d_eq_cache)
                        .launch(Self::cfg(count)).map_err(e)?;
                }
            }
        }
        Ok(())
    }

    fn terminals(&mut self, p: i32) -> Result<(), String> {
        self.terminals_masked(p, 1)
    }

    fn terminals_masked(&mut self, p: i32, gate: i32) -> Result<(), String> {
        #[cfg(test)]
        self.phase_mark("ordinary_terminals", p)?;
        let tcount = self.nterms as i32;
        unsafe {
            self.stream
                .launch_builder(&self.f_terminal)
                .arg(&self.d_terms)
                .arg(&tcount)
                .arg(&p)
                .arg(&self.np)
                .arg(&self.d_kind)
                .arg(&self.d_live)
                .arg(&self.d_winner)
                .arg(&self.d_potf)
                .arg(&self.d_pots)
                .arg(&self.d_inv)
                .arg(&self.d_rw)
                .arg(&self.d_potg)
                .arg(&self.d_calib)
                .arg(&self.d_cbase)
                .arg(&self.clip_lo)
                .arg(&self.clip_hi)
                .arg(&self.d_eq)
                .arg(&self.d_reach_src)
                .arg(&self.d_reach)
                .arg(&self.d_reach_mass)
                .arg(&self.d_eq_slots)
                .arg(&self.d_eq_cache)
                .arg(&self.use_eq_cache)
                .arg(&self.use_multiway)
                .arg(&self.d_val_slot)
                .arg(&mut self.d_val)
                .launch(Self::cfg(self.nterms))
                .map_err(e)?;
        }
        self.multiway_terminals(p, gate)
    }

    fn multiway_terminals(&mut self, p: i32, gate: i32) -> Result<(), String> {
        #[cfg(feature = "preflop-research")]
        if self.research_exact_reuse.is_some() { return self.exact_reuse_terminals(p, gate); }
        if self.use_multiway != 0 {
            let (work_start, work_count) = self.mw_spans[p as usize];
            if work_count > 0 {
                #[cfg(test)]
                self.phase_mark("prepare", p)?;
                // Minimal metadata has neither active flags nor prepared probabilities.
                // Force gate=0 so direct CDF never reads the null active pointer.
                let gate = if self.use_mw_prepared {gate} else {0};
                let slot_count = self.d_mw_active.len() as u32;
                unsafe {
                    // Fixed grid bounds and device-only state keep graph replay valid.
                    if self.use_mw_prepared {
                    if gate != 0 {
                    self.stream.launch_builder(&self.f_multiway_clear_active)
                        .arg(&mut self.d_mw_active).arg(&slot_count)
                        .launch(LaunchConfig { grid_dim: (slot_count.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    }
                    self.stream.launch_builder(&self.f_multiway_prepare)
                        .arg(&self.d_mw_terms).arg(&self.mw_nterms).arg(&p).arg(&self.np)
                        .arg(&self.d_live).arg(&self.d_reach_src).arg(&self.d_reach_mass)
                        .arg(&self.d_mw_slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob).arg(&gate)
                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    }
                    // Rebuild for every terminals call, even when evaluation disables
                    // active gating. Test/manual reach replacement must not reuse stale data.
                    if self.use_mw_normalized {
                        #[cfg(test)]
                        self.phase_mark("normalize", p)?;
                        self.stream.launch_builder(&self.f_multiway_normalize)
                            .arg(&self.d_mw_work).arg(&work_start).arg(&self.d_mw_blocks)
                            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&self.use_mw_compact)
                            .arg(&mut self.d_mw_normalized)
                            .launch(LaunchConfig { grid_dim: (work_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    }
                    #[cfg(feature = "preflop-research")]
                    if self.research_unit_probability {
                        self.stream.launch_builder(self.research_unit_fill.as_ref().ok_or("missing research fill kernel")?)
                            .arg(&mut self.d_mw_prob).arg(&self.mw_nterms)
                            .launch(LaunchConfig {grid_dim:(self.mw_nterms.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;
                    }
                }
                #[cfg(not(feature = "preflop-research"))]
                let samples = super::multiway::SAMPLES as u32;
                #[cfg(feature = "preflop-research")]
                let samples = self.research_samples;
                #[cfg(feature = "preflop-research")]
                self.research_pair_project(p,gate)?;
                for sample_start in (0..samples).step_by(self.mw_batch as usize) {
                    let sample_count = self.mw_batch.min(samples - sample_start);
                    unsafe {
                        #[cfg(test)]
                        self.phase_mark("cdf", p)?;
                        self.stream.launch_builder(&self.f_multiway_cdf)
                            .arg(&self.d_mw_work).arg(&work_start).arg(&self.d_mw_blocks)
                            .arg(&self.d_mw_order)
                            .arg(if self.use_mw_normalized { &self.d_mw_normalized } else { &self.d_reach })
                            .arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&self.use_mw_compact)
                            .arg(&mut self.d_mw_cdf).arg(&sample_start).arg(&sample_count).arg(&self.mw_batch)
                            .launch(LaunchConfig { grid_dim: (work_count, sample_count.div_ceil(4), 1), block_dim: (128, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                        #[cfg(test)]
                        self.phase_mark("coupled_terminals", p)?;
                        self.stream.launch_builder(&self.f_multiway_terminal)
                            .arg(&self.d_mw_terms).arg(&p).arg(&self.np)
                            .arg(&self.d_live).arg(&self.d_pots).arg(&self.d_inv)
                            .arg(&self.d_reach_src).arg(if self.use_mw_prepared { &self.d_mw_prob } else { &self.d_reach_mass })
                            .arg(&self.d_mw_slots).arg(&self.d_mw_compact).arg(&self.mw_union_slots).arg(&self.use_mw_compact).arg(&self.d_mw_cdf)
                            .arg(&self.d_mw_lower).arg(&self.d_mw_upper)
                            .arg(&sample_start).arg(&sample_count).arg(&self.mw_batch).arg(&samples)
                            .arg(&self.d_val_slot).arg(&mut self.d_val)
                            .launch(LaunchConfig { block_dim: (192, 1, 1), ..Self::cfg(self.mw_nterms) }).map_err(e)?;
                    }
                    #[cfg(feature = "preflop-research")]
                    self.research_pair_correct(p,sample_start,sample_count,samples)?;
                }
            }
        }
        Ok(())
    }

    /// Only action-node values are overwritten. Terminal values and reach
    /// stay available for another read-only evaluation of this seat.
    fn up(&mut self, p: i32, mode: i32) -> Result<(), String> {
        #[cfg(test)]
        self.phase_mark(match mode { 0 => "up_learn", 1 => "up_average", _ => "up_br" }, p)?;
        for li in (0..self.spans.len()).rev() {
            #[cfg(feature = "preflop-research")]
            if self.research_behavioral_up(p,li,mode)? {continue;}
            #[cfg(feature = "preflop-research")]
            if mode==0 && self.research_normalized_up(p,li)? {continue;}
            #[cfg(feature = "preflop-research")]
            if mode==0 && self.research_fixed_units_up(p,li)? {continue;}
            let (start, count) = self.spans[li];
            if count == 0 {
                continue;
            }
            let (start, count) = (start as i32, count as i32);
            unsafe {
                self.stream
                    .launch_builder(&self.f_up)
                    .arg(&self.d_act_nodes)
                    .arg(&start)
                    .arg(&count)
                    .arg(&p)
                    .arg(&self.np)
                    .arg(&mode)
                    .arg(&self.d_actor)
                    .arg(&self.d_na)
                    .arg(&self.d_off)
                    .arg(&self.d_cstart)
                    .arg(&self.d_children)
                    .arg(&self.d_src)
                    .arg(&self.d_foff)
                    .arg(&self.d_forced)
                    .arg(&self.d_reach_src)
                    .arg(&self.d_reach)
                    .arg(&mut self.d_regrets)
                    .arg(&mut self.d_strat)
                    .arg(&self.d_val_slot)
                    .arg(&mut self.d_val)
                    .launch(Self::cfg(count as u32))
                    .map_err(e)?;
            }
        }
        Ok(())
    }

    /// One DCFR iteration: sequential alternating updates per player (same
    /// semantics as the CPU), then the discount kernel. Bumps s.iteration.
    pub fn iterate(&mut self, s: &mut PreflopSolver) -> Result<(), String> {
        self.try_iterate(s, None).map(|_| ())
    }

    /// `iterate` with a cooperative stop checked between per-player sweeps;
    /// Ok(false) = interrupted (iteration count and discounting untouched,
    /// mirroring `PreflopSolver::try_iterate`).
    pub fn try_iterate(
        &mut self,
        s: &mut PreflopSolver,
        stop: Option<&AtomicBool>,
    ) -> Result<bool, String> {
        self.try_iterate_counter(&mut s.iteration, stop)
    }

    /// Device-owned learning without borrowing the published CPU solver.
    /// The caller must retain this counter across every device iteration and
    /// publish it with a successful arena download. It starts at the iteration
    /// used to construct this engine. Stop/error counter semantics are identical
    /// to `try_iterate`; interrupted sweeps are not rolled back.
    pub fn try_iterate_counter(
        &mut self,
        iteration: &mut u32,
        stop: Option<&AtomicBool>,
    ) -> Result<bool, String> {
        let stopped = || stop.map_or(false, |f| f.load(Ordering::Relaxed));
        #[cfg(feature = "preflop-research")]
        self.research_exploration_schedule(*iteration)?;
        for p in 0..self.np {
            if self.static_seats[p as usize] {
                continue; // frozen / fully ruled: its own pass writes nothing
            }
            if stopped() {
                self.stream.synchronize().map_err(e)?;
                return Ok(false);
            }
            #[cfg(feature = "preflop-research")]
            self.research_tables(true)?;
            #[cfg(feature = "preflop-research")]
            if self.research_cv.is_some() {
                self.cv_sweep(p, *iteration)?;
                continue;
            }
            if self.warmed && self.learning_graphs[p as usize].is_none() {
                // The topology and seat policies are fixed for this engine.
                // Capture one alternating update at a time so stop checks
                // still run between seats, exactly as with eager launches.
                self.stream.begin_capture(
                    sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL,
                ).map_err(e)?;
                let result = self.sweep(p, 0);
                let graph = self.stream.end_capture(
                    sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
                ).map_err(e)?;
                result?;
                self.learning_graphs[p as usize] = Some(
                    graph.ok_or_else(|| "preflop graph capture failed".to_string())?
                );
            }
            if let Some(graph) = &self.learning_graphs[p as usize] {
                graph.launch().map_err(e)?;
            } else {
                self.sweep(p, 0)?;
            }
        }
        if stopped() {
            self.stream.synchronize().map_err(e)?;
            return Ok(false);
        }
        *iteration += 1;
        let t = *iteration as f64;
        let pos = (t.powf(1.5) / (t.powf(1.5) + 1.0)) as f32;
        let neg = 0.5f32;
        let sd = ((t / (t + 1.0)).powi(2)) as f32;
        #[cfg(feature = "preflop-research")]
        let (pos, neg, sd) = self.research.as_ref().map_or((pos, neg, sd), |r| r.factors(*iteration));
        #[cfg(feature = "preflop-research")]
        let (pos, neg, sd) = if self.research_predictive.is_some() {
            (1.0f32, 1.0f32, (t / (t + 1.0)).powi(2) as f32)
        } else if self.research_rm_plus.is_some() {
            (1.0f32, 1.0f32, (t / (t + 1.0)) as f32)
        } else { (pos, neg, sd) };
        // per action node (not flat over the arena): a frozen actor's
        // strategy sums are its play and must not decay â€” same rule as the
        // CPU's iterate()
        #[cfg(test)]
        self.phase_mark("discount", -1)?;
        let n_act = self.n_act as i32;
        let discount_nodes=&self.d_act_nodes;
        #[cfg(feature = "preflop-research")]
        let (discount_nodes,n_act)=self.research_discount_nodes.as_ref()
            .map_or((discount_nodes,n_act),|nodes|(nodes,nodes.len() as i32));
        unsafe {
            self.stream
                .launch_builder(&self.f_discount)
                .arg(discount_nodes)
                .arg(&n_act)
                .arg(&self.d_na)
                .arg(&self.d_off)
                .arg(&self.d_src)
                .arg(&mut self.d_regrets)
                .arg(&mut self.d_strat)
                .arg(&pos)
                .arg(&neg)
                .arg(&sd)
                .launch(Self::cfg(n_act as u32))
                .map_err(e)?;
        }
        #[cfg(test)]
        self.phase_mark("end", -1)?;
        self.stream.synchronize().map_err(e)?;
        self.warmed = true;
        Ok(true)
    }

    /// Combine the last sweep's root values into a scalar EV.
    #[cfg(test)]
    fn root_ev(&self) -> Result<f64, String> {
        // node 0's block only â€” copying the full value scratch
        // stalls every checkpoint on big trees
        let root = self.d_val.slice(0..NUM_CLASSES);
        let v: Vec<f32> = self.stream.clone_dtoh(&root).map_err(e)?;
        let mut total = 0f64;
        for h in 0..NUM_CLASSES {
            total += class_prob(h) as f64 * v[h] as f64;
        }
        Ok(total)
    }

    /// Per-player best-response gaps and average-strategy EVs (bb).
    pub fn gaps_and_evs(&mut self) -> Result<(Vec<f64>, Vec<f64>), String> {
        #[cfg(feature = "preflop-research")]
        if self.research_learning_mask {return Err("research learning mask: evaluate using a fresh unmasked engine".into());}
        #[cfg(feature = "preflop-research")]
        self.research_tables(false)?;
        // The first check warms lazy-loaded kernels. Subsequent checks replay
        // the same evaluation and retain every root on device until one download.
        // Graphs capture addresses, not strategy values: solves can continue
        // between checks without rebuilding this immutable-topology graph.
        if self.eval_warmed && self.eval_graph.is_none() {
            self.stream.begin_capture(
                sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL,
            ).map_err(e)?;
            let result = self.queue_evaluation();
            let graph = self.stream.end_capture(
                sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
            ).map_err(e)?;
            result?;
            self.eval_graph = Some(graph.ok_or_else(|| "preflop evaluation graph capture failed".to_string())?);
        }
        if let Some(graph) = &self.eval_graph {
            graph.launch().map_err(e)?;
        } else {
            self.queue_evaluation()?;
        }
        #[cfg(test)]
        self.phase_mark("end", -1)?;
        let roots = self.stream.clone_dtoh(&self.d_eval_roots).map_err(e)?;
        self.eval_warmed = true;
        let dot = |_p:usize, values: &[f32]| {
            let mut total = 0f64;
            for h in 0..NUM_CLASSES {
                let weight=class_prob(h);
                #[cfg(feature = "preflop-research")]
                let weight=self.research_root_ranges.as_ref().map(|r|r.0[_p][h]).unwrap_or(weight);
                total += weight as f64 * values[h] as f64;
            }
            total
        };
        let mut gaps = Vec::with_capacity(self.np as usize);
        let mut evs = Vec::with_capacity(self.np as usize);
        for p in 0..self.np as usize {
            let off = 2 * p * NUM_CLASSES;
            let br = dot(p,&roots[off..off + NUM_CLASSES]);
            let avg = dot(p,&roots[off + NUM_CLASSES..off + 2 * NUM_CLASSES]);
            gaps.push(br - avg);
            evs.push(avg);
        }
        Ok((gaps, evs))
    }

    fn queue_evaluation(&mut self) -> Result<(), String> {
        self.down(1, -1)?;
        for p in 0..self.np {
            // Average reaches are typically dense: avoid mask atomics here.
            self.terminals_masked(p, 0)?;
            for (slot, mode) in [if self.constrained_br[p as usize] { 3 } else { 2 }, 1].into_iter().enumerate() {
                self.up(p, mode)?;
                #[cfg(test)]
                self.phase_mark("root_copy", p)?;
                let off = (2 * p as usize + slot) * NUM_CLASSES;
                let root = self.d_val.slice(0..NUM_CLASSES);
                let mut dst = self.d_eval_roots.slice_mut(off..off + NUM_CLASSES);
                self.stream.memcpy_dtod(&root, &mut dst).map_err(e)?;
            }
        }
        Ok(())
    }

    /// Copy the arenas back so node_view/export/browse see the GPU solve.
    pub fn sync_to_cpu(&self, s: &mut PreflopSolver) -> Result<(), String> {
        if self.arena_len == 0 {
            return Ok(());
        }
        // Stage both arenas before publishing either. Reusing pinned memory
        // avoids allocation and pageable-DMA staging at each checkpoint,
        // while preserving the old CPU snapshot if a transfer fails.
        let mut snapshot = self.h_snapshot.lock().map_err(e)?;
        if snapshot.is_none() {
            *snapshot = PinnedBuf::new(&self._ctx, self.arena_len * 2).ok();
        }
        let Some(buf) = snapshot.as_mut() else {
            // Page locking can be unavailable even when ordinary RAM is
            // available. Keep the original transactional download fallback.
            let regs = self.stream.clone_dtoh(&self.d_regrets).map_err(e)?;
            let strat = self.stream.clone_dtoh(&self.d_strat).map_err(e)?;
            unsafe {
                s.regrets.slice_mut().copy_from_slice(&regs);
                s.strat_sum.slice_mut().copy_from_slice(&strat);
            }
            return Ok(());
        };
        let (regs, strat) = buf.as_mut_slice().split_at_mut(self.arena_len);
        self.stream.memcpy_dtoh(&self.d_regrets, regs).map_err(e)?;
        self.stream.memcpy_dtoh(&self.d_strat, strat).map_err(e)?;
        self.stream.synchronize().map_err(e)?;
        // SAFETY: &mut PreflopSolver â†’ no concurrent traversal
        unsafe {
            s.regrets.slice_mut().copy_from_slice(regs);
            s.strat_sum.slice_mut().copy_from_slice(strat);
        }
        Ok(())
    }
}

// silence unused warnings for tree buffers only read by kernels
impl PreflopGpu {
    #[allow(dead_code)]
    fn _keep(&self) -> usize {
        self.d_kind.len() + self.d_winner.len() + self.arena_len
    }
}

// Diagnostic-only eager phase timing. This field, code and every call site are
// compiled out of production binaries (including the frozen example harness).
#[cfg(test)]
struct PhaseEventTrace {
    events: Vec<cudarc::driver::CudaEvent>,
    marks: Vec<(&'static str, i32)>,
}

#[cfg(test)]
impl PreflopGpu {
    fn phase_mark(&mut self, phase: &'static str, seat: i32) -> Result<(), String> {
        if let Some(trace) = &mut self.phase_trace {
            let event = trace.events.get(trace.marks.len())
                .ok_or_else(|| "phase event pool exhausted".to_string())?;
            event.record(&self.stream).map_err(e)?;
            trace.marks.push((phase, seat));
        }
        Ok(())
    }

    fn phase_profile_begin(&mut self) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
        assert!(self.phase_trace.is_none(), "nested phase profiling");
        // Host hooks are bypassed by graphs. Eager launch the same operations
        // with lazy kernels already warm; never change numerical state here.
        for graph in &mut self.learning_graphs { *graph = None; }
        self.eval_graph = None;
        self.warmed = false;
        self.eval_warmed = false;
        let batches = super::multiway::SAMPLES.div_ceil(self.mw_batch.max(1) as usize);
        let capacity = self.np as usize * (2 * batches + 16) + 8;
        let mut events = Vec::with_capacity(capacity);
        for _ in 0..capacity {
            events.push(self._ctx.new_event(Some(sys::CUevent_flags::CU_EVENT_DEFAULT)).map_err(e)?);
        }
        self.phase_trace = Some(PhaseEventTrace { events, marks: Vec::with_capacity(capacity) });
        Ok(())
    }

    fn phase_profile_end(&mut self) -> Result<serde_json::Value, String> {
        self.stream.synchronize().map_err(e)?;
        let trace = self.phase_trace.take().ok_or_else(|| "phase profiling not active".to_string())?;
        assert!(trace.marks.len() >= 2);
        assert_eq!(trace.marks.last().unwrap().0, "end");
        let mut phases = std::collections::BTreeMap::<(&str, i32), (f64, usize)>::new();
        for (i, &(phase, seat)) in trace.marks[..trace.marks.len()-1].iter().enumerate() {
            assert_ne!(phase, "end", "one operation per phase trace");
            let ms = trace.events[i].elapsed_ms(&trace.events[i+1]).map_err(e)? as f64;
            assert!(ms.is_finite() && ms >= 0.0);
            let row = phases.entry((phase, seat)).or_default();
            row.0 += ms; row.1 += 1;
        }
        let total = trace.events[0].elapsed_ms(&trace.events[trace.marks.len()-1]).map_err(e)?;
        let rows: Vec<_> = phases.iter().map(|((phase,seat),(ms,count))|
            serde_json::json!({"phase":phase,"seat":seat,"ms":ms,"intervals":count})).collect();
        Ok(serde_json::json!({"execution":"eager_cuda_events","gpu_ms":total,
            "interval_sum_ms":phases.values().map(|x|x.0).sum::<f64>(),"rows":rows}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

    #[test]
    fn coupled_minimal_metadata_preserves_graphs_and_counterfactual_values() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let mut results=Vec::new();
        let mut metadata=Vec::new();
        for minimal in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            let mut gpu=PreflopGpu::new_with_layout_mode(&s,2000,true,minimal).unwrap();
            assert_eq!(!gpu.use_mw_prepared,minimal);
            if minimal {
                assert!(!gpu.use_mw_normalized && gpu.use_mw_compact==0);
                assert_eq!((gpu.d_mw_active.len(),gpu.d_mw_prob.len(),gpu.d_mw_normalized.len(),gpu.d_mw_compact.len()),(0,0,0,0));
            }
            metadata.push((gpu.mw_batch,gpu.use_eq_cache));
            let mut checkpoints=Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (g,e)=gpu.gaps_and_evs().unwrap();
                checkpoints.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    g.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),e.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.learning_graphs.iter().any(|g|g.is_some()) && gpu.eval_graph.is_some());
            for g in &mut gpu.learning_graphs {*g=None;} gpu.eval_graph=None;
            let target=s.nodes.iter().position(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()==3).unwrap();
            let live:Vec<_>=(0..s.n).filter(|p|s.nodes[target].live&(1<<p)!=0).collect();
            let folded=(0..s.n).find(|p|s.nodes[target].live&(1<<p)==0).unwrap();
            let p=live[0];
            let sources=gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots=gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let at=slots[target] as usize*NUM_CLASSES;
            let mut terminals=Vec::new();
            // Same distributions for positive -> own-zero -> live-zero ->
            // folded-zero -> positive. Own zero must not affect counterfactual value.
            for (zero,gate) in [(None,1),(Some(p),1),(Some(live[1]),1),(Some(folded),1),(None,0)] {
                let mut reach=vec![0f32;gpu.d_reach.len()];
                for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    let h=block*17%NUM_CLASSES;
                    r[h]=0.03125;r[(h+53)%NUM_CLASSES]=0.0625;r[(h+107)%NUM_CLASSES]=0.125;
                }
                if let Some(q)=zero {let off=sources[target*s.n+q] as usize*NUM_CLASSES;reach[off..off+NUM_CLASSES].fill(0.0);}
                gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
                unsafe {gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                    .launch(LaunchConfig {block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
                gpu.d_mw_cdf=gpu.stream.clone_htod(&vec![f32::NAN;gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_val=gpu.stream.clone_htod(&vec![123456f32;gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32,gate).unwrap();
                let actual=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let local:Vec<Vec<f32>>=(0..s.n).map(|q|{let off=sources[target*s.n+q] as usize*NUM_CLASSES;reach[off..off+NUM_CLASSES].to_vec()}).collect();
                let mut expected=vec![0f32;NUM_CLASSES];s.terminal_value(target,p,&local,&mut expected);
                for h in 0..NUM_CLASSES {assert!(actual[at+h].is_finite() && (actual[at+h]-expected[h]).abs()<2e-5);}
                if zero.is_some() && zero!=Some(p) {assert!(actual[at..at+NUM_CLASSES].iter().all(|x|*x==0.0));}
                terminals.push(actual[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()).collect::<Vec<_>>());
            }
            assert_eq!(terminals[0],terminals[1],"own zero must not prune counterfactual values");
            assert_eq!(terminals[0],terminals[4],"ungated positive recovery must discard stale zero state");
            results.push((checkpoints,terminals));
        }
        assert_eq!(metadata[0],metadata[1],"same batch/cache required for exact control");
        assert_eq!(results[0],results[1]);
    }

    #[test]
    #[ignore = "supplementary real integer-MB low-memory constructor boundary"]
    fn coupled_minimal_metadata_retains_former_union_budget_fit() {
        let eq=phase_test_equity();
        let mut chosen=None;
        for n in 4usize..=6 {
            let mut posts=vec![0.0;n];posts[n-2]=0.5;posts[n-1]=1.0;
            let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
                "positions":(0..n).map(|p|format!("P{p}")).collect::<Vec<_>>(),
                "stack":20.0,"posts":posts,"limp":true,"open_raises":[2.0,3.0],
                "raise_mults":[3.0],"max_raises":2,"add_allin":false,
                "rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
            })).unwrap();
            let s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            if s.nodes.len()>250000 {continue;}
            let src=reach_sources(&s);let mw=EquityCachePlan::multiway(&s,&src);let hu=EquityCachePlan::build(&s,&src);
            let compact=MultiwayCompactPlan::build(&mw,s.n).unwrap();
            if !compact.enabled {continue;}
            let terms=s.nodes.iter().filter(|n|n.kind==KIND_POT_SHARE && n.live.count_ones()>=3).count();
            let literal_base=minimum_vram_mb(&s,ValuePlan::build(&s).blocks);
            let base=literal_base+forced_storage_bytes(0).unwrap() as f64/1e6;
            let fixed=mw.metadata_bytes()+terms*4+3*crate::preflop::multiway::SAMPLES*NUM_CLASSES*4;
            let extra=terms*4+mw.blocks.len()*4;
            let first=(base+(fixed+mw.blocks.len()*680) as f64/1e6).ceil() as u64;
            let last=(base+(fixed+mw.blocks.len()*680*32) as f64/1e6).ceil() as u64;
            for budget in first..=last {
                let union=deployed_compatible_multiway_plan(budget,base,literal_base,fixed,fixed+extra,mw.blocks.len(),mw.blocks.len(),hu.bytes(),!hu.blocks.is_empty(),false).unwrap();
                let Some(union)=union else {continue;};let union=union.plan;
                if !union.minimal_metadata {continue;}
                let compact_plan=deployed_compatible_multiway_plan(budget,base,literal_base,fixed,fixed+extra+compact.bytes,mw.blocks.len(),compact.capacity,hu.bytes(),!hu.blocks.is_empty(),false).unwrap().unwrap().plan;
                if compact_plan.minimal_metadata {continue;}
                chosen=Some((cfg.clone(),budget,union.storage.batch,union.reference.unwrap().use_eq_cache));break;
            }
            if chosen.is_some(){break;}
        }
        let (cfg,budget,batch,cache)=chosen.expect("bounded fixture must cross an integer-MB metadata boundary");
        let mut results=Vec::new();
        for allow_compact in [false,true] {
            let mut s=PreflopSolver::new(cfg.clone(),eq.clone()).unwrap();
            // Normal planner, no forced minimal override: union must automatically
            // retain its old fit while compact may keep the preferred metadata.
            let mut gpu=PreflopGpu::new_with_layout(&s,budget,allow_compact).unwrap();
            assert_eq!(gpu.use_mw_prepared,allow_compact);assert_eq!(gpu.mw_batch as usize,batch);
            assert_eq!(gpu.use_eq_cache!=0,cache);
            gpu.iterate(&mut s).unwrap();let (g,e)=gpu.gaps_and_evs().unwrap();
            results.push((gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                g.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),e.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
        }
        assert_eq!(results[0],results[1]);
        eprintln!("minimal metadata boundary: {budget} MB, batch {batch}, HU cache {cache}");
    }
    #[test]
    fn coupled_hu_cached_and_direct_terminal_bits_match() {
        let eq=phase_test_equity();
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let s=PreflopSolver::new(cfg,eq).unwrap();
        let mut gpu=PreflopGpu::new(&s,2000).unwrap();
        assert_eq!(gpu.use_eq_cache,1);
        let mut reach=vec![0f32;gpu.d_reach.len()];
        for (block,r) in reach.chunks_exact_mut(NUM_CLASSES).enumerate() {
            for (h,x) in r.iter_mut().enumerate() {*x=if (block+h)%7==0 {0.0} else {((h*13+block*3)%31+1) as f32/4096.0};}
        }
        gpu.d_reach=gpu.stream.clone_htod(&reach).unwrap();
        unsafe {gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
            .launch(LaunchConfig {block_dim:(128,1,1),..PreflopGpu::cfg((reach.len()/NUM_CLASSES) as u32)}).unwrap();}
        // Manual reach replacement bypasses down(), which normally refreshes
        // the HU cache. Populate the all-seat span before comparing dispatches.
        let (start,count)=gpu.eq_spans[s.n];assert!(count>0);
        unsafe {gpu.stream.launch_builder(&gpu.f_equities)
            .arg(&gpu.d_eq_work).arg(&start).arg(&gpu.d_eq_blocks).arg(&gpu.d_eq)
            .arg(&gpu.d_reach).arg(&gpu.d_reach_mass).arg(&mut gpu.d_eq_cache)
            .launch(PreflopGpu::cfg(count)).unwrap();}
        let slots=gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        for p in 0..s.n {
            let mut answers=Vec::new();
            // Only dispatch changes. Cache allocation remains valid and no graph
            // exists; all reaches, masses, terminals and coupled grouping are fixed.
            for enabled in [1,0] {
                gpu.use_eq_cache=enabled;
                gpu.terminals(p as i32).unwrap();
                let values=gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let mut hu=Vec::new();
                for (nd,n) in s.nodes.iter().enumerate().filter(|(_,n)|n.kind==KIND_POT_SHARE && n.live.count_ones()==2) {
                    let _=n;let at=slots[nd] as usize*NUM_CLASSES;
                    hu.extend(values[at..at+NUM_CLASSES].iter().map(|x|x.to_bits()));
                }
                assert!(!hu.is_empty());answers.push(hu);
            }
            assert_eq!(answers[0],answers[1],"HU cache changes terminal bits for seat {p}");
        }
    }

    fn phase_test_equity() -> Arc<crate::preflop::equity::EquityTable> {
        let path = std::env::var("PREFLOP_PHASE_EQ").unwrap_or_else(|_|
            concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin").to_string());
        let bytes = std::fs::read(&path).expect("phase tests require an existing equity cache");
        assert!(bytes.len() >= 4, "invalid equity cache");
        let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
        Arc::new(crate::preflop::equity::EquityTable::load_or_build(&path, samples))
    }

    fn assert_phase_counts(profile: &serde_json::Value, np: usize, batches: usize, average: bool) {
        let count = |phase: &str| -> usize {
            profile["rows"].as_array().unwrap().iter()
                .filter(|r| r["phase"].as_str() == Some(phase))
                .map(|r| r["intervals"].as_u64().unwrap() as usize).sum()
        };
        for phase in ["prepare", "normalize", "ordinary_terminals"] { assert_eq!(count(phase), np, "{phase}"); }
        for phase in ["cdf", "coupled_terminals"] { assert_eq!(count(phase), np*batches, "{phase}"); }
        assert_eq!(count("down"), if average { 1 } else { np });
        assert_eq!(count("up_learn"), if average { 0 } else { np });
        assert_eq!(count("up_average"), if average { np } else { 0 });
        assert_eq!(count("up_br"), if average { np } else { 0 });
        assert_eq!(count("root_copy"), if average { 2*np } else { 0 });
        assert_eq!(count("discount"), if average { 0 } else { 1 });
        let total = profile["gpu_ms"].as_f64().unwrap();
        let sum = profile["interval_sum_ms"].as_f64().unwrap();
        assert!(total.is_finite() && total >= 0.0 && sum.is_finite() && sum >= 0.0);
        // Independent event timestamp differences have finite resolution.
        assert!((total-sum).abs() < 1.0 + total*0.001);
    }

    #[test]
    fn coupled_phase_event_hooks_preserve_solver_bits() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let mut results = Vec::new();
        for profiling in [false, true] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert!(gpu.use_multiway != 0 && gpu.use_mw_normalized);
            let batches = crate::preflop::multiway::SAMPLES.div_ceil(gpu.mw_batch as usize);
            let mut rounds = Vec::new();
            for _ in 0..2 {
                if profiling { gpu.phase_profile_begin().unwrap(); }
                gpu.iterate(&mut s).unwrap();
                if profiling { assert_phase_counts(&gpu.phase_profile_end().unwrap(), s.n, batches, false); }
                if profiling { gpu.phase_profile_begin().unwrap(); }
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                if profiling { assert_phase_counts(&gpu.phase_profile_end().unwrap(), s.n, batches, true); }
                rounds.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x|x.to_bits()).collect::<Vec<_>>()));
            }
            if !profiling { assert!(gpu.eval_graph.is_some()); }
            results.push(rounds);
        }
        assert_eq!(results[0], results[1], "event instrumentation changed numerical outputs");
    }

    /// Supplementary diagnostic only. Does not write/save its input or modify
    /// the frozen benchmark harness. Requires explicit --ignored selection.
    #[test]
    #[ignore = "opt-in eager CUDA phase profiling; requires frozen input and idle GPU"]
    fn profile_coupled_gpu_phases_from_frozen_input() {
        let input = std::env::var("PREFLOP_PHASE_INPUT").expect("set PREFLOP_PHASE_INPUT to a frozen JSON or .gtop file");
        let eq = phase_test_equity();
        let mut s = if input.ends_with(".gtop") {
            PreflopSolver::load_game(&input, eq).unwrap()
        } else {
            let v: serde_json::Value = serde_json::from_slice(&std::fs::read(&input).unwrap()).unwrap();
            let cfg = serde_json::from_value(v.get("config").unwrap_or(&v).clone()).unwrap();
            PreflopSolver::new(cfg, eq).unwrap()
        };
        let number = |name: &str, default: usize| std::env::var(name).map(|x|x.parse::<usize>().expect(name)).unwrap_or(default);
        let budget = number("PREFLOP_PHASE_BUDGET_MB", 23000);
        let warmup = number("PREFLOP_PHASE_WARMUP", 2);
        let repeats = number("PREFLOP_PHASE_REPEATS", 3);
        assert!(repeats > 0 && repeats <= 100 && warmup <= 100);
        let mut gpu = PreflopGpu::new(&s, budget.try_into().unwrap()).unwrap();
        assert_ne!(gpu.use_multiway, 0, "this profile is for coupled multiway");
        println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"metadata","input":input,
            "model":s.multiway_equity_model(),"nodes":s.nodes.len(),"seats":s.n,
            "initial_iteration":s.iteration,"warmup":warmup,"repeats":repeats,"budget_mb":budget,
            "batch":gpu.mw_batch,"normalized":gpu.use_mw_normalized,"compact":gpu.use_mw_compact != 0,
            "cdf_bytes":gpu.d_mw_cdf.len()*4,"normalized_bytes":gpu.d_mw_normalized.len()*4}));
        for _ in 0..warmup { gpu.iterate(&mut s).unwrap(); }
        gpu.gaps_and_evs().unwrap(); // warm evaluation-only kernels too
        for sample in 0..repeats {
            gpu.phase_profile_begin().unwrap();
            let started = std::time::Instant::now();
            gpu.iterate(&mut s).unwrap();
            let wall_ms = started.elapsed().as_secs_f64()*1000.0;
            let phases = gpu.phase_profile_end().unwrap();
            println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"iteration","sample":sample,
                "iteration":s.iteration,"wall_ms":wall_ms,"phases":phases}));
            gpu.phase_profile_begin().unwrap();
            let started = std::time::Instant::now();
            let (gaps,evs) = gpu.gaps_and_evs().unwrap();
            let wall_ms = started.elapsed().as_secs_f64()*1000.0;
            let phases = gpu.phase_profile_end().unwrap();
            println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"average_check","sample":sample,
                "iteration":s.iteration,"wall_ms":wall_ms,"phases":phases,"gaps":gaps,"evs":evs}));
        }
        gpu.sync_to_cpu(&mut s).unwrap();
        let (regret,strategy) = s.arena_snapshot();
        let fingerprint = regret.iter().chain(&strategy).fold(0xcbf29ce484222325u64, |h,x|
            x.to_bits().to_le_bytes().iter().fold(h,|h,b|(h ^ *b as u64).wrapping_mul(0x100000001b3)));
        println!("PREFLOP_PHASE {}", serde_json::json!({"operation":"result","iteration":s.iteration,
            "arena_hash":format!("{fingerprint:016x}"),"execution":"eager_cuda_events"}));
    }

    #[test]
    fn multiway_normalization_budget_preserves_minimum_particle_fit() {
        let slots = 1000usize;
        let particle = slots * (NUM_CLASSES + 1) * 4;
        let normalized = slots * NUM_CLASSES * 4;
        assert_eq!(multiway_batch_plan(particle - 1, slots).unwrap(), None);
        for available in [particle, normalized + particle - 1] {
            let plan = multiway_batch_plan(available, slots).unwrap().unwrap();
            assert_eq!(plan.normalized_bytes, 0);
            assert_eq!(plan.batch, 1);
            assert!(plan.cache_len * 4 <= available);
        }
        let at_boundary = multiway_batch_plan(normalized + particle, slots).unwrap().unwrap();
        assert_eq!(at_boundary.normalized_bytes, normalized);
        assert_eq!(at_boundary.batch, 1);
        assert_eq!(at_boundary.cache_len * 4 + normalized, normalized + particle);
        // Even if direct division could fit two particles, prefer normalization
        // once at least one normalized particle fits; this is not a size tuner.
        let preferred = multiway_batch_plan(2 * particle, slots).unwrap().unwrap();
        assert_eq!(preferred.normalized_bytes, normalized);
        assert_eq!(preferred.batch, 1);
    }

    #[test]
    fn multiway_normalization_budget_caps_batches_and_checks_overflow() {
        let slots = 1000usize;
        let particle = slots * (NUM_CLASSES + 1) * 4;
        let normalized = slots * NUM_CLASSES * 4;
        for (available, expected_batch) in [
            (normalized + 32 * particle - 1, 31),
            (normalized + 32 * particle, 32),
            (normalized + 100 * particle, 32),
        ] {
            let plan = multiway_batch_plan(available, slots).unwrap().unwrap();
            assert_eq!(plan.normalized_bytes, normalized);
            assert_eq!(plan.batch, expected_batch);
            assert_eq!(plan.cache_len, slots * (NUM_CLASSES + 1) * expected_batch);
            assert!(plan.cache_len * 4 + plan.normalized_bytes <= available);
        }
        assert!(multiway_batch_plan(usize::MAX, 0).is_err());
        assert!(multiway_batch_plan(usize::MAX, usize::MAX).is_err());
    }


    #[test]
    #[ignore = "targeted one-particle CUDA boundary/parity test; run explicitly in release"]
    fn coupled_minimum_budget_direct_and_normalized_paths_match() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let mut chosen = None;
        // Search only small/medium CPU-built fixtures; no repeated GPU allocation
        // is used to locate the integer-MB boundary.
        for n in [4usize, 5, 6] {
            let mut posts = vec![0.0; n]; posts[n - 2] = 0.5; posts[n - 1] = 1.0;
            let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(),
                "stack":20.0, "posts":posts, "limp":true, "open_raises":[2.0,3.0],
                "raise_mults":[3.0], "max_raises":2, "add_allin":false,
                "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
            })).unwrap();
            let s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            if s.nodes.len() > 250_000 { continue; }
            let sources = reach_sources(&s);
            let mw = EquityCachePlan::multiway(&s, &sources);
            let compact = MultiwayCompactPlan::build(&mw, s.n).unwrap();
            let slots = compact.capacity;
            if slots < 3000 { continue; } // >2MB normalization interval
            let terms = s.nodes.iter().filter(|nd|
                nd.kind == KIND_POT_SHARE && nd.live.count_ones() >= 3).count();
            let fixed = mw.metadata_bytes() + terms * 8 + mw.blocks.len() * 4 + compact.bytes
                + 3 * crate::preflop::multiway::SAMPLES * NUM_CLASSES * 4;
            let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks) * 1e6 + fixed as f64;
            let particle = slots * (NUM_CLASSES + 1) * 4;
            let normalized = slots * NUM_CLASSES * 4;
            let eq_plan = EquityCachePlan::build(&s, &sources);
            let mut direct = None;
            let first = ((base + particle as f64) / 1e6).ceil() as u64;
            let last = ((base + normalized as f64 + 2.0 * particle as f64) / 1e6).floor() as u64;
            for budget in first..=last {
                let remaining = (budget as f64 * 1e6 - base).max(0.0) as usize;
                let Some(plan) = multiway_batch_plan(remaining, slots).unwrap() else { continue; };
                if plan.batch != 1 { continue; }
                let need = base + (plan.cache_len * 4 + plan.normalized_bytes) as f64;
                let eq_cached = !eq_plan.blocks.is_empty()
                    && need + eq_plan.bytes() as f64 <= budget as f64 * 1e6;
                if plan.normalized_bytes == 0 {
                    direct = Some((budget, eq_cached));
                } else if let Some((direct_budget, direct_eq)) = direct {
                    if eq_cached == direct_eq {
                        chosen = Some((cfg.clone(), direct_budget, budget, slots, s.nodes.len()));
                        break;
                    }
                }
            }
            if chosen.is_some() { break; }
        }
        let (cfg, direct_budget, normalized_budget, slots, nodes) = chosen
            .expect("medium fixture must admit both integer-MB paths with batch1 and identical HU cache mode");
        eprintln!("boundary fixture: {nodes} nodes, {slots} slots, direct {direct_budget}MB, normalized {normalized_budget}MB");
        let mut snapshots = Vec::new();
        let mut terminal_snapshots = Vec::new();
        let mut cache_modes = Vec::new();
        // Sequential construction avoids two simultaneous CUDA engines. Each
        // starts from the same fresh state; neither budget is mocked/overridden.
        for (budget, expect_normalized) in [(direct_budget, false), (normalized_budget, true)] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut gpu = PreflopGpu::new(&s, budget).expect("actual constructor must retain minimum fit");
            assert_eq!(gpu.use_mw_normalized, expect_normalized);
            assert_eq!(gpu.mw_batch, 1);
            assert_eq!(gpu.use_multiway, 1);
            cache_modes.push(gpu.use_eq_cache);
            let mut records = Vec::new();
            // First iteration is eager; later iterations exercise captured
            // learning graphs. Repeated checks exercise evaluation graph replay.
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                let regret_bits: Vec<u32> = gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x| x.to_bits()).collect();
                let strategy_bits: Vec<u32> = gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x| x.to_bits()).collect();
                records.push((regret_bits, strategy_bits,
                    gaps.iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x| x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.learning_graphs.iter().any(|g| g.is_some()));
            assert!(gpu.eval_graph.is_some());
            snapshots.push(records);
            // Drop captured graphs before replacing any of their input buffers.
            for graph in &mut gpu.learning_graphs { *graph = None; }
            gpu.eval_graph = None;
            let target = s.nodes.iter().position(|nd|
                nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
            let live: Vec<usize> = (0..s.n).filter(|&p| s.nodes[target].live & (1 << p) != 0).collect();
            let (p, other) = (live[0], live[1]);
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let value_slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let base = value_slots[target] as usize * NUM_CLASSES;
            gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();
            gpu.mw_nterms = 1;
            let mut terminal_records = Vec::new();
            // Exercise the selected direct kernel's zero writes and transition
            // to ungated evaluation; repeat identically on the normalized path.
            for (phase, gate, zero) in [(0usize, 1i32, false), (1, 1, true), (2, 0, false)] {
                let mut reaches = vec![0f32; gpu.d_reach.len()];
                for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    let scale = [1.0f32 / 32.0, 1.0 / 16.0, 1.0 / 8.0][(block + phase) % 3];
                    let h = (block * 17 + phase * 11) % NUM_CLASSES;
                    r[h] = scale; r[(h + 53) % NUM_CLASSES] = 2.0 * scale;
                    r[(h + 107) % NUM_CLASSES] = 4.0 * scale;
                }
                if zero {
                    let off = sources[target * s.n + other] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].fill(0.0);
                }
                if phase == 2 {
                    assert!(gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap().iter().all(|&x| x == 0));
                }
                gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig { block_dim: (128,1,1),
                            ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap();
                }
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                if expect_normalized {
                    gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                }
                gpu.terminals_masked(p as i32, gate).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let off = sources[target * s.n + q] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(target, p, &local, &mut expected);
                for h in 0..NUM_CLASSES {
                    assert!(actual[base + h].is_finite() && (actual[base + h] - expected[h]).abs() < 2e-5,
                        "budget {budget}, phase {phase}, h {h}: {} vs {}", actual[base + h], expected[h]);
                }
                if zero { assert!(actual[base..base + NUM_CLASSES].iter().all(|&x| x == 0.0)); }
                terminal_records.push(actual[base..base + NUM_CLASSES].iter().map(|x| x.to_bits()).collect::<Vec<_>>());
            }
            terminal_snapshots.push(terminal_records);
        }
        assert_eq!(cache_modes[0], cache_modes[1], "HU cache mode must not confound the comparison");
        for (step, (a, b)) in snapshots[0].iter().zip(&snapshots[1]).enumerate() {
            for (label, x, y) in [("regrets", &a.0, &b.0), ("strategy", &a.1, &b.1)] {
                assert_eq!(x.len(), y.len());
                if let Some(i) = x.iter().zip(y).position(|(u, v)| u != v) {
                    panic!("{label} differs at iteration {}, index {i}: {:08x} vs {:08x}", step + 1, x[i], y[i]);
                }
            }
            assert_eq!(a.2, b.2, "gap bits differ at iteration {}", step + 1);
            assert_eq!(a.3, b.3, "EV bits differ at iteration {}", step + 1);
        }
        assert_eq!(terminal_snapshots[0], terminal_snapshots[1], "direct stale/zero/ungated terminal behavior must match");
    }

    #[test]
    fn compact_slot_map_is_bijective_and_preserves_minimum_fit() {
        let rows = [vec![0u32,2,3,6,7,9], vec![1,2,5,7], vec![0,1,3,8,9]];
        let mut work = Vec::new(); let mut spans = Vec::new();
        for row in &rows { spans.push((work.len() as u32, row.len() as u32)); work.extend(row); }
        spans.push((work.len() as u32, 10)); work.extend(0..10u32);
        let plan = EquityCachePlan { slots: (0..10).collect(), blocks: (0..10).collect(), work, spans };
        let compact = MultiwayCompactPlan::build(&plan, 3).unwrap();
        assert!(compact.enabled);
        assert_eq!(compact.capacity, 6, "trailing union span is not a simultaneous traverser");
        assert_eq!(compact.bytes, 3 * 10 * 4);
        for p in 0..3 {
            for global in 0..10 {
                let expected = rows[p].iter().position(|&x| x == global as u32).map(|x| x as u32).unwrap_or(u32::MAX);
                assert_eq!(compact.map[p * 10 + global], expected);
            }
        }
        let old_minimum = 10 * (NUM_CLASSES + 1) * 4;
        let new_minimum = compact.bytes + compact.capacity * (NUM_CLASSES + 1) * 4;
        assert!(new_minimum < old_minimum);
        assert!(multiway_batch_plan(old_minimum - compact.bytes, compact.capacity).unwrap().is_some());
        let dense = EquityCachePlan {
            slots: (0..10).collect(), blocks: (0..10).collect(),
            work: (0..3).flat_map(|_| 0..10u32).collect(), spans: vec![(0,10),(10,10),(20,10)],
        };
        let fallback = MultiwayCompactPlan::build(&dense, 3).unwrap();
        assert!(!fallback.enabled, "do not spend mapping memory when minimum fit worsens");
        assert_eq!(fallback.capacity, 10); assert_eq!(fallback.bytes, 0);
        assert_eq!(fallback.map.len(), 1);
    }

    #[test]
    fn coupled_compact_and_union_storage_have_identical_outputs() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let mut results = Vec::new();
        let mut metadata = Vec::new();
        for allow_compact in [false, true] {
            let mut s = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let sources = reach_sources(&s);
            let plan = EquityCachePlan::multiway(&s, &sources);
            let mapping = MultiwayCompactPlan::build(&plan, s.n).unwrap();
            assert!(mapping.enabled, "fixture must exercise compact storage");
            // Validate every actual terminal/seat reference against the inverse
            // work-span mapping before involving a CUDA kernel.
            for (nd, node) in s.nodes.iter().enumerate().filter(|(_, n)|
                n.kind == KIND_POT_SHARE && n.live.count_ones() >= 3) {
                for p in 0..s.n {
                    if node.live & (1 << p) == 0 { continue; }
                    for q in 0..s.n {
                        if p == q || node.live & (1 << q) == 0 { continue; }
                        let global = plan.slots[sources[nd * s.n + q] as usize] as usize;
                        let local = mapping.map[p * plan.blocks.len() + global] as usize;
                        let (start, count) = plan.spans[p];
                        assert!(local < count as usize && local < mapping.capacity);
                        assert_eq!(plan.work[start as usize + local] as usize, global);
                    }
                }
            }
            let mut gpu = PreflopGpu::new_with_layout(&s, 2000, allow_compact).unwrap();
            assert_eq!(gpu.use_mw_compact != 0, allow_compact);
            assert_eq!(gpu.mw_batch, 32); assert!(gpu.use_mw_normalized);
            metadata.push((gpu.use_eq_cache, gpu.d_mw_cdf.len(), gpu.d_mw_normalized.len()));
            let mut snapshots = Vec::new();
            for _ in 0..3 {
                gpu.iterate(&mut s).unwrap();
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                snapshots.push((
                    gpu.stream.clone_dtoh(&gpu.d_regrets).unwrap().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    gpu.stream.clone_dtoh(&gpu.d_strat).unwrap().iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    gaps.iter().map(|x| x.to_bits()).collect::<Vec<_>>(),
                    evs.iter().map(|x| x.to_bits()).collect::<Vec<_>>()));
            }
            assert!(gpu.eval_graph.is_some());
            for graph in &mut gpu.learning_graphs { *graph = None; } gpu.eval_graph = None;
            // Alternate differently sized seat spans. Poisoning the same compact
            // capacity catches stale reads beyond the new seat's populated span.
            let mut terminal_values = Vec::new();
            for (p, gate) in [(0usize,1i32),(3,0),(1,1),(0,0)] {
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32, gate).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                assert!(actual.iter().all(|x| x.is_finite()), "compact stale read: p {p}, gate {gate}");
                terminal_values.push(actual.iter().map(|x| x.to_bits()).collect::<Vec<_>>());
            }
            results.push((snapshots, terminal_values));
        }
        assert_eq!(metadata[0].0, metadata[1].0);
        assert!(metadata[1].1 < metadata[0].1 && metadata[1].2 < metadata[0].2);
        for (step, (a,b)) in results[0].0.iter().zip(&results[1].0).enumerate() {
            for (label,x,y) in [("regret",&a.0,&b.0),("strategy",&a.1,&b.1)] {
                assert_eq!(x.len(),y.len());
                if let Some(i)=x.iter().zip(y).position(|(u,v)|u!=v) {
                    panic!("{label} differs at iteration {}, index {i}: {:08x} vs {:08x}",step+1,x[i],y[i]);
                }
            }
            assert_eq!(a.2,b.2,"gap bits differ at step {step}");
            assert_eq!(a.3,b.3,"EV bits differ at step {step}");
        }
        for (state,(a,b)) in results[0].1.iter().zip(&results[1].1).enumerate() {
            assert_eq!(a.len(),b.len());
            if let Some(i)=a.iter().zip(b).position(|(u,v)|u!=v) {
                panic!("terminal storage differs at state {state}, index {i}: {:08x} vs {:08x}",a[i],b[i]);
            }
        }
    }


    #[test]
    fn coupled_terminal_matches_cpu_across_particle_batches() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"], "stack":5.0, "posts":[0.0,0.5,1.0],
            "limp":true, "open_raises":[2.0], "raise_mults":[3.0], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        // Exercise every exact opponent-count specialization O=2..8.
        for n in 3usize..=9 {
            let mut cfg = cfg.clone();
            if n != 3 {
                cfg.positions = (0..n).map(|p| format!("P{p}")).collect();
                cfg.positions[n-2] = "SB".into(); cfg.positions[n-1] = "BB".into();
                cfg.posts = vec![0.0; n]; cfg.posts[n-2] = 0.5; cfg.posts[n-1] = 1.0;
                cfg.open_raises.clear(); cfg.stack = 2.0;
            }
            let s = PreflopSolver::new(cfg, eq.clone()).unwrap();
            assert_eq!(s.multiway_equity_model(), "coupled_deck_v1");
            let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
            assert_eq!(gpu.use_multiway, 1);
            let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
            let slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
            let target = s.nodes.iter().position(|n| n.kind == KIND_POT_SHARE && n.live.count_ones() as usize == s.n).unwrap();
            gpu.down(1, 0).unwrap();
            let mut reaches = gpu.stream.clone_dtoh(&gpu.d_reach).unwrap();
            // Unit counterfactual mass keeps a strict absolute tolerance meaningful
            // even at the nine-seat terminal after many preceding calls.
            for r in reaches.chunks_exact_mut(NUM_CLASSES) {
                let mass: f32 = r.iter().sum(); if mass > 0.0 { for x in r { *x /= mass; } }
            }
            gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
            unsafe { gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                .launch(LaunchConfig { block_dim: (128,1,1), ..PreflopGpu::cfg((reaches.len()/NUM_CLASSES) as u32) }).unwrap(); }
            let local: Vec<Vec<f32>> = (0..s.n).map(|p| {
                let base = sources[target * s.n + p] as usize * NUM_CLASSES;
                reaches[base..base + NUM_CLASSES].to_vec()
            }).collect();
            // Seven exercises a partial final batch; one verifies bounded scratch
            // never silently switches to the old equity formula.
            for batch in [32u32, 7, 1] {
                gpu.mw_batch = batch;
                let mut terminal_bits = Vec::<Vec<u32>>::new();
                for p in 0..s.n {
                    gpu.terminals(p as i32).unwrap();
                    let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                    let mut expected = vec![0.; NUM_CLASSES];
                    s.terminal_value(target, p, &local, &mut expected);
                    let base = slots[target] as usize * NUM_CLASSES;
                    for h in 0..NUM_CLASSES {
                        assert!((actual[base + h] - expected[h]).abs() < 2e-5,
                            "n {n}, batch {batch}, p {p}, h {h}: {} vs {}", actual[base + h], expected[h]);
                    }
                    terminal_bits.push(actual[base..base + NUM_CLASSES].iter().map(|x| x.to_bits()).collect());
                }
                // Optional exact GPU-control evidence: run this same test patch
                // before/after kernel specialization and compare every f32 bit.
                // Different batch sizes may legitimately round differently, so
                // compare control/candidate only at the same (n, batch).
                if std::env::var("PREFLOP_MW_TERMINAL_BITS").as_deref() == Ok("1") {
                    println!("PREFLOP_MW_TERMINAL_BITS {}", serde_json::json!({
                        "seats": n, "opponents": n-1, "batch": batch,
                        "model": s.multiway_equity_model(), "bits_by_seat": terminal_bits,
                    }));
                }
            }
        }
    }

    #[test]
    fn coupled_active_slots_preserve_counterfactual_zero_reach_and_reset_masks() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"], "stack":2.0,
            "posts":[0.0,0.0,0.5,1.0], "limp":true, "open_raises":[],
            "raise_mults":[], "max_raises":1, "add_allin":false,
            "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let s = PreflopSolver::new(cfg, eq).unwrap();
        let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
        assert_eq!(gpu.use_multiway, 1);
        // Three live seats plus a folded opponent distinguishes pot eligibility
        // from the counterfactual reach product, which includes the folded seat.
        let target = s.nodes.iter().position(|nd|
            nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
        let live: Vec<usize> = (0..s.n).filter(|&q| s.nodes[target].live & (1 << q) != 0).collect();
        let folded = (0..s.n).find(|&q| s.nodes[target].live & (1 << q) == 0).unwrap();
        let (p, other) = (live[0], live[1]);
        let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
        let value_slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        let cdf_slots = gpu.stream.clone_dtoh(&gpu.d_mw_slots).unwrap();
        let source = |q: usize| sources[target * s.n + q] as usize;
        assert_eq!((0..s.n).map(|q| source(q)).collect::<std::collections::HashSet<_>>().len(), s.n);
        // Isolate one multiway terminal, so every expected active slot is known.
        // Retain the production slot mapping and ordinary terminal kernel.
        gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();
        gpu.mw_nterms = 1;
        let mut baseline = vec![0f32; gpu.d_reach.len()];
        for (block, r) in baseline.chunks_exact_mut(NUM_CLASSES).enumerate() {
            // Dyadic probabilities give exact unit reach mass with asymmetric
            // ranges, avoiding reduction tolerance masking a reach-product bug.
            r[(block * 17) % NUM_CLASSES] = 0.5;
            r[(block * 17 + 53) % NUM_CLASSES] = 0.25;
            r[(block * 17 + 107) % NUM_CLASSES] = 0.25;
        }
        let base = value_slots[target] as usize * NUM_CLASSES;
        for batch in [32u32, 7, 1] {
            gpu.mw_batch = batch;
            // The middle calls change traverser without replacing/reinitializing
            // active/probability scratch. This exercises stale flags both ways.
            let cases = [
                ("positive", p, None),
                ("zero own reach", p, Some(p)),
                ("zero live opponent after changing traverser", other, Some(p)),
                ("positive after zero", p, None),
                ("zero live opponent", p, Some(other)),
                ("positive different traverser", other, None),
                ("zero folded opponent", p, Some(folded)),
                ("positive after folded zero", p, None),
            ];
            for (label, traverser, zero_seat) in cases {
                let mut reaches = baseline.clone();
                if let Some(q) = zero_seat {
                    let off = source(q) * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].fill(0.0);
                }
                gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_reach_mass)
                        .arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig { block_dim: (128,1,1),
                            ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap();
                }
                // Missing first-batch zero writes and reads of ungathered CDFs
                // must fail conspicuously instead of inheriting plausible data.
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                gpu.terminals(traverser as i32).unwrap();
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let off = source(q) * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(target, traverser, &local, &mut expected);
                let zero_opponent = zero_seat.is_some_and(|q| q != traverser);
                if zero_opponent {
                    assert!(actual[base..base + NUM_CLASSES].iter().all(|&v| v == 0.0), "{label}, batch {batch}");
                } else {
                    assert!(expected.iter().any(|v| v.abs() > 1e-4), "nontrivial fixture required");
                }
                for h in 0..NUM_CLASSES {
                    assert!(actual[base + h].is_finite() && (actual[base + h] - expected[h]).abs() < 2e-5,
                        "{label}, batch {batch}, h {h}: {} vs {}", actual[base + h], expected[h]);
                }
                let active = gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap();
                let prob = gpu.stream.clone_dtoh(&gpu.d_mw_prob).unwrap();
                assert_eq!(prob[0], if zero_opponent { 0.0 } else { 1.0 }, "{label}");
                let mut expected_active = vec![0u32; active.len()];
                if !zero_opponent {
                    for &q in &live {
                        if q != traverser { expected_active[cdf_slots[source(q)] as usize] = 1; }
                    }
                }
                assert_eq!(active, expected_active, "stale or missing slot mark: {label}, batch {batch}");
            }
        }
    }

    #[test]
    fn coupled_normalized_reach_refreshes_nonunit_inputs_and_ungated_evaluation() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"], "stack":2.0, "posts":[0.0,0.5,1.0],
            "limp":true, "open_raises":[], "raise_mults":[], "max_raises":1,
            "add_allin":false, "rake_pct":5.0, "rake_cap":1.0, "realization":"raw"
        })).unwrap();
        let s = PreflopSolver::new(cfg, eq).unwrap();
        let mut gpu = PreflopGpu::new(&s, 2000).unwrap();
        let target = s.nodes.iter().position(|nd|
            nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 3).unwrap();
        let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
        let value_slots = gpu.stream.clone_dtoh(&gpu.d_val_slot).unwrap();
        let slot_blocks = gpu.stream.clone_dtoh(&gpu.d_mw_blocks).unwrap();
        let work = gpu.stream.clone_dtoh(&gpu.d_mw_work).unwrap();
        gpu.d_mw_terms = gpu.stream.clone_htod(&[target as u32]).unwrap();
        gpu.mw_nterms = 1;
        let (p, other) = (0usize, 1usize);
        let base = value_slots[target] as usize * NUM_CLASSES;
        for batch in [32u32, 7, 1] {
            gpu.mw_batch = batch;
            // Each phase changes both total mass and hand composition. Thus a
            // cached normalized distribution cannot pass merely by rescaling.
            for (phase, gate, zero_opponent, poison) in [
                (0usize, 1i32, false, true),
                (1, 1, true, false),
                (2, 0, false, true), // empty stale active mask must be ignored
                (3, 0, false, false), // old finite normalized values must refresh
                (4, 1, false, true),
                (5, 0, true, false),
                (6, 0, false, true),
            ] {
                let mut reaches = vec![0f32; gpu.d_reach.len()];
                for (block, r) in reaches.chunks_exact_mut(NUM_CLASSES).enumerate() {
                    // Unit weights[1,2,4] divided by32/16/8 give non-unit exact
                    // dyadic masses and nontrivial f32 division by seven.
                    let scale = [1.0f32 / 32.0, 1.0 / 16.0, 1.0 / 8.0][(block + phase) % 3];
                    let h = (block * 17 + phase * 11) % NUM_CLASSES;
                    r[h] = scale;
                    r[(h + 53) % NUM_CLASSES] = 2.0 * scale;
                    r[(h + 107) % NUM_CLASSES] = 4.0 * scale;
                }
                if zero_opponent {
                    let off = sources[target * s.n + other] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].fill(0.0);
                }
                if phase == 2 {
                    assert!(gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap().iter().all(|&x| x == 0),
                        "preceding gated zero case must leave an empty mask");
                }
                gpu.d_reach = gpu.stream.clone_htod(&reaches).unwrap();
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_reach_mass)
                        .arg(&gpu.d_reach).arg(&mut gpu.d_reach_mass)
                        .launch(LaunchConfig { block_dim: (128,1,1),
                            ..PreflopGpu::cfg((reaches.len() / NUM_CLASSES) as u32) }).unwrap();
                }
                if poison {
                    gpu.d_mw_normalized = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_normalized.len()]).unwrap();
                }
                gpu.d_mw_cdf = gpu.stream.clone_htod(&vec![f32::NAN; gpu.d_mw_cdf.len()]).unwrap();
                gpu.d_val = gpu.stream.clone_htod(&vec![123456.0f32; gpu.d_val.len()]).unwrap();
                gpu.terminals_masked(p as i32, gate).unwrap();
                let mass = gpu.stream.clone_dtoh(&gpu.d_reach_mass).unwrap();
                let active = gpu.stream.clone_dtoh(&gpu.d_mw_active).unwrap();
                let normalized = gpu.stream.clone_dtoh(&gpu.d_mw_normalized).unwrap();
                let compact_slots = gpu.stream.clone_dtoh(&gpu.d_mw_compact).unwrap();
                let (start, count) = gpu.mw_spans[p];
                let mut checked = 0;
                for &slot in &work[start as usize..(start + count) as usize] {
                    let slot = slot as usize;
                    let block = slot_blocks[slot] as usize;
                    if (gate != 0 && active[slot] == 0) || mass[block] <= 0.0 { continue; }
                    assert_ne!(mass[block], 1.0, "non-unit mass fixture required");
                    for h in 0..NUM_CLASSES {
                        let expected = reaches[block * NUM_CLASSES + h] / mass[block];
                        let storage_slot = if gpu.use_mw_compact != 0 { compact_slots[p * gpu.mw_union_slots as usize + slot] as usize } else { slot };
                        assert_eq!(normalized[storage_slot * NUM_CLASSES + h].to_bits(), expected.to_bits(),
                            "phase {phase}, gate {gate}, batch {batch}, slot {slot}, h {h}");
                    }
                    checked += 1;
                }
                if !zero_opponent { assert!(checked > 0); }
                let local: Vec<Vec<f32>> = (0..s.n).map(|q| {
                    let off = sources[target * s.n + q] as usize * NUM_CLASSES;
                    reaches[off..off + NUM_CLASSES].to_vec()
                }).collect();
                let mut expected = vec![0f32; NUM_CLASSES];
                s.terminal_value(target, p, &local, &mut expected);
                let actual = gpu.stream.clone_dtoh(&gpu.d_val).unwrap();
                for h in 0..NUM_CLASSES {
                    assert!(actual[base + h].is_finite() && (actual[base + h] - expected[h]).abs() < 2e-5,
                        "phase {phase}, gate {gate}, batch {batch}, h {h}: {} vs {}", actual[base + h], expected[h]);
                }
                if zero_opponent {
                    assert!(actual[base..base + NUM_CLASSES].iter().all(|&x| x == 0.0));
                }
            }
        }
    }


    fn legacy_solver(cfg: PreflopConfig, eq: Arc<crate::preflop::equity::EquityTable>) -> Result<PreflopSolver, String> {
        let mut s = PreflopSolver::new(cfg, eq)?;
        s.set_multiway_equity_model("legacy_product")?;
        Ok(s)
    }
    #[test]
    fn reach_mass_preserves_original_addition_tree() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["SB","BB"], "stack":10.0, "posts":[0.5,1.0],
            "open_raises":[2.5], "raise_mults":[3.0], "max_raises":1,
            "realization":"static"
        })).unwrap();
        let s = legacy_solver(cfg, eq).unwrap();
        let gpu = PreflopGpu::new(&s, 2000).unwrap();
        let mut inputs = vec![0f32; 16 * NUM_CLASSES];
        let patterns = [0u32, 0x80000000, 1, 0x80000001, 0x3dcccccd,
            0xbdcccccd, 0x358637bd, 0x49742400, 0xc9742400];
        for (i, v) in inputs.iter_mut().enumerate() {
            *v = f32::from_bits(patterns[(i * 17 + i / NUM_CLASSES) % patterns.len()]);
        }
        inputs[..NUM_CLASSES].fill(0.0);
        inputs[NUM_CLASSES..2 * NUM_CLASSES].fill(-0.0);
        inputs[2 * NUM_CLASSES..3 * NUM_CLASSES].fill(f32::from_bits(1));
        inputs[3 * NUM_CLASSES..4 * NUM_CLASSES].fill(f32::from_bits(0x80000001));
        let mut expected = Vec::new();
        for values in inputs.chunks_exact(NUM_CLASSES) {
            let mut sums = [0f32; 256];
            for (dst, value) in sums.iter_mut().zip(values) { *dst += value; }
            for step in [128, 64, 32, 16, 8, 4, 2, 1] {
                for h in 0..step { sums[h] += sums[h + step]; }
            }
            expected.push(sums[0].to_bits());
        }
        let input = gpu.stream.clone_htod(&inputs).unwrap();
        let mut output = gpu.stream.alloc_zeros::<f32>(16).unwrap();
        unsafe {
            gpu.stream.launch_builder(&gpu.f_reach_mass).arg(&input).arg(&mut output)
                .launch(LaunchConfig { block_dim: (128, 1, 1), ..PreflopGpu::cfg(16) }).unwrap();
        }
        let actual = gpu.stream.clone_dtoh(&output).unwrap();
        assert_eq!(actual.into_iter().map(f32::to_bits).collect::<Vec<_>>(), expected);
    }

    #[test]
    fn compact_reach_has_unique_writers_and_fits_smaller_budget() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["UTG","HJ","CO","BTN","SB","BB"], "stack":100.0,
            "posts":[0.0,0.0,0.0,0.0,0.5,1.0], "limp":true,
            "open_raises":[2.5,4.0], "raise_mults":[3.0], "max_raises":3,
            "allin_threshold":0.85, "add_allin":false, "rake_pct":5.0,
            "rake_cap":3.0, "realization":"static"
        })).unwrap();
        let mut s = legacy_solver(cfg, eq).unwrap();
        let values = ValuePlan::build(&s);
        assert_eq!(values.slots[0], 0);
        assert!(values.blocks < s.nodes.len());
        assert!(values.slots.iter().all(|&slot| (slot as usize) < values.blocks));
        let terminal: std::collections::HashSet<_> = s.nodes.iter().enumerate()
            .filter(|(_, n)| n.kind != KIND_ACTION).map(|(i, _)| values.slots[i]).collect();
        assert_eq!(terminal.len(), s.nodes.iter().filter(|n| n.kind != KIND_ACTION).count());
        let mut previous = std::collections::HashSet::new();
        let mut used = terminal.clone();
        for &(start, count) in &values.spans {
            let nodes = &values.action_nodes[start as usize..(start + count) as usize];
            let writes: std::collections::HashSet<_> = nodes.iter().map(|&n| values.slots[n as usize]).collect();
            assert_eq!(writes.len(), count as usize);
            assert!(writes.is_disjoint(&terminal));
            assert!(writes.is_disjoint(&previous));
            for &n in nodes {
                for a in 0..s.nodes[n as usize].actions.len() {
                    assert!(!writes.contains(&values.slots[s.child(n as usize, a)]));
                }
            }
            used.extend(writes.iter().copied());
            previous = writes;
        }
        assert_eq!(used.len(), values.blocks);
        // This workload required about 1.2 GB before reach sharing.
        let mut gpu = PreflopGpu::new(&s, 700).expect("compact reach should fit 700 MB");
        let sources = gpu.stream.clone_dtoh(&gpu.d_reach_src).unwrap();
        let blocks = gpu.d_reach.len() / NUM_CLASSES;
        assert!(sources.iter().all(|&source| (source as usize) < blocks));
        let mut written = std::collections::HashSet::new();
        for q in 0..s.n { assert!(written.insert(sources[q])); }
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let actor = node.actor as usize;
            for a in 0..node.actions.len() {
                let c = s.child(i, a);
                for q in 0..s.n {
                    let parent = sources[i * s.n + q];
                    let child = sources[c * s.n + q];
                    if q == actor {
                        assert_ne!(parent, child);
                        assert!(written.insert(child), "two action edges must not share a writable block");
                    } else {
                        assert_eq!(parent, child, "unchanged reach must retain its source");
                    }
                }
            }
        }
        assert_eq!(written.len(), blocks, "every allocated reach block has exactly one writer");
        gpu.iterate(&mut s).unwrap();
        gpu.sync_to_cpu(&mut s).unwrap();
    }

    #[test]
    fn captured_learning_matches_eager_and_preserves_stop() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["SB","BB"], "stack":25.0, "posts":[0.5,1.0],
            "limp":true, "open_raises":[2.0,2.5], "raise_mults":[3.0],
            "max_raises":3, "add_allin":true, "realization":"static"
        })).unwrap();
        let mut a = legacy_solver(cfg.clone(), eq.clone()).unwrap();
        let mut b = legacy_solver(cfg, eq).unwrap();
        a.iteration = 37;
        b.iteration = 37;
        let mut graph = PreflopGpu::new(&a, 2000).unwrap();
        let mut eager = PreflopGpu::new(&b, 2000).unwrap();
        // Compare graph + cached equities to eager + direct equities.
        eager.use_eq_cache = 0;
        for _ in 0..15 {
            graph.iterate(&mut a).unwrap();
            eager.warmed = false;
            eager.iterate(&mut b).unwrap();
        }
        assert!(graph.learning_graphs.iter().all(Option::is_some));
        graph.sync_to_cpu(&mut a).unwrap();
        eager.sync_to_cpu(&mut b).unwrap();
        assert_eq!(a.arena_snapshot(), b.arena_snapshot());
        assert_eq!(graph.gaps_and_evs().unwrap(), eager.gaps_and_evs().unwrap());
        let stop = AtomicBool::new(true);
        assert!(!graph.try_iterate(&mut a, Some(&stop)).unwrap());
        graph.sync_to_cpu(&mut a).unwrap();
        assert_eq!(a.iteration, b.iteration);
        assert_eq!(a.arena_snapshot(), b.arena_snapshot());
        stop.store(false, Ordering::Relaxed);
        assert!(graph.try_iterate(&mut a, Some(&stop)).unwrap());
        eager.iterate(&mut b).unwrap();
        graph.sync_to_cpu(&mut a).unwrap();
        eager.sync_to_cpu(&mut b).unwrap();
        assert_eq!(a.arena_snapshot(), b.arena_snapshot());
    }

    #[test]
    fn detached_iterations_preserve_exact_trajectory_stale_host_stop_and_resume() {
        let eq = phase_test_equity();
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        for model in [super::super::multiway::MODEL] {
            let mut reference = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            let mut host = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
            reference.set_multiway_equity_model(model).unwrap();
            host.set_multiway_equity_model(model).unwrap();
            reference.iteration = 17;
            host.iteration = 17;
            let mut old = PreflopGpu::new(&reference, 2000).unwrap();
            let mut detached = PreflopGpu::new(&host, 2000).unwrap();
            let frozen_host = host.arena_snapshot();
            let mut counter = 17;
            let stop = AtomicBool::new(false);
            for pass in 0..4 {
                // Host metadata may intentionally be an older published clock;
                // poison it here to detect any accidental shared-solver read.
                host.iteration = 10_000 + pass;
                assert!(detached.try_iterate_counter(&mut counter, Some(&stop)).unwrap());
                old.iterate(&mut reference).unwrap();
                assert_eq!(counter, reference.iteration);
                assert_eq!(host.iteration, 10_000 + pass);
                assert_eq!(host.arena_snapshot(), frozen_host);
                assert_eq!(detached.gaps_and_evs().unwrap(), old.gaps_and_evs().unwrap());
                if pass == 1 {
                    let before = detached.stream.clone_dtoh(&detached.d_regrets).unwrap();
                    let before_sums = detached.stream.clone_dtoh(&detached.d_strat).unwrap();
                    let prior_counter = counter;
                    stop.store(true, Ordering::Relaxed);
                    assert!(!detached.try_iterate_counter(&mut counter, Some(&stop)).unwrap());
                    assert_eq!(counter, prior_counter);
                    assert_eq!(detached.stream.clone_dtoh(&detached.d_regrets).unwrap(), before);
                    assert_eq!(detached.stream.clone_dtoh(&detached.d_strat).unwrap(), before_sums);
                    stop.store(false, Ordering::Relaxed);
                }
            }
            detached.sync_to_cpu(&mut host).unwrap();
            host.iteration = counter; // Same successful-publication commit as server.
            old.sync_to_cpu(&mut reference).unwrap();
            assert_eq!(host.arena_snapshot(), reference.arena_snapshot());
            assert_eq!(host.iteration, reference.iteration);
            drop(detached);
            let mut resumed = PreflopGpu::new(&host, 2000).unwrap();
            assert!(resumed.try_iterate_counter(&mut counter, None).unwrap());
            old.iterate(&mut reference).unwrap();
            resumed.sync_to_cpu(&mut host).unwrap();
            host.iteration = counter;
            old.sync_to_cpu(&mut reference).unwrap();
            assert_eq!(host.arena_snapshot(), reference.arena_snapshot());
            assert_eq!(host.iteration, reference.iteration);
            assert_eq!(resumed.gaps_and_evs().unwrap(), old.gaps_and_evs().unwrap());
        }
    }

    fn assert_cached_evaluation(s: &mut PreflopSolver) {
        let mut gpu = PreflopGpu::new(s, 2000).expect("test requires CUDA");
        for _ in 0..5 {
            gpu.iterate(s).unwrap();
        }
        gpu.sync_to_cpu(s).unwrap();
        let before = s.arena_snapshot();
        let iteration = s.iteration;

        // Original algorithm: a complete independent traversal for every
        // seat and every mode. Compare exact bits, not a convergence margin.
        let cached = gpu.use_eq_cache;
        gpu.use_eq_cache = 0;
        let mut expected_gaps = Vec::new();
        let mut expected_evs = Vec::new();
        for p in 0..gpu.np {
            gpu.sweep(p, if gpu.constrained_br[p as usize] { 3 } else { 2 }).unwrap();
            let br = gpu.root_ev().unwrap();
            gpu.sweep(p, 1).unwrap();
            let avg = gpu.root_ev().unwrap();
            expected_gaps.push((br - avg).to_bits());
            expected_evs.push(avg.to_bits());
        }
        gpu.use_eq_cache = cached;
        for _ in 0..2 {
            let (gaps, evs) = gpu.gaps_and_evs().unwrap();
            assert!(gaps.iter().chain(&evs).all(|v| v.is_finite()));
            assert_eq!(gaps.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), expected_gaps);
            assert_eq!(evs.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), expected_evs);
        }
        gpu.sync_to_cpu(s).unwrap();
        assert_eq!(iteration, s.iteration);
        assert_eq!(before, s.arena_snapshot(), "evaluation must not change learning state");
    }

    #[test]
    fn cached_evaluation_matches_full_sweeps_exactly() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(path, 20000));
        for n in [2, 3] {
            for realization in ["raw", "static", "calibrated"] {
                let mut posts = vec![0.0; n];
                posts[n - 2] = 0.5;
                posts[n - 1] = 1.0;
                let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                    "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(),
                    "stack": 12.0, "posts": posts, "limp": true,
                    "open_raises": [2.0, 3.0], "raise_mults": [2.5],
                    "max_raises": 2, "add_allin": true, "rake_pct": 5.0,
                    "rake_cap": 1.0, "realization": realization,
                })).unwrap();
                let mut s = legacy_solver(cfg, eq.clone()).unwrap();
                if realization == "calibrated" {
                    assert!(s.fit.is_some(), "test requires the calibrated fit");
                }
                assert_cached_evaluation(&mut s);

                s.lock_point(&[], None).unwrap();
                let mut buckets = vec![None; NUM_BUCKETS];
                buckets[super::super::BUCKET_VS_RAISE as usize] = Some(BucketPolicy { raise_multiples: Vec::new(), raise_sizes: Vec::new(),
                    call: vec![0.5; NUM_CLASSES], raise: vec![0.1; NUM_CLASSES],
                    jam: vec![0.0; NUM_CLASSES], raise_size: "max".into(),
                });
                let mut profiles = vec![None; n];
                profiles[1] = Some(SeatProfile {
                    name: "test profile".into(), buckets, vs_raise_bands: None,
                    postflop: None, limp_defense: None, response: None,
                });
                s.set_table(vec![false; n], profiles).unwrap();
                assert_cached_evaluation(&mut s);

                let mut adaptive = s.seat_profiles.clone();
                adaptive[1].as_mut().unwrap().response = Some(super::super::ProfileResponse {
                    adaptive_from: Some(0.25), ..Default::default()
                });
                s.set_table(vec![false; n], adaptive).unwrap();
                assert_cached_evaluation(&mut s);
                let mut fixed = s.seat_profiles.clone();
                fixed[1].as_mut().unwrap().response = None;
                s.set_table(vec![false; n], fixed).unwrap();
                s.iterate();

                // Includes the bleed measurement of seats frozen by hero
                // mode, not just the seats whose strategies are learning.
                s.set_hero(Some(0)).unwrap();
                assert_cached_evaluation(&mut s);
            }
        }
    }
}

// Append to gpu.rs after applying the proposal. Host-only tests; no CUDA calls.
#[cfg(test)]
mod forced_budget_tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

    fn fixture() -> PreflopSolver {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let cache = std::fs::read(path).expect("existing cache required");
        assert_eq!(cache.len(), 4 + NUM_CLASSES * NUM_CLASSES * 4);
        let samples = u32::from_le_bytes(cache[..4].try_into().unwrap());
        let eq = Arc::new(crate::preflop::equity::EquityTable::load_or_build(
            path, samples,
        ));
        let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
            "positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":6,
            "limp":true,"open_raises":[2],"raise_mults":[2],"max_raises":2,
            "add_allin":true,"realization":"raw"
        }))
        .unwrap();
        PreflopSolver::new(cfg, eq).unwrap()
    }
    fn policy() -> BucketPolicy {
        serde_json::from_value(serde_json::json!({
            "call":vec![0.3;NUM_CLASSES],"raise":vec![0.4;NUM_CLASSES],
            "jam":vec![0.1;NUM_CLASSES],"raise_size":"max"
        }))
        .unwrap()
    }
    fn profile() -> SeatProfile {
        SeatProfile {
            name: "budget fixture".into(),
            buckets: vec![Some(policy()); NUM_BUCKETS],
            vs_raise_bands: None,
            limp_defense: None,
            postflop: None,
            response: None,
        }
    }

    #[test]
    fn forced_count_respects_profiles_frozen_hero_and_point_lock_precedence() {
        let mut s = fixture();
        let empty_estimate = vram_estimate_mb(&s);
        assert_eq!(forced_policy_elements(&s).unwrap(), 0);
        assert_eq!(forced_storage_bytes(0).unwrap(), 4); // CUDA placeholder
        s.seat_frozen[0] = true;
        assert_eq!(forced_policy_elements(&s).unwrap(), 0); // sums, not forced buffer
        s.seat_profiles[0] = Some(profile());
        let expected: usize = s
            .nodes
            .iter()
            .filter(|n| n.kind == KIND_ACTION && n.actor == 0)
            .map(|n| n.actions.len() * NUM_CLASSES)
            .sum();
        assert!(expected > 0);
        assert_eq!(forced_policy_elements(&s).unwrap(), expected); // profile wins over frozen
        assert!(
            (vram_estimate_mb(&s) - empty_estimate - (expected * 4 - 4) as f64 / 1e6).abs() < 1e-9
        );
        s.hero = Some(0); // direct state suffices for read-only route/count inspection
        assert_eq!(forced_policy_elements(&s).unwrap(), 0); // hero exempt from own profile
        s.lock_point(&[], Some(policy())).unwrap();
        let root_elements = s.nodes[0].actions.len() * NUM_CLASSES;
        assert_eq!(forced_policy_elements(&s).unwrap(), root_elements); // point lock beats hero
        s.hero = None;
        assert_eq!(forced_policy_elements(&s).unwrap(), expected); // root isn't double counted
    }

    #[test]
    fn adaptive_nodes_are_not_charged_as_fixed_policies() {
        let mut s = fixture();
        let mut p = profile();
        p.response =
            Some(serde_json::from_value(serde_json::json!({"adaptive_from":0.25})).unwrap());
        s.seat_profiles[0] = Some(p);
        let expected: usize = s
            .nodes
            .iter()
            .enumerate()
            .filter(|(_, n)| n.kind == KIND_ACTION && n.actor == 0)
            .filter(|(i, n)| {
                n.bucket < crate::preflop::BUCKET_VS_RAISE
                    || s.faced_to(*i) + 1e-9 < s.cfg.stack * 0.25
            })
            .map(|(_, n)| n.actions.len() * NUM_CLASSES)
            .sum();
        let all: usize = s
            .nodes
            .iter()
            .filter(|n| n.kind == KIND_ACTION && n.actor == 0)
            .map(|n| n.actions.len() * NUM_CLASSES)
            .sum();
        assert!(expected > 0 && expected < all);
        assert_eq!(forced_policy_elements(&s).unwrap(), expected);
    }

    #[test]
    fn forced_reservation_rejects_over_budget_legacy_and_overflow() {
        assert_eq!(reserve_forced_vram_mb(100.0, 250_000, 101).unwrap(), 101.0);
        assert!(reserve_forced_vram_mb(100.0, 250_001, 101).is_err());
        assert!(reserve_forced_vram_mb(100.0, 0, 100).is_err());
        assert!(forced_storage_bytes(usize::MAX).is_err());
        assert!(reserve_forced_vram_mb(f64::INFINITY, 1, u64::MAX).is_err());
    }

    #[test]
    fn forced_reservation_changes_batch_and_preserves_minimum_fit_fallback() {
        let slots = 1000;
        let particle = slots * (NUM_CLASSES + 1) * 4;
        let normalized = slots * NUM_CLASSES * 4;
        let available = normalized + 2 * particle;
        assert_eq!(
            multiway_batch_plan(available, slots)
                .unwrap()
                .unwrap()
                .batch,
            2
        );
        let forced = forced_storage_bytes(particle / 4).unwrap();
        let reduced = multiway_batch_plan(available - forced, slots)
            .unwrap()
            .unwrap();
        assert_eq!(reduced.batch, 1);
        assert_eq!(reduced.normalized_bytes, normalized);
        let direct = multiway_batch_plan(
            particle + normalized - forced_storage_bytes(1).unwrap(),
            slots,
        )
        .unwrap()
        .unwrap();
        assert_eq!(direct.batch, 1);
        assert_eq!(direct.normalized_bytes, 0);
        assert!(
            multiway_batch_plan(particle - forced_storage_bytes(1).unwrap(), slots)
                .unwrap()
                .is_none()
        );
    }
}

// Append to gpu.rs. Real CUDA test; run only in the parent's exclusive GPU slot.
#[cfg(test)]
mod forced_budget_cuda_tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

    fn cached_equity() -> Arc<crate::preflop::equity::EquityTable> {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../cache/preflop_eq169.bin");
        let bytes = std::fs::read(path).expect("existing equity cache required");
        assert_eq!(bytes.len(), 4 + NUM_CLASSES * NUM_CLASSES * 4);
        let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
        Arc::new(crate::preflop::equity::EquityTable::load_or_build(
            path, samples,
        ))
    }

    fn modeled(
        cfg: PreflopConfig,
        eq: Arc<crate::preflop::equity::EquityTable>,
        model: &str,
    ) -> PreflopSolver {
        let mut s = PreflopSolver::new(cfg, eq).unwrap();
        s.set_multiway_equity_model(model).unwrap();
        let policy: BucketPolicy = serde_json::from_value(serde_json::json!({
            "call":vec![0.3;NUM_CLASSES],"raise":vec![0.4;NUM_CLASSES],
            "jam":vec![0.1;NUM_CLASSES],"raise_size":"max"
        }))
        .unwrap();
        let profiles = s
            .cfg
            .positions
            .iter()
            .map(|position| {
                (position != "BTN").then(|| SeatProfile {
                    name: "GPU budget test".into(),
                    buckets: vec![Some(policy.clone()); NUM_BUCKETS],
                    vs_raise_bands: None,
                    limp_defense: None,
                    postflop: None,
                    response: None,
                })
            })
            .collect();
        s.set_table(vec![false; s.n], profiles).unwrap();
        s
    }

    // Find a tiny real tree whose forced payload crosses an integer-MB boundary.
    // Constructor budgets are whole MB; do not mock or perturb the byte planner.
    fn boundary_fixture(eq: Arc<crate::preflop::equity::EquityTable>) -> (PreflopConfig, u64) {
        for opens in [vec![2.0], vec![2.0, 3.0], vec![2.0, 3.0, 4.0]] {
            for max_raises in [2, 3] {
                let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
                    "positions":["CO","BTN","SB","BB"],"posts":[0,0,0.5,1],
                    "stack":12,"limp":true,"open_raises":opens,"raise_mults":[2,3],
                    "max_raises":max_raises,"add_allin":true,"realization":"raw"
                }))
                .unwrap();
                let s = modeled(cfg.clone(), eq.clone(), "legacy_product");
                assert!(s.nodes.len() < 250_000, "budget test must remain small");
                let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks);
                let elements = forced_policy_elements(&s).unwrap();
                let need = base + forced_storage_bytes(elements).unwrap() as f64 / 1e6;
                let bad_budget = base.ceil() as u64;
                if (bad_budget as f64) < need {
                    return (cfg, bad_budget);
                }
            }
        }
        panic!("no small real fixture crossed a whole-MB forced-payload boundary");
    }

    #[test]
    fn real_cuda_forced_allocation_and_budget_refusal_legacy_and_coupled() {
        let eq = cached_equity();
        let (cfg, bad_budget) = boundary_fixture(eq.clone());
        for model in ["legacy_product", "coupled_deck_v1"] {
            let mut s = modeled(cfg.clone(), eq.clone(), model);
            let expected_elements: usize = s
                .nodes
                .iter()
                .filter(|nd| nd.kind == KIND_ACTION && s.cfg.positions[nd.actor as usize] != "BTN")
                .map(|nd| nd.actions.len() * NUM_CLASSES)
                .sum();
            assert_eq!(forced_policy_elements(&s).unwrap(), expected_elements);
            let expected_bytes = expected_elements * std::mem::size_of::<f32>();
            assert_eq!(
                forced_storage_bytes(expected_elements).unwrap(),
                expected_bytes
            );
            assert!(expected_bytes > 0);
            let estimate = vram_estimate_mb(&s);
            assert!(
                estimate < 1000.0,
                "tiny fixture must fit below 1 GB estimate"
            );
            let good_budget = estimate.ceil() as u64 + 1;
            let mut gpu = PreflopGpu::new(&s, good_budget).expect("real modeled GPU allocation");
            assert_eq!(
                gpu.d_forced.len() * std::mem::size_of::<f32>(),
                expected_bytes
            );
            assert_eq!(gpu.use_multiway != 0, model == "coupled_deck_v1");
            let uploaded = gpu.stream.clone_dtoh(&gpu.d_forced).unwrap();
            let expected: Vec<f32> = s
                .nodes
                .iter()
                .enumerate()
                .filter(|(_, nd)| nd.kind == KIND_ACTION)
                .flat_map(|(i, _)| s.forced_sigma(i).unwrap_or_default())
                .collect();
            assert_eq!(uploaded.len(), expected.len());
            for (a, b) in uploaded.iter().zip(&expected) {
                assert_eq!(a.to_bits(), b.to_bits());
            }
            gpu.iterate(&mut s)
                .expect("materialized forced policies must execute");
            drop(gpu);

            // Base alone fits, but base+forced does not. Both models must fail
            // at the explicit forced reservation, not a later CUDA OOM/CDF check.
            let base = minimum_vram_mb(&s, ValuePlan::build(&s).blocks);
            assert!(base <= bad_budget as f64);
            assert!(base + expected_bytes as f64 / 1e6 > bad_budget as f64);
            let err = match PreflopGpu::new(&s, bad_budget) {
                Err(err) => err,
                Ok(_) => panic!("constructor accepted a budget omitting forced policy storage"),
            };
            assert!(err.contains("forced policies"), "wrong refusal: {err}");
            eprintln!(
                "FORCED_BUDGET_CUDA {}",
                serde_json::json!({
                    "model":model,"nodes":s.nodes.len(),"forced_elements":expected_elements,
                    "actual_forced_bytes":expected_bytes,"good_budget_mb":good_budget,
                    "base_mb":base,"refused_budget_mb":bad_budget,"iteration_executed":s.iteration
                })
            );
        }
    }
}

#[cfg(test)]
mod compatibility_batch_tests {
    use super::*;
    fn original_oracle(budget:u64,base:f64,fixed:usize,slots:usize,eq:usize,has_eq:bool)->Option<(usize,bool)> {
        let per_particle=slots*(NUM_CLASSES+1)*4;
        let remaining=(budget as f64*1e6-base*1e6-fixed as f64).max(0.0) as usize;
        let batch=(remaining/per_particle).min(32).min(super::super::multiway::SAMPLES);
        if batch==0{return None;}
        let need=base+(fixed+per_particle*batch) as f64/1e6;
        Some((batch,has_eq && need+eq as f64/1e6<=budget as f64))
    }
    #[test]
    fn compatibility_reference_matches_original_union_budget_arithmetic() {
        for slots in [1usize,1000,846156] {for budget in [1u64,19_000,21_000,23_000] {
            for (base,fixed,eq,has_eq) in [(0.,0,0,false),(64.,100_000,2_000_000,true),(5330.,171_096,302_708_744,true)] {
                let got=reference_multiway_plan(budget,base,fixed,slots,eq,has_eq).unwrap().map(|p|(p.batch,p.use_eq_cache));
                assert_eq!(got,original_oracle(budget,base,fixed,slots,eq,has_eq));
            }
        }}
    }
    #[test]
    fn compatibility_compaction_keeps_reference_batch_and_cache_at_19_21_23gb() {
        // Algebraically reduced fixed costs reproduce the observed modeled
        // six-seat planner totals; this is a pure planner test, not a GPU claim.
        for budget in [19_000,21_000,23_000] {
            let p=compatible_multiway_plan(budget,5330.,171_096,26_008_848,846156,432300,302_708_744,true).unwrap().unwrap();
            let r=original_oracle(budget,5330.,171_096,846156,302_708_744,true).unwrap();
            assert_eq!((p.storage.batch,p.reference.as_ref().unwrap().use_eq_cache),r);
            assert!(p.storage.normalized_bytes>0);
            let bytes=26_008_848+p.storage.normalized_bytes+p.storage.cache_len*4+if r.1{302_708_744}else{0};
            assert!(5330.+bytes as f64/1e6<=budget as f64);
            if budget==23_000 {assert_eq!(p.storage.batch,30);}
        }
    }
    #[test]
    fn compatibility_drops_normalization_to_keep_required_grouping() {
        // 2.5 MB available: original can fit 3 x 680,000-byte particles, but
        // adding a 676,000-byte normalized table would force a smaller batch.
        let p=compatible_multiway_plan(3,0.5,0,0,1000,1000,0,false).unwrap().unwrap();
        assert_eq!(p.storage.batch,3);assert_eq!(p.storage.normalized_bytes,0);
        // More room within the same original batch makes normalization safe
        // only if it actually fits; normalization is not a priority over B.
        let p=compatible_multiway_plan(4,0.1,0,0,1000,500,0,false).unwrap().unwrap();
        assert_eq!(p.storage.batch,5);assert!(p.storage.normalized_bytes>0);
    }
    #[test]
    fn compatibility_keeps_hu_cache_and_refuses_extra_metadata_regression() {
        let no_cache=compatible_multiway_plan(3,0.5,0,0,1000,500,500_000,true).unwrap().unwrap();
        assert!(!no_cache.reference.unwrap().use_eq_cache); // compaction's free room must not toggle it
        let cached=compatible_multiway_plan(3,0.5,0,0,1000,1000,400_000,true).unwrap().unwrap();
        assert!(cached.reference.unwrap().use_eq_cache);assert_eq!(cached.storage.batch,3);
        assert_eq!(cached.storage.normalized_bytes,0);
        let p=compatible_multiway_plan(3,0.5,0,100_000,1000,1000,400_000,true).unwrap().unwrap();
        assert!(p.minimal_metadata);assert_eq!(p.storage.batch,3);assert!(p.reference.unwrap().use_eq_cache);
        // Extra direct-CDF metadata cannot fit at B: keep B with original layout.
        let p=compatible_multiway_plan(3,0.5,0,500_000,1000,1000,0,false).unwrap().unwrap();
        assert!(p.minimal_metadata);assert_eq!(p.storage.batch,3);assert_eq!(p.storage.normalized_bytes,0);
    }
    #[test]
    fn compatibility_capacity_extension_has_no_fabricated_reference() {
        // Old union needs 680k/particle and has only 600k; compact fits.
        let p=compatible_multiway_plan(1,0.4,0,0,1000,500,0,false).unwrap().unwrap();
        assert!(p.reference.is_none());assert_eq!(p.storage.batch,1);assert_eq!(p.storage.normalized_bytes,0);
        assert!(compatible_multiway_plan(1,0.9,0,0,1000,500,0,false).unwrap().is_none());
        assert!(reference_multiway_plan(23_000,0.,0,usize::MAX,0,false).is_err());
        assert!(compatible_multiway_plan(23_000,0.,0,0,1000,usize::MAX,0,false).is_err());
        assert!(reference_multiway_plan(1,f64::NAN,0,1,0,false).is_err());
    }
}

#[cfg(test)]
mod deployed_reference_tests {
    use super::*;
    #[test]
    fn deployed_reference_retains_literal_choices_with_accurate_compact_budget() {
        // Fixed terms are folded into base for this measured-cost host fixture.
        // HU cost includes 13,564,508 metadata bytes, not just equity entries.
        let accurate=5316.606588;let literal=4902.313904;let fixed_extra=25_837_752;
        let hu=316_273_252;let u=846156;let c=432300;
        for (budget,old_b,old_hu,corrected_b,corrected_hu,expected_bytes) in [
            (19000,24,false,23,true,12_689_815_140u64),
            (21000,27,true,27,false,13_887_980_392),
            (23000,31,false,30,true,14_747_563_140),
        ] {
            let old=reference_multiway_plan(budget,literal,0,u,hu,true).unwrap().unwrap();
            let corrected=reference_multiway_plan(budget,accurate,0,u,hu,true).unwrap().unwrap();
            assert_eq!((old.batch,old.use_eq_cache),(old_b,old_hu));
            assert_eq!((corrected.batch,corrected.use_eq_cache),(corrected_b,corrected_hu));
            let selected=deployed_compatible_multiway_plan(budget,accurate,literal,0,fixed_extra,u,c,hu,true,false).unwrap().unwrap();
            assert_eq!(selected.reference_source,"deployed_prepass");assert_eq!(selected.literal_reference,Some(old));
            assert_eq!(selected.plan.reference,Some(old));assert_eq!(selected.plan.storage.batch,old_b);
            assert!(!selected.plan.minimal_metadata && selected.plan.storage.normalized_bytes>0);
            let physical=accurate*1e6+(fixed_extra+selected.plan.storage.cache_len*4
                +selected.plan.storage.normalized_bytes+if old_hu {hu}else{0}) as f64;
            assert_eq!(physical.round() as u64,expected_bytes);
            assert!(physical<=budget as f64*1e6);
        }
    }
    #[test]
    fn deployed_reference_only_changes_when_exact_target_cannot_fit() {
        // Literal B4 fits compact storage despite corrected union choosing B3.
        let p=deployed_compatible_multiway_plan(3,0.5,0.,0,0,1000,500,400_000,true,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,4);
        assert!(!p.plan.reference.unwrap().use_eq_cache);
        // No compaction: accurate B4 CDF itself exceeds budget even in minimal
        // metadata. Corrected B3/cache-on can fit via original-layout fallback.
        let p=deployed_compatible_multiway_plan(3,0.5,0.,0,100_000,1000,1000,400_000,true,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"corrected_budget_fallback");
        assert_eq!(p.literal_reference.unwrap().batch,4);assert_eq!(p.plan.storage.batch,3);
        assert!(p.plan.minimal_metadata && p.plan.reference.unwrap().use_eq_cache);
        let physical=0.5e6+(p.plan.storage.cache_len*4+400_000) as f64;
        assert!(physical<=3e6);
        // Literal B5 wins over optional normalization at the required B.
        let p=deployed_compatible_multiway_plan(4,0.5,0.,0,0,1000,1000,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,5);
        assert_eq!(p.plan.storage.normalized_bytes,0);
    }
    #[test]
    fn deployed_reference_keeps_no_forced_policy_four_byte_boundary() {
        // The pre-pass allocator omitted even the four-byte empty placeholder.
        // Compact storage can safely preserve B1 across that accounting edge.
        let corrected=reference_multiway_plan(1,0.320004,0,1000,0,false).unwrap();
        assert!(corrected.is_none());
        let p=deployed_compatible_multiway_plan(1,0.320004,0.32,0,0,1000,500,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"deployed_prepass");assert_eq!(p.plan.storage.batch,1);
        let actual=0.320004e6+(p.plan.storage.cache_len*4+p.plan.storage.normalized_bytes) as f64;
        assert!(actual<=1e6);
    }
    #[test]
    fn deployed_reference_identifies_capacity_extension_and_total_no_fit() {
        let p=deployed_compatible_multiway_plan(3,2.5,0.,0,0,1000,500,0,false,false).unwrap().unwrap();
        assert_eq!(p.reference_source,"capacity_extension");assert!(p.plan.reference.is_none());
        assert_eq!(p.literal_reference.unwrap().batch,4);assert_eq!(p.plan.storage.batch,1);
        assert!(!p.plan.minimal_metadata && p.plan.storage.normalized_bytes==0);
        assert!(2.5e6+p.plan.storage.cache_len as f64*4.<=3e6);
        assert!(deployed_compatible_multiway_plan(3,2.9,0.,0,0,1000,500,0,false,false).unwrap().is_none());
        assert!(deployed_compatible_multiway_plan(3,0.4,0.5,0,0,1000,500,0,false,false).is_err());
        assert!(deployed_compatible_multiway_plan(3,f64::NAN,0.,0,0,1000,500,0,false,false).is_err());
    }
}
