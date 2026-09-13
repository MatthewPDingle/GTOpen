use super::*;
use super::super::*;
use serde_json::json;
#[test]
fn terminal_unroll_partial_batches_are_exact() {
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let output=std::env::var("PREFLOP_GPU_UNROLL_DIAGNOSTICS").ok().map(std::path::PathBuf::from);
    if let Some(dir)=&output {assert!(!dir.exists());std::fs::create_dir_all(dir).unwrap();}
    let mut results=Vec::new();let mut records=Vec::new();
    let bases:Vec<u64>=(0..8).map(|o|(o*32*170) as u64).collect();
    let d_bases=stream.clone_htod(&bases).unwrap();
    let lo:Vec<u32>=(0..1024*169).map(|i|((i*37+i/169*13)%169) as u32).collect();
    let hi:Vec<u32>=lo.iter().enumerate().map(|(i,&v)|(v+(i%9) as u32).min(169)).collect();
    let d_lo=stream.clone_htod(&lo).unwrap();let d_hi=stream.clone_htod(&hi).unwrap();
    for enabled in [false,true] {
        let mut src=source(include_str!("../../kernels.cu"),enabled).unwrap();
        for o in 2..=8 {let q=(o+2)/2;
            src+=&format!("\nextern \"C\" __global__ void audit_{o}(const size_t* bases,const float* cdf,const u32* lo,const u32* hi,u32 start,u32 count,float* out) {{u32 h=threadIdx.x;if(h<NC)out[h]=pf_multiway_sum<{q},{o}>(h,bases,cdf,lo,hi,start,count);}}\n");
        }
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
        if let Some(dir)=&output {std::fs::write(dir.join(if enabled{"candidate.ptx"}else{"control.ptx"}),ptx.to_src()).unwrap();}
        let module=ctx.load_module(ptx).unwrap();let mut run=Vec::new();
        for name in std::iter::once("pf_multiway_terminal".to_string()).chain((2..=8).map(|o|format!("audit_{o}"))) {
            let f=module.load_function(&name).unwrap();records.push(json!({"unrolled":enabled,"function":name,"registers":f.num_regs().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap(),"local_bytes":f.local_size_bytes().unwrap()}));
        }
        for zero in [false,true,false] {
            let cdf:Vec<f32>=(0..8*32*170).map(|i|if zero{0.}else{((i%170)/((i/170)%5+1)*((i/170)%5+1)) as f32/169.}).collect();
            let d_cdf=stream.clone_htod(&cdf).unwrap();
            for o in 2..=8 {let f=module.load_function(&format!("audit_{o}")).unwrap();
                for start in [0u32,1,37,992] {for count in [1u32,7,23,31,32] {
                    let mut out=stream.clone_htod(&vec![f32::NAN;169]).unwrap();
                    unsafe {stream.launch_builder(&f).arg(&d_bases).arg(&d_cdf).arg(&d_lo).arg(&d_hi).arg(&start).arg(&count).arg(&mut out)
                        .launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                    let values=stream.clone_dtoh(&out).unwrap();assert!(values.iter().all(|v|v.is_finite()));
                    if zero {assert!(values.iter().all(|v|*v==0.));}
                    run.push(values.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                }}
            }
        }
        results.push(run);
    }
    assert_eq!(results[0],results[1],"partial sample-loop arithmetic changed");
    let record=json!({"exact":true,"cases_per_variant":results[0].len(),"hand_values_per_case":169,"opponents":[2,3,4,5,6,7,8],"counts":[1,7,23,31,32],"offsets":[0,1,37,992],"resources":records});
    if let Some(dir)=&output {std::fs::write(dir.join("resources.json"),serde_json::to_vec_pretty(&record).unwrap()).unwrap();}
    println!("C09_PARTIAL {}",record);
}
