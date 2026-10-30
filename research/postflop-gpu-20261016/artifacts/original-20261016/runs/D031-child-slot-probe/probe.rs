//! D031: compile and query only; no kernel launches or numerical/performance claim.
use cudarc::{driver::CudaContext, nvrtc::{compile_ptx_with_opts, CompileOptions}};
use std::{fs::OpenOptions, io::Write};

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
    assert_eq!(baseline.len(), 22624);
    assert_eq!(fnv1a64(baseline), "3f0594b037a1dda3");
    let begin = baseline.find("__device__ __forceinline__ void up_action_impl(").unwrap();
    let end = baseline[begin..].find("// Copy the first n floats").unwrap() + begin;
    let original = &baseline[begin..end];
    let replacements = [
        ("cfv_slot[children[cs + a]]", "child_cfv_slots[cs + a]", 4),
        ("const u32* __restrict__ children,", "const u32* __restrict__ child_cfv_slots,", 2),
        (", children, regrets_p", ", child_cfv_slots, regrets_p", 4),
    ];
    let mut mapped = original.to_owned();
    for (old, new, count) in replacements {
        assert_eq!(mapped.matches(old).count(), count);
        mapped = mapped.replace(old, new);
    }
    assert_eq!(candidate, format!("{}{}{}", &baseline[..begin], mapped, &baseline[end..]));
    let ctx = CudaContext::new(0).unwrap();
    let device = ctx.name().unwrap();
    assert_eq!(device, "NVIDIA GeForce RTX 5090");
    let (major, minor) = ctx.compute_capability().unwrap();
    assert_eq!((major, minor), (12, 0));
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (variant, source) in [("baseline", baseline), ("candidate", candidate)] {
        let ptx = compile_ptx_with_opts(source, CompileOptions {
            arch: Some(arch), ..Default::default()
        }).unwrap();
        let mut out = OpenOptions::new().write(true).create_new(true)
            .open(format!("{variant}.ptx")).unwrap();
        out.write_all(ptx.to_src().as_bytes()).unwrap();
        out.flush().unwrap();
        let module = ctx.load_module(ptx).unwrap();
        let f = module.load_function("up_action").unwrap();
        let blocks = f.occupancy_max_active_blocks_per_multiprocessor(128, 0, None).unwrap();
        println!("METRIC_JSON {}", serde_json::json!({
            "schema_version": 1, "experiment": "D031", "area": "postflop",
            "source_variant": variant, "source_fnv1a64": fnv1a64(source),
            "source_bytes": source.len(), "kernel": "up_action", "architecture": arch,
            "device": device, "device_ordinal": 0, "same_cuda_context": true,
            "compile_options": "architecture only; all other CompileOptions default",
            "registers": f.num_regs().unwrap(),
            "local_bytes_per_thread": f.local_size_bytes().unwrap(),
            "static_shared_bytes": f.shared_size_bytes().unwrap(),
            "block_threads": 128, "dynamic_shared_bytes": 0,
            "occupancy_blocks_per_sm_128": blocks, "occupancy_warps_per_sm_128": blocks * 4,
            "kernel_launches": 0, "solver_executions": 0,
            "performance_measurement": false, "numerical_validation": "not executed",
            "scope": "Compiler resources and theoretical residency only; zero dynamic shared matches up_action launch."
        }));
        std::io::stdout().flush().unwrap();
    }
}
