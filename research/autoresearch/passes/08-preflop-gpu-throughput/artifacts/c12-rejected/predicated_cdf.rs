//! C12: identical scan association, using the shuffle's source-valid predicate.
use super::*;
fn source(predicated:bool)->Result<String,String> {
    let base=include_str!("../kernels.cu");
    let body=base.split("extern \"C\" __global__ void pf_multiway_cdf(").nth(1).ok_or("CDF source")?
        .split("// Memory-constrained fallback.").next().ok_or("CDF end")?;
    let mut source=format!("typedef unsigned int u32;\n#define NC 169\nextern \"C\" __global__ void pf_predicated_cdf({body}")
        .replace("u32 batch_capacity)","u32 batch_capacity, const u32* aliases)")
        .replace("    u32 slot = work[start + blockIdx.x];","    if (aliases[blockIdx.x] != blockIdx.x) return;\n    u32 slot = work[start + blockIdx.x];");
    let original="            float add = __shfl_up_sync(0xffffffff, value, step);\n            if (lane >= (u32)step) value += add;";
    if source.matches(original).count()!=1 || !source.contains("const u32* aliases)"){return Err("predicated CDF rewrite invariant".into());}
    if predicated {source=source.replace(original,r#"            asm volatile("{ .reg .f32 other; .reg .pred valid;\n"
                "shfl.sync.up.b32 other|valid, %0, %1, 0, 0xffffffff;\n"
                "@valid add.rn.f32 %0, %0, other;\n}"
                : "+f"(value) : "r"(step));"#);}
    Ok(source)
}
fn compile(ctx:&Arc<CudaContext>,predicated:bool)->Result<(cudarc::nvrtc::Ptx,CudaFunction),String> {
    let (major,minor)=ctx.compute_capability().map_err(e)?;
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    static PTX:[std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>;2]=[std::sync::OnceLock::new(),std::sync::OnceLock::new()];
    let ptx=PTX[predicated as usize].get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source(predicated)?,
        cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
    let f=ctx.load_module(ptx.clone()).map_err(e)?.load_function("pf_predicated_cdf").map_err(e)?;
    Ok((ptx,f))
}
impl PreflopGpu {
    pub fn enable_research_predicated_cdf(&mut self)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.research_exact_reuse.is_none() || self.research_cohorts.is_none() || !self.exact_reuse_compatible() {
            return Err("predicated CDF requires fresh compatible cohort engine before capture".into());
        }
        self._ctx.bind_to_thread().map_err(e)?;
        self.research_exact_reuse.as_mut().unwrap().cdf=compile(&self._ctx,true)?.1;
        Ok(())
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn predicated_cdf_all_prefixes_and_masks_match() {
        let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
        let (reference_ptx,reference)=compile(&ctx,false).unwrap();let (candidate_ptx,candidate)=compile(&ctx,true).unwrap();
        if let Ok(out)=std::env::var("PREFLOP_GPU_SCAN_DIAGNOSTICS") {
            let out=std::path::Path::new(&out);assert!(!out.exists());std::fs::create_dir_all(out).unwrap();
            let mut resources=Vec::new();
            for (name,ptx,f) in [("reference",reference_ptx,&reference),("candidate",candidate_ptx,&candidate)] {
                std::fs::write(out.join(format!("{name}.ptx")),ptx.to_src()).unwrap();
                resources.push(serde_json::json!({"name":name,"registers":f.num_regs().unwrap(),
                    "local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));
            }
            std::fs::write(out.join("resources.json"),serde_json::to_vec_pretty(&resources).unwrap()).unwrap();
        }
        let deck=crate::preflop::multiway::CoupledDeck::shared();let order=stream.clone_htod(&deck.order).unwrap();
        let work=stream.clone_htod(&[8u32,7,6,5,4,3,2,1,0]).unwrap();let blocks=stream.clone_htod(&(0u32..9).collect::<Vec<_>>()).unwrap();
        let mass=stream.clone_htod(&[1f32,0.,1.,1.,0.,1.,1.,1.,1.]).unwrap();let active=stream.clone_htod(&[1u32,1,0,1,1,1,0,1,1]).unwrap();
        let aliases=stream.clone_htod(&[0u32,1,0,3,4,5,6]).unwrap();let count=7u32;let start=2u32;let capacity=32u32;
        for pattern in 0..4 {
            let mut seed=42u32;let normal:Vec<f32>=(0..9*169).map(|i| {seed=seed.wrapping_mul(1664525).wrapping_add(1013904223);
                match pattern {0=>(seed%10000) as f32/10000.,1=>if i%13==0{0.25}else{0.},2=>f32::from_bits(1+(seed%50000)),_=>if i%3==0{-0.}else{(seed%11) as f32*0.0000001}}}).collect();
            let normalized=stream.clone_htod(&normal).unwrap();
            for compact in [0i32,1] {for gate in [0i32,1] {for sample_start in [0u32,37,992] {for sample_count in [1u32,3,4,5,31,32] {
                let sentinel=f32::from_bits(0x7fc0abcd);let mut outputs=Vec::new();
                for f in [&reference,&candidate] {
                    let mut out=stream.clone_htod(&vec![sentinel;9*32*170]).unwrap();
                    unsafe {stream.launch_builder(f).arg(&work).arg(&start).arg(&blocks).arg(&order).arg(&normalized).arg(&mass)
                        .arg(&active).arg(&gate).arg(&compact).arg(&mut out).arg(&sample_start).arg(&sample_count).arg(&capacity).arg(&aliases)
                        .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}
                    outputs.push(stream.clone_dtoh(&out).unwrap().iter().map(|x|x.to_bits()).collect::<Vec<_>>());
                }
                assert_eq!(outputs[0],outputs[1],"CDF bits pattern={pattern} compact={compact} gate={gate} start={sample_start} count={sample_count}");
                assert!(outputs[0].iter().any(|x|*x!=sentinel.to_bits()));
            }}}}
        }
    }
}
