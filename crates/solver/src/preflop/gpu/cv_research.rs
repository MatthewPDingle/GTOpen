//! Bounded eager GPU control-variate prototype. No production entry point.
use super::*;

struct Reference {
    reach: CudaSlice<f32>,
    mass: CudaSlice<f32>,
    full: CudaSlice<f32>,
    valid: bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::{PreflopConfig, convergence_research::Experiment, equity::EquityTable};
    fn run(samples:u32, refresh:Option<u32>)->(Vec<f32>,Vec<f32>,Vec<f64>) {
        let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");
        let bytes=std::fs::read(path).unwrap();
        let eq=Arc::new(EquityTable::load_or_build(path,u32::from_le_bytes(bytes[..4].try_into().unwrap())));
        let cfg:PreflopConfig=serde_json::from_value(serde_json::json!({
            "positions":["CO","BTN","SB","BB"],"stack":5.0,"posts":[0.0,0.0,0.5,1.0],
            "limp":true,"open_raises":[2.0],"raise_mults":[3.0],"max_raises":1,
            "add_allin":false,"rake_pct":5.0,"rake_cap":1.0,"realization":"raw"
        })).unwrap();
        let mut s=PreflopSolver::new(cfg,eq).unwrap();
        let mut g=PreflopGpu::new(&s,2000).unwrap();
        g.configure_research(Experiment::new("dcfr",samples,1000,42).unwrap()).unwrap();
        if let Some(refresh)=refresh {
            assert!(g.enable_research_control_variate(refresh,0).is_err());
            assert!(g.research_cv.is_none());
            g.enable_research_control_variate(refresh,100).unwrap();
        }
        for _ in 0..3 {g.iterate(&mut s).unwrap();}
        let (gaps,_)=g.gaps_and_evs().unwrap();
        let regrets=g.stream.clone_dtoh(&g.d_regrets).unwrap();
        let strategy=g.stream.clone_dtoh(&g.d_strat).unwrap();
        (regrets,strategy,gaps)
    }
    #[test]
    fn cv_full_particle_correction_cancels_exactly() {
        let baseline=run(1024,None);
        let candidate=run(1024,Some(2));
        assert_eq!(baseline,candidate);
    }
    #[test]
    fn cv_refresh_every_iteration_tracks_full_gradient() {
        let baseline=run(1024,None);
        let candidate=run(64,Some(1));
        let error=baseline.0.iter().chain(&baseline.1).zip(candidate.0.iter().chain(&candidate.1))
            .map(|(&a,&b)|{assert!(b.is_finite());(a-b).abs()/(1.0+a.abs())}).fold(0.0f32,f32::max);
        eprintln!("CV refresh-one normalized arena error: {error}");
        assert!(error<=0.0002,"full-gradient floating-point tolerance exceeded: {error}");
        assert!(baseline.2.iter().zip(candidate.2).all(|(&a,b)|(a-b).abs()<=0.0002));
    }
}
pub(super) struct ControlVariate {
    references: Vec<Option<Reference>>,
    current: CudaSlice<f32>,
    store: CudaFunction,
    combine: CudaFunction,
    prior: CudaFunction,
    interval: u32,
    bytes: usize,
    refreshes: usize,
}

impl PreflopGpu {
    /// Explicit memory bound includes every reference range/mass/value array.
    /// All allocations and refreshes are timed by the caller. Learning uses
    /// eager launches in this first prototype; global checks stay canonical.
    pub fn enable_research_control_variate(&mut self, interval:u32, extra_limit_mb:usize)->Result<usize,String>{
        if interval==0 || self.research.is_none() || self.warmed || self.research_cv.is_some()
            || !self.use_mw_prepared || self.use_multiway==0 {
            return Err("control variate requires a fresh prepared research GPU engine".into());
        }
        let values=self.mw_nterms as usize*NUM_CLASSES;
        let active=self.static_seats.iter().filter(|&&s|!s).count();
        let floats=(self.d_reach.len()+self.d_reach_mass.len()+values).checked_mul(active)
            .and_then(|x|x.checked_add(values)).ok_or("CV storage overflow")?;
        let bytes=floats.checked_mul(4).ok_or("CV byte overflow")?;
        if bytes>extra_limit_mb.saturating_mul(1024*1024) {return Err(format!("CV needs {bytes} extra bytes; configured cap is {extra_limit_mb} MiB"));}
        let ptx=cudarc::nvrtc::compile_ptx(include_str!("cv_research.cu")).map_err(e)?;
        let module=self._ctx.load_module(ptx).map_err(e)?;
        let mut references=Vec::new();
        for &fixed in &self.static_seats {
            references.push(if fixed {None} else {Some(Reference {
                reach:self.stream.alloc_zeros::<f32>(self.d_reach.len()).map_err(e)?,
                mass:self.stream.alloc_zeros::<f32>(self.d_reach_mass.len()).map_err(e)?,
                full:self.stream.alloc_zeros::<f32>(values).map_err(e)?,valid:false})});
        }
        let cv=ControlVariate {references,current:self.stream.alloc_zeros::<f32>(values).map_err(e)?,
            store:module.load_function("cv_store").map_err(e)?,combine:module.load_function("cv_combine").map_err(e)?,
            prior:module.load_function("cv_zero_mass_prior").map_err(e)?,interval,bytes,refreshes:0};
        self.research_unit_fill=Some(module.load_function("cv_unit_probability").map_err(e)?);
        self.research_cv=Some(cv);
        Ok(bytes)
    }

    pub fn research_control_variate_stats(&self)->Option<(usize,usize)> {
        self.research_cv.as_ref().map(|c|(c.bytes,c.refreshes))
    }

    fn cv_store_values(&self, kernel:&CudaFunction, destination:&mut CudaSlice<f32>)->Result<(),String>{
        unsafe {self.stream.launch_builder(kernel).arg(&self.d_mw_terms).arg(&self.d_val_slot)
            .arg(&self.d_val).arg(destination).launch(LaunchConfig{grid_dim:(self.mw_nterms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
        Ok(())
    }

    fn cv_reference_values(&mut self,p:i32,reference:&mut Reference)->Result<(),String>{
        std::mem::swap(&mut self.d_reach,&mut reference.reach);
        std::mem::swap(&mut self.d_reach_mass,&mut reference.mass);
        self.research_unit_probability=true;
        let result=self.multiway_terminals(p,0);
        self.research_unit_probability=false;
        std::mem::swap(&mut self.d_reach,&mut reference.reach);
        std::mem::swap(&mut self.d_reach_mass,&mut reference.mass);
        result
    }

    pub(super) fn cv_sweep(&mut self,p:i32,iteration:u32)->Result<(),String>{
        let mut cv=self.research_cv.take().ok_or("missing CV state")?;
        let result=(|| {
            self.down(0,p)?;
            let reference=cv.references[p as usize].as_mut().ok_or("missing learning-seat reference")?;
            if !reference.valid || iteration%cv.interval==0 {
                self.stream.memcpy_dtod(&self.d_reach,&mut reference.reach).map_err(e)?;
                self.stream.memcpy_dtod(&self.d_reach_mass,&mut reference.mass).map_err(e)?;
                let blocks=reference.mass.len() as u32;
                // Reference ranges must define every live-opponent distribution,
                // even when its actual reach was zero at the refresh. A fixed
                // prior is a valid control function; stale CDF scratch is not.
                unsafe {self.stream.launch_builder(&cv.prior).arg(&mut reference.reach).arg(&mut reference.mass)
                    .arg(&self.d_cprob).launch(LaunchConfig{grid_dim:(blocks,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
                self.research_tables_select(false,false)?;
                self.cv_reference_values(p,reference)?;
                self.cv_store_values(&cv.store,&mut reference.full)?;
                self.research_tables_select(true,false)?; // same random offset, no extra draw
                reference.valid=true;cv.refreshes+=1;
            }
            self.terminals(p)?; // ordinary values plus weighted current sample
            self.cv_store_values(&cv.store,&mut cv.current)?;
            self.cv_reference_values(p,reference)?; // unit-weight reference, identical particles
            unsafe {self.stream.launch_builder(&cv.combine).arg(&self.d_mw_terms).arg(&p).arg(&self.np)
                .arg(&self.d_live).arg(&self.d_reach_src).arg(&self.d_reach_mass).arg(&self.d_val_slot)
                .arg(&cv.current).arg(&reference.full).arg(&mut self.d_val)
                .launch(LaunchConfig{grid_dim:(self.mw_nterms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;}
            self.up(p,0)
        })();
        self.research_cv=Some(cv);
        result
    }
}
