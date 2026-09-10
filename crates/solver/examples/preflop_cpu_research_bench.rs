//! Pass-3 CPU controls. Frozen before evaluating CPU implementation candidates.
use solver::preflop::{multiway::CoupledDeck, equity::EquityTable, PreflopConfig, PreflopSolver};
use serde_json::json;
use std::{hint::black_box, sync::Arc, time::Instant};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("terminal") {
        let deck = CoupledDeck::shared();
        for opponents in [2usize, 3, 5, 7, 8] {
            for sparse in [false, true] {
                let ranges: Vec<Vec<f32>> = (0..opponents).map(|p| {
                    let mut r: Vec<f32> = (0..169).map(|h| {
                        if sparse && (h + p * 7) % 11 != 0 { 0.0 }
                        else { ((h * 13 + p * 17) % 31 + 1) as f32 }
                    }).collect();
                    let mass: f32 = r.iter().sum();
                    for v in &mut r { *v /= mass; }
                    r
                }).collect();
                black_box(deck.equities(black_box(&ranges)));
                let mut times = Vec::new();
                let mut result = [0.0; 169];
                for _ in 0..30 {
                    let start = Instant::now();
                    result = black_box(deck.equities(black_box(&ranges)));
                    times.push(start.elapsed().as_secs_f64() * 1000.0);
                }
                println!("BENCH {}", json!({"phase":"cpu_terminal", "opponents":opponents,
                    "sparse":sparse,"times_ms":times,"equities":result.to_vec()}));
            }
        }
        return;
    }
    let cfg: PreflopConfig = serde_json::from_slice(&std::fs::read(&args[1]).unwrap()).unwrap();
    let limit: u32 = args[2].parse().unwrap();
    let target: f64 = args[3].parse().unwrap();
    let bytes = std::fs::read("cache/preflop_eq169.bin").unwrap();
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    let eq = Arc::new(EquityTable::load_or_build("cache/preflop_eq169.bin", samples));
    let mut s = PreflopSolver::new(cfg, eq).unwrap();
    assert!(s.fit.is_some());
    let start = Instant::now();
    let mut times = Vec::new();
    for i in 1..=limit {
        let t = Instant::now();
        s.iterate();
        times.push(t.elapsed().as_secs_f64() * 1000.0);
        if i % 10 == 0 || i == limit {
            let t = Instant::now();
            let (gaps, evs) = s.gaps_and_evs();
            let total: f64 = gaps.iter().sum();
            println!("BENCH {}", json!({"phase":"cpu_solve","iteration":i,
                "elapsed_ms":start.elapsed().as_secs_f64()*1000.0,"check_ms":t.elapsed().as_secs_f64()*1000.0,
                "gaps":gaps,"evs":evs,"target":target,"reached":total<=target,"times_ms":times}));
            times.clear();
            if total <= target { break; }
        }
    }
    println!("BENCH {}", json!({"phase":"cpu_strategy","iteration":s.iteration,"strategy":s.average_strategy(0)}));
}
