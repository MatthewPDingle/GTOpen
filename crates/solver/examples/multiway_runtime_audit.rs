//! Isolated production-model audit/benchmark; never connects to the live server.
use serde_json::{json, Value};
use solver::preflop::equity::{class_combos, class_index, EquityTable};
use solver::preflop::multiway::CoupledDeck;
use solver::preflop::{PreflopConfig, PreflopSolver};
use std::sync::Arc;
use std::time::Instant;

fn main() {
    let node: Value = serde_json::from_str(
        &std::fs::read_to_string("research/multiway-equity-audit/node.json").unwrap(),
    )
    .unwrap();
    let actor = node["actor"].as_u64().unwrap() as usize;
    let opponents: Vec<Vec<f32>> = node["live"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .filter(|(p, l)| *p != actor && l.as_bool().unwrap())
        .map(|(p, _)| {
            let mut w: Vec<f32> = (0..169)
                .map(|h| {
                    node["reaches_all"][p][h].as_f64().unwrap() as f32 * class_combos(h) as f32
                })
                .collect();
            let total: f32 = w.iter().sum();
            for v in &mut w {
                *v /= total;
            }
            w
        })
        .collect();
    let model = CoupledDeck::shared();
    let t = Instant::now();
    let values = model.equities(&opponents);
    println!(
        "{}",
        json!({"cpu_terminal_ms":t.elapsed().as_secs_f64()*1000.0,
        "equities": ([("KQo",class_index(11,10,false)),("AQo",class_index(12,10,false)),("KQs",class_index(11,10,true)),("76s",class_index(5,4,true)),("AA",168)].map(|(h,i)|json!({"hand":h,"equity":values[i]})))})
    );
    let args: Vec<_> = std::env::args().collect();
    if !args.iter().any(|x| x == "--solve") {
        return;
    }
    let session: Value = serde_json::from_str(
        &std::fs::read_to_string("research/multiway-equity-audit/session.json").unwrap(),
    )
    .unwrap();
    let cfg: PreflopConfig = serde_json::from_value(session["config"].clone()).unwrap();
    let bytes = std::fs::read("cache/preflop_eq169.bin").unwrap();
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    // Never allow a research run to replace the production equity cache.
    std::fs::write("target/multiway-audit-eq.bin", &bytes).unwrap();
    let eq = Arc::new(EquityTable::load_or_build(
        "target/multiway-audit-eq.bin",
        samples,
    ));
    let mut solver = if args.iter().any(|x| x == "--resume") {
        PreflopSolver::load_game("target/multiway-corrected.gtop", eq).unwrap()
    } else {
        PreflopSolver::new(cfg, eq).unwrap()
    };
    let iterations = args
        .windows(2)
        .find(|a| a[0] == "--iterations")
        .map(|a| a[1].parse::<u32>().unwrap())
        .unwrap_or(3);
    #[cfg(feature = "gpu")]
    {
        let mut gpu = solver::preflop::gpu::PreflopGpu::new(&solver, 14000).unwrap();
        for i in 0..iterations {
            let t = Instant::now();
            gpu.iterate(&mut solver).unwrap();
            println!(
                "{}",
                json!({"iteration":solver.iteration,"seconds":t.elapsed().as_secs_f64()})
            );
            if (i + 1) % 25 == 0 || i + 1 == iterations {
                let (gaps, evs) = gpu.gaps_and_evs().unwrap();
                println!(
                    "{}",
                    json!({"iteration":solver.iteration,"gaps":gaps,"evs":evs})
                );
                gpu.sync_to_cpu(&mut solver).unwrap();
                solver.save_game("target/multiway-corrected.gtop").unwrap();
                if gaps.iter().sum::<f64>() < 0.005 {
                    break;
                }
            }
        }
        gpu.sync_to_cpu(&mut solver).unwrap();
        solver.save_game("target/multiway-corrected.gtop").unwrap();
        let view = solver.node_view(&[2, 0, 0, 0, 1, 1]).unwrap();
        std::fs::write(
            "target/multiway-corrected-node.json",
            serde_json::to_string_pretty(&view).unwrap(),
        )
        .unwrap();
    }
    #[cfg(not(feature = "gpu"))]
    {
        let _ = (&mut solver, iterations);
        panic!("--solve requires --features gpu");
    }
}
