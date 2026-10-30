//! Compiler-resource sweep derived from the retained E004 kernel source.
//! Four modules share one CUDA context; no kernel is launched or timed.
#![cfg(feature = "gpu")]

use cudarc::{
    driver::CudaContext,
    nvrtc::{compile_ptx_with_opts, CompileOptions},
};
use std::io::Write;

const PLAIN_SIGNATURE: &str = "extern \"C\" __global__ void up_action(";
const BLOCK_THREADS: u32 = 128;
const E004_SOURCE_BYTES: usize = 22624;
const E004_SOURCE_FNV1A64: &str = "3f0594b037a1dda3";

fn fnv1a64(source: &str) -> String {
    let mut hash = 0xcbf29ce484222325u64;
    for &byte in source.as_bytes() {
        hash = (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3);
    }
    format!("{hash:016x}")
}

fn retained_baseline(source: &str) -> (String, Option<String>) {
    let count = source.matches("__launch_bounds__").count();
    assert!(count <= 1, "unexpected extra launch-bounds annotations");
    let removed = if count == 1 {
        let begin = source.find("__launch_bounds__").unwrap();
        assert!(
            source[..begin].ends_with("extern \"C\" __global__ "),
            "annotation must immediately follow the up_action global declaration"
        );
        let end = begin + source[begin..].find(')').expect("unterminated annotation") + 1;
        assert!(
            source[end..].starts_with(" void up_action("),
            "annotation must belong only to up_action"
        );
        let annotation = &source[begin..end];
        let arguments = annotation
            .strip_prefix("__launch_bounds__(")
            .unwrap()
            .strip_suffix(')')
            .unwrap()
            .split(',')
            .map(str::trim)
            .map(|value| {
                value
                    .parse::<u32>()
                    .expect("literal launch-bound arguments required")
            })
            .collect::<Vec<_>>();
        assert_eq!(
            arguments.len(),
            2,
            "expected max threads and minimum blocks"
        );
        assert_eq!(arguments[0], BLOCK_THREADS);
        assert!(arguments[1] > 0);
        Some(format!(" {annotation}"))
    } else {
        None
    };
    let baseline = match &removed {
        Some(annotation) => source.replacen(annotation.as_str(), "", 1),
        None => source.to_owned(),
    };
    assert_eq!(baseline.matches(PLAIN_SIGNATURE).count(), 1);
    assert!(!baseline.contains("__launch_bounds__"));
    // Fail closed if a different implementation sneaks into this resource-only
    // comparison. The preserved E004 kernel SHA256 is 8fe86cb859124592...c20d0.
    assert_eq!(
        baseline.len(),
        E004_SOURCE_BYTES,
        "retained E004 source length changed"
    );
    assert_eq!(
        fnv1a64(&baseline),
        E004_SOURCE_FNV1A64,
        "retained E004 source changed"
    );
    (baseline, removed)
}

#[test]
#[ignore = "manual CUDA register sweep for up_action bounds 128/9,10,12; no kernel launches"]
fn postflop_register_sweep() {
    let input = include_str!("../src/gpu/kernels.cu");
    let (baseline, removed_annotation) = retained_baseline(input);
    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for minimum_blocks in [None, Some(9u32), Some(10), Some(12)] {
        let (variant, source) = match minimum_blocks {
            Some(blocks) => {
                let signature = format!(
                    "extern \"C\" __global__ __launch_bounds__(128, {blocks}) void up_action("
                );
                let source = baseline.replacen(PLAIN_SIGNATURE, &signature, 1);
                assert_eq!(source.matches("__launch_bounds__").count(), 1);
                assert_eq!(source.matches(signature.as_str()).count(), 1);
                (format!("launch_bounds_128_{blocks}"), source)
            }
            None => ("baseline_no_launch_bounds".to_owned(), baseline.clone()),
        };
        let ptx = compile_ptx_with_opts(
            &source,
            CompileOptions {
                arch: Some(arch),
                ..Default::default()
            },
        )
        .unwrap();
        let module = ctx.load_module(ptx).unwrap();
        let function = module.load_function("up_action").unwrap();
        let blocks = function
            .occupancy_max_active_blocks_per_multiprocessor(BLOCK_THREADS, 0, None)
            .unwrap();
        println!(
            "METRIC_JSON {}",
            serde_json::json!({
                "schema_version": 1,
                "metrics": {},
                "experiment": "postflop_register_sweep",
                "area": "postflop",
                "kernel": "up_action",
                "source_variant": variant,
                "source_hash_algorithm": "fnv1a64",
                "source_fnv1a64": fnv1a64(&source),
                "source_bytes": source.len(),
                "input_source_fnv1a64": fnv1a64(input),
                "removed_input_annotation": removed_annotation,
                "baseline_source_fnv1a64": E004_SOURCE_FNV1A64,
                "baseline_source_bytes": E004_SOURCE_BYTES,
                "launch_bounds_min_blocks": minimum_blocks,
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
            })
        );
        std::io::stdout().flush().unwrap();
    }
}
