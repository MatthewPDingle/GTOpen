//! C20 test-only exact-zero scan bypass; original writer remains unchanged.
use super::*;
use serde_json::json;

fn candidate(base:&str)->String {
    let start=base.find("extern \"C\" __global__ void pf_exact_reuse_cdf(").unwrap();
    let end=start+base[start..].find("extern \"C\" __global__ void pf_exact_reuse_terminal(").unwrap();
    let writer=&base[start..end];
    let old="        #pragma unroll\n        for (int step = 1; step < 32; step <<= 1) {\n            float add = __shfl_up_sync(0xffffffff, value, step);\n            if (lane >= (u32)step) value += add;\n        }";
    let new="        if (__any_sync(0xffffffff, value != 0.f)) {\n            #pragma unroll\n            for (int step = 1; step < 32; step <<= 1) {\n                float add = __shfl_up_sync(0xffffffff, value, step);\n                if (lane >= (u32)step) value += add;\n            }\n        }";
    assert_eq!(writer.matches(old).count(),1);
    let sparse=writer.replace("pf_exact_reuse_cdf(","pf_exact_reuse_cdf_sparse(").replace(old,new);
    format!("{base}\n{sparse}")
}

#[test]
#[ignore = "manual CUDA writer compiler screen; requires output directory"]
fn zero_writer_matches_retained_prefix() {
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_CDF_ZERO_OUTPUT").unwrap());
    assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let base=narrow_offsets::source(&exact_reuse::kernel_source(true).unwrap(),true).unwrap();
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let order=super::super::multiway::CoupledDeck::shared();
    let d_order=stream.clone_htod(&order.order).unwrap();
    let work=stream.clone_htod(&[2u32,0,3,1]).unwrap();let start=0u32;
    let blocks=stream.clone_htod(&[0u32,1,2,3]).unwrap();
    let active=stream.clone_htod(&[1u32,1,0,1]).unwrap();
    let aliases=stream.clone_htod(&[0u32,0,2,3]).unwrap();
    let mut results=Vec::new();let mut records=Vec::new();let mut cases=Vec::new();
    for enabled in [false,true] {
        let source=if enabled {candidate(&base)}else{base.clone()};
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(&source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
        let label=if enabled{"candidate"}else{"control"};
        if !enabled {
            let old=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/autoresearch/passes/08-preflop-gpu-throughput/raw/r03-compiler-v2/exact-candidate.ptx");
            assert_eq!(ptx.to_src(),std::fs::read_to_string(old).unwrap());
        }
        std::fs::write(dir.join(format!("{label}.cu")),source).unwrap();
        std::fs::write(dir.join(format!("{label}.ptx")),ptx.to_src()).unwrap();
        let module=ctx.load_module(ptx).unwrap();let f=module.load_function(if enabled{"pf_exact_reuse_cdf_sparse"}else{"pf_exact_reuse_cdf"}).unwrap();
        records.push(json!({"variant":label,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));
        let mut run=Vec::new();
        for pattern in [1u32,0,1,2,3,4,5,6,7,8,9,10] {
            let zero=matches!(pattern,0|7|8);
            let norm:Vec<f32>=(0..4*169).map(|i|match pattern {
                0=>0.,
                1=>((i*37+i/169*13)%191) as f32/512.,
                2=>if i%47==0 {0.125}else{0.},
                3=>f32::from_bits((i%17+1) as u32),
                4=>if i%169==168 {1.}else{0.},
                5=>if i%13==0 {0.99999994}else{1e-30},
                6=>1e-20*((i%11+1) as f32),
                7=>-0.0,
                8=>if i%2==0 {-0.0}else{0.0},
                9=>if i%169==168 {f32::from_bits(1)}else{-0.0},
                10=>if i%29==0 {1e-30}else{-0.0},
                _=>unreachable!(),
            }).collect();
            let normalized=stream.clone_htod(&norm).unwrap();let mass=stream.clone_htod(&[1f32,0.,1.,1.]).unwrap();
            for compact in [0i32,1] {for gate in [0i32,1] {for (batch,count) in [(1u32,1u32),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] {for sample_start in [0u32,17,992] {
                let len=4*batch as usize*170;narrow_offsets::check_elements(len).unwrap();
                let sentinel=-937.25f32;let mut output=stream.clone_htod(&vec![sentinel;len+32]).unwrap();
                unsafe {stream.launch_builder(&f).arg(&work).arg(&start).arg(&blocks).arg(&d_order)
                    .arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                    .arg(&mut output).arg(&sample_start).arg(&count).arg(&batch).arg(&aliases)
                    .launch(LaunchConfig{grid_dim:(4,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();}
                let out=stream.clone_dtoh(&output).unwrap();assert!(out.iter().all(|v|v.is_finite()));
                assert!(out[len..].iter().all(|v|*v==sentinel));
                let mut written=vec![false;len];let host_work=[2usize,0,3,1];
                for block in 0..4 {
                    let slot=host_work[block];let skipped=block==1 || slot==1 || (gate!=0 && slot==2);
                    if skipped{continue;}
                    let row=if compact!=0{block}else{slot};
                    for local in 0..count as usize {for h in 0..170 {
                        let at=(row*batch as usize+local)*170+h;written[at]=true;
                        if zero{assert_eq!(out[at],0.);}
                    }}
                }
                for (i,w) in written.iter().enumerate(){if !w{assert_eq!(out[i],sentinel,"untouched element {i}");}}
                if !enabled{cases.push(json!({"pattern":pattern,"zero":zero,"compact":compact,"gate":gate,"batch":batch,"count":count,"sample_start":sample_start}));}
                run.push(out.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
            }}}}
        }
        results.push(run);
    }
    assert_eq!(results[0],results[1]);
    let result=json!({"exact":true,"cases_per_variant":results[0].len(),"cases":cases,"resources":records,"guard_and_untouched_slots_checked":true});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    println!("C20_WRITER {}",json!({"exact":true,"cases_per_variant":results[0].len(),"resources":records}));
}
