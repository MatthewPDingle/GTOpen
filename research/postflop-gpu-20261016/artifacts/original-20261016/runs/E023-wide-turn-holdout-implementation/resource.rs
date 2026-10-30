//! E023 fixed holdout: compile/load/resources only. No kernel launch or numerical/timing claim.
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
    writeln!(out,"WIDE_RESOURCE {}",value).unwrap();out.flush().unwrap();
}
#[test]
#[ignore = "manual resource query; zero kernel launches"]
fn postflop_wide_turn_resources() {
    let sources=[("baseline",include_str!("E020-kernels.cu")),("candidate",include_str!("E023-kernels.cu"))];
    assert_eq!(sources[0].1.len(),22878);
    assert_eq!(fnv(sources[0].1),"fd544fbd87847b9c");
    let ctx=CudaContext::new(0).unwrap();
    let device=ctx.name().unwrap();assert_eq!(device,"NVIDIA GeForce RTX 5090");
    let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
    let arch: &'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let shared_block=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
    let shared_optin=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN).unwrap();
    let shared_sm=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_MULTIPROCESSOR).unwrap();
    let threads_block=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
    emit(serde_json::json!({"stage":"device","device":device,"architecture":arch,
        "max_shared_bytes_per_block_default":shared_block,"max_shared_bytes_per_block_optin":shared_optin,
        "max_shared_bytes_per_multiprocessor":shared_sm,"max_threads_per_block":threads_block,
        "kernel_launches":0,"performance_measurement":false}));
    // The exact fixed holdout shape, not the conservative1326 diagnostic.
    let shapes=[("wide-turn-full169",1128u32,1081u32,"fixed turn full-range counts, asserted independently by native evaluator")];
    for (variant,source) in sources {
        let ptx=compile_ptx_with_opts(source,CompileOptions {arch:Some(arch),..Default::default()}).unwrap();
        let mut file=OpenOptions::new().write(true).create_new(true).open(format!("{variant}.ptx")).unwrap();
        file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();
        let module=ctx.load_module(ptx).unwrap();
        let f=module.load_function("up_show").unwrap();
        let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();
        let static_shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
        for (shape,nh_o,m_max,scope) in shapes {
            let multiplier=16u32;
            let dynamic_shared=4*nh_o+multiplier*m_max;
            let combined=static_shared+dynamic_shared as i32;
            let ordinary_limit_fit=combined<=shared_block && max_threads>=128 && threads_block>=128;
            let blocks=f.occupancy_max_active_blocks_per_multiprocessor(128,dynamic_shared as usize,None).unwrap();
            emit(serde_json::json!({"stage":"resource","source_variant":variant,"source_fnv1a64":fnv(source),
                "source_bytes":source.len(),"kernel":"up_show","device":device,"architecture":arch,
                "compile_options":"architecture only; all other CompileOptions default, matching accepted production",
                "shape":shape,"shape_scope":scope,"nh_o":nh_o,"max_valid_opponent_hands":m_max,
                "registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":static_shared,
                "max_threads_per_block":max_threads,"block_threads":128,"dynamic_shared_bytes":dynamic_shared,
                "static_plus_dynamic_shared_bytes":combined,"fits_queried_default_shared_and_thread_limits":ordinary_limit_fit,
                "occupancy_blocks_per_sm_128":blocks,"occupancy_warps_per_sm_128":blocks*4,
                "kernel_launches":0,"solver_executions":0,"numerical_validation":"not executed",
                "performance_measurement":false,"scope":"compiler resources and theoretical occupancy only"}));
        }
        drop(f);drop(module);ctx.check_err().unwrap();
    }
    ctx.check_err().unwrap();
    emit(serde_json::json!({"stage":"complete","resource_rows":2,"source_variants":2,
        "kernel_launches":0,"solver_executions":0,"numerical_validation":"not executed",
        "performance_measurement":false,"candidate_accepted":false}));
}
