//! One shared policy snapshot with a packed live-traverser payoff cache.
use super::*;
use serde_json::{json,Value};

struct Plan {
    offsets:Vec<u32>,full:usize,reach:usize,mass:usize,current:usize,
}
impl Plan {
    fn build(kind:&[i32],live:&[i32],terms:&[u32],fixed:&[bool],reach:usize,mass:usize)->Result<Self,String>{
        let np=fixed.len();
        if kind.len()!=live.len() || !(2..=9).contains(&np) || terms.is_empty() || fixed.iter().all(|v|*v)
            || reach!=mass.checked_mul(NUM_CLASSES).ok_or("reference geometry overflow")? {
            return Err("invalid shared CV geometry".into());
        }
        let count=np.checked_mul(terms.len()).ok_or("map overflow")?;
        let current=terms.len().checked_mul(NUM_CLASSES).ok_or("scratch overflow")?;
        let mut plan=Self{offsets:Vec::with_capacity(count),full:0,reach,mass,current};
        for (p,&frozen) in fixed.iter().enumerate(){for &nd in terms{
            let lv=*live.get(nd as usize).ok_or("terminal index out of bounds")?;
            if kind[nd as usize]!=KIND_POT_SHARE as i32 || lv<0 || lv>>np!=0 || lv.count_ones()<3{return Err("invalid multiway mask".into());}
            if !frozen && lv&(1<<p)!=0{
                plan.offsets.push(u32::try_from(plan.full).map_err(|_|"packed offset overflow")?);
                plan.full=plan.full.checked_add(NUM_CLASSES).ok_or("cache overflow")?;
                if plan.full>=u32::MAX as usize{return Err("sentinel overlaps packed offsets".into());}
            }else{plan.offsets.push(u32::MAX);}
        }}
        plan.bytes()?;Ok(plan)
    }
    fn bytes(&self)->Result<usize,String>{
        [self.full,self.reach,self.mass,self.current,self.offsets.len()].iter().try_fold(0usize,|a,&b|a.checked_add(b))
            .and_then(|v|v.checked_mul(4)).ok_or("shared CV byte overflow".into())
    }
    fn report(&self)->Result<Value,String>{Ok(json!({"reference_reach_bytes":self.reach*4,
        "reference_mass_bytes":self.mass*4,"full_payoff_bytes":self.full*4,"current_scratch_bytes":self.current*4,
        "offset_bytes":self.offsets.len()*4,"live_learning_terminal_entries":self.full/NUM_CLASSES,
        "persistent_extra_bytes":self.bytes()?,"cap_bytes":4usize*1024*1024*1024,
        "fits_four_gib":self.bytes()?<=4usize*1024*1024*1024}))}
}

pub(super) struct SharedReference {
    reach:CudaSlice<f32>,mass:CudaSlice<f32>,full:CudaSlice<f32>,offsets:CudaSlice<u32>,
    store:CudaFunction,combine:CudaFunction,last_refresh:Option<u32>,report:Value,
}

impl PreflopSolver {
    pub fn research_shared_cv_storage(&self)->Result<Value,String>{
        let kind:Vec<_>=self.nodes.iter().map(|n|n.kind as i32).collect();
        let live:Vec<_>=self.nodes.iter().map(|n|n.live as i32).collect();
        let terms:Vec<_>=self.nodes.iter().enumerate().filter(|(_,n)|n.kind==KIND_POT_SHARE && n.live.count_ones()>=3).map(|(i,_)|i as u32).collect();
        let fixed:Vec<_>=(0..self.n).map(|p|self.seat_static(p)).collect();
        let mass=self.nodes.len().checked_add(self.n-1).ok_or("reach count overflow")?;
        let plan=Plan::build(&kind,&live,&terms,&fixed,mass.checked_mul(NUM_CLASSES).ok_or("reach size overflow")?,mass)?;
        Ok(json!({"nodes":self.nodes.len(),"players":self.n,"multiway_terminals":terms.len(),
            "model":self.multiway_equity_model(),"storage":plan.report()?,"read_only":true}))
    }
}

impl PreflopGpu {
    pub fn enable_research_shared_control_variate(&mut self,interval:u32,extra_limit_mb:usize)->Result<Value,String>{
        if interval==0 || self.research.is_none() || self.warmed || self.eval_warmed || self.research_cv.is_some()
            || self.research_behavioral.is_some() || self.research_predictive.is_some() || self.research_rm_plus.is_some() || self.research_pair_control.is_some()
            || self.research_normalized_regret.is_some() || self.research_exploration.is_some() || self.research_history_units.is_some()
            || self.research_average_opponents.is_some() || self.research_learning_mask || self.research_root_ranges.is_some()
            || !self.use_mw_prepared || self.use_multiway==0 {return Err("fresh configured native-unit prepared engine required".into());}
        let kind=self.stream.clone_dtoh(&self.d_kind).map_err(e)?;
        let live=self.stream.clone_dtoh(&self.d_live).map_err(e)?;
        let terms=self.stream.clone_dtoh(&self.d_mw_terms).map_err(e)?;
        let plan=Plan::build(&kind,&live,&terms,&self.static_seats,self.d_reach.len(),self.d_reach_mass.len())?;
        if plan.bytes()?>extra_limit_mb.min(4096).saturating_mul(1024*1024){return Err(format!("shared CV needs {} extra bytes; cap exceeded",plan.bytes()?));}
        let source=[include_str!("cv_research.cu"),include_str!("cv_shared.cu")].join("\n");
        let module=self._ctx.load_module(cudarc::nvrtc::compile_ptx(source).map_err(e)?).map_err(e)?;
        let shared=SharedReference{reach:self.stream.alloc_zeros::<f32>(plan.reach).map_err(e)?,
            mass:self.stream.alloc_zeros::<f32>(plan.mass).map_err(e)?,full:self.stream.alloc_zeros::<f32>(plan.full).map_err(e)?,
            offsets:self.stream.clone_htod(&plan.offsets).map_err(e)?,store:module.load_function("cv_shared_store").map_err(e)?,
            combine:module.load_function("cv_shared_combine").map_err(e)?,last_refresh:None,report:plan.report()?};
        let cv=ControlVariate{shared:Some(shared),references:Vec::new(),current:self.stream.alloc_zeros::<f32>(plan.current).map_err(e)?,
            store:module.load_function("cv_store").map_err(e)?,combine:module.load_function("cv_combine").map_err(e)?,
            prior:module.load_function("cv_zero_mass_prior").map_err(e)?,interval,bytes:plan.bytes()?,refreshes:0};
        self.research_unit_fill=Some(module.load_function("cv_unit_probability").map_err(e)?);
        self.research_cv=Some(cv);plan.report()
    }
    pub fn research_shared_control_variate_stats(&self)->Option<Value>{
        self.research_cv.as_ref().and_then(|cv|cv.shared.as_ref().map(|s|json!({"storage":s.report,
            "refresh_epochs":cv.refreshes,"last_refresh_iteration":s.last_refresh,"captured_sweeps":self.learning_graphs.iter().filter(|g|g.is_some()).count()})))
    }
    fn shared_reference_values(&mut self,p:i32,reference:&mut SharedReference)->Result<(),String>{
        std::mem::swap(&mut self.d_reach,&mut reference.reach);std::mem::swap(&mut self.d_reach_mass,&mut reference.mass);
        self.research_unit_probability=true;let result=self.multiway_terminals(p,0);self.research_unit_probability=false;
        std::mem::swap(&mut self.d_reach,&mut reference.reach);std::mem::swap(&mut self.d_reach_mass,&mut reference.mass);result
    }
    fn shared_store_full(&self,p:i32,reference:&mut SharedReference)->Result<(),String>{
        unsafe{self.stream.launch_builder(&reference.store).arg(&self.d_mw_terms).arg(&self.d_val_slot).arg(&self.d_val)
            .arg(&mut reference.full).arg(&reference.offsets).arg(&self.mw_nterms).arg(&p)
            .launch(LaunchConfig{grid_dim:(self.mw_nterms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
        Ok(())
    }
    fn shared_refresh(&mut self,p:i32,iteration:u32,cv:&mut ControlVariate)->Result<(),String>{
        let reference=cv.shared.as_mut().ok_or("missing shared reference")?;
        if reference.last_refresh.is_some() && (iteration%cv.interval!=0 || reference.last_refresh==Some(iteration)){return Ok(());}
        self.down(0,p)?;
        self.stream.memcpy_dtod(&self.d_reach,&mut reference.reach).map_err(e)?;
        self.stream.memcpy_dtod(&self.d_reach_mass,&mut reference.mass).map_err(e)?;
        let blocks=reference.mass.len() as u32;
        unsafe{self.stream.launch_builder(&cv.prior).arg(&mut reference.reach).arg(&mut reference.mass).arg(&self.d_cprob)
            .launch(LaunchConfig{grid_dim:(blocks,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
        self.research_tables_select(false,false)?;
        for q in 0..self.np{if !self.static_seats[q as usize]{
            self.shared_reference_values(q,reference)?;self.shared_store_full(q,reference)?;
        }}
        self.research_tables_select(true,false)?;
        reference.last_refresh=Some(iteration);cv.refreshes+=1;Ok(())
    }
    fn shared_correct_terminals(&mut self,p:i32,cv:&mut ControlVariate)->Result<(),String>{
        self.terminals(p)?;self.cv_store_values(&cv.store,&mut cv.current)?;
        let reference=cv.shared.as_mut().ok_or("missing shared reference")?;
        self.shared_reference_values(p,reference)?;
        unsafe{self.stream.launch_builder(&reference.combine).arg(&self.d_mw_terms).arg(&p).arg(&self.np)
            .arg(&self.d_reach_src).arg(&self.d_reach_mass).arg(&self.d_val_slot).arg(&cv.current)
            .arg(&reference.full).arg(&mut self.d_val).arg(&reference.offsets).arg(&self.mw_nterms)
            .launch(LaunchConfig{grid_dim:(self.mw_nterms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
        Ok(())
    }
    fn shared_update(&mut self,p:i32,cv:&mut ControlVariate)->Result<(),String>{
        self.down(0,p)?;self.shared_correct_terminals(p,cv)?;self.up(p,0)
    }
    pub(super) fn cv_shared_sweep(&mut self,p:i32,iteration:u32)->Result<(),String>{
        let mut cv=self.research_cv.take().ok_or("missing shared CV state")?;
        let result=(||{
            self.shared_refresh(p,iteration,&mut cv)?;
            if self.warmed && self.learning_graphs[p as usize].is_none(){
                self.stream.begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL).map_err(e)?;
                let update=self.shared_update(p,&mut cv);
                let graph=self.stream.end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH).map_err(e)?;
                update?;self.learning_graphs[p as usize]=Some(graph.ok_or("CV graph capture failed")?);
            }
            if let Some(graph)=&self.learning_graphs[p as usize]{graph.launch().map_err(e)?;}else{self.shared_update(p,&mut cv)?;}
            Ok(())
        })();self.research_cv=Some(cv);result
    }
}

#[cfg(test)]
#[path="cv_shared_tests.rs"]
mod tests;
