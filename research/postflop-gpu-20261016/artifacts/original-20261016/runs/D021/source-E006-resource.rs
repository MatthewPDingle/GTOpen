//! E006 compiler-resource diagnostic, separate from the frozen solve evaluator.
//! Loads two CUDA modules in one context; never launches a kernel.
#![cfg(feature = "gpu")]

use cudarc::{
    driver::CudaContext,
    nvrtc::{compile_ptx_with_opts, CompileOptions},
};
use std::io::Write;

fn fnv1a64(source: &str) -> String {
    let mut hash = 0xcbf29ce484222325u64;
    for &byte in source.as_bytes() {
        hash = (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3);
    }
    format!("{hash:016x}")
}

#[test]
#[ignore = "manual E006 CUDA register/occupancy inspection; no kernel launches"]
fn postflop_register_resources() {
    const ANNOTATION: &str = " __launch_bounds__(128, 8)";
    const SIGNATURE: &str =
        "extern \"C\" __global__ __launch_bounds__(128, 8) void up_action(";
    const BLOCK_THREADS: u32 = 128;

    let candidate = include_str!("../src/gpu/kernels.cu");
    assert_eq!(candidate.matches(ANNOTATION).count(), 1,
        "E006 requires exactly one launch-bounds annotation");
    assert_eq!(candidate.matches(SIGNATURE).count(), 1,
        "the annotation must belong to up_action");
    let baseline = candidate.replacen(ANNOTATION, "", 1);
    assert_eq!(baseline.matches("extern \"C\" __global__ void up_action(").count(), 1);
    assert!(!baseline.contains(ANNOTATION));

    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (variant, source) in [
        ("baseline_no_launch_bounds", baseline.as_str()),
        ("candidate_launch_bounds_128_8", candidate),
    ] {
        let ptx = compile_ptx_with_opts(source, CompileOptions {
            arch: Some(arch),
            ..Default::default()
        }).unwrap();
        let module = ctx.load_module(ptx).unwrap();
        let function = module.load_function("up_action").unwrap();
        let blocks = function.occupancy_max_active_blocks_per_multiprocessor(
            BLOCK_THREADS, 0, None,
        ).unwrap();
        println!("METRIC_JSON {}", serde_json::json!({
            "schema_version": 1,
            "metrics": {},
            "experiment": "E006",
            "area": "postflop",
            "kernel": "up_action",
            "source_variant": variant,
            "source_hash_algorithm": "fnv1a64",
            "source_fnv1a64": fnv1a64(source),
            "source_bytes": source.len(),
            "architecture": arch,
            "device_ordinal": 0,
            "same_cuda_context": true,
            "compile_options": "architecture only; all other options default",
            "registers": function.num_regs().unwrap(),
            "local_bytes_per_thread": function.local_size_bytes().unwrap(),
            "static_shared_bytes": function.shared_size_bytes().unwrap(),
            "block_threads": BLOCK_THREADS,
            "dynamic_shared_bytes": 0,
            "occupancy_blocks_per_sm_128": blocks,
            "occupancy_warps_per_sm_128": blocks * (BLOCK_THREADS / 32),
            "kernel_launches": 0,
            "performance_measurement": false,
            "scope": "Compiler resources and theoretical residency; not performance or numerical correctness"
        }));
        std::io::stdout().flush().unwrap();
    }
}
