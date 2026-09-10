//! Manual compiler/occupancy context for the coupled terminal launch sweep.
#![cfg(feature = "gpu")]
use cudarc::{driver::{CudaContext, sys}, nvrtc::{compile_ptx_with_opts, CompileOptions}};

#[test]
#[ignore = "manual CUDA compiler and occupancy inspection; not a solve benchmark"]
fn coupled_terminal_resources() {
    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let started = std::time::Instant::now();
    let ptx = compile_ptx_with_opts(include_str!("../src/preflop/kernels.cu"), CompileOptions {
        arch: Some(arch), ..Default::default()
    }).unwrap();
    let compile_ms = started.elapsed().as_secs_f64()*1000.0;
    let ptx_bytes = ptx.to_src().len();
    let before_load = std::time::Instant::now();
    let module = ctx.load_module(ptx).unwrap();
    let f = module.load_function("pf_multiway_terminal").unwrap();
    let load_ms = before_load.elapsed().as_secs_f64()*1000.0;
    let warp = ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_WARP_SIZE).unwrap() as u32;
    let threads_per_sm = ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR).unwrap() as u32;
    let max_threads = f.max_threads_per_block().unwrap() as u32;
    let occupancy: Vec<_> = [96u32,128,160,192,256,384,512].into_iter().map(|threads| {
        let active = if threads <= max_threads {
            Some(f.occupancy_max_active_blocks_per_multiprocessor(threads,0,None).unwrap())
        } else { None };
        serde_json::json!({
            "threads":threads,"warps_per_block":threads.div_ceil(warp),
            "active_blocks_per_sm":active,
            "resident_warps_upper_bound":active.map(|blocks|blocks*threads.div_ceil(warp)),
            "thread_occupancy_fraction":active.map(|blocks|(blocks*threads) as f64/threads_per_sm as f64),
            "max_hero_loop_passes":169u32.div_ceil(threads),
            "unused_threads_first_hero_pass":threads.saturating_sub(169),
        })
    }).collect();
    println!("COUPLED_TERMINAL_RESOURCES {}",serde_json::json!({
        "arch":arch,"registers_per_thread":f.num_regs().unwrap(),
        "local_bytes_per_thread":f.local_size_bytes().unwrap(),
        "static_shared_bytes":f.shared_size_bytes().unwrap(),
        "kernel_max_threads_per_block":max_threads,"device_threads_per_sm":threads_per_sm,
        "ptx_source_bytes":ptx_bytes,"compile_ms":compile_ms,"module_load_ms":load_ms,
        "occupancy":occupancy,
        "note":"Compiler resource/maximum occupancy estimates only; no kernel launch or solve timing."
    }));
}
