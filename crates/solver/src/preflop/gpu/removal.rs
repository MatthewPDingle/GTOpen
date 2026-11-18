//! Blockers (card removal) on the GPU: three kernels around the ordinary
//! terminal pass (removal.cu). The CPU reference is
//! `removal_terminal_value` in preflop/removal.rs.
use super::*;

pub(super) struct RemovalGpu {
    pub(super) f_rank_mass: CudaFunction,
    pub(super) f_heads_up: CudaFunction,
    pub(super) f_scale: CudaFunction,
    /// 13 per-rank masses per reach block.
    pub(super) d_rank_mass: CudaSlice<f32>,
    /// The equity tables (as `d_eq`), each entry times its removal weight.
    pub(super) d_eq_w: CudaSlice<f32>,
    /// Heads-up single-pot pot-share terminals.
    pub(super) d_hu_terms: CudaSlice<u32>,
    pub(super) hu_count: u32,
}

/// Heads-up pot-share terminals without side pots, the ones the CPU prices
/// with the opponent's range conditioned on the hero's cards.
fn heads_up_terminals(s: &PreflopSolver) -> Vec<u32> {
    s.nodes.iter().enumerate()
        .filter(|(_, nd)| nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 2 && nd.side_pots.is_empty())
        .map(|(i, _)| i as u32)
        .collect()
}

impl RemovalGpu {
    /// Device bytes, for the VRAM estimate.
    pub(super) fn bytes(s: &PreflopSolver, reach_blocks: usize, eq_len: usize) -> usize {
        if !s.cfg.card_removal {
            return 0;
        }
        reach_blocks * 13 * 4 + eq_len * 4 + heads_up_terminals(s).len() * 4
    }

    /// `eq` is the host copy of the equity tables as uploaded to `d_eq`
    /// (channels x 169 x 169, opponent class major).
    pub(super) fn new(
        ctx: &Arc<CudaContext>, stream: &Arc<CudaStream>, s: &PreflopSolver, arch: &'static str,
        reach_blocks: usize, eq: &[f32],
    ) -> Result<Option<Self>, String> {
        if !s.cfg.card_removal {
            return Ok(None);
        }
        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> = std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("removal.cu"),
                    cudarc::nvrtc::CompileOptions { arch: Some(arch), ..Default::default() },
                )
                .map_err(e)
            })
            .clone()?;
        let module = ctx.load_module(ptx).map_err(e)?;
        let w = crate::preflop::removal::weights();
        let mut eq_w = eq.to_vec();
        for (k, value) in eq_w.iter_mut().enumerate() {
            let (j, h) = ((k / NUM_CLASSES) % NUM_CLASSES, k % NUM_CLASSES);
            *value *= w[h * NUM_CLASSES + j];
        }
        let mut hu = heads_up_terminals(s);
        let hu_count = hu.len() as u32;
        if hu.is_empty() {
            hu.push(0);
        }
        Ok(Some(Self {
            f_rank_mass: module.load_function("pf_removal_rank_mass").map_err(e)?,
            f_heads_up: module.load_function("pf_removal_heads_up").map_err(e)?,
            f_scale: module.load_function("pf_removal_scale").map_err(e)?,
            d_rank_mass: stream.alloc_zeros::<f32>(reach_blocks * 13).map_err(e)?,
            d_eq_w: stream.clone_htod(&eq_w).map_err(e)?,
            d_hu_terms: stream.clone_htod(&hu).map_err(e)?,
            hu_count,
        }))
    }
}

impl PreflopGpu {
    /// Per-rank masses of the current reach, and the heads-up showdowns
    /// repriced against the conditioned opponent range. Runs right after
    /// pf_terminal, before the kernels that add to its values.
    pub(super) fn removal_heads_up(&mut self, p: i32) -> Result<(), String> {
        let Some(r) = &mut self.removal else { return Ok(()) };
        let blocks = self.d_reach_mass.len() as u32;
        unsafe {
            self.stream.launch_builder(&r.f_rank_mass)
                .arg(&self.d_reach).arg(&blocks).arg(&mut r.d_rank_mass)
                .launch(LaunchConfig { grid_dim: (blocks.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 })
                .map_err(e)?;
            if r.hu_count > 0 {
                let count = r.hu_count as i32;
                self.stream.launch_builder(&r.f_heads_up)
                    .arg(&r.d_hu_terms).arg(&count).arg(&p).arg(&self.np)
                    .arg(&self.d_live).arg(&self.d_pots).arg(&self.d_inv).arg(&self.d_rw)
                    .arg(&self.d_potg).arg(&self.d_calib).arg(&self.d_cbase)
                    .arg(&self.clip_lo).arg(&self.clip_hi)
                    .arg(&r.d_eq_w)
                    .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&r.d_rank_mass)
                    .arg(&self.d_eq_slots).arg(&self.d_eq_cache).arg(&self.use_eq_cache).arg(&self.eq_cache_stride)
                    .arg(&self.d_val_slot).arg(&mut self.d_val)
                    .launch(LaunchConfig { grid_dim: (r.hu_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 })
                    .map_err(e)?;
            }
        }
        Ok(())
    }

    /// Rescale every terminal from the plain reach product to each class's
    /// own conditioned one. Runs after every other terminal kernel.
    pub(super) fn removal_scale(&mut self, p: i32) -> Result<(), String> {
        let Some(r) = &self.removal else { return Ok(()) };
        let count = self.nterms as i32;
        unsafe {
            self.stream.launch_builder(&r.f_scale)
                .arg(&self.d_terms).arg(&count).arg(&p).arg(&self.np)
                .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&r.d_rank_mass)
                .arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(LaunchConfig { grid_dim: (self.nterms, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 })
                .map_err(e)?;
        }
        Ok(())
    }
}
