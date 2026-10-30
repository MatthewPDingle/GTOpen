//! CUDA-accelerated CFR: level-synchronous batched traversal of the game
//! tree, with regrets/strategy resident in VRAM.
//!
//! Supports DCFR/CFR+, fixed node locks, suit isomorphism and either CPU
//! storage mode. GPU arithmetic remains f32. Queries and saves use a CPU
//! `Solver`; call `sync_to_cpu` to download its arenas.

pub mod plan;
mod arena;
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
use arena::ArenaLayout;

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

    pub iteration: u32,
    pub algo: Algorithm,
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
            plan.use_full_action_arenas(&solver.spot);
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
        // cross-stream event tracking is unnecessary â€” and the events it
        // records would invalidate CUDA graph capture.
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

        let up32 = |v: &Vec<u32>| stream.clone_htod(v).map_err(e);
        let upi32 = |v: &Vec<i32>| stream.clone_htod(v).map_err(e);
        let up64 = |v: &Vec<u64>| stream.clone_htod(v).map_err(e);
        let upf = |v: &Vec<f32>| stream.clone_htod(v).map_err(e);

        let data_len = plan.arena_elements;
        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;
        let mut arena_layout = [
            ArenaLayout::new(solver, &plan, 0),
            ArenaLayout::new(solver, &plan, 1),
        ];
        let d_regrets = [
            arena_layout[0].upload(&stream, solver, 0, 0, h_staging.as_mut_slice())?,
            arena_layout[1].upload(&stream, solver, 1, 0, h_staging.as_mut_slice())?,
        ];
        let d_strat = [
            arena_layout[0].upload(&stream, solver, 0, 1, h_staging.as_mut_slice())?,
            arena_layout[1].upload(&stream, solver, 1, 1, h_staging.as_mut_slice())?,
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

    /// Copy only the cumulative strategy back â€” all that exploitability
    /// checks and strategy queries need; half the PCIe traffic.
    pub fn sync_strategy(&mut self, solver: &mut Solver) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
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


    // Pinned accepted E020 up_show only; entry rename is the sole body change.
    const SHOW_ORIGINAL_REFERENCE: &str = r###"typedef unsigned int u32;
typedef unsigned long long u64;
#define SENTINEL 0xFFFFFFFFu

extern "C" __global__ void up_show_reference(
    const u32* __restrict__ nodes, int start, int count,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const float* __restrict__ node_ttie,
    const int* __restrict__ node_river_slot,
    const u32* __restrict__ rsrc_o,
    const float* __restrict__ reach_o_buf,
    const u32* __restrict__ p_off, const u32* __restrict__ p_cnt,
    const u32* __restrict__ p_idx,
    const u32* __restrict__ p_lower, const u32* __restrict__ p_upper,
    const u32* __restrict__ o_off, const u32* __restrict__ o_cnt,
    const u32* __restrict__ o_idx,
    const u32* __restrict__ o_card_off, const u32* __restrict__ o_card_pos,
    const u32* __restrict__ same_p,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    extern __shared__ char shraw[];
    int b = blockIdx.x;
    if (b >= count) return;
    u32 n = nodes[start + b];
    int slot = node_river_slot[n];
    int m_o = o_cnt[slot];
    u32 ob = o_off[slot];
    float* ro_sh = (float*)shraw; // nh_o entries, original hand order
    float* reach_sh = (float*)(shraw + sizeof(float) * nh_o);
    float* prefix = (float*)(shraw + sizeof(float) * (nh_o + m_o));
    u32* card_pos_sh = (u32*)(prefix + m_o); // 2*m_o immutable position indices
    u32 card_base = o_card_off[(u64)slot * 53];
    const float* ro_g = reach_o_buf + (u64)rsrc_o[n] * nh_o;

    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
    for (int j = threadIdx.x; j < 2 * m_o; j += blockDim.x)
        card_pos_sh[j] = o_card_pos[card_base + j];
    __syncthreads();
    const float* ro = ro_sh;
    for (int k = threadIdx.x; k < m_o; k += blockDim.x) {
        reach_sh[k] = ro[o_idx[ob + k]];
    }
    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;
    __syncthreads();
    // Blocked inclusive scan: per-thread chunk scan, thread-0 scans chunk
    // totals, then chunk offsets are added back.
    __shared__ float chunk_sum[257];
    {
        int chunk = (m_o + blockDim.x - 1) / blockDim.x;
        int lo_k = threadIdx.x * chunk;
        int hi_k = min(lo_k + chunk, m_o);
        float acc = 0.f;
        for (int k = lo_k; k < hi_k; k++) {
            acc += reach_sh[k];
            prefix[k] = acc;
        }
        chunk_sum[threadIdx.x + 1] = acc;
        __syncthreads();
        if (threadIdx.x == 0) {
            chunk_sum[0] = 0.f;
            for (int t = 1; t <= (int)blockDim.x; t++) chunk_sum[t] += chunk_sum[t - 1];
        }
        __syncthreads();
        float base = chunk_sum[threadIdx.x];
        for (int k = lo_k; k < hi_k; k++) prefix[k] += base;
    }
    __syncthreads();
    float total = m_o > 0 ? prefix[m_o - 1] : 0.f;
    float win = node_twin[n], lose = node_tlose[n], tie = node_ttie[n];

    int m_p = p_cnt[slot];
    u32 pb = p_off[slot];
    for (int k = threadIdx.x; k < m_p; k += blockDim.x) {
        u32 i = p_idx[pb + k];
        u32 lb = p_lower[pb + k], ub = p_upper[pb + k];
        float lower = lb > 0 ? prefix[lb - 1] : 0.f;
        float higher = total - (ub > 0 ? prefix[ub - 1] : 0.f);
        float tot_c = 0.f, lower_c = 0.f, higher_c = 0.f;
        u32 cc[2] = { pc1[i], pc2[i] };
        for (int x = 0; x < 2; x++) {
            u32 c0 = o_card_off[(u64)slot * 53 + cc[x]];
            u32 c1 = o_card_off[(u64)slot * 53 + cc[x] + 1];
            for (u32 t = c0; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
            }
        }
        u32 sc = same_p[i];
        float same_r = sc != SENTINEL ? ro[sc] : 0.f;
        float valid = total - tot_c + same_r;
        lower -= lower_c;
        higher -= higher_c;
        float tied = valid - lower - higher;
        cfv[(u64)cfv_slot[n] * nh_max + i] = win * lower + lose * higher + tie * tied;
    }
}
"###;

    #[test]
    fn show_positive_zero_matches_original_kernel() {
        fn bits(values: &[f32]) -> Vec<u32> { values.iter().map(|v| v.to_bits()).collect() }
        fn sorted(hands: &[(u8,u8)], board: &[u8], mode: u32, own: bool) -> Vec<(u32,usize)> {
            let mut result = Vec::new();
            for (i, &(a,b)) in hands.iter().enumerate() {
                if mode == 2 || (mode == 0 && if own { i%5 == 0 } else { i%7 == 0 || i+1 == hands.len() }) { continue; }
                let mut cards = board.to_vec(); cards.extend([a,b]);
                result.push((crate::evaluator::evaluate7(&cards),i));
            }
            result.sort_unstable();
            result
        }
        const GUARD: u32 = 0x4f12_3456;
        const NH_MAX: usize = 272;
        let ctx = CudaContext::new(0).unwrap();
        let stream = ctx.default_stream();
        let (major,minor) = ctx.compute_capability().unwrap();
        let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        let compile = |source: &str, entry: &str| {
            let ptx = cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions {
                arch: Some(arch), ..Default::default()
            }).unwrap();
            ctx.load_module(ptx).unwrap().load_function(entry).unwrap()
        };
        let reference = compile(SHOW_ORIGINAL_REFERENCE,"up_show_reference");
        let candidate = compile(include_str!("kernels.cu"),"up_show");
        let board = crate::cards::parse_cards("Ks7h2dQhTc").unwrap();
        let all_hands: Vec<(u8,u8)> = (0..52u8).flat_map(|a|((a+1)..52).map(move |b|(a,b)))
            .filter(|(a,b)|!board.contains(a) && !board.contains(b)).collect();
        let hands_a = all_hands[..257].to_vec();
        let hands_b: Vec<_> = (0..129).map(|i|if i%2==0 { hands_a[i] } else { all_hands[300+i] }).collect();
        let overflow = f64::MAX as f32;
        assert_eq!(overflow.to_bits(),0x7f80_0000);
        let mix = [0x4020_0000,0xc020_0000,0x3f40_0000];
        let neg = [0xc020_0000,0xbfc0_0000,0xbf40_0000];
        // name, reach profile, three actual f32 payoff bits, own/opponent list modes, eligibility.
        // list modes: 0 partial, 1 full, 2 empty. Partial opponent excludes the last logical word.
        let cases = [
            ("zero_mixed",0,mix,0,0,true), ("zero_all_negative",0,neg,0,0,true),
            ("zero_positive_zero",0,[0,0,0],0,0,true),
            ("zero_negative_zero",0,[0x8000_0000;3],0,0,true),
            ("zero_full",0,mix,1,1,true), ("zero_empty_own",0,neg,2,1,true),
            ("zero_empty_opponent",0,neg,1,2,true), ("zero_both_empty",0,neg,2,2,true),
            ("zero_win_overflow",0,[overflow.to_bits(),mix[1],mix[2]],0,0,false),
            ("zero_lose_overflow",0,[mix[0],(-overflow).to_bits(),mix[2]],0,0,false),
            ("zero_tie_nan",0,[mix[0],mix[1],0x7fc1_2345],0,0,false),
            ("negative_zero_excluded_tail",1,mix,0,0,false),
            ("positive_nonzero_excluded_tail",2,mix,0,0,false),
            ("signed_cancellation",3,mix,0,0,false),
            ("infinite_excluded_tail",4,mix,0,0,false),
            ("nan_excluded_tail",5,mix,0,0,false),
        ];
        let mut pairs = 0usize;
        let mut launches = 0usize;
        for &(name,profile,payout_bits,own_mode,opp_mode,eligible) in &cases { for orientation in 0..2 {
            let (own,opponent) = if orientation==0 { (&hands_b,&hands_a) } else { (&hands_a,&hands_b) };
            let (nh_p,nh_o) = (own.len(),opponent.len());
            let ps = sorted(own,&board,own_mode,true);
            let os = sorted(opponent,&board,opp_mode,false);
            if own_mode==0 {
                assert!(ps.iter().enumerate().any(|(k,&(_,i))|k%128!=i%128),"cross-lane witness {name}");
                assert!(ps.len()<nh_p && !ps.is_empty());
            }
            if opp_mode==0 { assert!(os.iter().all(|&(_,i)|i+1!=nh_o),"excluded tail {name}"); }
            let pc1: Vec<u32> = own.iter().map(|h|h.0 as u32).collect();
            let pc2: Vec<u32> = own.iter().map(|h|h.1 as u32).collect();
            let same: Vec<u32> = own.iter().map(|h|opponent.iter().position(|x|x==h).map_or(u32::MAX,|i|i as u32)).collect();
            assert!(same.contains(&u32::MAX) && same.iter().any(|&v|v!=u32::MAX));
            let mut row = vec![0.0f32;nh_o];
            match profile {
                0=>{}, 1=>row[nh_o-1]=f32::from_bits(0x8000_0000),
                2=>{row[os[0].1]=0.5;row[nh_o-1]=0.25;},
                3=>{row[os[0].1]=1.0;row[os[1].1]=-1.0;},
                4=>row[nh_o-1]=f32::INFINITY,
                5=>row[nh_o-1]=f32::from_bits(0x7fc1_2345), _=>unreachable!(),
            }
            let payout = payout_bits.map(f32::from_bits);
            assert_eq!(row.iter().all(|x|x.to_bits()==0) && payout.iter().all(|x|x.is_finite()),eligible,"{name}");
            let nodes = vec![u32::MAX,2,u32::MAX];
            let mut twin=vec![9.5f32;4];twin[2]=payout[0];
            let mut tlose=vec![9.5f32;4];tlose[2]=payout[1];
            let mut ttie=vec![9.5f32;4];ttie[2]=payout[2];
            let river_slot=vec![-1i32,-1,1,-1];
            let reach_slot=if orientation==0 {2usize} else {1usize};
            let rsrc=vec![0u32,0,reach_slot as u32,0];
            let mut reach=vec![3.5f32;4*nh_o];reach[reach_slot*nh_o..(reach_slot+1)*nh_o].copy_from_slice(&row);
            let p_off=vec![0u32,3];let p_cnt=vec![0u32,ps.len() as u32];
            let mut p_idx=vec![u32::MAX;3];p_idx.extend(ps.iter().map(|&(_,i)|i as u32));p_idx.push(u32::MAX);
            let mut lower=vec![u32::MAX;3];let mut upper=vec![u32::MAX;3];
            for &(strength,_) in &ps {
                lower.push(os.partition_point(|&(s,_)|s<strength) as u32);
                upper.push(os.partition_point(|&(s,_)|s<=strength) as u32);
            }
            lower.push(u32::MAX);upper.push(u32::MAX);
            let o_off=vec![0u32,5];let o_cnt=vec![0u32,os.len() as u32];
            let mut o_idx=vec![u32::MAX;5];o_idx.extend(os.iter().map(|&(_,i)|i as u32));o_idx.push(u32::MAX);
            let mut card_off=vec![0u32;53];let mut card_pos=vec![u32::MAX;3];
            for card in 0..52u8 {
                card_off.push(card_pos.len() as u32);
                for (pos,&(_,i)) in os.iter().enumerate() {
                    let (a,b)=opponent[i];if card==a || card==b {card_pos.push(pos as u32);}
                }
            }
            card_off.push(card_pos.len() as u32);assert_eq!(card_pos.len(),3+2*os.len());card_pos.push(u32::MAX);
            let slots=vec![u32::MAX,u32::MAX,2,u32::MAX];
            let d_nodes=stream.clone_htod(&nodes).unwrap();let d_twin=stream.clone_htod(&twin).unwrap();
            let d_tlose=stream.clone_htod(&tlose).unwrap();let d_ttie=stream.clone_htod(&ttie).unwrap();
            let d_river=stream.clone_htod(&river_slot).unwrap();let d_rsrc=stream.clone_htod(&rsrc).unwrap();
            let d_reach=stream.clone_htod(&reach).unwrap();
            let d_poff=stream.clone_htod(&p_off).unwrap();let d_pcnt=stream.clone_htod(&p_cnt).unwrap();
            let d_pidx=stream.clone_htod(&p_idx).unwrap();let d_lower=stream.clone_htod(&lower).unwrap();let d_upper=stream.clone_htod(&upper).unwrap();
            let d_ooff=stream.clone_htod(&o_off).unwrap();let d_ocnt=stream.clone_htod(&o_cnt).unwrap();let d_oidx=stream.clone_htod(&o_idx).unwrap();
            let d_coff=stream.clone_htod(&card_off).unwrap();let d_cpos=stream.clone_htod(&card_pos).unwrap();
            let d_same=stream.clone_htod(&same).unwrap();let d_pc1=stream.clone_htod(&pc1).unwrap();let d_pc2=stream.clone_htod(&pc2).unwrap();
            let d_slots=stream.clone_htod(&slots).unwrap();
            let counts: &[i32]=if name=="zero_mixed" {&[1,0]} else {&[1]};
            let mut present=vec![false;nh_p];for &(_,i) in &ps {present[i]=true;}
            for &count in counts {
                let initial=vec![f32::from_bits(GUARD);4*NH_MAX];let mut outputs=Vec::new();
                for function in [&reference,&candidate] {
                    let mut out=stream.clone_htod(&initial).unwrap();
                    let start=1i32;let hp=nh_p as i32;let ho=nh_o as i32;let hm=NH_MAX as i32;
                    unsafe {stream.launch_builder(function).arg(&d_nodes).arg(&start).arg(&count)
                        .arg(&d_twin).arg(&d_tlose).arg(&d_ttie).arg(&d_river).arg(&d_rsrc).arg(&d_reach)
                        .arg(&d_poff).arg(&d_pcnt).arg(&d_pidx).arg(&d_lower).arg(&d_upper)
                        .arg(&d_ooff).arg(&d_ocnt).arg(&d_oidx).arg(&d_coff).arg(&d_cpos)
                        .arg(&d_same).arg(&d_pc1).arg(&d_pc2).arg(&d_slots).arg(&mut out).arg(&hp).arg(&ho).arg(&hm)
                        .launch(LaunchConfig {grid_dim:(2,1,1),block_dim:(128,1,1),shared_mem_bytes:((nh_o+4*os.len())*4) as u32}).unwrap();}
                    launches+=1;
                    let actual=bits(&stream.clone_dtoh(&out).unwrap());
                    for (i,&word) in actual.iter().enumerate() {
                        if count==1 && (2*NH_MAX..2*NH_MAX+nh_p).contains(&i) {
                            let logical=i-2*NH_MAX;assert_ne!(word,GUARD,"active store {name}/{orientation}/{i}");
                            if !present[logical] {assert_eq!(word,0,"absent +0 {name}/{orientation}/{i}");}
                            else if eligible {
                                let negative=payout_bits.iter().all(|v|v&0x8000_0000!=0);
                                assert_eq!(word,if negative {0x8000_0000} else {0},"present signedzero {name}/{orientation}/{i}");
                            }
                        } else {assert_eq!(word,GUARD,"guard {name}/{orientation}/{i}");}
                    }
                    macro_rules! same_int {($h:expr,$d:expr)=>{assert_eq!(&stream.clone_dtoh($d).unwrap(),$h,"immutable {name}/{orientation}");};}
                    macro_rules! same_float {($h:expr,$d:expr)=>{assert_eq!(bits(&stream.clone_dtoh($d).unwrap()),bits($h),"immutable float {name}/{orientation}");};}
                    same_int!(&nodes,&d_nodes);same_float!(&twin,&d_twin);same_float!(&tlose,&d_tlose);same_float!(&ttie,&d_ttie);
                    same_int!(&river_slot,&d_river);same_int!(&rsrc,&d_rsrc);same_float!(&reach,&d_reach);
                    same_int!(&p_off,&d_poff);same_int!(&p_cnt,&d_pcnt);same_int!(&p_idx,&d_pidx);same_int!(&lower,&d_lower);same_int!(&upper,&d_upper);
                    same_int!(&o_off,&d_ooff);same_int!(&o_cnt,&d_ocnt);same_int!(&o_idx,&d_oidx);same_int!(&card_off,&d_coff);same_int!(&card_pos,&d_cpos);
                    same_int!(&same,&d_same);same_int!(&pc1,&d_pc1);same_int!(&pc2,&d_pc2);same_int!(&slots,&d_slots);
                    stream.synchronize().unwrap();outputs.push(actual);
                }
                assert_eq!(outputs[0],outputs[1],"full original GPU comparison {name}/{orientation}/count{count}");
                if count==1 && profile==2 {assert!(outputs[0][2*NH_MAX..2*NH_MAX+nh_p].iter().any(|&x|x&0x7fff_ffff!=0),"nonzero witness {name}/{orientation}");}
                pairs+=1;
            }
        }}
        stream.synchronize().unwrap();drop(reference);drop(candidate);ctx.check_err().unwrap();
        assert_eq!((pairs,launches),(34,68));
        println!("E036_SHOW_ZERO_TEST {{\"comparison_pairs\":34,\"kernel_launches\":68,\"threads\":128,\"exact\":true,\"performance_measurement\":false}}");
    }

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

}
