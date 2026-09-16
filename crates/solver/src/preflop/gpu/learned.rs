//! Explicit opt-in for offline learned-value experiments. No server integration.
use super::*;
use serde_json::{json,Value};

pub(super) struct Learned {
    function:CudaFunction, terms:CudaSlice<u32>, seats:CudaSlice<i32>, spr:CudaSlice<f64>, count:u32,
}
impl PreflopGpu {
    pub fn enable_learned_research(&mut self,s:&PreflopSolver,source:&str)->Result<Value,String> {
        if self.warmed || self.eval_warmed || self.learned.is_some() || s.cfg.realization!="balanced"
            || s.cfg.rake_pct!=0.0 || s.cfg.ante!=0.0 || self.research.is_some()
            || self.research_cohorts.is_some() || self.research_exact_reuse.is_some()
            || self.research_cv.is_some() || self.research_behavioral.is_some()
            || self.research_predictive.is_some() || self.research_rm_plus.is_some()
            || self.research_history_units.is_some() || self.research_root_ranges.is_some() {
            return Err("learned research requires a fresh GPU engine, Balanced base, zero rake and no ante".into());
        }
        let mut terms=Vec::new();let mut seats=Vec::new();let mut spr=Vec::new();let mut outside=0;
        for (i,nd) in s.nodes.iter().enumerate(){
            if nd.kind!=KIND_POT_SHARE || nd.live.count_ones()!=2 {continue;}
            let mut live:Vec<_>=(0..s.n).filter(|&p|nd.live&(1<<p)!=0).collect();
            live.sort_by(|&a,&b|nd.posf[a].total_cmp(&nd.posf[b]));
            let left=live.iter().map(|&p|s.cfg.stack-nd.invested[p]+s.cfg.ante).fold(f64::INFINITY,f64::min);
            let ratio=left/nd.pot;
            if !(1.0..=20.0).contains(&ratio){outside+=1;continue;}
            terms.push(i as u32);seats.extend(live.into_iter().map(|p|p as i32));spr.push(ratio);
        }
        if terms.is_empty(){return Err("no supported heads-up terminals".into());}
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch: &'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)?;
        let function=self._ctx.load_module(ptx).map_err(e)?.load_function("learned_terminal").map_err(e)?;
        let count=terms.len() as u32;
        self.learned=Some(Learned{function,count,terms:self.stream.clone_htod(&terms).map_err(e)?,
            seats:self.stream.clone_htod(&seats).map_err(e)?,spr:self.stream.clone_htod(&spr).map_err(e)?});
        Ok(json!({"supported_hu_terminals":count,"unsupported_hu_terminals":outside,
            "scope":"Zero-rake HU SPR 1..20; other terminals retain Balanced/all-in/multiway pricing. Predictions update with current ranges. No standard CFR convergence guarantee for range-dependent values."}))
    }
    pub(super) fn learned_terminals(&mut self,p:i32)->Result<(),String>{
        let Some(l)=self.learned.as_ref() else{return Ok(());};
        unsafe{self.stream.launch_builder(&l.function)
            .arg(&l.terms).arg(&p).arg(&self.np).arg(&l.seats).arg(&l.spr)
            .arg(&self.d_potg).arg(&self.d_inv).arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass)
            .arg(&self.d_eq).arg(&self.d_val_slot).arg(&mut self.d_val)
            .launch(LaunchConfig{grid_dim:(l.count,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;}
        Ok(())
    }
    /// Exercise the exact inference kernel independently of tree traversal.
    pub fn check_learned_inference(&self,fixtures:&Value)->Result<Value,String>{
        let l=self.learned.as_ref().ok_or("learned engine required")?;
        let terms=self.stream.clone_htod(&[0u32]).map_err(e)?;
        let seats=self.stream.clone_htod(&[0i32,1]).map_err(e)?;
        let pots=self.stream.clone_htod(&[1f32]).map_err(e)?;
        let inv=self.stream.clone_htod(&[0f32,0.]).map_err(e)?;
        let src=self.stream.clone_htod(&[0u32,1]).map_err(e)?;
        let totals=self.stream.clone_htod(&[1f32,1.]).map_err(e)?;
        let slot=self.stream.clone_htod(&[0u32]).map_err(e)?;
        let mut val=self.stream.alloc_zeros::<f32>(169).map_err(e)?;
        let mut max_error=0f64;let mut cases=Vec::new();
        for c in fixtures["cases"].as_array().ok_or("cases")?{
            let w:Vec<Vec<f64>>=serde_json::from_value(c["weights"].clone()).map_err(e)?;
            let expected:Vec<Vec<f64>>=serde_json::from_value(c["expected"].clone()).map_err(e)?;
            let mut dist=Vec::new();
            for row in &w{let mass:f64=row.iter().enumerate().map(|(h,v)|v*class_prob(h) as f64).sum();
                dist.extend(row.iter().enumerate().map(|(h,v)|(v*class_prob(h) as f64/mass) as f32));}
            let reach=self.stream.clone_htod(&dist).map_err(e)?;
            let spr=self.stream.clone_htod(&[c["spr"].as_f64().ok_or("spr")?]).map_err(e)?;
            let mut err=0f64;
            for p in 0..2i32{
                unsafe{self.stream.launch_builder(&l.function).arg(&terms).arg(&p).arg(&2i32).arg(&seats).arg(&spr)
                    .arg(&pots).arg(&inv).arg(&src).arg(&reach).arg(&totals).arg(&self.d_eq).arg(&slot).arg(&mut val)
                    .launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;}
                for (h,v) in self.stream.clone_dtoh(&val).map_err(e)?.iter().enumerate(){
                    if !v.is_finite(){return Err("nonfinite learned prediction".into());}
                    err=err.max((*v as f64-expected[p as usize][h]).abs());
                }
            }
            max_error=max_error.max(err);cases.push(json!({"id":c["id"],"max_absolute_error":err}));
        }
        if max_error>2e-5{return Err(format!("CUDA/Python frozen inference mismatch: {max_error}"));}
        Ok(json!({"max_absolute_error":max_error,"cases":cases,"tolerance":2e-5}))
    }
}
