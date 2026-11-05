//! ICM payoffs on the GPU. Before each traverser's terminal pass,
//! `pf_icm_prepare` (icm.cu) rewrites that traverser's pot amounts and
//! investments so the chip-EV terminal kernels return ICM values; see
//! `IcmTables` in preflop/icm.rs for the model and the CPU reference.
use super::*;

pub(super) struct IcmGpu {
    f_prepare: CudaFunction,
    count: u32,
    d_nodes: CudaSlice<u32>,
    d_kinds: CudaSlice<i32>,
    d_pot_start: CudaSlice<u32>,
    d_masks: CudaSlice<u32>,
    d_sp_base: CudaSlice<u32>,
    d_out_start: CudaSlice<u32>,
    d_winners: CudaSlice<u32>,
    d_values: CudaSlice<f32>,
    d_bal: CudaSlice<f32>,
}

impl IcmGpu {
    /// Device bytes the tables need, for the VRAM estimate.
    pub(super) fn bytes(s: &PreflopSolver) -> usize {
        let Some(t) = s.icm.as_ref() else { return 0 };
        let summary = s.icm_summary().map_or(0, |x| x.outcomes);
        let terms = t.terminal_count();
        terms * 20 + summary * (4 + 4 * s.n) + terms * 8 * 4 + NUM_CLASSES * NUM_CLASSES * 4
    }

    /// `sp_terms`/`sp_start` are the side-pot list as uploaded, so each
    /// side-pot terminal knows where its amounts start.
    pub(super) fn new(
        ctx: &Arc<CudaContext>, stream: &Arc<CudaStream>, s: &PreflopSolver, arch: &'static str,
        sp_terms: &[u32], sp_start: &[u32], sp_count: usize,
    ) -> Result<Option<Self>, String> {
        let Some(tables) = s.icm.as_ref() else { return Ok(None) };
        let flat = tables.flat(s).ok_or("an ICM terminal has more than eight pots")?;
        let mut sp_pos = std::collections::HashMap::new();
        for i in 0..sp_count {
            sp_pos.insert(sp_terms[i], sp_start[i]);
        }
        let mut sp_base = Vec::with_capacity(flat.nodes.len());
        for (t, &node) in flat.nodes.iter().enumerate() {
            sp_base.push(if flat.kinds[t] == 2 {
                *sp_pos.get(&node).ok_or("side-pot terminal missing from the GPU side-pot list")?
            } else {
                0
            });
        }
        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> = std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("icm.cu"),
                    cudarc::nvrtc::CompileOptions { arch: Some(arch), ..Default::default() },
                )
                .map_err(e)
            })
            .clone()?;
        let module = ctx.load_module(ptx).map_err(e)?;
        let nonempty = |v: &[u32]| if v.is_empty() { vec![0u32] } else { v.to_vec() };
        Ok(Some(Self {
            f_prepare: module.load_function("pf_icm_prepare").map_err(e)?,
            count: flat.nodes.len() as u32,
            d_nodes: stream.clone_htod(&nonempty(&flat.nodes)).map_err(e)?,
            d_kinds: stream.clone_htod(if flat.kinds.is_empty() { &[0i32][..] } else { &flat.kinds }).map_err(e)?,
            d_pot_start: stream.clone_htod(&flat.pot_start).map_err(e)?,
            d_masks: stream.clone_htod(&nonempty(&flat.masks)).map_err(e)?,
            d_sp_base: stream.clone_htod(&nonempty(&sp_base)).map_err(e)?,
            d_out_start: stream.clone_htod(&flat.out_start).map_err(e)?,
            d_winners: stream.clone_htod(&nonempty(&flat.winners)).map_err(e)?,
            d_values: stream.clone_htod(if flat.values.is_empty() { &[0f32][..] } else { &flat.values }).map_err(e)?,
            d_bal: stream.clone_htod(&flat.bal).map_err(e)?,
        }))
    }
}

impl PreflopGpu {
    /// Point traverser p's terminal money at its ICM coefficients.
    pub(super) fn icm_prepare(&mut self, p: i32) -> Result<(), String> {
        let Some(icm) = &self.icm else { return Ok(()) };
        if icm.count == 0 {
            return Ok(());
        }
        unsafe {
            self.stream
                .launch_builder(&icm.f_prepare)
                .arg(&icm.count).arg(&p).arg(&self.np)
                .arg(&icm.d_nodes).arg(&icm.d_kinds).arg(&icm.d_pot_start).arg(&icm.d_masks)
                .arg(&icm.d_sp_base).arg(&icm.d_out_start).arg(&icm.d_winners).arg(&icm.d_values)
                .arg(&icm.d_bal).arg(&self.d_live)
                .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass)
                .arg(&mut self.d_pots).arg(&mut self.d_potg).arg(&mut self.d_inv).arg(&mut self.d_sp_amount)
                .launch(LaunchConfig { grid_dim: (icm.count, 1, 1), block_dim: (128, 1, 1), shared_mem_bytes: 0 })
                .map_err(e)?;
        }
        Ok(())
    }
}
