//! Research-only lossless CDF run format for masked learning passes.
use super::*;
pub(super) struct Rle {pub(super) cdf:CudaFunction,pub(super) terminal:CudaFunction,
    pub(super) decode:CudaFunction,pub(super) masks:CudaSlice<u32>}
impl PreflopGpu {
    pub fn enable_research_rle_cdf(&mut self,headroom_bytes:usize)->Result<(),String>{
        if self.warmed||self.eval_warmed||self.research_exact_reuse.as_ref().map_or(true,|r|r.rle.is_some()) {
            return Err("RLE requires fresh exact CDF reuse engine".into());
        }
        let capacity=self.d_mw_normalized.len()/NUM_CLASSES;
        let count=capacity.checked_mul(self.mw_batch as usize).and_then(|x|x.checked_mul(6)).ok_or("RLE capacity overflow")?;
        let bytes=count.checked_mul(4).ok_or("RLE byte overflow")?;
        if bytes>512*1024*1024||bytes>headroom_bytes{return Err("RLE exceeds explicit remaining budget or 512 MiB cap".into());}
        let base=include_str!("../../kernels.cu");
        let original_sum=base.split("template<int Q, int O>").nth(1).ok_or("sum start")?
            .split("extern \"C\" __global__ void pf_multiway_terminal(").next().ok_or("sum end")?;
        let sum=format!("template<int Q, int O>{original_sum}")
            .replace("pf_multiway_sum(","pf_rle_sum(")
            .replace("u32 sample_start, u32 sample_count)","u32 sample_start, u32 sample_count, const u32* masks)")
            .replace("cdf[base + lo]","pf_rle_read(cdf, masks, base, lo)")
            .replace("cdf[base + hi]","pf_rle_read(cdf, masks, base, hi)");
        let original_terminal=base.split("extern \"C\" __global__ void pf_multiway_terminal(").nth(1).ok_or("terminal source")?
            .split("// Minimum-memory compatibility entry:").next().ok_or("terminal end")?;
        let terminal=format!("extern \"C\" __global__ void pf_rle_terminal({original_terminal}")
            .replace("float* val)","float* val, const u32* aliases, const u32* masks)")
            .replace("                // Cast before multiplying:","                cdf_slot = aliases[cdf_slot];\n                // Cast before multiplying:")
            .replace("pf_multiway_sum<","pf_rle_sum<")
            .replace("sample_count); break;","sample_count, masks); break;");
        if !sum.contains("const u32* masks)")||terminal.matches("sample_count, masks); break;").count()!=7||!terminal.contains("cdf_slot = aliases[cdf_slot]"){return Err("RLE source rewrite invariant".into());}
        let source=[base,include_str!("rle.cu"),&sum,&terminal].join("\n");
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
        let module=self._ctx.load_module(ptx).map_err(e)?;
        self.research_exact_reuse.as_mut().unwrap().rle=Some(Rle{
            cdf:module.load_function("pf_rle_cdf").map_err(e)?,terminal:module.load_function("pf_rle_terminal").map_err(e)?,
            decode:module.load_function("pf_rle_decode_test").map_err(e)?,masks:self.stream.alloc_zeros::<u32>(count).map_err(e)?});Ok(())
    }
}
#[cfg(test)] mod tests;
