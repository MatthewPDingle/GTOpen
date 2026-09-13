//! Exact within-traverser CDF reuse. Isolated throughput prototype.
use super::*;
pub(super) struct ExactReuse {
    classify:CudaFunction, cdf:CudaFunction, terminal:CudaFunction,
    table:CudaSlice<u32>, aliases:CudaSlice<u32>,
    aligned:bool,
}
impl PreflopGpu {
    fn exact_reuse_compatible(&self)->bool {
        self.research.is_none() && self.research_cv.is_none() && self.research_behavioral.is_none()
            && self.research_predictive.is_none() && self.research_rm_plus.is_none()
            && self.research_pair_control.is_none() && self.research_exploration.is_none()
            && self.research_history_units.is_none() && self.research_average_opponents.is_none()
            && self.research_normalized_regret.is_none() && !self.research_learning_mask
            && self.research_root_ranges.is_none() && self.use_multiway!=0
            && self.use_mw_normalized && self.use_mw_prepared && self.use_mw_compact!=0
    }
    pub fn enable_research_exact_cdf_reuse(&mut self)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.research_exact_reuse.is_some() || !self.exact_reuse_compatible() {
            return Err("exact CDF reuse requires fresh native compact/normalized engine".into());
        }
        let capacity=self.d_mw_normalized.len()/NUM_CLASSES;
        let table_len=capacity.checked_mul(2).and_then(|v|v.checked_next_power_of_two()).ok_or("reuse capacity overflow")?;
        if capacity==0 || (capacity+table_len)*4>16*1024*1024 {return Err("reuse scratch exceeds 16 MiB research cap".into());}
        let base=include_str!("../kernels.cu");
        let original_cdf=base.split("extern \"C\" __global__ void pf_multiway_cdf(").nth(1).ok_or("CDF source")?
            .split("// Memory-constrained fallback.").next().ok_or("CDF end")?;
        let cdf=format!("extern \"C\" __global__ void pf_exact_reuse_cdf({original_cdf}")
            .replace("u32 batch_capacity)","u32 batch_capacity, const u32* aliases)")
            .replace("    u32 slot = work[start + blockIdx.x];","    if (aliases[blockIdx.x] != blockIdx.x) return;\n    u32 slot = work[start + blockIdx.x];");
        let original_terminal=base.split("extern \"C\" __global__ void pf_multiway_terminal(").nth(1).ok_or("terminal source")?
            .split("// Minimum-memory compatibility entry:").next().ok_or("terminal end")?;
        let terminal=format!("extern \"C\" __global__ void pf_exact_reuse_terminal({original_terminal}")
            .replace("float* val)","float* val, const u32* aliases)")
            .replace("                // Cast before multiplying:","                cdf_slot = aliases[cdf_slot];\n                // Cast before multiplying:");
        if !cdf.contains("const u32* aliases)") || !terminal.contains("cdf_slot = aliases[cdf_slot]") {return Err("source rewrite invariant".into());}
        let source=[base,&cdf,&terminal,include_str!("exact_reuse.cu")].join("\n");
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{
            arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
        let module=self._ctx.load_module(ptx).map_err(e)?;
        let r=ExactReuse{classify:module.load_function("pf_exact_reuse_classify").map_err(e)?,
            cdf:module.load_function("pf_exact_reuse_cdf").map_err(e)?,
            terminal:module.load_function("pf_exact_reuse_terminal").map_err(e)?,
            table:self.stream.alloc_zeros::<u32>(table_len).map_err(e)?,
            aliases:self.stream.alloc_zeros::<u32>(capacity).map_err(e)?,aligned:false};
        self.research_exact_reuse=Some(r);Ok(())
    }
    pub(super) fn exact_reuse_terminals(&mut self,p:i32,gate:i32)->Result<(),String> {
        if !self.exact_reuse_compatible() {return Err("incompatible research state after exact reuse enable".into());}
        let (start,count)=self.mw_spans[p as usize]; if count==0 {return Ok(());}
        let active_count=self.d_mw_active.len() as u32;
        let r=self.research_exact_reuse.as_mut().ok_or("reuse disabled")?;
        let table_count=r.table.len() as u32;let mask=table_count-1;
        unsafe {
            #[cfg(test)]
            super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"prepare",p)?;
            if gate!=0 {
                self.stream.launch_builder(&self.f_multiway_clear_active).arg(&mut self.d_mw_active).arg(&active_count)
                    .launch(LaunchConfig{grid_dim:(active_count.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;
            }
            self.stream.launch_builder(&self.f_multiway_prepare)
                .arg(&self.d_mw_terms).arg(&self.mw_nterms).arg(&p).arg(&self.np)
                .arg(&self.d_live).arg(&self.d_reach_src).arg(&self.d_reach_mass)
                .arg(&self.d_mw_slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob).arg(&gate)
                .launch(LaunchConfig{grid_dim:(self.mw_nterms.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;
            #[cfg(test)]
            super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"normalize",p)?;
            self.stream.launch_builder(&self.f_multiway_normalize)
                .arg(&self.d_mw_work).arg(&start).arg(&self.d_mw_blocks)
                .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                .arg(&self.use_mw_compact).arg(&mut self.d_mw_normalized)
                .launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;
            #[cfg(test)]
            super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"classify",p)?;
            self.stream.launch_builder(&self.f_multiway_clear_active).arg(&mut r.table).arg(&table_count)
                .launch(LaunchConfig{grid_dim:(table_count.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;
            self.stream.launch_builder(&r.classify)
                .arg(&self.d_mw_work).arg(&start).arg(&self.d_mw_blocks).arg(&self.d_reach_mass)
                .arg(&self.d_mw_active).arg(&gate).arg(&self.d_mw_normalized)
                .arg(&mut r.table).arg(&mask).arg(&mut r.aliases)
                .launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(32,1,1),shared_mem_bytes:0}).map_err(e)?;
            let samples=super::super::multiway::SAMPLES as u32;
            for sample_start in (0..samples).step_by(self.mw_batch as usize) {
                let sample_count=self.mw_batch.min(samples-sample_start);
                #[cfg(test)]
                super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"cdf",p)?;
                self.stream.launch_builder(&r.cdf)
                    .arg(&self.d_mw_work).arg(&start).arg(&self.d_mw_blocks).arg(&self.d_mw_order)
                    .arg(&self.d_mw_normalized).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&self.use_mw_compact)
                    .arg(&mut self.d_mw_cdf).arg(&sample_start).arg(&sample_count).arg(&self.mw_batch).arg(&r.aliases)
                    .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).map_err(e)?;
                #[cfg(test)]
                super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"coupled_terminals",p)?;
                self.stream.launch_builder(&r.terminal)
                    .arg(&self.d_mw_terms).arg(&p).arg(&self.np).arg(&self.d_live).arg(&self.d_pots).arg(&self.d_inv)
                    .arg(&self.d_reach_src).arg(&self.d_mw_prob).arg(&self.d_mw_slots).arg(&self.d_mw_compact)
                    .arg(&self.mw_union_slots).arg(&self.use_mw_compact).arg(&self.d_mw_cdf).arg(&self.d_mw_lower).arg(&self.d_mw_upper)
                    .arg(&sample_start).arg(&sample_count).arg(&self.mw_batch).arg(&samples)
                    .arg(&self.d_val_slot).arg(&mut self.d_val).arg(&r.aliases)
                    .launch(LaunchConfig{block_dim:(192,1,1),..Self::cfg(self.mw_nterms)}).map_err(e)?;
            }
        }
        Ok(())
    }
}
#[cfg(test)]
mod tests;

mod aligned;
