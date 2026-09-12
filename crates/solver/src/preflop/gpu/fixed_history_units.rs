//! Internal research representation. No public resume or branch ownership API.
use super::*;

pub(super) struct FixedHistoryUnits {
    function:CudaFunction,
    regret:CudaSlice<f32>,
    average:CudaSlice<f32>,
}

impl PreflopGpu {
    /// All validation/allocation precedes publishing state; stored histories never change here.
    pub(crate) fn research_set_history_units(&mut self,regret:&[f32],average:&[f32],extra_bytes:usize)->Result<usize,String> {
        if self.research_rm_plus.is_some() || self.warmed || self.eval_warmed || self.research_history_units.is_some() || self.research.is_some()
            || self.research_root_ranges.is_some() || self.research_learning_mask || self.research_cv.is_some()
            || self.research_normalized_regret.is_some() || self.research_pair_control.is_some() || self.research_exploration.is_some() {
            return Err("fixed history units require a fresh full native research engine".into());
        }
        let n=self.d_src.len();let bytes=n.checked_mul(8).ok_or("history unit size overflow")?;
        if regret.len()!=n || average.len()!=n || bytes>extra_bytes
            || regret.iter().chain(average).any(|v|!v.is_finite() || !(1e-8..=1.0).contains(v)) {
            return Err("invalid history unit dimensions, bounds or extra-memory budget".into());
        }
        let sources=self.stream.clone_dtoh(&self.d_src).map_err(e)?;
        let kinds=self.stream.clone_dtoh(&self.d_kind).map_err(e)?;
        for i in 0..n {
            if (sources[i]!=0 || kinds[i]!=KIND_ACTION as i32) && (regret[i]!=1.0 || average[i]!=1.0) {
                return Err("fixed and terminal nodes require unit-one metadata".into());
            }
        }
        let source=[include_str!("../kernels.cu"),include_str!("fixed_history_units.cu")].join("\n");
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?).map_err(e)?;
        let function=module.load_function("pf_up_fixed_history_units").map_err(e)?;
        let regret=self.stream.clone_htod(regret).map_err(e)?;
        let average=self.stream.clone_htod(average).map_err(e)?;
        self.research_history_units=Some(FixedHistoryUnits{function,regret,average});
        Ok(bytes)
    }

    pub(super) fn research_fixed_units_up(&mut self,p:i32,li:usize)->Result<bool,String> {
        let Some(u)=&self.research_history_units else {return Ok(false)};
        let (start,count)=self.spans[li];if count==0 {return Ok(true);}
        let (start,count)=(start as i32,count as i32);
        unsafe {
            self.stream.launch_builder(&u.function).arg(&self.d_act_nodes).arg(&start).arg(&count)
                .arg(&p).arg(&self.np).arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off)
                .arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src).arg(&self.d_foff)
                .arg(&self.d_forced).arg(&self.d_reach_src).arg(&self.d_reach).arg(&u.regret).arg(&u.average)
                .arg(&mut self.d_regrets).arg(&mut self.d_strat).arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(true)
    }
}
