//! Build (or verify) the 3-way equity table cache for three_way_table_v1.
//!
//!     cargo run --release -p solver --example build_three_way_table
//!
//! PREFLOP_EQ3_SAMPLES overrides the boards per class triple (default 20000).
use solver::preflop::three_way::{ThreeWayTable, CACHE_PATH, DEFAULT_SAMPLES};

fn main() {
    let samples = std::env::var("PREFLOP_EQ3_SAMPLES").ok().and_then(|v| v.parse().ok()).unwrap_or(DEFAULT_SAMPLES);
    let start = std::time::Instant::now();
    let table = ThreeWayTable::load_or_build(CACHE_PATH, samples);
    println!("{CACHE_PATH}: {} boards per class triple, ready in {:.0} s", table.samples, start.elapsed().as_secs_f64());
}
