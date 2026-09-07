"""Frozen raking cases; compile the current private routine without exposing API."""
from pathlib import Path
import subprocess
s=Path("crates/solver/src/query.rs").read_text(encoding="utf-8")
a=s.index("fn rake_to_target(")
b=s.index("#[derive(Debug, Clone, Serialize)]", a)
routine=s[a:b]
main=r'''
fn main() {
    use std::time::Instant;
    let mut seed = 0x9e3779b97f4a7c15u64;
    let mut rand = || { seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1); ((seed >> 32) % 1001) as f32 / 1000.0 };
    let mut cases = Vec::new();
    for na in 1..=8 {
        for nh in [1, 7, 53, 169] {
            for case in 0..16 {
                let mut sigma = vec![0.0f32; na * nh];
                for h in 0..nh {
                    let mut sum = 0.0f32;
                    for a in 0..na {
                        let v = if case % 3 == 0 && (h + a) % 3 == 0 { 0.0 } else { rand() };
                        sigma[a * nh + h] = v;
                        sum += v;
                    }
                    if sum > 0.0 { for a in 0..na { sigma[a * nh + h] /= sum; } }
                }
                let reach: Vec<f32> = (0..nh).map(|h| if case == 0 || (h + case) % 4 == 0 { 0.0 } else { rand() }).collect();
                let mut target: Vec<f32> = (0..na).map(|a| if case % 2 == 0 && a % 2 == 1 { 0.0 } else { rand() + 0.01 }).collect();
                let sum: f32 = target.iter().sum();
                for v in &mut target { *v /= sum; }
                cases.push((na, nh, sigma, reach, target));
            }
        }
    }
    let mut times = Vec::new();
    let mut expected_hash = None;
    for _ in 0..5 {
        let start = Instant::now();
        let mut hash = 0xcbf29ce484222325u64;
        for (na, nh, source, reach, target) in &cases {
            let mut sigma = source.clone();
            rake_to_target(&mut sigma, *na, *nh, reach, target);
            for v in sigma {
                for byte in v.to_bits().to_le_bytes() {
                    hash = (hash ^ byte as u64).wrapping_mul(0x100000001b3);
                }
            }
        }
        times.push(start.elapsed().as_secs_f64() * 1000.0);
        if let Some(expected) = expected_hash { assert_eq!(hash, expected); }
        expected_hash = Some(hash);
    }
    times.sort_by(f64::total_cmp);
    println!("METRIC_JSON {{\"metrics\":{{\"lifecycle.raking_ms\":{}}},\"raking_hash\":\"{:016x}\",\"cases\":{}}}", times[2], expected_hash.unwrap(), cases.len());
}
'''
out=Path("target/research-rake-check.rs")
out.parent.mkdir(exist_ok=True)
out.write_text(routine+main,encoding="utf-8",newline="\n")
exe=out.with_suffix(".exe").resolve()
subprocess.run(["rustc","-O","--edition=2021",str(out),"-o",str(exe)],check=True)
subprocess.run([str(exe)],check=True)
