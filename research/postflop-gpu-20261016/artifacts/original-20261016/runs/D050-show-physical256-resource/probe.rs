//! D050: same-context compiler/resources only. No kernel launch, solver or timing claim.
use cudarc::{driver::{CudaContext, sys::CUdevice_attribute as Attr},
    nvrtc::{compile_ptx_with_opts, CompileOptions}};
use std::{fs::OpenOptions, io::Write};

fn fnv(source: &str) -> String {
    let mut h=0xcbf29ce484222325u64;
    for b in source.bytes() {h=(h^u64::from(b)).wrapping_mul(0x100000001b3);}
    format!("{h:016x}")
}
fn emit(value: serde_json::Value) {
    let mut out=std::io::stdout().lock();
    writeln!(out,"D050_RESOURCE {}",value).unwrap();out.flush().unwrap();
}
fn main() {
    let sources=[("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))];
    assert_eq!(sources[0].1.len(),22878);
    assert_eq!(fnv(sources[0].1),"fd544fbd87847b9c");
    assert_eq!(sources[1].1.len(),23101);
    assert_eq!(fnv(sources[1].1),"b2c6a93ad4316e82");
    let baseline_scan = include_str!("baseline-scan.txt");
    let candidate_scan = include_str!("candidate-scan.txt");
    assert_eq!(sources[0].1.matches(baseline_scan).count(),1);
    assert_eq!(sources[1].1.matches(candidate_scan).count(),1);
    assert_eq!(sources[1].1.replace(candidate_scan,baseline_scan),sources[0].1);
    let ctx=CudaContext::new(0).unwrap();
    let device=ctx.name().unwrap();assert_eq!(device,"NVIDIA GeForce RTX 5090");
    let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
    let arch: &'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let shared_block=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
    let threads_block=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
    let (mut nvrtc_major,mut nvrtc_minor)=(0,0);
    // Public pinned cudarc sys API; this queries compiler identity, not a kernel.
    let nvrtc_status=unsafe {cudarc::nvrtc::sys::nvrtcVersion(&mut nvrtc_major,&mut nvrtc_minor)};
    assert_eq!(nvrtc_status,cudarc::nvrtc::sys::nvrtcResult::NVRTC_SUCCESS);
    emit(serde_json::json!({"stage":"device","device":device,"architecture":arch,
        "nvrtc_major":nvrtc_major,"nvrtc_minor":nvrtc_minor,
        "max_shared_bytes_per_block_default":shared_block,"max_threads_per_block":threads_block,
        "kernel_launches":0,"performance_measurement":false}));
    let shapes: &[(&str,u32)] = &[
        ("rainbow_p0",6300),("rainbow_p1",5060),
        ("wide_turn_1128_1081",21808),("valid_range_upper_bound1326",26520),
    ];
    for (variant,source) in sources {
        let threads: u32 = if variant == "baseline" {128} else {256};
        let ptx=compile_ptx_with_opts(source,CompileOptions {arch:Some(arch),..Default::default()}).unwrap();
        let mut file=OpenOptions::new().write(true).create_new(true).open(format!("{variant}.ptx")).unwrap();
        file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();
        let module=ctx.load_module(ptx).unwrap();
        let names:&[&str]=&["up_show"];
        for &name in names {
            let f=module.load_function(name).unwrap();
            let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();
            let static_shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
            for &(case_id,dynamic_shared) in shapes {
                let blocks=f.occupancy_max_active_blocks_per_multiprocessor(threads,dynamic_shared as usize,None).unwrap();
                emit(serde_json::json!({"stage":"resource","source_variant":variant,"source_fnv1a64":fnv(source),
                    "source_bytes":source.len(),"kernel":name,"device":device,"architecture":arch,"case_id":case_id,
                    "compile_options":"architecture only; all other CompileOptions default, matching accepted production",
                    "registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":static_shared,
                    "max_threads_per_block":max_threads,"block_threads":threads,"dynamic_shared_bytes":dynamic_shared,
                    "fits_queried_default_shared_and_thread_limits":static_shared as i64 + i64::from(dynamic_shared)<=i64::from(shared_block) && max_threads>=threads as i32 && threads_block>=threads as i32,
                    "occupancy_blocks_per_sm":blocks,"occupancy_warps_per_sm":blocks*(threads/32),
                    "kernel_launches":0,"solver_executions":0,"numerical_validation":"not executed",
                    "performance_measurement":false,"scope":"compiler resources and theoretical occupancy only"}));
            }
            drop(f);
        }
        drop(module);ctx.check_err().unwrap();
    }
    ctx.check_err().unwrap();
    emit(serde_json::json!({"stage":"complete","resource_rows":8,"source_variants":2,
        "kernel_launches":0,"solver_executions":0,"numerical_validation":"not executed",
        "performance_measurement":false,"candidate_accepted":false}));
}
