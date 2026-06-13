//! CUDA-accelerated CFR: level-synchronous batched traversal of the game
//! tree, with regrets/strategy resident in VRAM.
//!
//! Scope (phase 1): f32 arenas, DCFR/CFR+, no node locks, no suit
//! isomorphism (every chance branch is solved independently — exact, just no
//! orbit sharing). Queries, best response and saves stay on the CPU: call
//! `sync_to_cpu` to pull the arenas back into a `Solver`.

pub mod plan;

use crate::cfr::{Algorithm, Discounts, Solver};
use crate::store::Store;
use cudarc::driver::{
    sys, CudaContext, CudaFunction, CudaGraph, CudaModule, CudaSlice, CudaStream, LaunchConfig,
    PushKernelArg,
};
use plan::{GpuPlan, LevelSpan};
use std::sync::Arc;

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
    f_copy_span: CudaFunction,

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
    d_hand_c1: [CudaSlice<u32>; 2],
    d_hand_c2: [CudaSlice<u32>; 2],
    d_hand_mask: [CudaSlice<u64>; 2],
    d_same: [CudaSlice<u32>; 2],
    d_weights: [CudaSlice<f32>; 2],
    // device: river tables
    d_riv_off: [CudaSlice<u32>; 2],
    d_riv_cnt: [CudaSlice<u32>; 2],
    d_riv_idx: [CudaSlice<u32>; 2],
    d_riv_str: [CudaSlice<u32>; 2],
    d_riv_card_off: [CudaSlice<u32>; 2],
    d_riv_card_pos: [CudaSlice<u32>; 2],
    // device: locks (rebuilt via update_locks)
    d_lock_off: CudaSlice<i64>,
    d_lock_sigma: CudaSlice<f32>,
    // device: solver state + staging
    d_regrets: [CudaSlice<f32>; 2],
    d_strat: [CudaSlice<f32>; 2],
    d_reach: [CudaSlice<f32>; 2],
    d_cfv: CudaSlice<f32>,
    d_root_cfv: CudaSlice<f32>,
    d_disc: CudaSlice<f32>,
    /// Captured iteration sweeps (one per traverser); rebuilt if locks change.
    graphs: Option<[CudaGraph; 2]>,
    /// Cached+page-locked host staging for fast arena transfers.
    h_staging: PinnedBuf,

    pub iteration: u32,
    pub algo: Algorithm,
}

impl GpuSolver {
    pub fn new(solver: &Solver) -> Result<GpuSolver, String> {
        if solver.algo == Algorithm::PcfrPlus {
            return Err("GPU solver supports dcfr/cfr+ only".into());
        }

        let plan = GpuPlan::build(&solver.spot, solver.use_isomorphism);
        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
        // Everything in a GpuSolver runs on this one stream, so cudarc's
        // cross-stream event tracking is unnecessary — and the events it
        // records would invalidate CUDA graph capture.
        unsafe { ctx.disable_event_tracking() };

        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> =
            std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("kernels.cu"),
                    cudarc::nvrtc::CompileOptions {
                        arch: Some("compute_86"),
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

        // f32 view of an arena regardless of CPU storage mode
        let arena = |which: usize, p: usize| -> std::borrow::Cow<[f32]> {
            let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
            match store {
                Store::F32(b) => std::borrow::Cow::Borrowed(b.as_slice()),
                _ => std::borrow::Cow::Owned(solver.arena_to_f32(store, p)),
            }
        };
        let data_len = [
            solver.spot.tree.data_size[0] as usize,
            solver.spot.tree.data_size[1] as usize,
        ];
        let (lock_off, lock_sigma) = build_lock_table(solver);

        let n = plan.num_nodes;
        let nh = plan.nh;
        let staging =
            (n * (nh[0] + nh[1] + plan.nh_max)) as u64 * 4 + (data_len[0] + data_len[1]) as u64 * 8;
        println!(
            "gpu: {} nodes, {} levels, staging+arenas {:.1} MB",
            n,
            plan.num_levels,
            staging as f64 / 1e6
        );

        Ok(GpuSolver {
            f_copy_root: func("copy_root")?,
            f_down_action: func("down_action")?,
            f_down_chance: func("down_chance")?,
            f_up_fold: func("up_fold")?,
            f_up_show: func("up_show")?,
            f_up_chance: func("up_chance")?,
            f_up_action: func("up_action")?,
            f_up_action_eval: func("up_action_eval")?,
            f_copy_span: func("copy_span")?,
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
            d_rsrc: [up32(&plan.reach_src[0])?, up32(&plan.reach_src[1])?],
            d_children: up32(&solver.spot.tree.children)?,
            d_hand_c1: [up32(&plan.hand_c1[0])?, up32(&plan.hand_c1[1])?],
            d_hand_c2: [up32(&plan.hand_c2[0])?, up32(&plan.hand_c2[1])?],
            d_hand_mask: [up64(&plan.hand_mask[0])?, up64(&plan.hand_mask[1])?],
            d_same: [up32(&plan.same_combo[0])?, up32(&plan.same_combo[1])?],
            d_weights: [upf(&plan.weights[0])?, upf(&plan.weights[1])?],
            d_riv_off: [up32(&plan.riv_off[0])?, up32(&plan.riv_off[1])?],
            d_riv_cnt: [up32(&plan.riv_cnt[0])?, up32(&plan.riv_cnt[1])?],
            d_riv_idx: [up32(&plan.riv_sorted_idx[0])?, up32(&plan.riv_sorted_idx[1])?],
            d_riv_str: [up32(&plan.riv_sorted_str[0])?, up32(&plan.riv_sorted_str[1])?],
            d_riv_card_off: [up32(&plan.riv_card_off[0])?, up32(&plan.riv_card_off[1])?],
            d_riv_card_pos: [up32(&plan.riv_card_pos[0])?, up32(&plan.riv_card_pos[1])?],
            d_lock_off: stream.clone_htod(&lock_off).map_err(e)?,
            d_lock_sigma: stream.clone_htod(&lock_sigma).map_err(e)?,
            d_regrets: [
                stream.clone_htod(&arena(0, 0)[..]).map_err(e)?,
                stream.clone_htod(&arena(0, 1)[..]).map_err(e)?,
            ],
            d_strat: [
                stream.clone_htod(&arena(1, 0)[..]).map_err(e)?,
                stream.clone_htod(&arena(1, 1)[..]).map_err(e)?,
            ],
            d_reach: [
                stream.alloc_zeros::<f32>(n * nh[0]).map_err(e)?,
                stream.alloc_zeros::<f32>(n * nh[1]).map_err(e)?,
            ],
            d_cfv: stream.alloc_zeros::<f32>(n * plan.nh_max).map_err(e)?,
            d_root_cfv: stream.alloc_zeros::<f32>(plan.nh_max).map_err(e)?,
            d_disc: stream.alloc_zeros::<f32>(3).map_err(e)?,
            graphs: None,
            h_staging: PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?,
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
                let res = self.sweep(p, None);
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
                self.sweep(p, None)?;
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
            self.sweep(p, Some(&mut prof))?;
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
        let mut br = [0f64; 2];
        for p in 0..2 {
            let cfv = self.eval_root_cfv(p, 0)?;
            br[p] = dot(&cfv, p);
        }
        if solver.spot.tree.config.rake_pct > 0.0 {
            // With rake the game is not zero-sum: compare against actual EVs.
            let mut v = [0f64; 2];
            for p in 0..2 {
                let cfv = self.eval_root_cfv(p, 1)?;
                v[p] = dot(&cfv, p);
            }
            Ok(((br[0] - v[0]) + (br[1] - v[1])) / 2.0)
        } else {
            Ok((br[0] + br[1]) / 2.0)
        }
    }

    /// Run one evaluation sweep (mode 0 = best response, 1 = average) for
    /// traverser `p` and return the root counterfactual values.
    fn eval_root_cfv(&mut self, p: usize, mode: i32) -> Result<Vec<f32>, String> {
        self.eval_sweep(p, mode)?;
        let nh_p = self.nh[p];
        unsafe {
            self.stream
                .launch_builder(&self.f_copy_span)
                .arg(&self.d_cfv)
                .arg(&mut self.d_root_cfv)
                .arg(&nh_p)
                .launch(Self::cfg(8, 0))
                .map_err(e)?;
        }
        self.stream.synchronize().map_err(e)?;
        let mut v: Vec<f32> = self.stream.clone_dtoh(&self.d_root_cfv).map_err(e)?;
        v.truncate(nh_p as usize);
        Ok(v)
    }

    fn eval_sweep(&mut self, p: usize, mode: i32) -> Result<(), String> {
        let nh0 = self.nh[0];
        let nh1 = self.nh[1];
        let nh_p = self.nh[p];
        let nh_o = self.nh[1 - p];
        let nh_max = self.nh_max;

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

        let pi = p as i32;
        let show_shared = (self.riv_max_cnt[1 - p] * 12 + nh_o as usize * 4) as u32;
        for l in (0..self.num_levels).rev() {
            let sp = self.fold_spans[l];
            if sp.count > 0 {
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
                        .arg(&self.d_hand_c1[1 - p])
                        .arg(&self.d_hand_c2[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
            }
            let sp = self.show_spans[l];
            if sp.count > 0 {
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
                        .arg(&self.d_riv_str[p])
                        .arg(&self.d_riv_off[1 - p])
                        .arg(&self.d_riv_cnt[1 - p])
                        .arg(&self.d_riv_idx[1 - p])
                        .arg(&self.d_riv_str[1 - p])
                        .arg(&self.d_riv_card_off[1 - p])
                        .arg(&self.d_riv_card_pos[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
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

    fn sweep(&mut self, p: usize, mut prof: Option<&mut Profile>) -> Result<(), String> {
        let nh0 = self.nh[0];
        let nh1 = self.nh[1];
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
                .arg(&nh1)
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
                        .arg(&nh1)
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
                        .arg(&nh1)
                        .launch(Self::cfg(sp.count, 0))
                        .map_err(e)?;
                }
                prof_acc(&self.stream, &mut prof, 2, t0)?;
            }
        }

        let pi = p as i32;
        let show_shared = (self.riv_max_cnt[1 - p] * 12 + nh_o as usize * 4) as u32;
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
                        .arg(&self.d_hand_c1[1 - p])
                        .arg(&self.d_hand_c2[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&mut self.d_cfv)
                        .arg(&nh_p)
                        .arg(&nh_o)
                        .arg(&nh_max)
                        .launch(Self::cfg(sp.count, 0))
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
                        .arg(&self.d_riv_str[p])
                        .arg(&self.d_riv_off[1 - p])
                        .arg(&self.d_riv_cnt[1 - p])
                        .arg(&self.d_riv_idx[1 - p])
                        .arg(&self.d_riv_str[1 - p])
                        .arg(&self.d_riv_card_off[1 - p])
                        .arg(&self.d_riv_card_pos[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
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
            write_arena(solver, false, p, &self.h_staging.as_slice()[..len]);
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            write_arena(solver, true, p, &self.h_staging.as_slice()[..len]);
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
        for p in 0..2 {
            let len = self.d_strat[p].len();
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            write_arena(solver, true, p, &self.h_staging.as_slice()[..len]);
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
        Ok(())
    }
}

/// Cached (not write-combined) page-locked host memory: fast DMA in both
/// directions and normal-speed CPU reads for the encode step.
struct PinnedBuf {
    ptr: *mut f32,
    len: usize,
}

unsafe impl Send for PinnedBuf {}
unsafe impl Sync for PinnedBuf {}

impl PinnedBuf {
    fn new(ctx: &Arc<CudaContext>, len: usize) -> Result<PinnedBuf, String> {
        let _ = ctx; // context must be alive/bound; held by GpuSolver anyway
        let ptr = unsafe { cudarc::driver::result::malloc_host(len * 4, 0) }.map_err(e)?;
        Ok(PinnedBuf {
            ptr: ptr as *mut f32,
            len,
        })
    }
    fn as_slice(&self) -> &[f32] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
    }
    fn as_mut_slice(&mut self) -> &mut [f32] {
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
/// f32 arenas, river tables and slack).
pub fn estimate_vram(spot: &crate::game::Spot) -> u64 {
    let n = spot.tree.nodes.len() as u64;
    let nh0 = spot.hands[0].len() as u64;
    let nh1 = spot.hands[1].len() as u64;
    let nh_max = nh0.max(nh1);
    let staging = n * (nh0 + nh1 + nh_max) * 4;
    let arenas = (spot.tree.data_size[0] + spot.tree.data_size[1]) * 2 * 4;
    staging + arenas + 512 * 1024 * 1024
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
            for (idx, node) in solver.spot.tree.nodes.iter().enumerate() {
                if node.kind == crate::tree::KIND_ACTION && node.player as usize == p {
                    let cnt = node.num_children as usize * nh;
                    let off = node.data_offset as usize;
                    unsafe {
                        store.write_f32(idx as u32, node.data_offset, cnt, &data[off..off + cnt]);
                    }
                }
            }
        }
    }
}
