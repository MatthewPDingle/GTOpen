//! Fixed behavioral perturbation: research only, with canonical evaluation.
use super::*;

pub(super) struct Behavioral { epsilon:f32, down:CudaFunction, up:CudaFunction }

impl PreflopGpu {
    /// No changing-epsilon history transfer is implemented or implied.
    pub fn enable_research_behavioral_perturbation(&mut self,epsilon:f32)->Result<(),String>{
        if !epsilon.is_finite() || !(0.0..=0.2).contains(&epsilon) || self.research.is_none()
            || self.warmed || self.eval_warmed || self.research_behavioral.is_some()
            || self.research_cv.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some()
            || self.research_pair_control.is_some() || self.research_normalized_regret.is_some()
            || self.research_exploration.is_some() || self.research_history_units.is_some()
            || self.research_average_opponents.is_some() || self.research_learning_mask || self.research_root_ranges.is_some(){
            return Err("fixed behavioral perturbation requires fresh configured uncombined engine and epsilon in [0,0.2]".into());
        }
        let source=[include_str!("../kernels.cu"),include_str!("behavioral.cu")].join("\n");
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?).map_err(e)?;
        self.research_behavioral=Some(Behavioral{epsilon,down:module.load_function("behavioral_reach").map_err(e)?,
            up:module.load_function("behavioral_up").map_err(e)?});Ok(())
    }
    pub(super) fn research_behavioral_reach(&mut self,start:i32,count:i32,mode:i32)->Result<(),String>{
        let Some(b)=&self.research_behavioral else{return Ok(())};
        if mode!=0 || b.epsilon==0.0{return Ok(())}
        unsafe{self.stream.launch_builder(&b.down).arg(&self.d_act_nodes).arg(&start).arg(&count).arg(&self.np)
            .arg(&self.d_actor).arg(&self.d_na).arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src)
            .arg(&self.d_reach_src).arg(&b.epsilon).arg(&mut self.d_reach).launch(Self::cfg(count as u32)).map_err(e)?;}
        Ok(())
    }
    pub(super) fn research_behavioral_up(&mut self,p:i32,li:usize,mode:i32)->Result<bool,String>{
        let Some(b)=&self.research_behavioral else{return Ok(false)};
        if mode!=4 && (mode!=0 || b.epsilon==0.0){return Ok(false)}
        let (start,count)=self.spans[li];if count==0{return Ok(true)}
        let (start,count)=(start as i32,count as i32);
        unsafe{self.stream.launch_builder(&b.up).arg(&self.d_act_nodes).arg(&start).arg(&count)
            .arg(&p).arg(&self.np).arg(&mode).arg(&b.epsilon).arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off)
            .arg(&self.d_cstart).arg(&self.d_children).arg(&self.d_src).arg(&self.d_foff).arg(&self.d_forced)
            .arg(&self.d_reach_src).arg(&self.d_reach).arg(&mut self.d_regrets).arg(&mut self.d_strat)
            .arg(&self.d_val_slot).arg(&mut self.d_val).launch(Self::cfg(count as u32)).map_err(e)?;}
        Ok(true)
    }
    /// Diagnostic only: full-particle BR restricted to the installed simplex.
    /// Evaluation uses the saved average behavior, without applying epsilon twice.
    /// This gap cannot qualify unrestricted convergence; frozen seats contribute 0.
    pub fn research_behavioral_constrained_gaps(&mut self)->Result<Vec<f64>,String>{
        if self.research_behavioral.is_none(){return Err("behavioral mode required".into())}
        self.research_tables(false)?;self.down(1,-1)?;
        let mut gaps=vec![0.0;self.np as usize];
        for p in 0..self.np{
            if self.static_seats[p as usize]{continue}
            self.terminals_masked(p,0)?;
            self.up(p,4)?;let br=self.stream.clone_dtoh(&self.d_val.slice(0..NUM_CLASSES)).map_err(e)?;
            self.up(p,1)?;let avg=self.stream.clone_dtoh(&self.d_val.slice(0..NUM_CLASSES)).map_err(e)?;
            gaps[p as usize]=br.iter().zip(&avg).enumerate().map(|(h,(b,a))|class_prob(h) as f64*(*b as f64-*a as f64)).sum();
        }
        self.eval_warmed=true;Ok(gaps)
    }
}

#[cfg(test)]
#[path="behavioral_tests.rs"]
mod tests;
