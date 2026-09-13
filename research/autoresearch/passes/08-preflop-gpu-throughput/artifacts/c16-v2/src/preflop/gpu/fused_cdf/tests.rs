use super::*;
use serde_json::json;
#[test]
#[ignore="manual C16 kernel/prefix audit; guarded idle GPU"]
fn fused_prefix_and_terminal_bits() {
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_FUSED_OUTPUT").unwrap());
    assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let base=narrow_offsets::source(&exact_reuse::kernel_source(true).unwrap(),true).unwrap();
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();let(major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (label,kernel,base) in [("exact","pf_exact_reuse_terminal",base.clone()),("cohort","pf_cohort_terminal",narrow_offsets::source(&cohort_reuse::kernel_source(true).unwrap(),true).unwrap())] {
        let src=source(&base,kernel,true).unwrap();let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
        std::fs::write(dir.join(format!("{label}-candidate.cu")),src).unwrap();std::fs::write(dir.join(format!("{label}-candidate.ptx")),ptx.to_src()).unwrap();
    }
    let mut src=source(&base,"pf_exact_reuse_terminal",true).unwrap();
    for o in 2..=8 {let q=(o+2)/2;
        src+=&format!(r#"
extern "C" __global__ void ref_{o}(const u32* bases,const float* cdf,const u32* lo,const u32* hi,u32 start,u32 count,float* out) {{u32 h=threadIdx.x;if(h<NC)out[h]=pf_multiway_sum<{q},{o}>(h,bases,cdf,lo,hi,start,count);}}
extern "C" __global__ void fused_{o}(const u32* bases,const float* normalized,const u32* order,const u32* lo,const u32* hi,u32 start,u32 count,float* out) {{
 __shared__ float norm[{o}*NC];__shared__ float cdf[{o}*(NC+1)];u32 h=threadIdx.x;
 float sum=pf_fused_sum<{q},{o}>(h,bases,normalized,order,lo,hi,start,count,norm,cdf);if(h<NC)out[h]=sum;
}}
extern "C" __global__ void prefix_{o}(const u32* bases,const float* normalized,const u32* order,u32 start,u32 count,u32 batch,float* out) {{
 __shared__ float norm[{o}*NC];__shared__ float cdf[{o}*(NC+1)];pf_fused_stage<{o}>(bases,normalized,norm);
 for(u32 local=0;local<count;local++) {{pf_fused_prefix<{o}>(start+local,order,norm,cdf);
 for(u32 i=threadIdx.x;i<{o}*(NC+1);i+=blockDim.x) out[((i/(NC+1))*batch+local)*(NC+1)+i%(NC+1)]=cdf[i];__syncthreads();}}
}}
"#);
    }
    let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
    std::fs::write(dir.join("audit.cu"),&src).unwrap();std::fs::write(dir.join("audit.ptx"),ptx.to_src()).unwrap();
    let module=ctx.load_module(ptx).unwrap();let prefix=module.load_function("pf_exact_reuse_cdf").unwrap();
    let table=super::super::super::multiway::CoupledDeck::shared();
    let order=stream.clone_htod(&table.order).unwrap();let lo=stream.clone_htod(&table.lower).unwrap();let hi=stream.clone_htod(&table.upper).unwrap();
    let rows:Vec<u32>=(0..8).collect();let work=stream.clone_htod(&rows).unwrap();let blocks=stream.clone_htod(&rows).unwrap();let aliases=stream.clone_htod(&rows).unwrap();
    let active=stream.clone_htod(&[1u32;8]).unwrap();let mass=stream.clone_htod(&[1f32;8]).unwrap();let zero=0u32;let gate=0i32;let compact=1i32;
    let chosen=[0u32,1,1,4,7,7,2,5];let norm_bases=stream.clone_htod(&chosen.iter().map(|r|r*169).collect::<Vec<_>>()).unwrap();
    let sentinel=-937.25f32;let mut cases=Vec::new();let mut resources=Vec::new();
    for o in 2..=8 {for name in [format!("ref_{o}"),format!("fused_{o}"),format!("prefix_{o}")] {
        let f=module.load_function(&name).unwrap();resources.push(json!({"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));}}
    for kind in [0u32,1,2,0] {
        let norm:Vec<f32>=(0..8*169).map(|i|if kind==2 || (kind==1 && i%13!=0){0.}else{((i*37+i/169*13)%191) as f32/512.}).collect();
        let normalized=stream.clone_htod(&norm).unwrap();
        for (batch,count) in [(5u32,1u32),(5,4),(5,5),(32,1),(32,7),(32,23),(32,31),(32,32)] {for start in [0u32,17,992] {
            let mut cdf=stream.clone_htod(&vec![sentinel;8*batch as usize*170+32]).unwrap();
            unsafe{stream.launch_builder(&prefix).arg(&work).arg(&zero).arg(&blocks).arg(&order).arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                .arg(&mut cdf).arg(&start).arg(&count).arg(&batch).arg(&aliases).launch(LaunchConfig{grid_dim:(8,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}
            let expected=stream.clone_dtoh(&cdf).unwrap();assert!(expected[8*batch as usize*170..].iter().all(|v|*v==sentinel));
            let cdf_bases=stream.clone_htod(&chosen.iter().map(|r|r*batch*170).collect::<Vec<_>>()).unwrap();
            for o in 2..=8 {
                let f=module.load_function(&format!("prefix_{o}")).unwrap();let mut out=stream.clone_htod(&vec![sentinel;o*batch as usize*170+32]).unwrap();
                unsafe{stream.launch_builder(&f).arg(&norm_bases).arg(&normalized).arg(&order).arg(&start).arg(&count).arg(&batch).arg(&mut out)
                    .launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                let actual=stream.clone_dtoh(&out).unwrap();let mut exp=vec![sentinel;actual.len()];
                for q in 0..o {for local in 0..count as usize {let a=(q*batch as usize+local)*170;let b=(chosen[q] as usize*batch as usize+local)*170;exp[a..a+170].copy_from_slice(&expected[b..b+170]);}}
                assert_eq!(actual.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),exp.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),"prefix o={o} kind={kind} count={count}");
                let mut values=Vec::new();
                for fused in [false,true] {
                    let f=module.load_function(&format!("{}_{o}",if fused{"fused"}else{"ref"})).unwrap();let mut out=stream.clone_htod(&vec![sentinel;169+32]).unwrap();
                    unsafe {let mut a=stream.launch_builder(&f);
                        if fused{a.arg(&norm_bases).arg(&normalized).arg(&order);}else{a.arg(&cdf_bases).arg(&cdf);}
                        a.arg(&lo).arg(&hi).arg(&start).arg(&count).arg(&mut out).launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                    let v=stream.clone_dtoh(&out).unwrap();assert!(v.iter().all(|v|v.is_finite()));assert!(v[169..].iter().all(|v|*v==sentinel));
                    if kind==2{assert!(v[..169].iter().all(|v|*v==0.));}values.push(v.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                }
                assert_eq!(values[0],values[1],"terminal o={o} kind={kind} start={start} count={count}");
                cases.push(json!({"opponents":o,"kind":kind,"start":start,"batch":batch,"count":count}));
            }
        }}
    }
    let record=json!({"exact":true,"cases":cases,"prefix_and_terminal_guards":true,"hand_classes":169,"resources":resources});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&record).unwrap()).unwrap();println!("C16_KERNEL {}",json!({"exact":true,"cases":cases.len(),"prefix_and_terminal_guards":true}));
}
