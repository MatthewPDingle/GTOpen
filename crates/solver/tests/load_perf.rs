//! Fixed warm-load control, isolated from solving and report allocations.
use solver::Solver;
use std::time::Instant;

#[test]
#[ignore = "manual load-only control; run lifecycle fixture preparation first"]
fn warm_f32_load() {
    let file = concat!(env!("CARGO_MANIFEST_DIR"), "/target/research-fixtures/lifecycle.gto");
    for _ in 0..2 { std::hint::black_box(Solver::load(file).unwrap()); }
    let mut samples = Vec::new();
    for _ in 0..20 {
        let start = Instant::now();
        let s = Solver::load(file).unwrap();
        samples.push(start.elapsed().as_secs_f64() * 1000.0);
        assert_eq!(s.iteration, 18);
        assert_eq!(s.spot.tree.nodes.len(), 208516);
        std::hint::black_box(&s);
    }
    samples.sort_by(f64::total_cmp);
    let s = Solver::load(file).unwrap();
    let exploit = s.exploitability();
    assert_eq!(exploit.to_bits(), 0.36963080697589445f64.to_bits());
    println!("METRIC_JSON {}", serde_json::json!({
        "metrics":{"lifecycle.warm_load_ms":samples[samples.len()/2]},
        "samples_ms":samples, "iteration":s.iteration, "exploitability":exploit
    }));
}
