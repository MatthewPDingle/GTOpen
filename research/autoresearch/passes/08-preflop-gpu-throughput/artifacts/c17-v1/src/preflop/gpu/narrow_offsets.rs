//! C13: narrow element arithmetic only where the whole CDF fits u32 indices.
use super::*;

pub(super) fn check_elements(elements: usize) -> Result<(),String> {
    if elements==0 || elements>u32::MAX as usize {
        Err("C13 requires a nonempty CDF with at most u32::MAX float elements".into())
    } else {Ok(())}
}

pub(super) fn select(prefer:bool,elements:usize)->bool {
    prefer && check_elements(elements).is_ok()
}

pub(super) fn source(input:&str, enabled:bool)->Result<String,String> {
    if !enabled {return Ok(input.to_owned());}
    let mut out=input.to_owned();
    for (old,new,count) in [
        ("u32 h, const size_t* opponent_bases, const float* cdf,","u32 h, const u32* opponent_bases, const float* cdf,",1),
        ("__shared__ size_t opponent_bases[9];","__shared__ u32 opponent_bases[9];",3),
        ("opponent_bases[nopponents++] = (size_t)cdf_slot * batch_capacity * (NC + 1);","opponent_bases[nopponents++] = cdf_slot * batch_capacity * (NC + 1);",3),
        ("size_t base = opponent_bases[q] + (size_t)local * (NC + 1);","u32 base = opponent_bases[q] + local * (NC + 1);",1),
        ("cdf[base + lo]","cdf[(size_t)(base + lo)]",1),
        ("cdf[base + hi]","cdf[(size_t)(base + hi)]",1),
    ] {
        if out.matches(old).count()!=count {return Err(format!("C13 source rewrite invariant: {old}"));}
        out=out.replace(old,new);
    }
    Ok(out)
}

#[cfg(feature = "preflop-research")]
impl PreflopGpu {
    pub fn enable_research_narrow_offsets(&mut self)->Result<(),String> {
        if self.warmed || self.eval_warmed || !self.exact_reuse_compatible()
            || self.research_exact_reuse.is_none() || self.research_cohorts.is_none() {
            return Err("C13 requires fresh native exact-reuse cohorts before graph capture".into());
        }
        if self.research_exact_reuse.as_ref().unwrap().is_packed(){return Err("C17 cannot replace packed terminal after construction".into());}
        check_elements(self.d_mw_cdf.len())?;
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:[std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>;2]=[std::sync::OnceLock::new(),std::sync::OnceLock::new()];
        let mut functions=Vec::new();
        for (i,name) in ["pf_exact_reuse_terminal","pf_cohort_terminal"].iter().enumerate() {
            let ptx=PTX[i].get_or_init(|| {
                let base=if i==0 {exact_reuse::kernel_source(true)?}else{cohort_reuse::kernel_source(true)?};
                cudarc::nvrtc::compile_ptx_with_opts(source(&base,true)?,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)
            }).clone()?;
            let module=self._ctx.load_module(ptx).map_err(e)?;
            functions.push(module.load_function(name).map_err(e)?);
        }
        // Publish only after both modules/functions are valid. Existing CDF,
        // classification kernels and every device allocation retain their identity.
        self.research_cohorts.as_mut().unwrap().terminal=functions.pop().unwrap();
        self.research_exact_reuse.as_mut().unwrap().terminal=functions.pop().unwrap();
        Ok(())
    }
}

#[cfg(all(test, feature = "preflop-research"))]
mod tests;
