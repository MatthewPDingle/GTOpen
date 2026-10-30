//! D021 resource-only derivative of the preserved E006 diagnostic. No launches.
use cudarc::{driver::CudaContext, nvrtc::{compile_ptx_with_opts, CompileOptions}};
use std::io::Write;

fn fnv1a64(source: &str) -> String {
    let mut hash = 0xcbf29ce484222325u64;
    for &byte in source.as_bytes() {
        hash = (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3);
    }
    format!("{hash:016x}")
}

fn main() {
    let baseline = include_str!("baseline.cu");
    let candidate = include_str!("candidate.cu");
    assert!(candidate.starts_with(baseline));
    assert_eq!(candidate.matches("extern \"C\" __global__ void up_action_3(").count(), 1);
    assert!(!baseline.contains("up_action_3("));
    assert_eq!(baseline.matches("extern \"C\" __global__ void up_action(").count(), 1);
    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (variant, source, names) in [
        ("baseline", baseline, &["up_action"][..]),
        ("candidate", candidate, &["up_action", "up_action_3"][..]),
    ] {
        let ptx = compile_ptx_with_opts(source, CompileOptions {
            arch: Some(arch), ..Default::default()
        }).unwrap();
        std::fs::write(format!("{variant}.ptx"), ptx.to_src()).unwrap();
        let module = ctx.load_module(ptx).unwrap();
        for name in names {
            let f = module.load_function(name).unwrap();
            let blocks = f.occupancy_max_active_blocks_per_multiprocessor(128, 0, None).unwrap();
            println!("METRIC_JSON {}", serde_json::json!({
                "schema_version": 1, "experiment": "D021", "area": "postflop",
                "source_variant": variant, "source_fnv1a64": fnv1a64(source),
                "source_bytes": source.len(), "kernel": name, "architecture": arch,
                "device": ctx.name().unwrap(), "device_ordinal": 0, "same_cuda_context": true,
                "compile_options": "architecture only; all other options default",
                "registers": f.num_regs().unwrap(),
                "local_bytes_per_thread": f.local_size_bytes().unwrap(),
                "static_shared_bytes": f.shared_size_bytes().unwrap(),
                "block_threads": 128, "dynamic_shared_bytes": 0,
                "occupancy_blocks_per_sm_128": blocks, "occupancy_warps_per_sm_128": blocks * 4,
                "kernel_launches": 0, "performance_measurement": false,
                "scope": "Compiler resources and theoretical residency only; no numerical or performance qualification"
            }));
            std::io::stdout().flush().unwrap();
        }
    }
}
