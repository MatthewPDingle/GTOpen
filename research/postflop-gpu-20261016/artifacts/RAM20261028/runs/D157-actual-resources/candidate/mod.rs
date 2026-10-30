//! CUDA-accelerated CFR: level-synchronous batched traversal of the game
//! tree, with regrets/strategy resident in VRAM.
//!
//! Supports DCFR/CFR+, fixed node locks, suit isomorphism and either CPU
//! storage mode. GPU arithmetic remains f32. Queries and saves use a CPU
//! `Solver`; call `sync_to_cpu` to download its arenas.

pub mod plan { pub use solver::gpu::plan::*; pub fn full_arena_adapter(plan: &mut GpuPlan, spot: &solver::Spot) {
        plan.arena_elements = [spot.tree.data_size[0] as usize, spot.tree.data_size[1] as usize];
        for (i, node) in spot.tree.nodes.iter().enumerate() {
            plan.node_data_off[i] = node.data_offset;
        }
    } }
mod arena;
mod packet_readback;
#[cfg(feature = "preflop-research")]
mod continuation;
#[cfg(feature = "preflop-research")]
pub use continuation::{SymmetricContinuationGpu, StoredContinuationGpu, StoredWorkspace};
#[cfg(feature = "preflop-research")]
mod continuation_capacity;
#[cfg(feature = "preflop-research")]
pub use continuation_capacity::stored_capacity_plan;
#[cfg(feature = "preflop-research")]
mod continuation_paging;
#[cfg(feature = "preflop-research")]
pub use continuation_paging::{ContinuationWorkspace, PagedContinuationGpu};
use arena::{ArenaLayout, ZeroCheck};

use crate::cfr::{Algorithm, Discounts, Solver};
use crate::store::Store;
use cudarc::driver::{
    sys, CudaContext, CudaFunction, CudaGraph, CudaModule, CudaSlice, CudaStream, LaunchConfig,
    PushKernelArg,
};
use plan::{GpuPlan, LevelSpan};
use std::sync::Arc;
use rayon::prelude::*;

const BLOCK: u32 = 128;

pub const KERNEL_NAMES: [&str; 7] = [
    "copy_root",
    "down_action",
    "down_chance",
    "up_fold",
    "up_show",
    "up_chance",
    "up_action",
];

#[derive(Default)]
pub struct Profile {
    pub ms: [f64; 7],
    pub launches: [u32; 7],
}

fn profq(prof: &Option<&mut Profile>) -> Option<std::time::Instant> {
    prof.as_ref().map(|_| std::time::Instant::now())
}

fn prof_acc(
    stream: &CudaStream,
    prof: &mut Option<&mut Profile>,
    k: usize,
    t0: Option<std::time::Instant>,
) -> Result<(), String> {
    if let (Some(t0), Some(pr)) = (t0, prof.as_deref_mut()) {
        stream.synchronize().map_err(e)?;
        pr.ms[k] += t0.elapsed().as_secs_f64() * 1e3;
        pr.launches[k] += 1;
    }
    Ok(())
}

fn e(err: impl std::fmt::Debug) -> String {
    format!("cuda: {err:?}")
}

pub struct GpuSolver {
    _ctx: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    _module: Arc<CudaModule>,
    f_copy_root: CudaFunction,
    f_down_action: CudaFunction,
    f_down_chance: CudaFunction,
    f_up_fold: CudaFunction,
    f_up_show: CudaFunction,
    f_up_chance: CudaFunction,
    f_up_action: CudaFunction,
    f_up_action_eval: CudaFunction,

    // plan metadata kept host-side
    num_levels: usize,
    nh: [i32; 2],
    nh_max: i32,
    action_spans: Vec<LevelSpan>,
    chance_spans: Vec<LevelSpan>,
    chance_node_spans: Vec<LevelSpan>,
    fold_spans: Vec<LevelSpan>,
    show_spans: Vec<LevelSpan>,
    riv_max_cnt: [usize; 2],

    // device: work lists
    d_action_nodes: CudaSlice<u32>,
    d_chance_parents: CudaSlice<u32>,
    d_chance_children: CudaSlice<u32>,
    d_chance_cards: CudaSlice<u32>,
    d_chance_nodes: CudaSlice<u32>,
    d_fold_nodes: CudaSlice<u32>,
    d_show_nodes: CudaSlice<u32>,
    // device: per-node
    d_node_player: CudaSlice<i32>,
    d_node_na: CudaSlice<i32>,
    d_node_data_off: CudaSlice<u64>,
    d_node_children_start: CudaSlice<u32>,
    d_node_twin: CudaSlice<f32>,
    d_node_tlose: CudaSlice<f32>,
    d_node_ttie: CudaSlice<f32>,
    d_node_cdiv: CudaSlice<f32>,
    d_node_river_slot: CudaSlice<i32>,
    d_cc_start: CudaSlice<u32>,
    d_cc_count: CudaSlice<u32>,
    d_cc_card: CudaSlice<u32>,
    d_cc_child: CudaSlice<u32>,
    d_cc_perm: CudaSlice<u32>,
    d_hand_perm: [CudaSlice<u32>; 2],
    /// Orbit folding active: syncs must mark the CPU solver sym-dirty.
    iso_active: bool,
    d_rsrc: [CudaSlice<u32>; 2],
    d_children: CudaSlice<u32>,
    // device: hands
    d_fold_card_off: [CudaSlice<u32>; 2],
    d_fold_card_idx: [CudaSlice<u32>; 2],
    d_hand_c1: [CudaSlice<u32>; 2],
    d_hand_c2: [CudaSlice<u32>; 2],
    d_hand_mask: [CudaSlice<u64>; 2],
    d_same: [CudaSlice<u32>; 2],
    d_weights: [CudaSlice<f32>; 2],
    // device: river tables
    d_riv_off: [CudaSlice<u32>; 2],
    d_riv_cnt: [CudaSlice<u32>; 2],
    d_riv_idx: [CudaSlice<u32>; 2],
    d_riv_lower: [CudaSlice<u32>; 2],
    d_riv_upper: [CudaSlice<u32>; 2],
    d_riv_card_off: [CudaSlice<u32>; 2],
    d_riv_card_pos: [CudaSlice<u32>; 2],
    // device: locks (rebuilt via update_locks)
    d_lock_off: CudaSlice<i64>,
    d_lock_sigma: CudaSlice<f32>,
    // device: solver state + staging
    d_regrets: [CudaSlice<f32>; 2],
    d_strat: [CudaSlice<f32>; 2],
    d_reach: [CudaSlice<f32>; 2],
    d_cfv_slot: CudaSlice<u32>,
    d_cfv: CudaSlice<f32>,
    d_eval_roots: CudaSlice<f32>,
    eval_graphs: [Option<CudaGraph>; 2],
    eval_warmed: [bool; 2],
    d_disc: CudaSlice<f32>,
    /// Captured iteration sweeps (one per traverser); rebuilt if locks change.
    graphs: Option<[CudaGraph; 2]>,
    /// Cached+page-locked host staging for fast arena transfers.
    h_staging: PinnedBuf,
    arena_layout: [ArenaLayout; 2],
    packet_functions: Option<packet_readback::Functions>,

    pub iteration: u32,
    pub algo: Algorithm,
}

fn checks_with_setup<S,V:Send,F:FnOnce()->Result<S,String>,C:Fn()->V+Sync>(eligible:bool,setup:F,checks:C)->Result<(S,V),String>{
 if !eligible{let s=setup()?;return Ok((s,checks()));}
 std::thread::scope(|scope|{
  let worker=std::thread::Builder::new().name("gtopen-zero-check".into()).spawn_scoped(scope,||checks());
  let s=setup();let result=worker.ok().map(|h|h.join());let s=s?;
  let values=match result{Some(Ok(v))=>v,Some(Err(payload))=>std::panic::resume_unwind(payload),None=>checks()};Ok((s,values))
 })
}

impl GpuSolver {
    /// Research-only counterpart of Solver::research_continuation_sweep.
    /// This deliberately uses eager launches until integrated correctness is
    /// established. Its changing root reaches must never be used with the
    /// ordinary exploitability API's fixed-range normalization.
    #[cfg(feature = "preflop-research")]
    pub fn research_continuation_sweep(
        &mut self, p: usize, t: u32, own: &[f32], opponent: &[f32],
    ) -> Result<Vec<f32>, String> {
        self.research_continuation_sweep_impl(p, t, own, opponent, false)
    }

    #[cfg(feature = "preflop-research")]
    fn research_continuation_sweep_impl(
        &mut self, p: usize, t: u32, own: &[f32], opponent: &[f32], allow_iso: bool,
    ) -> Result<Vec<f32>, String> {
        if p > 1 || t == 0 || (self.iso_active && !allow_iso) || self.algo != Algorithm::CfrPlus {
            return Err("research continuation requires p=0/1, t>0, CFR+ and no isomorphism".into());
        }
        if own.len() != self.nh[p] as usize || opponent.len() != self.nh[1-p] as usize
            || own.iter().chain(opponent).any(|x| !x.is_finite() || *x < 0.) {
            return Err("invalid continuation reaches".into());
        }
        self.stream.memcpy_htod(own, &mut self.d_weights[p]).map_err(e)?;
        self.stream.memcpy_htod(opponent, &mut self.d_weights[1-p]).map_err(e)?;
        self.iteration = t;
        let disc = Discounts::for_iteration(self.algo, t);
        self.stream.memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc).map_err(e)?;
        self.sweep(p, None)?;
        self.stream.clone_dtoh(&self.d_cfv.slice(0..self.nh[p] as usize)).map_err(e)
    }

    pub fn new(solver: &Solver) -> Result<GpuSolver, String> {
        Self::new_with_budget(solver, u64::MAX)
    }

    /// Check the configured traversal's compact buffers before device allocation.
    /// Build the plan once and reuse it for both the budget check and upload.
    pub fn new_with_budget(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
        if solver.algo == Algorithm::PcfrPlus {
            return Err("GPU solver supports dcfr/cfr+ only".into());
        }

        let mut plan = GpuPlan::build(&solver.spot, solver.use_isomorphism);
        // F32 stores already support cheap direct DMA. Prefer that path if it
        // fits, avoiding inactive host snapshots on warm full-precision solves.
        // Compressed stores benefit from packing and parallel readback anyway;
        // a tight F32 budget can use the same exact compact representation.
        let full_needed = plan.staging_bytes()
            + (solver.spot.tree.data_size[0] + solver.spot.tree.data_size[1]) * 8
            + 512 * 1024 * 1024;
        if solver.storage == crate::store::Storage::F32 && full_needed <= budget_bytes {
            plan::full_arena_adapter(&mut plan, &solver.spot);
        }
        let arena_bytes = (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8;
        let needed = plan.staging_bytes() + arena_bytes + 512 * 1024 * 1024;
        if needed > budget_bytes {
            return Err(format!("spot needs ~{:.0} MB VRAM (budget {:.0} MB)",
                needed as f64 / 1e6, budget_bytes as f64 / 1e6));
        }
        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
        // Everything in a GpuSolver runs on this one stream, so cudarc's
        // cross-stream event tracking is unnecessary — and the events it
        // records would invalidate CUDA graph capture.
        unsafe { ctx.disable_event_tracking() };

        let stores = [&solver.regrets[0], &solver.regrets[1], &solver.strat[0], &solver.strat[1]];
        let q_bytes: usize = stores.iter().map(|store| match store {
            Store::I16 { q, .. } => q.len() * 2,
            Store::U16 { q, .. } => q.len() * 2,
            Store::F32(_) => 0,
        }).sum();
        let overlap = q_bytes >= 64 * 1024 * 1024;
        // Only immutable store scans leave this caller. Context, compilation,
        // allocation and every CUDA API stay here; joining precedes all uploads.
        let ((module, mut h_staging, mut arena_layout), zero_checks) = checks_with_setup(
            overlap,
            || {
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

        let data_len = plan.arena_elements;
        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;
        let mut arena_layout = [
            ArenaLayout::new(solver, &plan, 0),
            ArenaLayout::new(solver, &plan, 1),
        ];

                Ok((module, h_staging, arena_layout))
            },
            || overlap.then(|| stores.map(ZeroCheck::new)),
        )?;
        let func = |name: &str| module.load_function(name).map_err(e);

        let up32 = |v: &Vec<u32>| stream.clone_htod(v).map_err(e);
        let upi32 = |v: &Vec<i32>| stream.clone_htod(v).map_err(e);
        let up64 = |v: &Vec<u64>| stream.clone_htod(v).map_err(e);
        let upf = |v: &Vec<f32>| stream.clone_htod(v).map_err(e);

        let data_len = plan.arena_elements;
        let d_regrets = [
            arena_layout[0].upload_prechecked(&stream, solver, 0, 0, h_staging.as_mut_slice(), zero_checks.as_ref().map(|checks| &checks[0]))?,
            arena_layout[1].upload_prechecked(&stream, solver, 1, 0, h_staging.as_mut_slice(), zero_checks.as_ref().map(|checks| &checks[1]))?,
        ];
        let d_strat = [
            arena_layout[0].upload_prechecked(&stream, solver, 0, 1, h_staging.as_mut_slice(), zero_checks.as_ref().map(|checks| &checks[2]))?,
            arena_layout[1].upload_prechecked(&stream, solver, 1, 1, h_staging.as_mut_slice(), zero_checks.as_ref().map(|checks| &checks[3]))?,
        ];
        let (lock_off, lock_sigma) = build_lock_table(solver);

        let n = plan.num_nodes;
        let nh = plan.nh;
        let staging =
            plan.staging_bytes() + (data_len[0] + data_len[1]) as u64 * 8;
        println!(
            "gpu: {} nodes, {} levels, staging+arenas {:.1} MB",
            n,
            plan.num_levels,
            staging as f64 / 1e6
        );

        let mut fold_card_off = [Vec::with_capacity(53), Vec::with_capacity(53)];
        let mut fold_card_idx = [Vec::new(), Vec::new()];
        for p in 0..2 {
            for card in 0..52u8 {
                fold_card_off[p].push(fold_card_idx[p].len() as u32);
                for (i, hand) in solver.spot.hands[p].iter().enumerate() {
                    if hand.mask & (1u64 << card) != 0 {
                        fold_card_idx[p].push(i as u32);
                    }
                }
            }
            fold_card_off[p].push(fold_card_idx[p].len() as u32);
        }

        Ok(GpuSolver {
            f_copy_root: func("copy_root")?,
            f_down_action: func("down_action")?,
            f_down_chance: func("down_chance")?,
            f_up_fold: func("up_fold")?,
            f_up_show: func("up_show")?,
            f_up_chance: func("up_chance")?,
            f_up_action: func("up_action")?,
            f_up_action_eval: func("up_action_eval")?,
            num_levels: plan.num_levels,
            nh: [nh[0] as i32, nh[1] as i32],
            nh_max: plan.nh_max as i32,
            action_spans: plan.action_spans,
            chance_spans: plan.chance_spans,
            chance_node_spans: plan.chance_node_spans,
            fold_spans: plan.fold_spans,
            show_spans: plan.show_spans,
            riv_max_cnt: plan.riv_max_cnt,

            d_action_nodes: up32(&plan.action_nodes)?,
            d_chance_parents: up32(&plan.chance_parents)?,
            d_chance_children: up32(&plan.chance_children)?,
            d_chance_cards: up32(&plan.chance_cards)?,
            d_chance_nodes: up32(&plan.chance_nodes)?,
            d_fold_nodes: up32(&plan.fold_nodes)?,
            d_show_nodes: up32(&plan.show_nodes)?,
            d_node_player: upi32(&plan.node_player)?,
            d_node_na: upi32(&plan.node_na)?,
            d_node_data_off: up64(&plan.node_data_off)?,
            d_node_children_start: up32(&plan.node_children_start)?,
            d_node_twin: upf(&plan.node_twin)?,
            d_node_tlose: upf(&plan.node_tlose)?,
            d_node_ttie: upf(&plan.node_ttie)?,
            d_node_cdiv: upf(&plan.node_cdiv)?,
            d_node_river_slot: upi32(&plan.node_river_slot)?,
            d_cc_start: up32(&plan.cc_start)?,
            d_cc_count: up32(&plan.cc_count)?,
            d_cc_card: up32(&plan.cc_card)?,
            d_cc_child: up32(&plan.cc_child)?,
            d_cc_perm: up32(&plan.cc_perm)?,
            d_hand_perm: [up32(&plan.hand_perm_flat[0])?, up32(&plan.hand_perm_flat[1])?],
            iso_active: plan.iso_active,
            d_rsrc: [up32(&plan.reach_slot[0])?, up32(&plan.reach_slot[1])?],
            d_children: up32(&solver.spot.tree.children)?,
            d_fold_card_off: [up32(&fold_card_off[0])?, up32(&fold_card_off[1])?],
            d_fold_card_idx: [up32(&fold_card_idx[0])?, up32(&fold_card_idx[1])?],
            d_hand_c1: [up32(&plan.hand_c1[0])?, up32(&plan.hand_c1[1])?],
            d_hand_c2: [up32(&plan.hand_c2[0])?, up32(&plan.hand_c2[1])?],
            d_hand_mask: [up64(&plan.hand_mask[0])?, up64(&plan.hand_mask[1])?],
            d_same: [up32(&plan.same_combo[0])?, up32(&plan.same_combo[1])?],
            d_weights: [upf(&plan.weights[0])?, upf(&plan.weights[1])?],
            d_riv_off: [up32(&plan.riv_off[0])?, up32(&plan.riv_off[1])?],
            d_riv_cnt: [up32(&plan.riv_cnt[0])?, up32(&plan.riv_cnt[1])?],
            d_riv_idx: [up32(&plan.riv_sorted_idx[0])?, up32(&plan.riv_sorted_idx[1])?],
            d_riv_lower: [up32(&plan.riv_lower[0])?, up32(&plan.riv_lower[1])?],
            d_riv_upper: [up32(&plan.riv_upper[0])?, up32(&plan.riv_upper[1])?],
            d_riv_card_off: [up32(&plan.riv_card_off[0])?, up32(&plan.riv_card_off[1])?],
            d_riv_card_pos: [up32(&plan.riv_card_pos[0])?, up32(&plan.riv_card_pos[1])?],
            d_lock_off: stream.clone_htod(&lock_off).map_err(e)?,
            d_lock_sigma: stream.clone_htod(&lock_sigma).map_err(e)?,
            d_regrets,
            d_strat,
            arena_layout,
            packet_functions: None,
            d_reach: [
                stream.alloc_zeros::<f32>(plan.reach_blocks[0] * nh[0]).map_err(e)?,
                stream.alloc_zeros::<f32>(plan.reach_blocks[1] * nh[1]).map_err(e)?,
            ],
            d_cfv_slot: up32(&plan.cfv_slot)?,
            d_cfv: stream.alloc_zeros::<f32>(plan.cfv_blocks * plan.nh_max).map_err(e)?,
            d_disc: stream.alloc_zeros::<f32>(3).map_err(e)?,
            d_eval_roots: stream.alloc_zeros::<f32>(4 * plan.nh_max).map_err(e)?,
            eval_graphs: [None, None],
            eval_warmed: [false; 2],
            graphs: None,
            h_staging,
            iteration: solver.iteration,
            algo: solver.algo,
            _ctx: ctx,
            stream,
            _module: module,
        })
    }

    fn cfg(blocks: u32, shared: u32) -> LaunchConfig {
        LaunchConfig {
            grid_dim: (blocks, 1, 1),
            block_dim: (BLOCK, 1, 1),
            shared_mem_bytes: shared,
        }
    }

    pub fn iterate(&mut self) -> Result<(), String> {
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        self.stream
            .memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc)
            .map_err(e)?;
        let _ = &disc;
        if self.graphs.is_none() && self.iteration > 1 {
            // First iteration ran eagerly (JIT warm); capture the two sweeps
            // into CUDA graphs. Kernels read discounts from d_disc, so the
            // captured graphs stay valid for every later iteration.
            let mut captured = Vec::with_capacity(2);
            for p in 0..2 {
                self.stream
                    .begin_capture(
                        sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL,
                    )
                    .map_err(e)?;
                let res = self.paired_sweep(p, None, p == 1);
                let graph = self
                    .stream
                    .end_capture(
                        sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
                    )
                    .map_err(e)?;
                res?; // surface sweep errors only after capture mode is exited
                captured.push(graph.ok_or_else(|| "graph capture failed".to_string())?);
            }
            let g1 = captured.pop().unwrap();
            let g0 = captured.pop().unwrap();
            self.graphs = Some([g0, g1]);
        }
        if let Some(graphs) = &self.graphs {
            for g in graphs {
                g.launch().map_err(e)?;
            }
        } else {
            for p in 0..2 {
                self.paired_sweep(p, None, p == 1)?;
            }
        }
        Ok(())
    }

    /// One iteration with a stream sync after every launch, accumulating wall
    /// time per kernel kind. Sync overhead distorts absolute numbers, but the
    /// proportions show where the time goes.
    pub fn iterate_profiled(&mut self) -> Result<Profile, String> {
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        self.stream
            .memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc)
            .map_err(e)?;
        let mut prof = Profile::default();
        for p in 0..2 {
            self.paired_sweep(p, Some(&mut prof), p == 1)?;
        }
        Ok(prof)
    }

    /// Exploitability of the current average strategy, computed entirely on
    /// the GPU (best-response and, with rake, average-EV sweeps). Mirrors
    /// `Solver::exploitability`.
    pub fn exploitability(&mut self, solver: &Solver) -> Result<f64, String> {
        let denom = solver.pair_weight_sum();
        if denom <= 0.0 {
            return Ok(f64::NAN);
        }
        let dot = |cfv: &[f32], p: usize| -> f64 {
            solver.spot.weights[p]
                .iter()
                .zip(cfv.iter())
                .map(|(&w, &v)| w as f64 * v as f64)
                .sum::<f64>()
                / denom
        };
        let raked = solver.spot.tree.config.rake_pct > 0.0;
        let key = raked as usize;
        // Warm kernels eagerly once, then capture the fixed evaluation work.
        // Root copies remain on device until a single host download. Dot products
        // below retain the original f64 order and normalization exactly.
        let roots = if !self.eval_warmed[key] {
            // Preserve the original first-check path: very short solves should
            // not pay for device-to-device copy setup or graph instantiation.
            self.eval_down()?;
            let mut roots = vec![0f32; 4 * self.nh_max as usize];
            for p in 0..2 {
                for mode in 0..if raked { 2 } else { 1 } {
                    let cfv = self.eval_root_cfv(p, mode, mode == 0)?;
                    let off = (2 * p + mode as usize) * self.nh_max as usize;
                    roots[off..off + cfv.len()].copy_from_slice(&cfv);
                }
            }
            self.eval_warmed[key] = true;
            roots
        } else {
            if self.eval_graphs[key].is_none() {
                self.stream.begin_capture(
                    sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL,
                ).map_err(e)?;
                let result = self.queue_evaluation(raked);
                let graph = self.stream.end_capture(
                    sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
                ).map_err(e)?;
                result?;
                self.eval_graphs[key] = Some(graph.ok_or_else(|| "evaluation graph capture failed".to_string())?);
            }
            self.eval_graphs[key].as_ref().unwrap().launch().map_err(e)?;
            self.stream.clone_dtoh(&self.d_eval_roots).map_err(e)?
        };
        let mut br = [0f64; 2];
        let mut v = [0f64; 2];
        for p in 0..2 {
            let off = 2 * p * self.nh_max as usize;
            br[p] = dot(&roots[off..off + self.nh[p] as usize], p);
            if raked {
                let off = off + self.nh_max as usize;
                v[p] = dot(&roots[off..off + self.nh[p] as usize], p);
            }
        }
        if solver.spot.tree.config.rake_pct > 0.0 {
            // With rake the game is not zero-sum: compare against actual EVs.
            Ok(((br[0] - v[0]) + (br[1] - v[1])) / 2.0)
        } else {
            Ok((br[0] + br[1]) / 2.0)
        }
    }

    fn queue_evaluation(&mut self, raked: bool) -> Result<(), String> {
        self.eval_down()?;
        for p in 0..2 {
            for mode in 0..if raked { 2 } else { 1 } {
                self.eval_up(p, mode, mode == 0)?;
                let off = (2 * p + mode as usize) * self.nh_max as usize;
                let len = self.nh[p] as usize;
                let root = self.d_cfv.slice(0..len);
                let mut dst = self.d_eval_roots.slice_mut(off..off + len);
                self.stream.memcpy_dtod(&root, &mut dst).map_err(e)?;
            }
        }
        Ok(())
    }

    /// Evaluate using the existing reaches. Terminals can be reused only
    /// between modes for the SAME player, with no intervening solve update.
    fn eval_root_cfv(&mut self, p: usize, mode: i32, terminals: bool) -> Result<Vec<f32>, String> {
        self.eval_up(p, mode, terminals)?;
        // The root already occupies the first CFV span; no staging kernel.
        let root = self.d_cfv.slice(0..self.nh[p] as usize);
        self.stream.clone_dtoh(&root).map_err(e)
    }

    fn eval_down(&mut self) -> Result<(), String> {
        let nh0 = self.nh[0];
        let nh1 = self.nh[1];

        let [reach0, reach1] = &mut self.d_reach;
        unsafe {
            self.stream
                .launch_builder(&self.f_copy_root)
                .arg(&self.d_weights[0])
                .arg(&self.d_weights[1])
                .arg(&mut *reach0)
                .arg(&mut *reach1)
                .arg(&nh0)
                .arg(&nh1)
                .launch(Self::cfg(4, 0))
                .map_err(e)?;
        }
        for l in 0..self.num_levels {
            let sp = self.action_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                // average sigma comes from the strategy arenas
                unsafe {
                    self.stream
                        .launch_builder(&self.f_down_action)
                        .arg(&self.d_action_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_na)
                        .arg(&self.d_node_data_off)
                        .arg(&self.d_node_children_start)
                        .arg(&self.d_children)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_strat[0])
                        .arg(&self.d_strat[1])
                        .arg(&self.d_lock_off)
                        .arg(&self.d_lock_sigma)
                        .arg(&mut *reach0)
                        .arg(&mut *reach1)
                        .arg(&nh0)
                        .arg(&nh1)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
            }
            let sp = self.chance_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    self.stream
                        .launch_builder(&self.f_down_chance)
                        .arg(&self.d_chance_parents)
                        .arg(&self.d_chance_children)
                        .arg(&self.d_chance_cards)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_hand_mask[0])
                        .arg(&self.d_hand_mask[1])
                        .arg(&mut *reach0)
                        .arg(&mut *reach1)
                        .arg(&nh0)
                        .arg(&nh1)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
            }
        }

        Ok(())
    }

    fn eval_up(&mut self, p: usize, mode: i32, terminals: bool) -> Result<(), String> {
        let nh_p = self.nh[p];
        let nh_o = self.nh[1 - p];
        let nh_max = self.nh_max;
        let pi = p as i32;
        let show_shared = (self.riv_max_cnt[1 - p] * 16 + nh_o as usize * 4) as u32;
        for l in (0..self.num_levels).rev() {
            let sp = self.fold_spans[l];
            if terminals && sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_fold)
                        .arg(&self.d_fold_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&pi)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_twin)
                        .arg(&self.d_node_tlose)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_reach[0])
                        .arg(&self.d_reach[1])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
                        .arg(&self.d_fold_card_off[1 - p])
                        .arg(&self.d_fold_card_idx[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, nh_o as u32 * 4))
                        .map_err(e)?;
                }
            }
            let sp = self.show_spans[l];
            if terminals && sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_show)
                        .arg(&self.d_show_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_node_twin)
                        .arg(&self.d_node_tlose)
                        .arg(&self.d_node_ttie)
                        .arg(&self.d_node_river_slot)
                        .arg(&self.d_rsrc[1 - p])
                        .arg(&self.d_reach[1 - p])
                        .arg(&self.d_riv_off[p])
                        .arg(&self.d_riv_cnt[p])
                        .arg(&self.d_riv_idx[p])
                        .arg(&self.d_riv_lower[p])
                        .arg(&self.d_riv_upper[p])
                        .arg(&self.d_riv_off[1 - p])
                        .arg(&self.d_riv_cnt[1 - p])
                        .arg(&self.d_riv_idx[1 - p])
                        .arg(&self.d_riv_card_off[1 - p])
                        .arg(&self.d_riv_card_pos[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, show_shared))
                        .map_err(e)?;
                }
            }
            let sp = self.chance_node_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_chance)
                        .arg(&self.d_chance_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_cc_start)
                        .arg(&self.d_cc_count)
                        .arg(&self.d_cc_card)
                        .arg(&self.d_cc_child)
                        .arg(&self.d_cc_perm)
                        .arg(&self.d_node_cdiv)
                        .arg(&self.d_hand_mask[p])
                        .arg(&self.d_hand_perm[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
            }
            let sp = self.action_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_action_eval)
                        .arg(&self.d_action_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&pi)
                        .arg(&mode)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_na)
                        .arg(&self.d_node_data_off)
                        .arg(&self.d_node_children_start)
                        .arg(&self.d_children)
                        .arg(&self.d_strat[p])
                        .arg(&self.d_lock_off)
                        .arg(&self.d_lock_sigma)
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
            }
        }
        Ok(())
    }

    // Standalone/continuation calls may follow changed roots or a workspace
    // swap, so even p=1 must refresh both players' reaches.
    fn sweep(&mut self, p: usize, prof: Option<&mut Profile>) -> Result<(), String> {
        self.paired_sweep(p, prof, false)
    }

    fn paired_sweep(
        &mut self, p: usize, mut prof: Option<&mut Profile>, reuse_player1_reach: bool,
    ) -> Result<(), String> {
        debug_assert!(!reuse_player1_reach || p == 1);
        let nh0 = self.nh[0];
        let nh1 = self.nh[1];
        // Only the second sweep of an uninterrupted pair can reuse reach1:
        // p0 up updates player0 learning state and never writes either reach.
        // Every first sweep stays full, including after evaluation or resume.
        let down_nh1 = if reuse_player1_reach { 0 } else { nh1 };
        let nh_p = self.nh[p];
        let nh_o = self.nh[1 - p];
        let nh_max = self.nh_max;

        let [reach0, reach1] = &mut self.d_reach;
        let t0 = profq(&prof);
        unsafe {
            self.stream
                .launch_builder(&self.f_copy_root)
                .arg(&self.d_weights[0])
                .arg(&self.d_weights[1])
                .arg(&mut *reach0)
                .arg(&mut *reach1)
                .arg(&nh0)
                .arg(&down_nh1)
                .launch(Self::cfg(4, 0))
                .map_err(e)?;
        }
        prof_acc(&self.stream, &mut prof, 0, t0)?;

        for l in 0..self.num_levels {
            let sp = self.action_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_down_action)
                        .arg(&self.d_action_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_na)
                        .arg(&self.d_node_data_off)
                        .arg(&self.d_node_children_start)
                        .arg(&self.d_children)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_regrets[0])
                        .arg(&self.d_regrets[1])
                        .arg(&self.d_lock_off)
                        .arg(&self.d_lock_sigma)
                        .arg(&mut *reach0)
                        .arg(&mut *reach1)
                        .arg(&nh0)
                        .arg(&down_nh1)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 1, t0)?;
            }
            let sp = self.chance_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_down_chance)
                        .arg(&self.d_chance_parents)
                        .arg(&self.d_chance_children)
                        .arg(&self.d_chance_cards)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_hand_mask[0])
                        .arg(&self.d_hand_mask[1])
                        .arg(&mut *reach0)
                        .arg(&mut *reach1)
                        .arg(&nh0)
                        .arg(&down_nh1)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 2, t0)?;
            }
        }

        let pi = p as i32;
        let show_shared = (self.riv_max_cnt[1 - p] * 16 + nh_o as usize * 4) as u32;
        for l in (0..self.num_levels).rev() {
            let sp = self.fold_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_fold)
                        .arg(&self.d_fold_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&pi)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_twin)
                        .arg(&self.d_node_tlose)
                        .arg(&self.d_rsrc[0])
                        .arg(&self.d_rsrc[1])
                        .arg(&self.d_reach[0])
                        .arg(&self.d_reach[1])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
                        .arg(&self.d_fold_card_off[1 - p])
                        .arg(&self.d_fold_card_idx[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, nh_o as u32 * 4))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 3, t0)?;
            }
            let sp = self.show_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_show)
                        .arg(&self.d_show_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_node_twin)
                        .arg(&self.d_node_tlose)
                        .arg(&self.d_node_ttie)
                        .arg(&self.d_node_river_slot)
                        .arg(&self.d_rsrc[1 - p])
                        .arg(&self.d_reach[1 - p])
                        .arg(&self.d_riv_off[p])
                        .arg(&self.d_riv_cnt[p])
                        .arg(&self.d_riv_idx[p])
                        .arg(&self.d_riv_lower[p])
                        .arg(&self.d_riv_upper[p])
                        .arg(&self.d_riv_off[1 - p])
                        .arg(&self.d_riv_cnt[1 - p])
                        .arg(&self.d_riv_idx[1 - p])
                        .arg(&self.d_riv_card_off[1 - p])
                        .arg(&self.d_riv_card_pos[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, show_shared))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 4, t0)?;
            }
            let sp = self.chance_node_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_chance)
                        .arg(&self.d_chance_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&self.d_cc_start)
                        .arg(&self.d_cc_count)
                        .arg(&self.d_cc_card)
                        .arg(&self.d_cc_child)
                        .arg(&self.d_cc_perm)
                        .arg(&self.d_node_cdiv)
                        .arg(&self.d_hand_mask[p])
                        .arg(&self.d_hand_perm[p])
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 5, t0)?;
            }
            let sp = self.action_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                let t0 = profq(&prof);
                unsafe {
                    self.stream
                        .launch_builder(&self.f_up_action)
                        .arg(&self.d_action_nodes)
                        .arg(&start)
                        .arg(&count)
                        .arg(&pi)
                        .arg(&self.d_node_player)
                        .arg(&self.d_node_na)
                        .arg(&self.d_node_data_off)
                        .arg(&self.d_node_children_start)
                        .arg(&self.d_children)
                        .arg(&mut self.d_regrets[p])
                        .arg(&mut self.d_strat[p])
                        .arg(&self.d_rsrc[p])
                        .arg(&self.d_reach[p])
                        .arg(&self.d_lock_off)
                        .arg(&self.d_lock_sigma)
                        .arg(&self.d_cfv_slot)
                        .arg(&mut self.d_cfv)
                        .arg(&self.d_disc)
                        .arg(&nh_p)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 6, t0)?;
            }
        }
        Ok(())
    }

    /// Copy GPU arenas back into the CPU solver (for queries/BR/saves).
    /// Works for both f32 and compressed CPU storage (encodes per node).
    pub fn sync_to_cpu(&mut self, solver: &mut Solver) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
        if self.try_packet_sync(solver, false, packet_readback::MIN_SOURCE_BYTES)? {return Ok(());}
        for p in 0..2 {
            let len = self.d_regrets[p].len();
            self.stream
                .memcpy_dtoh(&self.d_regrets[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 0, &self.h_staging.as_slice()[..len]);
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 1, &self.h_staging.as_slice()[..len]);
        }
        solver.iteration = self.iteration;
        if self.iso_active {
            // only representative branches hold fresh data; queries/saves
            // re-materialize siblings via Solver::ensure_symmetric
            solver.mark_sym_dirty();
        }
        Ok(())
    }

    /// Copy only the cumulative strategy back — all that exploitability
    /// checks and strategy queries need; half the PCIe traffic.
    pub fn sync_strategy(&mut self, solver: &mut Solver) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
        if self.try_packet_sync(solver, true, packet_readback::MIN_SOURCE_BYTES)? {return Ok(());}
        for p in 0..2 {
            let len = self.d_strat[p].len();
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 1, &self.h_staging.as_slice()[..len]);
        }
        solver.iteration = self.iteration;
        if self.iso_active {
            solver.mark_sym_dirty();
        }
        Ok(())
    }

    /// Block until all queued GPU work is done (for timing).
    pub fn synchronize(&self) -> Result<(), String> {
        self.stream.synchronize().map_err(e)
    }

    /// Re-upload the lock table after `solver.locks` changed.
    pub fn update_locks(&mut self, solver: &Solver) -> Result<(), String> {
        // Drain in-flight kernels before the assignments below drop (free) the
        // old device buffers. The server's mutex ordering already prevents an
        // overlap, but the safety of a device free shouldn't depend on it.
        self.stream.synchronize().map_err(e)?;
        let (lock_off, lock_sigma) = build_lock_table(solver);
        self.d_lock_off = self.stream.clone_htod(&lock_off).map_err(e)?;
        self.d_lock_sigma = self.stream.clone_htod(&lock_sigma).map_err(e)?;
        // captured graphs hold pointers to the old lock buffers
        self.graphs = None;
        self.eval_graphs = [None, None];
        self.eval_warmed = [false; 2];
        Ok(())
    }
}

/// Cached (not write-combined) page-locked host memory: fast DMA in both
/// directions and normal-speed CPU reads for the encode step.
pub(crate) struct PinnedBuf {
    ptr: *mut f32,
    len: usize,
}

unsafe impl Send for PinnedBuf {}
unsafe impl Sync for PinnedBuf {}

impl PinnedBuf {
    pub(crate) fn new(ctx: &Arc<CudaContext>, len: usize) -> Result<PinnedBuf, String> {
        ctx.bind_to_thread().map_err(e)?;
        let ptr = unsafe { cudarc::driver::result::malloc_host(len * 4, 0) }.map_err(e)?;
        Ok(PinnedBuf {
            ptr: ptr as *mut f32,
            len,
        })
    }
    pub(crate) fn as_slice(&self) -> &[f32] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
    }
    pub(crate) fn as_mut_slice(&mut self) -> &mut [f32] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
    }
}

impl Drop for PinnedBuf {
    fn drop(&mut self) {
        unsafe {
            cudarc::driver::result::free_host(self.ptr as _).ok();
        }
    }
}

/// Rough VRAM requirement for solving this spot on the GPU (staging buffers,
/// f32 arenas, river tables and slack). The formula lives on `Spot` so the
/// server can show the estimate without the `gpu` feature.
pub fn estimate_vram(spot: &crate::game::Spot) -> u64 {
    spot.vram_estimate_bytes()
}

/// (free, total) device VRAM in MB for GPU 0, or None if it can't be queried
/// (no device / driver). Caches the primary-context handle so repeated queries
/// don't re-init the device; `mem_get_info` always reads live free memory.
pub fn vram_info_mb() -> Option<(u64, u64)> {
    static MEM_CTX: std::sync::OnceLock<Option<Arc<CudaContext>>> = std::sync::OnceLock::new();
    let ctx = MEM_CTX.get_or_init(|| CudaContext::new(0).ok()).as_ref()?;
    let (free, total) = ctx.mem_get_info().ok()?;
    Some((free as u64 / 1_000_000, total as u64 / 1_000_000))
}

/// Per-node offset (-1 = unlocked) plus concatenated locked sigmas.
fn build_lock_table(solver: &Solver) -> (Vec<i64>, Vec<f32>) {
    let n = solver.spot.tree.nodes.len();
    let mut off = vec![-1i64; n];
    let mut sigma = Vec::new();
    for (&node_idx, lock) in &solver.locks {
        off[node_idx as usize] = sigma.len() as i64;
        sigma.extend_from_slice(lock);
    }
    if sigma.is_empty() {
        sigma.push(0.0); // avoid zero-length device buffer
    }
    (off, sigma)
}

/// Write an f32 arena image into a CPU store (encoding if compressed).
fn write_arena(solver: &Solver, which_strat: bool, p: usize, data: &[f32]) {
    let store = if which_strat {
        &solver.strat[p]
    } else {
        &solver.regrets[p]
    };
    match store {
        Store::F32(b) => unsafe { b.slice(0, data.len()) }.copy_from_slice(data),
        _ => {
            let nh = solver.spot.hands[p].len();
            // Every node owns disjoint entries and its own scale factor.
            solver.spot.tree.nodes.par_iter().enumerate().for_each(|(idx, node)| {
                if node.kind == crate::tree::KIND_ACTION && node.player as usize == p {
                    let cnt = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe {
                        store.write_f32(idx as u32, node.data_offset, cnt, &data[off..off + cnt]);
                    }
                }
            });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{parse_sizes, LockMode, PathStep, Spot, SpotConfig, StreetSizing, TreeConfig};

    fn reach_reuse_solver(storage: crate::store::Storage, algo: Algorithm, compact: bool, menu: &str) -> Solver {
        let sizing = || StreetSizing { bet: parse_sizes(menu).unwrap(), raise: vec![], donk: vec![] };
        let mut s = Solver::with_storage(Arc::new(Spot::new(SpotConfig {
            board: "KsQs2dJd".into(),
            range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0,
                rake_pct: 0.05, rake_cap: 1.0, allin_threshold: 1.0,
                oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
                ..Default::default() },
        }).unwrap()), storage);
        s.algo = algo;
        s.use_isomorphism = compact;
        s
    }

    fn reach_reuse_gpu(s: &Solver, compact: bool) -> GpuSolver {
        let plan = GpuPlan::build(&s.spot, s.use_isomorphism);
        let budget = if compact {
            plan.staging_bytes() + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
                + 512 * 1024 * 1024
        } else { u64::MAX };
        let gpu = GpuSolver::new_with_budget(s, budget).expect("test requires CUDA");
        for p in 0..2 {
            if compact {
                assert!(gpu.d_regrets[p].len() < s.spot.tree.data_size[p] as usize,
                    "fixture must actually exercise compact action arenas");
            } else {
                assert_eq!(gpu.d_regrets[p].len(), s.spot.tree.data_size[p] as usize);
            }
        }
        gpu
    }

    fn device_bits(gpu: &GpuSolver, data: &CudaSlice<f32>) -> Vec<u32> {
        gpu.stream.clone_dtoh(data).unwrap().into_iter().map(f32::to_bits).collect()
    }

    fn assert_device_bits(a: &[u32], b: &[u32], label: &str) {
        assert_eq!(a.len(), b.len(), "{label}: length");
        if let Some(i) = a.iter().zip(b).position(|(a, b)| a != b) {
            panic!("{label}: first mismatch at {i}: {:08x} != {:08x}", a[i], b[i]);
        }
    }

    fn assert_reach_reuse_state(candidate: &GpuSolver, reference: &GpuSolver, stage: &str) {
        assert_eq!(candidate.iteration, reference.iteration, "{stage}");
        for p in 0..2 {
            for (name, a, b) in [
                ("regrets", &candidate.d_regrets[p], &reference.d_regrets[p]),
                ("strategy", &candidate.d_strat[p], &reference.d_strat[p]),
                ("reach", &candidate.d_reach[p], &reference.d_reach[p]),
            ] {
                assert_device_bits(&device_bits(candidate, a), &device_bits(reference, b),
                    &format!("{stage}/{name}/{p}"));
            }
        }
        // CFV storage is reused scratch; no comparison of inactive/unwritten slots.
    }

    fn legacy_iteration(gpu: &mut GpuSolver) {
        gpu.iteration += 1;
        let d = Discounts::for_iteration(gpu.algo, gpu.iteration);
        gpu.stream.memcpy_htod(&[d.pos, d.neg, d.strat], &mut gpu.d_disc).unwrap();
        gpu.sweep(0, None).unwrap();
        gpu.sweep(1, None).unwrap();
    }

    // Test-only copy of the original full-down dispatch. This deliberately
    // does not call paired_sweep or share its hand-count override.
    fn legacy_down(gpu: &mut GpuSolver) {
        let [reach0, reach1] = &mut gpu.d_reach;
        let nh0 = gpu.nh[0];
        let nh1 = gpu.nh[1];
        unsafe {
            gpu.stream.launch_builder(&gpu.f_copy_root)
                .arg(&gpu.d_weights[0]).arg(&gpu.d_weights[1])
                .arg(&mut *reach0).arg(&mut *reach1).arg(&nh0).arg(&nh1)
                .launch(GpuSolver::cfg(4, 0)).unwrap();
        }
        for l in 0..gpu.num_levels {
            let sp = gpu.action_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_down_action)
                        .arg(&gpu.d_action_nodes).arg(&start).arg(&count)
                        .arg(&gpu.d_node_player).arg(&gpu.d_node_na).arg(&gpu.d_node_data_off)
                        .arg(&gpu.d_node_children_start).arg(&gpu.d_children)
                        .arg(&gpu.d_rsrc[0]).arg(&gpu.d_rsrc[1])
                        .arg(&gpu.d_regrets[0]).arg(&gpu.d_regrets[1])
                        .arg(&gpu.d_lock_off).arg(&gpu.d_lock_sigma)
                        .arg(&mut *reach0).arg(&mut *reach1).arg(&nh0).arg(&nh1)
                        .launch(GpuSolver::cfg(sp.count, 0)).unwrap();
                }
            }
            let sp = gpu.chance_spans[l];
            if sp.count > 0 {
                let start = sp.start as i32;
                let count = sp.count as i32;
                unsafe {
                    gpu.stream.launch_builder(&gpu.f_down_chance)
                        .arg(&gpu.d_chance_parents).arg(&gpu.d_chance_children)
                        .arg(&gpu.d_chance_cards).arg(&start).arg(&count)
                        .arg(&gpu.d_rsrc[0]).arg(&gpu.d_rsrc[1])
                        .arg(&gpu.d_hand_mask[0]).arg(&gpu.d_hand_mask[1])
                        .arg(&mut *reach0).arg(&mut *reach1).arg(&nh0).arg(&nh1)
                        .launch(GpuSolver::cfg(sp.count, 0)).unwrap();
                }
            }
        }
    }

    #[test]
    fn paired_reach_reuse_matches_full_sweeps_across_lifecycle() {
        use crate::store::Storage;
        let mut arities = std::collections::BTreeSet::new();
        for (ai, algo) in [Algorithm::Dcfr, Algorithm::CfrPlus].into_iter().enumerate() {
            for (si, storage) in [Storage::F32, Storage::Compressed].into_iter().enumerate() {
                for compact in [false, true] {
                    let menu = ["50", "25,75", "25,50,75", "20,40,60,80"][ai * 2 + si];
                    let mut s = reach_reuse_solver(storage, algo, compact, menu);
                    arities.extend(s.spot.tree.nodes.iter().filter(|n| n.kind == crate::tree::KIND_ACTION)
                        .map(|n| n.num_children));
                    let mut candidate = reach_reuse_gpu(&s, compact);
                    let mut reference = reach_reuse_gpu(&s, compact);
                    let case = format!("{algo:?}/{storage:?}/compact={compact}");
                    for step in 1..=3 {
                        candidate.iterate().unwrap();
                        legacy_iteration(&mut reference);
                        assert_eq!(candidate.graphs.is_some(), step > 1);
                        assert!(reference.graphs.is_none());
                        assert_reach_reuse_state(&candidate, &reference, &format!("{case}/iteration{step}"));
                    }
                    assert!(device_bits(&candidate, &candidate.d_strat[1]).iter().any(|&b| b != 0));
                    // Evaluation overwrites reaches with average-strategy values.
                    // The following p0 sweep must refresh both before any reuse.
                    for _ in 0..2 {
                        assert_eq!(candidate.exploitability(&s).unwrap().to_bits(),
                            reference.exploitability(&s).unwrap().to_bits(), "{case}/evaluation");
                    }
                    assert_reach_reuse_state(&candidate, &reference, &format!("{case}/evaluated"));
                    candidate.iterate().unwrap();
                    legacy_iteration(&mut reference);
                    assert_reach_reuse_state(&candidate, &reference, &format!("{case}/after-evaluation"));
                    let profile = candidate.iterate_profiled().unwrap();
                    assert_eq!(profile.launches[0], 2);
                    legacy_iteration(&mut reference);
                    assert_reach_reuse_state(&candidate, &reference, &format!("{case}/profiled"));
                    candidate.sync_to_cpu(&mut s).unwrap();
                    // Lock both actors, invalidate the captured pair, then recapture.
                    s.lock_node(&[], LockMode::Freeze, "reach reuse OOP".into()).unwrap();
                    s.lock_node(&[PathStep::Action { index: 0 }], LockMode::Freeze,
                        "reach reuse IP".into()).unwrap();
                    candidate.update_locks(&s).unwrap();
                    reference.update_locks(&s).unwrap();
                    assert!(candidate.graphs.is_none());
                    for _ in 0..2 {
                        candidate.iterate().unwrap();
                        legacy_iteration(&mut reference);
                        assert!(candidate.graphs.is_some());
                        assert_reach_reuse_state(&candidate, &reference, &format!("{case}/locked"));
                    }
                    candidate.sync_to_cpu(&mut s).unwrap();
                    assert!(s.iteration > 0);
                    drop(candidate);
                    drop(reference);
                    // Both start from the same warm CPU image (including compressed
                    // re-encoding), with fresh zeroed reaches and no captured graph.
                    let mut resumed = reach_reuse_gpu(&s, compact);
                    let mut resumed_reference = reach_reuse_gpu(&s, compact);
                    for _ in 0..2 {
                        resumed.iterate().unwrap();
                        legacy_iteration(&mut resumed_reference);
                        assert!(resumed.graphs.is_some(), "warm first call must capture");
                        assert_reach_reuse_state(&resumed, &resumed_reference, &format!("{case}/warm"));
                    }
                }
            }
        }
        for arity in [1, 2, 3, 4, 5] {
            assert!(arities.contains(&arity), "missing action arity {arity}");
        }
    }

    #[test]
    fn paired_reach_reuse_preserves_raw_player1_and_standalone_refresh() {
        for compact in [false, true] {
            let s = reach_reuse_solver(crate::store::Storage::F32, Algorithm::CfrPlus,
                compact, "25,50,75,100");
            let mut gpu = reach_reuse_gpu(&s, compact);
            for _ in 0..3 { legacy_iteration(&mut gpu); }
            // Independent original down, then p0's full sweep/up, then the old
            // p1 down: all three complete reach1 images must match bit for bit.
            legacy_down(&mut gpu);
            let before_up0 = device_bits(&gpu, &gpu.d_reach[1]);
            gpu.sweep(0, None).unwrap();
            let after_up0 = device_bits(&gpu, &gpu.d_reach[1]);
            assert_device_bits(&before_up0, &after_up0, "p0 up preserves reach1");
            legacy_down(&mut gpu);
            assert_device_bits(&after_up0, &device_bits(&gpu, &gpu.d_reach[1]),
                "legacy p1 down repeats reach1 exactly");

            // Simulate externally changed roots/workspace contents without a p0
            // predecessor. Arbitrary weights need not respect suit isomorphism:
            // this checks dispatch refresh, not an isomorphic game solution.
            for p in 0..2 {
                let weights: Vec<f32> = (0..gpu.nh[p] as usize)
                    .map(|i| if i % 7 == 0 { -0.0 } else { (i % 11 + 1) as f32 / 16.0 }).collect();
                gpu.stream.memcpy_htod(&weights, &mut gpu.d_weights[p]).unwrap();
            }
            let poison = f32::from_bits(0x7fc1_2345);
            let poison_reaches = |gpu: &mut GpuSolver| {
                for p in 0..2 {
                    let values = vec![poison; gpu.d_reach[p].len()];
                    gpu.stream.memcpy_htod(&values, &mut gpu.d_reach[p]).unwrap();
                }
            };
            poison_reaches(&mut gpu);
            legacy_down(&mut gpu);
            let expected = [device_bits(&gpu, &gpu.d_reach[0]), device_bits(&gpu, &gpu.d_reach[1])];
            for p in 0..2 {
                assert!(expected[p].iter().any(|&b| b != poison.to_bits()));
            }
            poison_reaches(&mut gpu);
            // Same generic entrypoint used by continuation, including isolated p1.
            gpu.sweep(1, None).unwrap();
            for p in 0..2 {
                assert_device_bits(&expected[p], &device_bits(&gpu, &gpu.d_reach[p]),
                    &format!("standalone p1 refreshes player{p}"));
            }
        }
    }

    fn arenas(s: &Solver) -> Vec<Vec<f32>> {
        s.regrets.iter().chain(&s.strat).map(|arena| match arena {
            Store::F32(data) => data.as_slice().to_vec(),
            _ => unreachable!(),
        }).collect()
    }

    fn assert_shared_evaluation(gpu: &mut GpuSolver, s: &mut Solver) {
        gpu.sync_to_cpu(s).unwrap();
        let before = arenas(s);
        let iteration = s.iteration;
        let denom = s.pair_weight_sum();
        let mut br = [0.0; 2];
        let mut avg = [0.0; 2];
        for p in 0..2 {
            let dot = |v: Vec<f32>| -> f64 {
                s.spot.weights[p].iter().zip(v).map(|(&w, v)| w as f64 * v as f64).sum::<f64>() / denom
            };
            // Independent full traversals, with no reach or terminal reuse.
            gpu.eval_down().unwrap();
            br[p] = dot(gpu.eval_root_cfv(p, 0, true).unwrap());
            gpu.eval_down().unwrap();
            avg[p] = dot(gpu.eval_root_cfv(p, 1, true).unwrap());
        }
        let expected = if s.spot.tree.config.rake_pct > 0.0 {
            ((br[0] - avg[0]) + (br[1] - avg[1])) / 2.0
        } else {
            (br[0] + br[1]) / 2.0
        };
        for _ in 0..2 {
            let actual = gpu.exploitability(s).unwrap();
            // Fixed-order fold reductions make independent evaluations
            // reproducible, including when terminal values are reused.
            assert_eq!(actual.to_bits(), expected.to_bits(), "{actual} vs {expected}");
        }
        gpu.sync_to_cpu(s).unwrap();
        assert_eq!(iteration, s.iteration);
        assert_eq!(before, arenas(s), "evaluation must not change learning state");
    }

    #[test]
    fn shared_evaluation_matches_independent_sweeps() {
        for (board, iso) in [("KsQs2d", true), ("Qs7h2dKh", false), ("AsKsQsJsTs", true)] {
            for rake in [0.0, 0.05] {
                let sizing = || StreetSizing {
                    bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![],
                };
                let mut s = Solver::new(Arc::new(Spot::new(SpotConfig {
                    board: board.into(),
                    range_oop: "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
                    range_ip: "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
                    tree: TreeConfig {
                        starting_pot: 10.0, effective_stack: 20.0,
                        rake_pct: rake, rake_cap: 1.0,
                        oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
                        ..Default::default()
                    },
                }).unwrap()));
                s.use_isomorphism = iso;
                let plan = GpuPlan::build(&s.spot, s.use_isomorphism);
                let budget = plan.staging_bytes()
                    + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
                    + 512 * 1024 * 1024;
                assert!(GpuSolver::new_with_budget(&s, budget - 1).is_err());
                if plan.cfv_blocks < plan.num_nodes {
                    assert!(budget < s.spot.vram_estimate_bytes(),
                        "compact plan should admit trees the conservative estimate rejected");
                }
                let mut gpu = GpuSolver::new_with_budget(&s, budget).expect("test requires CUDA");
                for _ in 0..40 { gpu.iterate().unwrap(); }
                let mut repeat = GpuSolver::new(&s).unwrap();
                for _ in 0..40 { repeat.iterate().unwrap(); }
                repeat.sync_to_cpu(&mut s).unwrap();
                let repeated_arenas = arenas(&s);
                drop(repeat);
                assert_shared_evaluation(&mut gpu, &mut s);
                assert_eq!(arenas(&s), repeated_arenas, "learning must be reproducible");
                s.lock_node(&[PathStep::Action { index: 0 }], LockMode::Freeze, "test lock".into()).unwrap();
                gpu.update_locks(&s).unwrap();
                for _ in 0..20 { gpu.iterate().unwrap(); }
                assert_shared_evaluation(&mut gpu, &mut s);
            }
        }
    }

    #[test]
    fn tight_f32_budget_preserves_warm_and_queried_inactive_state() {
        for warm in [false, true] {
            let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
            let mut s = Solver::new(Arc::new(Spot::new(SpotConfig {
                board: "KsQs2dJd".into(),
                range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
                range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
                tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0,
                    oop: [sizing(), sizing(), sizing()], ip: [sizing(), sizing(), sizing()],
                    ..Default::default() },
            }).unwrap()));
            s.use_isomorphism = false;
            if warm { for _ in 0..4 { s.iterate(); } }
            s.use_isomorphism = true;
            let plan = GpuPlan::build(&s.spot, true);
            for (i, node) in s.spot.tree.nodes.iter().enumerate() {
                if node.kind == crate::tree::KIND_ACTION && plan.node_data_off[i] == u64::MAX {
                    if let Store::F32(b) = &s.regrets[node.player as usize] {
                        unsafe { b.write_at(node.data_offset as usize, -0.0); }
                    }
                }
            }
            let budget = plan.staging_bytes()
                + (plan.arena_elements[0] + plan.arena_elements[1]) as u64 * 8
                + 512 * 1024 * 1024;
            let mut compact = GpuSolver::new_with_budget(&s, budget).unwrap();
            let mut full = GpuSolver::new(&s).unwrap();
            assert!(compact.d_regrets[0].len() < full.d_regrets[0].len());
            for _ in 0..20 { compact.iterate().unwrap(); full.iterate().unwrap(); }
            full.sync_to_cpu(&mut s).unwrap();
            let expected = arenas(&s);
            s.ensure_symmetric();
            compact.sync_to_cpu(&mut s).unwrap();
            assert_eq!(arenas(&s), expected);
            assert_eq!(compact.exploitability(&s).unwrap().to_bits(),
                full.exploitability(&s).unwrap().to_bits());
        }
    }

    #[test]
    fn zero_check_setup_preserves_caller_error_priority_and_joined_cleanup() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        struct Mock(Arc<AtomicUsize>);
        impl Drop for Mock { fn drop(&mut self) { self.0.fetch_add(1, Ordering::SeqCst); } }
 let mut lifecycle=0;let caller=std::thread::current().id();
 for eligible in[false,true]{for setupmode in[0,1,2]{for checkmode in[0,1]{
  let calls=Arc::new(AtomicUsize::new(0));let drops=Arc::new(AtomicUsize::new(0));let c=calls.clone();let d=drops.clone();
  let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||checks_with_setup(eligible,||{assert_eq!(std::thread::current().id(),caller);match setupmode{0=>Ok(7usize),1=>Err("setup".into()),_=>panic!("setup mock")}},||{c.fetch_add(1,Ordering::SeqCst);assert_eq!(std::thread::current().id()==caller,!eligible);if checkmode==1{panic!("check mock");}Mock(d.clone())})));
  let expected=if eligible||setupmode==0{1}else{0};assert_eq!(calls.load(Ordering::SeqCst),expected);
  match(setupmode,checkmode,outcome){(1,_,Ok(Err(x)))=>assert_eq!(x,"setup"),(2,_,Err(_))=>{},(0,0,Ok(Ok((s,v))))=>{assert_eq!(s,7);drop(v);},(0,1,Err(_))=>{},_=>panic!("incorrect lifecycle")}
  assert_eq!(drops.load(Ordering::SeqCst),if checkmode==0{expected}else{0});lifecycle+=1;
 }}}

        assert_eq!(lifecycle, 12);
    }

}

impl GpuSolver {
    pub fn d157_resources(&self,stage:&str) -> serde_json::Value {
        self.stream.synchronize().unwrap();
        let (free,total)=self._ctx.mem_get_info().unwrap();
        let stack=self._ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
        let heap=self._ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
        serde_json::json!({"kind":"GPU_snapshot","stage":stage,"iteration":self.iteration,
            "explicit_device_payload_bytes":self.d_action_nodes.len()*std::mem::size_of::<u32>() + self.d_chance_parents.len()*std::mem::size_of::<u32>() + self.d_chance_children.len()*std::mem::size_of::<u32>() + self.d_chance_cards.len()*std::mem::size_of::<u32>() + self.d_chance_nodes.len()*std::mem::size_of::<u32>() + self.d_fold_nodes.len()*std::mem::size_of::<u32>() + self.d_show_nodes.len()*std::mem::size_of::<u32>() + self.d_node_player.len()*std::mem::size_of::<i32>() + self.d_node_na.len()*std::mem::size_of::<i32>() + self.d_node_data_off.len()*std::mem::size_of::<u64>() + self.d_node_children_start.len()*std::mem::size_of::<u32>() + self.d_node_twin.len()*std::mem::size_of::<f32>() + self.d_node_tlose.len()*std::mem::size_of::<f32>() + self.d_node_ttie.len()*std::mem::size_of::<f32>() + self.d_node_cdiv.len()*std::mem::size_of::<f32>() + self.d_node_river_slot.len()*std::mem::size_of::<i32>() + self.d_cc_start.len()*std::mem::size_of::<u32>() + self.d_cc_count.len()*std::mem::size_of::<u32>() + self.d_cc_card.len()*std::mem::size_of::<u32>() + self.d_cc_child.len()*std::mem::size_of::<u32>() + self.d_cc_perm.len()*std::mem::size_of::<u32>() + self.d_hand_perm[0].len()*std::mem::size_of::<u32>() + self.d_hand_perm[1].len()*std::mem::size_of::<u32>() + self.d_rsrc[0].len()*std::mem::size_of::<u32>() + self.d_rsrc[1].len()*std::mem::size_of::<u32>() + self.d_children.len()*std::mem::size_of::<u32>() + self.d_fold_card_off[0].len()*std::mem::size_of::<u32>() + self.d_fold_card_off[1].len()*std::mem::size_of::<u32>() + self.d_fold_card_idx[0].len()*std::mem::size_of::<u32>() + self.d_fold_card_idx[1].len()*std::mem::size_of::<u32>() + self.d_hand_c1[0].len()*std::mem::size_of::<u32>() + self.d_hand_c1[1].len()*std::mem::size_of::<u32>() + self.d_hand_c2[0].len()*std::mem::size_of::<u32>() + self.d_hand_c2[1].len()*std::mem::size_of::<u32>() + self.d_hand_mask[0].len()*std::mem::size_of::<u64>() + self.d_hand_mask[1].len()*std::mem::size_of::<u64>() + self.d_same[0].len()*std::mem::size_of::<u32>() + self.d_same[1].len()*std::mem::size_of::<u32>() + self.d_weights[0].len()*std::mem::size_of::<f32>() + self.d_weights[1].len()*std::mem::size_of::<f32>() + self.d_riv_off[0].len()*std::mem::size_of::<u32>() + self.d_riv_off[1].len()*std::mem::size_of::<u32>() + self.d_riv_cnt[0].len()*std::mem::size_of::<u32>() + self.d_riv_cnt[1].len()*std::mem::size_of::<u32>() + self.d_riv_idx[0].len()*std::mem::size_of::<u32>() + self.d_riv_idx[1].len()*std::mem::size_of::<u32>() + self.d_riv_lower[0].len()*std::mem::size_of::<u32>() + self.d_riv_lower[1].len()*std::mem::size_of::<u32>() + self.d_riv_upper[0].len()*std::mem::size_of::<u32>() + self.d_riv_upper[1].len()*std::mem::size_of::<u32>() + self.d_riv_card_off[0].len()*std::mem::size_of::<u32>() + self.d_riv_card_off[1].len()*std::mem::size_of::<u32>() + self.d_riv_card_pos[0].len()*std::mem::size_of::<u32>() + self.d_riv_card_pos[1].len()*std::mem::size_of::<u32>() + self.d_lock_off.len()*std::mem::size_of::<i64>() + self.d_lock_sigma.len()*std::mem::size_of::<f32>() + self.d_regrets[0].len()*std::mem::size_of::<f32>() + self.d_regrets[1].len()*std::mem::size_of::<f32>() + self.d_strat[0].len()*std::mem::size_of::<f32>() + self.d_strat[1].len()*std::mem::size_of::<f32>() + self.d_reach[0].len()*std::mem::size_of::<f32>() + self.d_reach[1].len()*std::mem::size_of::<f32>() + self.d_cfv_slot.len()*std::mem::size_of::<u32>() + self.d_cfv.len()*std::mem::size_of::<f32>() + self.d_eval_roots.len()*std::mem::size_of::<f32>() + self.d_disc.len()*std::mem::size_of::<f32>(),"pinned_bytes":self.h_staging.len*4,
            "wrapper_bytes":std::mem::size_of::<Self>(),"packet_module_loaded":self.packet_functions.is_some(),
            "graphs_present":self.graphs.is_some(),"eval_graphs_present":[self.eval_graphs[0].is_some(),self.eval_graphs[1].is_some()],
            "current_CFV_words":self.d_cfv.len(),"current_regret_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
            "current_strategy_words":[self.d_strat[0].len(),self.d_strat[1].len()],"context_stack_limit":stack,"context_heap_limit":heap,
            "driver_free_bytes":free,"driver_total_bytes":total,"driver_accounting_scope":"current driver context/device query,not a private instantaneous peak"})
    }
}
