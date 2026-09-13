//! Research-only first-prefix-aligned CDF storage; arithmetic is unchanged.
use super::*;
const STRIDE:usize=192;
const BIAS:usize=31;
fn allocation(old_words:usize,headroom:usize)->Result<usize,String>{
    if old_words==0||old_words%(NUM_CLASSES+1)!=0{return Err("invalid original CDF capacity".into());}
    let rows=old_words/(NUM_CLASSES+1);
    let words=rows.checked_mul(STRIDE).and_then(|n|n.checked_add(BIAS+1)).ok_or("aligned capacity overflow")?;
    let bytes=words.checked_mul(4).ok_or("aligned byte overflow")?;
    let old_bytes=old_words.checked_mul(4).ok_or("original byte overflow")?;
    if bytes>headroom||bytes-old_bytes>headroom{return Err("aligned CDF exceeds explicit transient/steady headroom".into());}
    Ok(words)
}
impl PreflopGpu {
    pub fn enable_research_aligned_cdf(&mut self,headroom:usize)->Result<(),String>{
        if self.warmed||self.eval_warmed||!self.exact_reuse_compatible()||self.research_exact_reuse.as_ref().map_or(true,|r|r.aligned){return Err("aligned CDF requires a fresh C01 engine".into());}
        let words=allocation(self.d_mw_cdf.len(),headroom)?;
        let base=include_str!("../../kernels.cu");
        let original_cdf=base.split("extern \"C\" __global__ void pf_multiway_cdf(").nth(1).ok_or("CDF source")?
            .split("// Memory-constrained fallback.").next().ok_or("CDF end")?;
        let cdf=format!("extern \"C\" __global__ void pf_aligned_cdf({original_cdf}")
            .replace("u32 batch_capacity)","u32 batch_capacity, const u32* aliases)")
            .replace("    u32 slot = work[start + blockIdx.x];","    if (aliases[blockIdx.x] != blockIdx.x) return;\n    u32 slot = work[start + blockIdx.x];")
            .replace(") * (NC + 1);",") * 192 + 31;");
        let original_sum=base.split("template<int Q, int O>").nth(1).ok_or("sum source")?
            .split("extern \"C\" __global__ void pf_multiway_terminal(").next().ok_or("sum end")?;
        let sum=format!("template<int Q, int O>{original_sum}")
            .replace("pf_multiway_sum(","pf_aligned_sum(")
            .replace("local * (NC + 1)","local * 192");
        let original_terminal=base.split("extern \"C\" __global__ void pf_multiway_terminal(").nth(1).ok_or("terminal source")?
            .split("// Minimum-memory compatibility entry:").next().ok_or("terminal end")?;
        let terminal=format!("extern \"C\" __global__ void pf_aligned_terminal({original_terminal}")
            .replace("float* val)","float* val, const u32* aliases)")
            .replace("                // Cast before multiplying:","                cdf_slot = aliases[cdf_slot];\n                // Cast before multiplying:")
            .replace("* batch_capacity * (NC + 1);","* batch_capacity * 192 + 31;")
            .replace("pf_multiway_sum<","pf_aligned_sum<");
        if cdf.matches("* 192 + 31;").count()!=1||sum.matches("local * 192").count()!=1||terminal.matches("* 192 + 31;").count()!=1||terminal.matches("pf_aligned_sum<").count()!=7{return Err("aligned source rewrite invariant".into());}
        let source=[base,&cdf,&sum,&terminal].join("\n");
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
        let module=self._ctx.load_module(ptx).map_err(e)?;
        let cdf=module.load_function("pf_aligned_cdf").map_err(e)?;
        let terminal=module.load_function("pf_aligned_terminal").map_err(e)?;
        let buffer=self.stream.alloc_zeros::<f32>(words).map_err(e)?;
        self.stream.synchronize().map_err(e)?;
        // All fallible work completed: publish matching buffer and functions together.
        self.d_mw_cdf=buffer;
        let r=self.research_exact_reuse.as_mut().unwrap();r.cdf=cdf;r.terminal=terminal;r.aligned=true;
        Ok(())
    }
}
#[cfg(test)] mod tests;
