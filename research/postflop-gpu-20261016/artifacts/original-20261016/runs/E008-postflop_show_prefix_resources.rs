//! E008 compiler diagnostic, separate from the frozen solve evaluator.
//! POSTFLOP_SHOW_PREFIX_PTX_DIR must name a new absolute directory whose parent
//! exists. Occupancy is labeled theoretical with zero dynamic shared memory.
//! This test compiles/loads modules and queries resources; it never launches kernels.
#![cfg(feature = "gpu")]

use cudarc::{
    driver::CudaContext,
    nvrtc::{compile_ptx_with_opts, CompileOptions},
};
use serde_json::json;
use std::fs::OpenOptions;
use std::io::{self, Write};
use std::path::{Path, PathBuf};

const BASELINE_FNV1A64: u64 = 0x3f0594b037a1dda3;
const BASELINE_BYTES: usize = 22624;
const BLOCK_THREADS: u32 = 128;
const ORIGINAL_PREFIX: &str = concat!(
    "        if (threadIdx.x == 0) {\n",
    "            chunk_sum[0] = 0.f;\n",
    "            for (int t = 1; t <= (int)blockDim.x; t++) chunk_sum[t] += chunk_sum[t - 1];\n",
    "        }",
);
const REGISTER_PREFIX: &str = concat!(
    "        if (threadIdx.x == 0) {\n",
    "            chunk_sum[0] = 0.f;\n",
    "            float running = 0.f;\n",
    "            for (int t = 1; t <= (int)blockDim.x; t++) {\n",
    "                running = chunk_sum[t] + running;\n",
    "                chunk_sum[t] = running;\n",
    "            }\n",
    "        }",
);

fn fnv1a64(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf29ce484222325u64, |hash, &byte| {
        (hash ^ u64::from(byte)).wrapping_mul(0x100000001b3)
    })
}

fn write_new(path: &Path, bytes: &[u8]) {
    let mut file = OpenOptions::new().write(true).create_new(true).open(path)
        .unwrap_or_else(|err| panic!("refusing to overwrite or unable to create {}: {err}", path.display()));
    file.write_all(bytes).unwrap();
    file.sync_all().unwrap();
}

#[test]
#[ignore = "manual E008 compiler/occupancy inspection; no kernel launches"]
fn postflop_show_prefix_resources() {
    let included = include_str!("../src/gpu/kernels.cu");
    let mut baseline = included.to_owned();
    let included_prefix_variant = match (
        baseline.matches(ORIGINAL_PREFIX).count(), baseline.matches(REGISTER_PREFIX).count(),
    ) {
        (1, 0) => "original_shared_prefix",
        (0, 1) => {
            baseline = baseline.replacen(REGISTER_PREFIX, ORIGINAL_PREFIX, 1);
            "explicit_register_prefix"
        }
        counts => panic!("expected exactly one original or register prefix, never both: {counts:?}"),
    };

    // Permit the previous E006/E007 annotation only on up_action, then remove
    // it so this experiment compares the prefix against exact retained E004.
    const ACTION_SIGNATURE: &str = "extern \"C\" __global__ void up_action(";
    let mut removed_launch_bounds = String::new();
    for minimum_blocks in [8, 9] {
        let annotation = format!(" __launch_bounds__(128, {minimum_blocks})");
        let annotated_signature = format!("extern \"C\" __global__{annotation} void up_action(");
        let count = baseline.matches(annotated_signature.as_str()).count();
        assert!(count <= 1, "duplicate up_action launch-bounds signature");
        if count == 1 {
            assert!(removed_launch_bounds.is_empty(), "mixed launch-bounds transformations");
            baseline = baseline.replacen(annotated_signature.as_str(), ACTION_SIGNATURE, 1);
            removed_launch_bounds = annotation;
        }
    }
    assert!(!baseline.contains("__launch_bounds__"), "unrecognized launch-bounds change");
    assert_eq!(baseline.matches(ACTION_SIGNATURE).count(), 1);
    assert_eq!(baseline.matches(ORIGINAL_PREFIX).count(), 1);
    assert_eq!(baseline.matches(REGISTER_PREFIX).count(), 0);
    assert_eq!(baseline.len(), BASELINE_BYTES, "retained E004 source length changed");
    assert_eq!(fnv1a64(baseline.as_bytes()), BASELINE_FNV1A64,
        "retained E004 source identity changed");
    let candidate = baseline.replacen(ORIGINAL_PREFIX, REGISTER_PREFIX, 1);
    assert_eq!(candidate.matches(ORIGINAL_PREFIX).count(), 0);
    assert_eq!(candidate.matches(REGISTER_PREFIX).count(), 1);
    assert_eq!(candidate.replacen(REGISTER_PREFIX, ORIGINAL_PREFIX, 1), baseline);

    let output_dir = PathBuf::from(std::env::var_os("POSTFLOP_SHOW_PREFIX_PTX_DIR")
        .expect("set POSTFLOP_SHOW_PREFIX_PTX_DIR to a new absolute directory"));
    assert!(output_dir.is_absolute(), "PTX output directory must be absolute");
    std::fs::create_dir(&output_dir).unwrap_or_else(|err| {
        panic!("PTX output directory must be new with an existing parent ({}): {err}", output_dir.display())
    });
    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (variant, source) in [
        ("baseline_E004_shared_prefix", baseline.as_str()),
        ("candidate_E008_register_prefix", candidate.as_str()),
    ] {
        let ptx = compile_ptx_with_opts(source, CompileOptions {
            arch: Some(arch),
            ..Default::default()
        }).unwrap();
        let ptx_source = ptx.to_src();
        let ptx_path = output_dir.join(format!("{variant}.ptx"));
        write_new(&ptx_path, ptx_source.as_bytes());
        let module = ctx.load_module(ptx).unwrap();
        let function = module.load_function("up_show").unwrap();
        let blocks = function.occupancy_max_active_blocks_per_multiprocessor(
            BLOCK_THREADS, 0, None,
        ).unwrap();
        println!("METRIC_JSON {}", json!({
            "schema_version": 1, "metrics": {}, "experiment": "E008",
            "area": "postflop", "kernel": "up_show", "source_variant": variant,
            "source_fnv1a64": format!("{:016x}", fnv1a64(source.as_bytes())),
            "source_bytes": source.len(),
            "included_source_fnv1a64": format!("{:016x}", fnv1a64(included.as_bytes())),
            "included_prefix_variant": included_prefix_variant,
            "removed_up_action_annotation": removed_launch_bounds,
            "baseline_E004_fnv1a64": format!("{BASELINE_FNV1A64:016x}"),
            "baseline_E004_bytes": BASELINE_BYTES,
            "ptx_path": ptx_path.to_string_lossy(),
            "ptx_fnv1a64": format!("{:016x}", fnv1a64(ptx_source.as_bytes())),
            "architecture": arch, "device_ordinal": 0, "same_cuda_context": true,
            "compile_options": "architecture only; all other options default",
            "registers": function.num_regs().unwrap(),
            "local_bytes_per_thread": function.local_size_bytes().unwrap(),
            "static_shared_bytes": function.shared_size_bytes().unwrap(),
            "block_threads": BLOCK_THREADS, "dynamic_shared_bytes": 0,
            "occupancy_blocks_per_sm_128": blocks,
            "occupancy_warps_per_sm_128": blocks * (BLOCK_THREADS / 32),
            "occupancy_scope": "theoretical_zero_dynamic_shared_memory; real fixture launches require additional dynamic shared memory",
            "kernel_launches": 0, "performance_measurement": false,
            "scope": "Compiler resources and theoretical residency; not performance or numerical correctness"
        }));
        io::stdout().flush().unwrap();
    }
}
