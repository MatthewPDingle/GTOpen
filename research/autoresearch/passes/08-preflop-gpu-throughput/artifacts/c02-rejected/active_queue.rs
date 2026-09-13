//! Research-only compact positive-probability terminal scheduling.
use super::*;
pub(super) struct ActiveQueue {
    pub(super) compact:CudaFunction,
    pub(super) terminal:CudaFunction,
    pub(super) indices:CudaSlice<u32>,
    pub(super) count:CudaSlice<u32>,
}
impl PreflopGpu {
    pub fn enable_research_active_terminal_queue(&mut self)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.research_exact_reuse.as_ref().map_or(true,|r|r.queue.is_some()) {
            return Err("active queue requires fresh exact CDF reuse engine".into());
        }
        let base=include_str!("../../kernels.cu");
        let original=base.split("extern \"C\" __global__ void pf_multiway_terminal(").nth(1).ok_or("terminal source")?
            .split("// Minimum-memory compatibility entry:").next().ok_or("terminal end")?;
        let terminal=format!("extern \"C\" __global__ void pf_active_queue_terminal({original}")
            .replace("float* val)","float* val, const u32* aliases, const u32* queue, const u32* queue_count)")
            .replace("    u32 nd = terms[blockIdx.x];", "    for (u32 k=blockIdx.x;k<*queue_count;k+=gridDim.x) {\n    u32 ti=queue[k];\n    u32 nd = terms[ti];")
            .replace("if (!((lv >> p) & 1)) return;", "if (!((lv >> p) & 1)) continue;")
            .replace("terminal_prob[blockIdx.x]", "terminal_prob[ti]")
            .replace("                // Cast before multiplying:", "                cdf_slot = aliases[cdf_slot];\n                // Cast before multiplying:");
        let mut terminal=terminal.trim_end().to_string();
        assert!(terminal.ends_with('}'));terminal.pop();
        terminal.push_str("    __syncthreads();\n    }\n}\n");
        if !terminal.contains("const u32* queue_count)") || !terminal.contains("u32 ti=queue[k]") || !terminal.contains("cdf_slot = aliases[cdf_slot]") {
            return Err("active queue source rewrite invariant".into());
        }
        let compact=r#"
extern "C" __global__ void pf_active_queue_compact(const float* probability, u32 n, u32* queue, u32* count) {
    u32 t=blockIdx.x*blockDim.x+threadIdx.x;
    if(t<n && probability[t]>0.f) {u32 at=atomicAdd(count,1u);queue[at]=t;}
}
"#;
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts([base,&terminal,compact].join("\n"),cudarc::nvrtc::CompileOptions{
            arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
        let module=self._ctx.load_module(ptx).map_err(e)?;
        let queue=ActiveQueue{compact:module.load_function("pf_active_queue_compact").map_err(e)?,
            terminal:module.load_function("pf_active_queue_terminal").map_err(e)?,
            indices:self.stream.alloc_zeros::<u32>(self.mw_nterms as usize).map_err(e)?,
            count:self.stream.alloc_zeros::<u32>(1).map_err(e)?};
        self.research_exact_reuse.as_mut().unwrap().queue=Some(queue);Ok(())
    }
}
