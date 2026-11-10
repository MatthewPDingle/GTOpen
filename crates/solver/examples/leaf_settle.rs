//! Research: how the learned flop corrections should follow the strategies.
//!
//!     cargo run --release -p solver --example leaf_settle -- 3 4000 100 50:0.3 50:1.0 50:lin
//!
//! SEATS is the number of seats, or SEATS,STACK,OPEN (default 100 bb deep,
//! opens to 2.5 bb). SCHEDULE is `INTERVAL:WEIGHT`: refresh the corrections
//! every INTERVAL iterations with WEIGHT on the newest net output (`lin` =
//! 2/(k+1), the average used before 2026-11). Every STEP iterations it
//! prints the gap against the blended corrections the solve iterates on
//! ("reported", what a solve showed before 2026-11), the gap against the
//! net's output at the current strategies ("real", what a solve shows now),
//! and how far the blend is from that output (fraction of the pot). The net
//! is LEAF_NET or the shipped one.
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver};
use std::{sync::Arc, time::Instant};

fn game(n: usize, stack: f64, open: f64, eq: Arc<EquityTable>) -> PreflopSolver {
    let names = ["UTG", "HJ", "CO", "BTN", "SB", "BB"];
    let positions: Vec<&str> = names[6 - n..].to_vec();
    let mut posts = vec![0.0; n];
    posts[n - 2] = 0.5;
    posts[n - 1] = 1.0;
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": positions, "stack": stack, "posts": posts, "limp": true, "open_raises": [open],
        "raise_mults": [3.0], "max_raises": 4, "add_allin": false, "rake_pct": 5.0, "rake_cap": 3.0,
        "no_flop_no_drop": true, "realization": "leafnet",
    })).unwrap();
    PreflopSolver::new(cfg, eq).unwrap()
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.len() < 4 {
        eprintln!("usage: leaf_settle SEATS ITERATIONS STEP INTERVAL:WEIGHT...");
        std::process::exit(1);
    }
    // SEATS or SEATS,STACK,OPEN (defaults 100 bb and 2.5 bb)
    let table: Vec<&str> = args[0].split(',').collect();
    let seats: usize = table[0].parse().expect("SEATS");
    let stack: f64 = table.get(1).map_or(100.0, |v| v.parse().expect("STACK"));
    let open: f64 = table.get(2).map_or(2.5, |v| v.parse().expect("OPEN"));
    let total: u32 = args[1].parse().expect("ITERATIONS");
    let step: u32 = args[2].parse().expect("STEP");
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", 20000));
    for spec in &args[3..] {
        let (interval, weight) = spec.split_once(':').expect("INTERVAL:WEIGHT");
        let interval: u32 = interval.parse().expect("INTERVAL");
        let weight: Option<f32> = if weight == "lin" { None } else { Some(weight.parse().expect("WEIGHT")) };
        let mut s = game(seats, stack, open, eq.clone());
        s.set_leaf_schedule(interval, weight);
        let t0 = Instant::now();
        println!("# seats {seats} stack {stack} open {open} nodes {} schedule {spec}", s.nodes.len());
        println!("iteration\treported\treal\tdrift\tseconds");
        for it in 1..=total {
            s.iterate();
            if it % step == 0 {
                let reported: f64 = s.gaps_and_evs().0.iter().sum();
                let (gaps, _, drift) = s.consistent_gaps_and_evs().unwrap();
                println!("{it}\t{reported:.5}\t{:.5}\t{drift:.5}\t{:.0}", gaps.iter().sum::<f64>(), t0.elapsed().as_secs_f64());
            }
        }
    }
}
