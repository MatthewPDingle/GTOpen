//! CUDA engine for the preflop solver: level-synchronous CFR mirroring the
//! CPU traversal exactly (validated by tests/preflop_gpu.rs on a GPU
//! machine). Built blind on a laptop — every deviation from the CPU math is
//! a bug by definition; keep the two in lockstep.
//!
//! Falls back cleanly: `PreflopGpu::new` errors when the game exceeds the
//! VRAM budget or CUDA is unavailable, and the server then solves on the
//! CPU + system RAM instead.

use super::{PreflopSolver, KIND_ACTION};
use crate::preflop::equity::{class_prob, NUM_CLASSES};
use cudarc::driver::{CudaContext, CudaFunction, CudaSlice, CudaStream, LaunchConfig, PushKernelArg};
use std::sync::Arc;

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
    d_eq: CudaSlice<f32>,
    d_cprob: CudaSlice<f32>,
    d_act_nodes: CudaSlice<u32>,
    d_terms: CudaSlice<u32>,
    // mutable state
    d_regrets: CudaSlice<f32>,
    d_strat: CudaSlice<f32>,
    d_sigma: CudaSlice<f32>,
    d_reach: CudaSlice<f32>,
    d_val: CudaSlice<f32>,
    // level spans into d_act_nodes: (start, count) top-down
    spans: Vec<(u32, u32)>,
    nterms: u32,
    np: i32,
    arena_len: usize,
}

/// VRAM the engine would need for this game, in MB.
pub fn vram_estimate_mb(s: &PreflopSolver) -> f64 {
    let n = s.nodes.len() as f64;
    let np = s.n as f64;
    let nc = NUM_CLASSES as f64;
    let arena = s.arena_len as f64;
    // reach + val + regrets/strat/sigma + tree arrays + slack
    (n * np * nc * 4.0 + n * nc * 4.0 + 3.0 * arena * 4.0 + n * (np * 8.0 + 40.0)) / 1e6 + 64.0
}

impl PreflopGpu {
    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        let need = vram_estimate_mb(s);
        if need > budget_mb as f64 {
            return Err(format!(
                "needs ~{need:.0} MB VRAM (budget {budget_mb} MB)"
            ));
        }
        if s.nodes.iter().any(|nd| nd.actions.len() > MAX_NA) {
            return Err("a node has more than 16 actions".into());
        }

        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
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
        let mut terms: Vec<u32> = Vec::new();
        for (i, nd) in s.nodes.iter().enumerate() {
            kind[i] = nd.kind as i32;
            actor[i] = nd.actor as i32;
            na[i] = nd.actions.len() as i32;
            off[i] = nd.data_off as u32;
            cstart[i] = nd.child_start;
            live[i] = nd.live as i32;
            winner[i] = nd.winner as i32;
            let rake = (nd.pot * s.cfg.rake_pct / 100.0).min(s.cfg.rake_cap);
            potf[i] = if s.cfg.no_flop_no_drop {
                nd.pot as f32
            } else {
                (nd.pot - rake) as f32
            };
            pots[i] = (nd.pot - rake) as f32;
            for q in 0..np {
                inv[i * np + q] = nd.invested[q] as f32;
                rw[i * np + q] = if nd.r.is_empty() { 0.0 } else { nd.r[q] };
            }
            if nd.kind != KIND_ACTION {
                terms.push(i as u32);
            }
        }

        // levels: BFS depth over action-node children, top-down spans
        let mut depth = vec![u32::MAX; n];
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

        // equity table + class probabilities
        let mut eq = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for i in 0..NUM_CLASSES {
            for j in 0..NUM_CLASSES {
                eq[i * NUM_CLASSES + j] = s.eq.eq(i, j);
            }
        }
        let cprob: Vec<f32> = (0..NUM_CLASSES).map(class_prob).collect();

        let arena_len = s.arena_len;
        // SAFETY: exclusive access (no solve is running while we construct)
        let (regs, strat) = unsafe { (s.regrets.slice(), s.strat_sum.slice()) };

        println!(
            "preflop gpu: {n} nodes, {} levels, {} terminals, ~{need:.0} MB VRAM",
            spans.len(),
            terms.len()
        );

        Ok(PreflopGpu {
            f_init: func("pf_init_root")?,
            f_down: func("pf_down")?,
            f_terminal: func("pf_terminal")?,
            f_up: func("pf_up")?,
            f_discount: func("pf_discount")?,
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
            d_eq: stream.clone_htod(&eq).map_err(e)?,
            d_cprob: stream.clone_htod(&cprob).map_err(e)?,
            d_act_nodes: stream.clone_htod(&act_nodes).map_err(e)?,
            d_terms: stream.clone_htod(&terms).map_err(e)?,
            d_regrets: stream.clone_htod(&regs.to_vec()).map_err(e)?,
            d_strat: stream.clone_htod(&strat.to_vec()).map_err(e)?,
            d_sigma: stream.alloc_zeros::<f32>(arena_len.max(1)).map_err(e)?,
            d_reach: stream
                .alloc_zeros::<f32>(n * np * NUM_CLASSES)
                .map_err(e)?,
            d_val: stream.alloc_zeros::<f32>(n * NUM_CLASSES).map_err(e)?,
            spans,
            nterms: terms.len() as u32,
            np: np as i32,
            arena_len,
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
                    .arg(&mut self.d_sigma)
                    .arg(&mut self.d_reach)
                    .arg(&self.np)
                    .arg(&mode)
                    .launch(Self::cfg(count as u32))
                    .map_err(e)?;
            }
        }
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
                .arg(&self.d_eq)
                .arg(&self.d_reach)
                .arg(&mut self.d_val)
                .launch(Self::cfg(self.nterms))
                .map_err(e)?;
        }
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
                    .arg(&self.d_sigma)
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
        for p in 0..self.np {
            self.sweep(p, 0)?;
        }
        s.iteration += 1;
        let t = s.iteration as f64;
        let pos = (t.powf(1.5) / (t.powf(1.5) + 1.0)) as f32;
        let neg = 0.5f32;
        let sd = ((t / (t + 1.0)).powi(2)) as f32;
        let len = self.arena_len as u32;
        unsafe {
            self.stream
                .launch_builder(&self.f_discount)
                .arg(&mut self.d_regrets)
                .arg(&mut self.d_strat)
                .arg(&len)
                .arg(&pos)
                .arg(&neg)
                .arg(&sd)
                .launch(Self::cfg(256))
                .map_err(e)?;
        }
        self.stream.synchronize().map_err(e)?;
        Ok(())
    }

    /// Root values for traverser p under `mode`, combined into a scalar EV.
    fn root_ev(&mut self, p: i32, mode: i32) -> Result<f64, String> {
        self.sweep(p, mode)?;
        let v: Vec<f32> = self.stream.clone_dtoh(&self.d_val).map_err(e)?;
        let mut total = 0f64;
        for h in 0..NUM_CLASSES {
            total += class_prob(h) as f64 * v[h] as f64; // node 0's block
        }
        Ok(total)
    }

    /// Per-player best-response gaps and average-strategy EVs (bb).
    pub fn gaps_and_evs(&mut self) -> Result<(Vec<f64>, Vec<f64>), String> {
        let mut gaps = Vec::new();
        let mut evs = Vec::new();
        for p in 0..self.np {
            let br = self.root_ev(p, 2)?;
            let avg = self.root_ev(p, 1)?;
            gaps.push(br - avg);
            evs.push(avg);
        }
        Ok((gaps, evs))
    }

    /// Copy the arenas back so node_view/export/browse see the GPU solve.
    pub fn sync_to_cpu(&self, s: &mut PreflopSolver) -> Result<(), String> {
        let regs: Vec<f32> = self.stream.clone_dtoh(&self.d_regrets).map_err(e)?;
        let strat: Vec<f32> = self.stream.clone_dtoh(&self.d_strat).map_err(e)?;
        // SAFETY: &mut PreflopSolver → no concurrent traversal
        unsafe {
            s.regrets.slice_mut().copy_from_slice(&regs);
            s.strat_sum.slice_mut().copy_from_slice(&strat);
        }
        Ok(())
    }
}

// silence unused warnings for tree buffers only read by kernels
impl PreflopGpu {
    #[allow(dead_code)]
    fn _keep(&self) -> usize {
        self.d_kind.len() + self.d_winner.len()
    }
}
