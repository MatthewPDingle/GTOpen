//! CPU-only full-flop storage fixtures, not a strategy accuracy experiment.
//! SUBTREE OUTPUT_DIRECTORY. No CUDA, production session or user-save access.
use serde_json::{json, Value};
use solver::preflop::equity::class_label;
use solver::{parse_sizes, Algorithm, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::{path::Path, sync::Arc};

fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(args.len(), 2, "SUBTREE OUTPUT_DIRECTORY");
    let out = Path::new(&args[1]);
    assert!(!out.exists(), "Refuse to replace fixture output");
    std::fs::create_dir(out).unwrap();
    let data: Value = serde_json::from_slice(&std::fs::read(&args[0]).unwrap()).unwrap();
    let ranges: Vec<String> = (0..2).map(|p| {
        let weights: Vec<f64> = (0..169).map(|c| {
            data["incoming_class_mass"][p][c].as_f64().unwrap()
                / if c / 13 == c % 13 { 6. } else if c / 13 > c % 13 { 4. } else { 12. }
        }).collect();
        let max = weights.iter().copied().fold(0., f64::max);
        (0..169).filter(|&c| weights[c] / max >= 1e-5)
            .map(class_label).collect::<Vec<_>>().join(",")
    }).collect();
    let sizing = StreetSizing {
        bet: parse_sizes("50,75").unwrap(),
        raise: parse_sizes("100").unwrap(),
        donk: parse_sizes("50,75").unwrap(),
    };
    let mut rows = vec![];
    // Both boards belong to the DEVELOPMENT report47 panel. First is the
    // largest full-arena case in the menu50-75 planner; second adds a high
    // two-tone board and the other called pot. Selection uses no strategy.
    for (index, (board, pot, stack)) in [
        ("5c2h2d", 39.5, 182.),
        ("AcQd9d", 93.5, 155.),
    ].into_iter().enumerate() {
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board: board.into(), range_oop: ranges[0].clone(), range_ip: ranges[1].clone(),
            tree: TreeConfig {
                starting_pot: pot, effective_stack: stack, rake_pct: 0.04, rake_cap: 6.,
                max_raises: 1, oop: [sizing.clone(), sizing.clone(), sizing.clone()],
                ip: [sizing.clone(), sizing.clone(), sizing.clone()], ..Default::default()
            },
        }, Some(2_000_000)).unwrap());
        let mut solver = Solver::new(spot);
        solver.algo = Algorithm::CfrPlus;
        solver.use_isomorphism = false;
        assert!(solver.arena_bytes() < 2_000_000_000);
        let started = std::time::Instant::now();
        for iteration in 1..=1000 {
            solver.iterate();
            if [1, 100, 1000].contains(&iteration) {
                let path = out.join(format!("fixture-{index}-{iteration}.gto"));
                assert!(!path.exists());
                solver.save(path.to_str().unwrap()).unwrap();
                let row = json!({"board":board,"pot":pot,"iteration":iteration,
                    "file":path.file_name().unwrap().to_str().unwrap(),
                    "arena_bytes":solver.arena_bytes(),"nodes":solver.spot.tree.nodes.len(),
                    "hands":[solver.spot.hands[0].len(),solver.spot.hands[1].len()],
                    "seconds":started.elapsed().as_secs_f64()});
                println!("{row}");
                rows.push(row);
                std::fs::write(out.join("fixtures.json"), serde_json::to_vec_pretty(&json!({
                    "rows":rows,"storage":"F32","algorithm":"CFR+","future_card_isomorphism":false,
                    "complete":index == 1 && iteration == 1000,
                    "note":"Full-flop CPU storage fixtures, fixed uniform weights on registered entry support. No convergence, changing-range, native pager, isolated speed or preflop accuracy claim."
                })).unwrap()).unwrap();
            }
        }
    }
}
