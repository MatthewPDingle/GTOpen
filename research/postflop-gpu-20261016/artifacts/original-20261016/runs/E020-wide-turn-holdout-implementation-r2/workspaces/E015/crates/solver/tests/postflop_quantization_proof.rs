//! Isolated experimental encoding proof, not a solver or performance benchmark.
//! cargo test --release -p solver --features gpu --test postflop_quantization_proof -- --ignored --nocapture --test-threads=1
#![cfg(feature = "gpu")]

use cudarc::driver::{CudaContext, LaunchConfig, PushKernelArg};
use cudarc::nvrtc::{compile_ptx_with_opts, CompileOptions};
use serde_json::json;
use solver::store::{encode_i16, encode_u16};
use std::io::Write;

const SOURCE: &str = include_str!("fixtures/postflop_quantization_prototype.cu");
const CPU_SOURCE: &str = include_str!("../src/store.rs");
const SEED: u64 = 0x5eed_2026_1016_f00d;
const GUARD: u16 = 0xa55a;
const GUARD_WORDS: usize = 3;
const LENGTHS: &[usize] = &[
    0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128, 129,
    255, 256, 257, 511, 512, 513, 1023, 1024, 1025, 4095, 4096, 4097,
];

#[derive(Clone, Copy)]
struct Hash(u64);
impl Hash {
    fn new() -> Self { Self(0xcbf2_9ce4_8422_2325) }
    fn bytes(&mut self, bytes: &[u8]) {
        for &byte in bytes { self.0 = (self.0 ^ byte as u64).wrapping_mul(0x100_0000_01b3); }
    }
    fn u64(&mut self, value: u64) { self.bytes(&value.to_le_bytes()); }
    fn hex(self) -> String { format!("{:016x}", self.0) }
}
fn bytes_hash(bytes: &[u8]) -> String {
    let mut hash = Hash::new();
    hash.bytes(bytes);
    hash.hex()
}
fn words_hash(words: &[u16], scales: &[f32]) -> String {
    let mut hash = Hash::new();
    hash.u64(words.len() as u64);
    for &word in words { hash.bytes(&word.to_le_bytes()); }
    hash.u64(scales.len() as u64);
    for &scale in scales { hash.bytes(&scale.to_bits().to_le_bytes()); }
    hash.hex()
}
fn metric(value: serde_json::Value) {
    println!("METRIC_JSON {value}");
    std::io::stdout().flush().unwrap();
}

struct Case { name: String, values: Vec<f32> }
fn add(cases: &mut Vec<Case>, name: impl Into<String>, values: Vec<f32>) {
    cases.push(Case { name: name.into(), values });
}
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u32 {
        self.0 = self.0.wrapping_add(0x9e37_79b9_7f4a_7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
        ((z ^ (z >> 31)) >> 32) as u32
    }
}

fn cases() -> Vec<Case> {
    let mut cases = Vec::new();
    let specials = [
        0, 0x8000_0000, 1, 0x8000_0001, 0x007f_ffff, 0x807f_ffff,
        0x0080_0000, 0x8080_0000, 0x3f80_0000, 0xbf80_0000,
        0x7f7f_ffff, 0xff7f_ffff, 0x7f80_0000, 0xff80_0000,
        0x7fc0_0000, 0xffc0_0123, 0x7f80_0001, 0xff80_0001,
    ];
    add(&mut cases, "empty", vec![]);
    for &bits in &specials {
        add(&mut cases, format!("singleton_{bits:08x}"), vec![f32::from_bits(bits)]);
    }
    for &length in LENGTHS {
        add(&mut cases, format!("signed_zeros_{length}"),
            (0..length).map(|i| if i % 2 == 0 { 0.0 } else { -0.0 }).collect());
        add(&mut cases, format!("special_cycle_{length}"),
            (0..length).map(|i| f32::from_bits(specials[i % specials.len()])).collect());
        add(&mut cases, format!("all_nan_{length}"),
            (0..length).map(|i| f32::from_bits(specials[14 + i % 4])).collect());
        add(&mut cases, format!("negative_u16_{length}"),
            (0..length).map(|i| -((i % 65535 + 1) as f32)).collect());
    }
    // Every zero/NaN/negative U16 item is also exercised with a finite positive max.
    for &bits in &specials {
        add(&mut cases, format!("mixed_finite_{bits:08x}"),
            vec![1.0, f32::from_bits(bits), -1.0, 0.0]);
    }
    // With max == C, k == 1: half-integers and their adjacent f32s are exact ties.
    for limit in [32767u32, 65535u32] {
        let mut values = vec![limit as f32];
        for n in [0u32, 1, 2, 3, 126, 127, 128, 129, 1023, 16383, 32765, 65533] {
            if n >= limit { continue; }
            let bits = (n as f32 + 0.5).to_bits();
            for nearby in [bits - 1, bits, bits + 1] {
                values.push(f32::from_bits(nearby));
                values.push(-f32::from_bits(nearby));
            }
        }
        add(&mut cases, format!("ties_adjacent_max_{limit}"), values);
    }
    for bits in [1u32, 2, 0x007f_ffff, 0x0080_0000, 0x0200_0000, 0x0400_0000] {
        let tiny = f32::from_bits(bits);
        add(&mut cases, format!("tiny_scale_{bits:08x}"),
            vec![tiny, -tiny, 0.0, -0.0, tiny * 0.5, -tiny * 0.5,
                 f32::from_bits(0x7fc0_0123), f32::from_bits(0xff80_0001)]);
    }
    add(&mut cases, "max_finite_and_tiny", vec![
        f32::MAX, -f32::MAX, f32::MIN_POSITIVE, -f32::MIN_POSITIVE,
        f32::from_bits(1), -f32::from_bits(1), 1.0, -1.0, 0.0, -0.0,
    ]);
    // Large tails make each CTA process many strided items as well as partial lanes.
    for length in [65537usize, 131071] {
        add(&mut cases, format!("long_tail_{length}"),
            (0..length).map(|i| ((i % 4093) as i32 - 2046) as f32 / 32.0).collect());
    }

    let mut rng = Rng(SEED);
    for index in 0..2048 {
        let length = if index % 2 == 0 { LENGTHS[index % LENGTHS.len()] }
            else { (rng.next() % 2050) as usize };
        let mode = index % 8;
        let values = (0..length).map(|_| {
            let bits = rng.next();
            match mode {
                0 => f32::from_bits(bits), // Unrestricted bits, including exceptional values.
                1 => f32::from_bits((bits & 0x807f_ffff) | (((rng.next() % 254) + 1) << 23)),
                2 => f32::from_bits(bits & 0x803f_ffff), // Signed subnormals, k overflows.
                3 => f32::from_bits((bits & 0x807f_ffff) | 0x7f00_0000),
                4 => f32::from_bits(specials[bits as usize % specials.len()]),
                5 => (bits % 1_000_003) as f32 / 1024.0,
                6 => -((bits % 1_000_003) as f32 / 1024.0),
                _ => ((bits % 65535) as i32 - 32767) as f32 + 0.5,
            }
        }).collect();
        add(&mut cases, format!("random_{index:04}_mode_{mode}"), values);
    }
    cases
}

#[test]
#[ignore = "isolated CUDA numerical proof; run serially on the research GPU"]
fn postflop_quantization_matches_cpu() {
    let cases = cases();
    let mut data = Vec::new();
    let mut offsets = Vec::new();
    let mut lengths = Vec::new();
    let mut manifest = Hash::new();
    let mut input = Hash::new();
    let mut values_count = 0usize;
    for case in &cases {
        manifest.u64(case.name.len() as u64);
        manifest.bytes(case.name.as_bytes());
        manifest.u64(case.values.len() as u64);
        input.u64(case.values.len() as u64);
        for &value in &case.values { input.bytes(&value.to_bits().to_le_bytes()); }
        data.extend(std::iter::repeat_n(f32::from_bits(0x7fc0_55aa), GUARD_WORDS));
        offsets.push(data.len() as u64);
        lengths.push(u32::try_from(case.values.len()).unwrap());
        data.extend_from_slice(&case.values);
        data.extend(std::iter::repeat_n(f32::from_bits(0x7fc0_55aa), GUARD_WORDS));
        values_count += case.values.len();
    }
    metric(json!({
        "experiment": "postflop_quantization_proof", "stage": "prepared",
        "seed": format!("{SEED:016x}"), "cases": cases.len(), "values_per_type": values_count,
        "empty_cases": lengths.iter().filter(|&&n| n == 0).count(),
        "case_manifest_fnv64": manifest.hex(), "input_fnv64": input.hex(),
        "cuda_source_fnv64": bytes_hash(SOURCE.as_bytes()),
        "cpu_oracle_source_fnv64": bytes_hash(CPU_SOURCE.as_bytes()),
        "performance_measurement": false,
    }));

    let context = CudaContext::new(0).unwrap();
    let stream = context.new_stream().unwrap();
    let (major, minor) = context.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let ptx = compile_ptx_with_opts(SOURCE, CompileOptions {
        arch: Some(arch), ftz: Some(false), prec_div: Some(true),
        use_fast_math: Some(false), ..Default::default()
    }).unwrap();
    let module = context.load_module(ptx).unwrap();
    let d_data = stream.clone_htod(&data).unwrap();
    let d_offsets = stream.clone_htod(&offsets).unwrap();
    let d_lengths = stream.clone_htod(&lengths).unwrap();

    for signed in [true, false] {
        let variant = if signed { "i16" } else { "u16" };
        let mut expected = vec![GUARD; data.len()];
        let mut expected_scales = Vec::with_capacity(cases.len());
        for (case, &offset) in cases.iter().zip(&offsets) {
            let output = &mut expected[offset as usize..offset as usize + case.values.len()];
            let scale = if signed {
                let mut q = vec![0i16; case.values.len()];
                let scale = encode_i16(&case.values, &mut q);
                for (word, value) in output.iter_mut().zip(q) { *word = value as u16; }
                scale
            } else { encode_u16(&case.values, output) };
            expected_scales.push(scale);
        }
        let initial = vec![GUARD; data.len()];
        let mut d_words = stream.clone_htod(&initial).unwrap();
        let mut d_scales = stream.clone_htod(&vec![f32::from_bits(0x7fc0_dead); cases.len()]).unwrap();
        let function = module.load_function(if signed { "quantize_i16_proof" } else { "quantize_u16_proof" }).unwrap();
        unsafe {
            stream.launch_builder(&function).arg(&d_data).arg(&d_offsets).arg(&d_lengths)
                .arg(&mut d_words).arg(&mut d_scales)
                .launch(LaunchConfig { grid_dim: (cases.len() as u32, 1, 1),
                    block_dim: (128, 1, 1), shared_mem_bytes: 0 }).unwrap();
        }
        let actual = stream.clone_dtoh(&d_words).unwrap();
        let actual_scales = stream.clone_dtoh(&d_scales).unwrap();
        stream.synchronize().unwrap();
        for (index, case) in cases.iter().enumerate() {
            assert_eq!(actual_scales[index].to_bits(), expected_scales[index].to_bits(),
                "{variant} scale mismatch case={index} name={} length={}", case.name, case.values.len());
            let start = offsets[index] as usize;
            for (i, value) in case.values.iter().enumerate() {
                assert_eq!(actual[start + i], expected[start + i],
                    "{variant} word mismatch case={index} name={} element={i} input_bits={:08x} scale_bits={:08x}",
                    case.name, value.to_bits(), expected_scales[index].to_bits());
            }
            for i in (start - GUARD_WORDS..start).chain(start + case.values.len()..start + case.values.len() + GUARD_WORDS) {
                assert_eq!(actual[i], GUARD, "{variant} guard corruption case={index} name={} flat_index={i}", case.name);
            }
        }
        let expected_hash = words_hash(&expected, &expected_scales);
        let actual_hash = words_hash(&actual, &actual_scales);
        assert_eq!(expected_hash, actual_hash);
        metric(json!({
            "experiment": "postflop_quantization_proof", "stage": "verified", "variant": variant,
            "cases": cases.len(), "values": values_count, "guard_words_checked": cases.len() * GUARD_WORDS * 2,
            "scale_bits_checked": cases.len(), "case_manifest_fnv64": manifest.hex(), "input_fnv64": input.hex(),
            "expected_output_fnv64": expected_hash, "gpu_output_fnv64": actual_hash,
            "cuda_source_fnv64": bytes_hash(SOURCE.as_bytes()), "cpu_oracle_source_fnv64": bytes_hash(CPU_SOURCE.as_bytes()),
            "device": context.name().unwrap(), "architecture": arch, "block_threads": 128,
            "ftz": false, "prec_div": true, "fast_math": false, "kernel_launches": 1,
            "exact": true, "performance_measurement": false,
            "scope": "standalone q bytes and scale bits only; no GpuSolver integration or speed claim",
        }));
    }
    let unchanged_input = stream.clone_dtoh(&d_data).unwrap();
    stream.synchronize().unwrap();
    let mut packed_input_hash = Hash::new();
    for (index, (&before, &after)) in data.iter().zip(&unchanged_input).enumerate() {
        assert_eq!(before.to_bits(), after.to_bits(), "input changed at flat_index={index}");
        packed_input_hash.bytes(&after.to_bits().to_le_bytes());
    }
    metric(json!({
        "experiment": "postflop_quantization_proof", "stage": "complete",
        "cases_per_type": cases.len(), "types_checked": 2, "kernel_launches": 2,
        "case_manifest_fnv64": manifest.hex(), "input_fnv64": input.hex(),
        "packed_input_including_guards_fnv64": packed_input_hash.hex(),
        "input_bits_checked": data.len(), "input_unchanged": true, "exact": true,
        "performance_measurement": false,
    }));
}
