use super::*;
use super::super::*;
use serde_json::json;
#[test]
fn narrow_address_bounds_preserve_wide_byte_pointers() {
    assert!(check_elements(0).is_err());
    assert!(check_elements(u32::MAX as usize+1).is_err());
    assert!(check_elements(usize::MAX).is_err());
    assert!(check_elements(u32::MAX as usize).is_ok());
    let mut input=Vec::<u32>::new();let mut expected=Vec::<u64>::new();
    for batch in [1u32,5,32,1024] {
        let capacity=u32::MAX as u64/(batch as u64*170);
        check_elements((capacity*batch as u64*170) as usize).unwrap();
        for slot in [0,1,capacity-1] {for local in [0,batch-1] {for hand in [0,169] {
            input.extend([slot as u32,batch,local,hand]);
            let element=(slot*batch as u64+local as u64)*170+hand as u64;
            assert!(element<capacity*batch as u64*170 && element<=u32::MAX as u64);
            expected.extend([element,element*4]);
        }}}
    }
    assert!(expected.chunks_exact(2).any(|x|x[1]>u32::MAX as u64));
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let(major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let ptx=cudarc::nvrtc::compile_ptx_with_opts(r#"
        extern "C" __global__ void offsets(const unsigned* inputs, unsigned long long* outputs, unsigned count) {
            static_assert(sizeof(size_t)==8,"byte pointers must remain wide");
            unsigned i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;
            unsigned slot=inputs[4*i],batch=inputs[4*i+1],local=inputs[4*i+2],hand=inputs[4*i+3];
            unsigned base=slot*batch*170;unsigned at=base+local*170+hand;
            outputs[2*i]=at;outputs[2*i+1]=(size_t)at*sizeof(float);
        }
    "#,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
    let module=ctx.load_module(ptx).unwrap();let f=module.load_function("offsets").unwrap();
    let args=stream.clone_htod(&input).unwrap();let mut out=stream.alloc_zeros::<u64>(expected.len()).unwrap();
    let count=input.len() as u32/4;
    unsafe {stream.launch_builder(&f).arg(&args).arg(&mut out).arg(&count)
        .launch(LaunchConfig{grid_dim:(count.div_ceil(128),1,1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}
    assert_eq!(stream.clone_dtoh(&out).unwrap(),expected);
    println!("C13_ADDRESS {}",json!({"cases":count,"exact":true,"max_byte_offset":expected.iter().max().unwrap(),"oversized_buffers_refused":true}));
}

#[test]
fn narrow_partial_batches_and_compiler_match() {
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let output=std::env::var("PREFLOP_GPU_NARROW_DIAGNOSTICS").ok().map(std::path::PathBuf::from);
    if let Some(dir)=&output {assert!(!dir.exists());std::fs::create_dir_all(dir).unwrap();}
    let mut results=Vec::new();let mut records=Vec::new();
    let bases:Vec<u64>=(0..8).map(|o|(o*32*170) as u64).collect();
    let d_bases=stream.clone_htod(&bases).unwrap();
    let d_narrow_bases=stream.clone_htod(&bases.iter().map(|v|*v as u32).collect::<Vec<_>>()).unwrap();
    let lo:Vec<u32>=(0..1024*169).map(|i|((i*37+i/169*13)%169) as u32).collect();
    let hi:Vec<u32>=lo.iter().enumerate().map(|(i,&v)|(v+(i%9) as u32).min(169)).collect();
    let d_lo=stream.clone_htod(&lo).unwrap();let d_hi=stream.clone_htod(&hi).unwrap();
    for enabled in [false,true] {
        for (kind,base,kernel,old) in [
            ("exact",exact_reuse::kernel_source(true).unwrap(),"pf_exact_reuse_terminal","exact-2.ptx"),
            ("cohort",cohort_reuse::kernel_source(true).unwrap(),"pf_cohort_terminal","cohort-2.ptx")
        ] {
            let src=source(&base,enabled).unwrap();
            let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
            if !enabled {
                let archived=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/autoresearch/passes/08-preflop-gpu-throughput/raw/c10-runtime-compiler-v1").join(old);
                assert_eq!(ptx.to_src(),std::fs::read_to_string(archived).unwrap(),"retained source extraction changed compiler output");
            }
            if let Some(dir)=&output {std::fs::write(dir.join(format!("{kind}-{}.ptx",if enabled{"candidate"}else{"control"})),ptx.to_src()).unwrap();}
            let module=ctx.load_module(ptx).unwrap();let f=module.load_function(kernel).unwrap();
            records.push(json!({"narrow":enabled,"function":kernel,"module":kind,"registers":f.num_regs().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap(),"local_bytes":f.local_size_bytes().unwrap()}));
        }
        let mut src=source(&exact_reuse::kernel_source(true).unwrap(),enabled).unwrap();
        for o in 2..=8 {let q=(o+2)/2;
            let offset_type=if enabled{"u32"}else{"size_t"};
            src+=&format!("\nextern \"C\" __global__ void audit_{o}(const {offset_type}* bases,const float* cdf,const u32* lo,const u32* hi,u32 start,u32 count,float* out) {{u32 h=threadIdx.x;if(h<NC)out[h]=pf_multiway_sum<{q},{o}>(h,bases,cdf,lo,hi,start,count);}}\n");
        }
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
        if let Some(dir)=&output {std::fs::write(dir.join(if enabled{"helper-candidate.ptx"}else{"helper-control.ptx"}),ptx.to_src()).unwrap();}
        let module=ctx.load_module(ptx).unwrap();let mut run=Vec::new();
        for name in std::iter::once("pf_exact_reuse_terminal".to_string()).chain((2..=8).map(|o|format!("audit_{o}"))) {
            let f=module.load_function(&name).unwrap();records.push(json!({"narrow":enabled,"function":name,"registers":f.num_regs().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap(),"local_bytes":f.local_size_bytes().unwrap()}));
        }
        for zero in [false,true,false] {
            let cdf:Vec<f32>=(0..8*32*170).map(|i|if zero{0.}else{((i%170)/((i/170)%5+1)*((i/170)%5+1)) as f32/169.}).collect();
            let d_cdf=stream.clone_htod(&cdf).unwrap();
            for o in 2..=8 {let f=module.load_function(&format!("audit_{o}")).unwrap();
                for start in [0u32,1,37,992] {for count in [1u32,7,23,31,32] {
                    let mut out=stream.clone_htod(&vec![f32::NAN;169]).unwrap();
                    unsafe {let mut args=stream.launch_builder(&f);
                        if enabled{args.arg(&d_narrow_bases);}else{args.arg(&d_bases);}
                        args.arg(&d_cdf).arg(&d_lo).arg(&d_hi).arg(&start).arg(&count).arg(&mut out)
                        .launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                    let values=stream.clone_dtoh(&out).unwrap();assert!(values.iter().all(|v|v.is_finite()));
                    if zero {assert!(values.iter().all(|v|*v==0.));}
                    run.push(values.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                }}
            }
        }
        results.push(run);
    }
    assert_eq!(results[0],results[1],"narrow terminal arithmetic changed");
    let record=json!({"exact":true,"cases_per_variant":results[0].len(),"hand_values_per_case":169,"opponents":[2,3,4,5,6,7,8],"counts":[1,7,23,31,32],"offsets":[0,1,37,992],"resources":records});
    if let Some(dir)=&output {std::fs::write(dir.join("resources.json"),serde_json::to_vec_pretty(&record).unwrap()).unwrap();}
    println!("C13_PARTIAL {}",record);
}
