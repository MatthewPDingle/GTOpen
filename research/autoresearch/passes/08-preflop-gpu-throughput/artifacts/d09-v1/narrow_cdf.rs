//! D09 test-only writer address screen; no runtime selection hook.
use super::*;
use serde_json::json;

fn candidate(base:&str)->String {
    let start=base.find("extern \"C\" __global__ void pf_exact_reuse_cdf(").unwrap();
    let end=start+base[start..].find("extern \"C\" __global__ void pf_exact_reuse_terminal(").unwrap();
    let mut writer=base[start..end].to_string();
    for (old,new) in [
        ("size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);",
         "u32 base = ((compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);"),
        ("cdf[base]", "cdf[(size_t)base]"),
        ("cdf[base + index + 1]", "cdf[(size_t)(base + index + 1)]"),
    ] {
        assert_eq!(writer.matches(old).count(),1, "writer rewrite: {old}");
        writer=writer.replace(old,new);
    }
    format!("{}{}{}",&base[..start],writer,&base[end..])
}

#[test]
fn bounded_writer_matches_retained_prefix() {
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_CDF_WRITER_OUTPUT").unwrap());
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
        let module=ctx.load_module(ptx).unwrap();let f=module.load_function("pf_exact_reuse_cdf").unwrap();
        records.push(json!({"variant":label,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));
        let mut run=Vec::new();
        for zero in [false,true,false] {
            let norm:Vec<f32>=(0..4*169).map(|i|if zero{0.}else{((i*37+i/169*13)%191) as f32/512.}).collect();
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
                if !enabled{cases.push(json!({"zero":zero,"compact":compact,"gate":gate,"batch":batch,"count":count,"sample_start":sample_start}));}
                run.push(out.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
            }}}}
        }
        results.push(run);
    }
    assert_eq!(results[0],results[1]);
    let result=json!({"exact":true,"cases_per_variant":results[0].len(),"cases":cases,"resources":records,"guard_and_untouched_slots_checked":true});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    println!("D09_WRITER {}",json!({"exact":true,"cases_per_variant":results[0].len(),"resources":records}));
}
