//! CUDA engine for the preflop solver: level-synchronous CFR mirroring the
//! CPU traversal exactly (validated by tests/preflop_gpu.rs on a GPU
//! machine). Built blind on a laptop — every deviation from the CPU math is
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

const BLOCK: u32 = 256; // power of two >= 169 (the terminal reduction relies on it)
const MAX_NA: usize = 16;

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
    n_act: u32,
    // mutable state
    d_regrets: CudaSlice<f32>,
    d_strat: CudaSlice<f32>,
    d_sigma: CudaSlice<f32>,
    d_reach_src: CudaSlice<u32>,
    d_reach: CudaSlice<f32>,
    d_reach_mass: CudaSlice<f32>,
    d_val: CudaSlice<f32>,
    // level spans into d_act_nodes: (start, count) top-down
    spans: Vec<(u32, u32)>,
    nterms: u32,
    np: i32,
    arena_len: usize,
    learning_graphs: Vec<Option<CudaGraph>>,
    warmed: bool,
    h_snapshot: Mutex<Option<PinnedBuf>>,
}

fn minimum_vram_mb(s: &PreflopSolver) -> f64 {
    let n = s.nodes.len() as f64;
    let np = s.n as f64;
    let nc = NUM_CLASSES as f64;
    let arena = s.arena_len as f64;
    // One root reach per seat, then one actor reach per action edge.
    // Other seats alias their nearest written ancestor through reach_src.
    ((n + np - 1.0) * (nc + 1.0) * 4.0 + n * nc * 4.0 + 3.0 * arena * 4.0
        + n * (np * 12.0 + 40.0)) / 1e6 + 64.0
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
        let nblocks = s.nodes.len() + s.n - 1;
        let mut needed = vec![vec![false; nblocks]; s.n];
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind != KIND_POT_SHARE { continue; }
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
        Self { slots, blocks, work, spans }
    }
    fn bytes(&self) -> usize {
        (self.slots.len() + self.blocks.len() + self.work.len()
            + self.blocks.len() * NUM_CLASSES) * 4
    }
    fn disabled(np: usize) -> Self {
        Self { slots: vec![0], blocks: vec![0], work: vec![0], spans: vec![(0, 0); np + 1] }
    }
}

/// Preferred VRAM including the exact-equity cache, in MB. The constructor
/// can omit that optional cache to fit a smaller budget without changing results.
pub fn vram_estimate_mb(s: &PreflopSolver) -> f64 {
    let sources = reach_sources(s);
    minimum_vram_mb(s) + EquityCachePlan::build(s, &sources).bytes() as f64 / 1e6
}

impl PreflopGpu {
    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        let mut need = minimum_vram_mb(s);
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
                "arenas have {} entries — beyond the GPU engine's 32-bit arena indexing; solving on CPU",
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
        let reach_blocks = n.checked_add(np - 1)
            .filter(|&len| len <= u32::MAX as usize)
            .ok_or_else(|| "reach table beyond 32-bit block indexing; solving on CPU".to_string())?;

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
        let static_seats: Vec<bool> = (0..np).map(|p| s.seat_static(p)).collect();
        let n_forced = src.iter().filter(|&&x| x == 2).count();
        let n_frozen = src.iter().filter(|&&x| x == 1).count();

        // levels: BFS depth over action-node children, top-down spans
        let mut depth = vec![u32::MAX; n];
        let reach_src = reach_sources(s);
        depth[0] = 0;
        let mut maxd = 0u32;
        // nodes are created parent-before-child by the recursive builder, so
        // a single forward pass assigns every depth
        for i in 0..n {
            if depth[i] == u32::MAX || s.nodes[i].kind != KIND_ACTION {
                continue;
            }
            let d = depth[i];
            maxd = maxd.max(d + 1);
            for a in 0..s.nodes[i].actions.len() {
                let c = s.child(i, a);
                depth[c] = d + 1;
            }
        }
        let mut act_nodes: Vec<u32> = Vec::new();
        let mut spans: Vec<(u32, u32)> = Vec::new();
        for d in 0..=maxd {
            let start = act_nodes.len() as u32;
            for i in 0..n {
                if depth[i] == d && s.nodes[i].kind == KIND_ACTION {
                    act_nodes.push(i as u32);
                }
            }
            spans.push((start, act_nodes.len() as u32 - start));
        }

        let mut eq_plan = EquityCachePlan::build(s, &reach_src);
        let use_eq_cache = !eq_plan.blocks.is_empty()
            && need + eq_plan.bytes() as f64 / 1e6 <= budget_mb as f64;
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
        println!(
            "preflop gpu: {n} nodes, {} levels, {} terminals ({ncalib} calibrated), \
             {n_forced} forced + {n_frozen} frozen nodes, ~{need:.0} MB VRAM",
            spans.len(),
            terms.len()
        );

        Ok(PreflopGpu {
            f_init: func("pf_init_root")?,
            f_down: func("pf_down")?,
            f_terminal: func("pf_terminal")?,
            f_reach_mass: func("pf_reach_mass")?,
            f_equities: func("pf_equities")?,
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
            d_cprob: stream.clone_htod(&cprob).map_err(e)?,
            n_act: act_nodes.len() as u32,
            d_act_nodes: stream.clone_htod(&act_nodes).map_err(e)?,
            d_terms: stream.clone_htod(&terms).map_err(e)?,
            d_src: stream.clone_htod(&src).map_err(e)?,
            d_foff: stream.clone_htod(&foff).map_err(e)?,
            d_forced: if forced.is_empty() {
                stream.alloc_zeros::<f32>(1).map_err(e)?
            } else {
                stream.clone_htod(&forced).map_err(e)?
            },
            static_seats,
            d_regrets: stream.clone_htod(regs).map_err(e)?,
            d_strat: stream.clone_htod(strat).map_err(e)?,
            d_sigma: stream.alloc_zeros::<f32>(arena_len.max(1)).map_err(e)?,
            d_reach_src: stream.clone_htod(&reach_src).map_err(e)?,
            d_reach: stream
                .alloc_zeros::<f32>(reach_blocks * NUM_CLASSES)
                .map_err(e)?,
            d_reach_mass: stream.alloc_zeros::<f32>(reach_blocks).map_err(e)?,
            d_val: stream.alloc_zeros::<f32>(n * NUM_CLASSES).map_err(e)?,
            spans,
            nterms: terms.len() as u32,
            np: np as i32,
            arena_len,
            learning_graphs: (0..np).map(|_| None).collect(),
            warmed: false,
            h_snapshot: Mutex::new(None),
            _ctx: ctx,
            stream,
        })
    }

    fn cfg(blocks: u32) -> LaunchConfig {
        LaunchConfig {
            grid_dim: (blocks.max(1), 1, 1),
            block_dim: (BLOCK, 1, 1),
            shared_mem_bytes: 0,
        }
    }

    /// One full pass for traverser `p`. mode 0 updates regrets/strategy;
    /// 1 evaluates the average strategy; 2 is best response vs average.
    fn sweep(&mut self, p: i32, mode: i32) -> Result<(), String> {
        self.down(mode, p)?;
        self.terminals(p)?;
        self.up(p, mode)
    }

    /// Reach and sigma depend on the strategy source, not the traverser.
    /// Evaluation modes 1 and 2 both use the same average strategy.
    fn down(&mut self, mode: i32, p: i32) -> Result<(), String> {
        unsafe {
            self.stream
                .launch_builder(&self.f_init)
                .arg(&self.d_cprob)
                .arg(&mut self.d_reach)
                .arg(&self.np)
                .launch(Self::cfg(4))
                .map_err(e)?;
        }
        for li in 0..self.spans.len() {
            let (start, count) = self.spans[li];
            if count == 0 {
                continue;
            }
            let (start, count) = (start as i32, count as i32);
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
                    .arg(&self.d_regrets)
                    .arg(&self.d_strat)
                    .arg(&self.d_src)
                    .arg(&self.d_foff)
                    .arg(&self.d_forced)
                    .arg(&mut self.d_sigma)
                    .arg(&self.d_reach_src)
                    .arg(&mut self.d_reach)
                    .arg(&self.np)
                    .arg(&mode)
                    .launch(Self::cfg(count as u32))
                    .map_err(e)?;
            }
        }
        let blocks = self.d_reach_mass.len() as u32;
        unsafe {
            self.stream.launch_builder(&self.f_reach_mass)
                .arg(&self.d_reach)
                .arg(&mut self.d_reach_mass)
                .launch(Self::cfg(blocks))
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
                .arg(&mut self.d_val)
                .launch(Self::cfg(self.nterms))
                .map_err(e)?;
        }
        Ok(())
    }

    /// Only action-node values are overwritten. Terminal values, reach and
    /// sigma stay available for another read-only evaluation of this seat.
    fn up(&mut self, p: i32, mode: i32) -> Result<(), String> {
        for li in (0..self.spans.len()).rev() {
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
                    .arg(&self.d_sigma)
                    .arg(&self.d_reach_src)
                    .arg(&self.d_reach)
                    .arg(&mut self.d_regrets)
                    .arg(&mut self.d_strat)
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
        let stopped = || stop.map_or(false, |f| f.load(Ordering::Relaxed));
        for p in 0..self.np {
            if self.static_seats[p as usize] {
                continue; // frozen / fully ruled: its own pass writes nothing
            }
            if stopped() {
                self.stream.synchronize().map_err(e)?;
                return Ok(false);
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
        s.iteration += 1;
        let t = s.iteration as f64;
        let pos = (t.powf(1.5) / (t.powf(1.5) + 1.0)) as f32;
        let neg = 0.5f32;
        let sd = ((t / (t + 1.0)).powi(2)) as f32;
        // per action node (not flat over the arena): a frozen actor's
        // strategy sums are its play and must not decay — same rule as the
        // CPU's iterate()
        let n_act = self.n_act as i32;
        unsafe {
            self.stream
                .launch_builder(&self.f_discount)
                .arg(&self.d_act_nodes)
                .arg(&n_act)
                .arg(&self.d_na)
                .arg(&self.d_off)
                .arg(&self.d_src)
                .arg(&mut self.d_regrets)
                .arg(&mut self.d_strat)
                .arg(&pos)
                .arg(&neg)
                .arg(&sd)
                .launch(Self::cfg(self.n_act))
                .map_err(e)?;
        }
        self.stream.synchronize().map_err(e)?;
        self.warmed = true;
        Ok(true)
    }

    /// Combine the last sweep's root values into a scalar EV.
    fn root_ev(&self) -> Result<f64, String> {
        // node 0's block only — d_val is nodes x 169 and copying it whole
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
        // All 2*np evaluations use the same average-strategy reach/sigma.
        // For each seat BR and average also share the same terminal values;
        // only their bottom-up action aggregation differs. Nothing here
        // updates regrets or strategy, so this reuse is exact.
        self.down(1, -1)?;
        let mut gaps = Vec::with_capacity(self.np as usize);
        let mut evs = Vec::with_capacity(self.np as usize);
        for p in 0..self.np {
            self.terminals(p)?;
            self.up(p, 2)?;
            let br = self.root_ev()?;
            self.up(p, 1)?;
            let avg = self.root_ev()?;
            gaps.push(br - avg);
            evs.push(avg);
        }
        Ok((gaps, evs))
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
        // SAFETY: &mut PreflopSolver → no concurrent traversal
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{BucketPolicy, PreflopConfig, SeatProfile, NUM_BUCKETS};

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
        let mut s = PreflopSolver::new(cfg, eq).unwrap();
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
        let mut a = PreflopSolver::new(cfg.clone(), eq.clone()).unwrap();
        let mut b = PreflopSolver::new(cfg, eq).unwrap();
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
            gpu.sweep(p, 2).unwrap();
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
                let mut s = PreflopSolver::new(cfg, eq.clone()).unwrap();
                if realization == "calibrated" {
                    assert!(s.fit.is_some(), "test requires the calibrated fit");
                }
                assert_cached_evaluation(&mut s);

                s.lock_point(&[], None).unwrap();
                let mut buckets = vec![None; NUM_BUCKETS];
                buckets[super::super::BUCKET_VS_RAISE as usize] = Some(BucketPolicy {
                    call: vec![0.5; NUM_CLASSES], raise: vec![0.1; NUM_CLASSES],
                    jam: vec![0.0; NUM_CLASSES], raise_size: "max".into(),
                });
                let mut profiles = vec![None; n];
                profiles[1] = Some(SeatProfile {
                    name: "test profile".into(), buckets, vs_raise_bands: None,
                    postflop: None, limp_defense: None,
                });
                s.set_table(vec![false; n], profiles).unwrap();
                assert_cached_evaluation(&mut s);

                // Includes the bleed measurement of seats frozen by hero
                // mode, not just the seats whose strategies are learning.
                s.set_hero(Some(0)).unwrap();
                assert_cached_evaluation(&mut s);
            }
        }
    }
}
