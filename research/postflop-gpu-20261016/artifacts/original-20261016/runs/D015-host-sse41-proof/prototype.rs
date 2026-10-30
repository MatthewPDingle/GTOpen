use std::{hint::black_box, time::Instant};
mod baseline;
mod candidate;
include!("corpus_constants.rs");
include!("corpus.rs");

// Stable assembly labels. Both measured functions take the same call boundary.
#[no_mangle]
#[inline(never)]
pub fn d015_baseline_i16(src: &[f32], dst: &mut [i16]) -> f32 { baseline::encode_i16(src, dst) }
#[no_mangle]
#[inline(never)]
pub fn d015_candidate_i16(src: &[f32], dst: &mut [i16]) -> f32 { candidate::encode_i16(src, dst) }
#[no_mangle]
#[inline(never)]
pub fn d015_baseline_u16(src: &[f32], dst: &mut [u16]) -> f32 { baseline::encode_u16(src, dst) }
#[no_mangle]
#[inline(never)]
pub fn d015_candidate_u16(src: &[f32], dst: &mut [u16]) -> f32 { candidate::encode_u16(src, dst) }

#[derive(Clone, Copy)]
struct Hash(u64);
impl Hash {
    fn new() -> Self { Self(0xcbf2_9ce4_8422_2325) }
    fn bytes(&mut self, bytes: &[u8]) {
        for &b in bytes { self.0 = (self.0 ^ b as u64).wrapping_mul(0x100_0000_01b3); }
    }
    fn count(&mut self, n: usize) { self.bytes(&(n as u64).to_le_bytes()); }
}

fn proof() {
    let inject_failure = std::env::args().any(|arg| arg == "--inject-failure");
    let mut injected = false;
    let mut all = cases();
    let d010_cases = all.len();
    let special = [0, 0x8000_0000, 1, 0x8000_0001, 0x007f_ffff, 0x0080_0000,
        0x7f7f_ffff, 0xff7f_ffff, 0x7f80_0000, 0xff80_0000, 0x7fc0_1234, 0x7f80_0001];
    // Place each exceptional item and the unique maximum in every lane and tail.
    for n in 0..=20 {
        for at in 0..n {
            for &bits in &special {
                let mut values = vec![-0.0; n];
                values[at] = f32::from_bits(bits);
                all.push(Case { name: format!("lane_tail_n{n}_at{at}_{bits:08x}"), values });
                let mut values: Vec<f32> = (0..n).map(|i| (i % 3) as f32 - 1.0).collect();
                values[at] = f32::from_bits(bits);
                all.push(Case { name: format!("mixed_lane_n{n}_at{at}_{bits:08x}"), values });
            }
        }
    }
    let mut rng = Rng(SEED ^ 0xd014);
    for index in 0..4096 {
        let n = if index < 128 { index } else { (rng.next() % 4098) as usize };
        let values = (0..n).map(|_| f32::from_bits(rng.next())).collect();
        all.push(Case { name: format!("extra_random_{index}"), values });
    }
    let mut inputs = Hash::new();
    let mut output = Hash::new();
    let mut cases_hash = Hash::new();
    let mut values_count = 0usize;
    let mut guards = 0usize;
    for case in &all {
        let n = case.values.len();
        values_count += n;
        cases_hash.count(case.name.len()); cases_hash.bytes(case.name.as_bytes()); cases_hash.count(n);
        inputs.count(n);
        let before: Vec<u32> = case.values.iter().map(|v| v.to_bits()).collect();
        for &bits in &before { inputs.bytes(&bits.to_le_bytes()); }
        let mut want_i = vec![GUARD as i16; n + 2 * GUARD_WORDS];
        let mut got_i = want_i.clone();
        let mut want_u = vec![GUARD; n + 2 * GUARD_WORDS];
        let mut got_u = want_u.clone();
        let range = GUARD_WORDS..GUARD_WORDS + n;
        let want_is = d015_baseline_i16(&case.values, &mut want_i[range.clone()]);
        let got_is = d015_candidate_i16(&case.values, &mut got_i[range.clone()]);
        let want_us = d015_baseline_u16(&case.values, &mut want_u[range.clone()]);
        let got_us = d015_candidate_u16(&case.values, &mut got_u[range.clone()]);
        if inject_failure && !injected && n > 0 {
            got_i[GUARD_WORDS] ^= 1;
            injected = true;
        }
        assert_eq!(got_is.to_bits(), want_is.to_bits(), "i16 scale {}", case.name);
        assert_eq!(got_us.to_bits(), want_us.to_bits(), "u16 scale {}", case.name);
        assert_eq!(got_i, want_i, "i16 words {}", case.name);
        assert_eq!(got_u, want_u, "u16 words {}", case.name);
        for at in (0..GUARD_WORDS).chain(GUARD_WORDS + n..n + 2 * GUARD_WORDS) {
            assert_eq!(got_i[at] as u16, GUARD, "i16 guard {}", case.name);
            assert_eq!(got_u[at], GUARD, "u16 guard {}", case.name);
            guards += 2;
        }
        assert_eq!(before, case.values.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), "input bits {}", case.name);
        output.count(n);
        for v in got_i { output.bytes(&v.to_le_bytes()); }
        output.bytes(&got_is.to_bits().to_le_bytes());
        for v in got_u { output.bytes(&v.to_le_bytes()); }
        output.bytes(&got_us.to_bits().to_le_bytes());
    }
    println!("{{\"stage\":\"proof\",\"exact\":true,\"d010_cases\":{d010_cases},\"cases_per_type\":{},\"values_per_type\":{values_count},\"q_words_compared\":{},\"scale_bits_compared\":{},\"guard_words_checked\":{guards},\"input_bits_unchanged\":true,\"seed\":\"{SEED:016x}\",\"case_manifest_fnv64\":\"{:016x}\",\"input_fnv64\":\"{:016x}\",\"output_fnv64\":\"{:016x}\"}}",
        all.len(), values_count * 2, all.len() * 2, cases_hash.0, inputs.0, output.0);
}

fn bench_i(f: fn(&[f32], &mut [i16]) -> f32, src: &[Vec<f32>], reps: usize) -> f64 {
    let mut dst = vec![0i16; src[0].len()];
    let started = Instant::now();
    for rep in 0..reps {
        let scale = f(black_box(&src[rep % src.len()]), black_box(&mut dst));
        black_box(scale); black_box(&dst);
    }
    started.elapsed().as_secs_f64() * 1e9 / reps as f64
}
fn bench_u(f: fn(&[f32], &mut [u16]) -> f32, src: &[Vec<f32>], reps: usize) -> f64 {
    let mut dst = vec![0u16; src[0].len()];
    let started = Instant::now();
    for rep in 0..reps {
        let scale = f(black_box(&src[rep % src.len()]), black_box(&mut dst));
        black_box(scale); black_box(&dst);
    }
    started.elapsed().as_secs_f64() * 1e9 / reps as f64
}
fn benchmark() {
    let mut rng = Rng(SEED ^ 0xbec4);
    // Registered 257/319 hands times 2/3 actions plus representative 2-4 action blocks.
    for n in [512usize, 514, 638, 682, 768, 771, 957, 1023, 1024, 1366, 1536, 2048, 2049, 2732] {
        for mode in ["positive_zero", "finite"] {
            let src: Vec<Vec<f32>> = (0..8).map(|_| (0..n).map(|_| if mode == "positive_zero" { 0.0 }
                else { ((rng.next() % 200_001) as i32 - 100_000) as f32 / 64.0 }).collect()).collect();
            let reps = (2_000_000 / n).max(1024);
            for signed in [true, false] {
                let src: Vec<Vec<f32>> = src.iter().map(|block| block.iter()
                    .map(|&v| if signed { v } else { v.abs() }).collect()).collect();
                // Warm both paths, then alternate which is first in each matched pair.
                if signed { black_box(bench_i(d015_baseline_i16, &src, 32)); black_box(bench_i(d015_candidate_i16, &src, 32)); }
                else { black_box(bench_u(d015_baseline_u16, &src, 32)); black_box(bench_u(d015_candidate_u16, &src, 32)); }
                for pair in 0..9 {
                    let order = if pair % 2 == 0 { [false, true] } else { [true, false] };
                    for candidate in order {
                        let ns = if signed {
                            bench_i(if candidate { d015_candidate_i16 } else { d015_baseline_i16 }, &src, reps)
                        } else {
                            bench_u(if candidate { d015_candidate_u16 } else { d015_baseline_u16 }, &src, reps)
                        };
                        println!("{{\"stage\":\"timing\",\"type\":\"{}\",\"mode\":\"{mode}\",\"length\":{n},\"pair\":{pair},\"candidate_first\":{},\"variant\":\"{}\",\"reps\":{reps},\"ns_per_block\":{ns:.6}}}",
                            if signed { "i16" } else { "u16" }, pair % 2 != 0, if candidate { "sse41" } else { "baseline" });
                    }
                }
            }
        }
    }
}
fn main() {
    if !candidate::available() {
        println!("{{\"stage\":\"unsupported\",\"sse4_1\":false,\"candidate_executed\":false}}");
        std::process::exit(3);
    }
    println!("{{\"stage\":\"feature_gate\",\"sse4_1\":true,\"runtime_guarded\":true,\"portable_fallback\":true}}");
    // A mismatch panics before benchmarks, producing failure and no exact-success record.
    proof();
    if std::env::args().any(|arg| arg == "--proof-only") { return; }
    benchmark();
    println!("{{\"stage\":\"complete\",\"diagnostic_only\":true,\"end_to_end_claim\":false}}");
}
