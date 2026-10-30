//! Solve a heads-up preflop-to-river game on the GPU.
//!
//! Usage: fullgame-cli <config.json> <iterations> [eval_every] [out.json]
//!
//! The config is a `FullGameConfig`; an empty `flops` list takes the first
//! `panel` canonical flops by systematic sampling, where `panel` is the
//! FULLGAME_PANEL env var (default 5). Writes the final evaluation and the
//! SB's first decision to out.json when given.

use solver::cards::canonical_flops_subset;
use solver::fullgame::{FullGame, FullGameConfig};
use solver::preflop::equity::{class_label, NUM_CLASSES};
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("usage: fullgame-cli <config.json> <iterations> [eval_every] [out.json]");
        std::process::exit(2);
    }
    let text = std::fs::read_to_string(&args[1]).unwrap_or_else(|e| panic!("{}: {e}", args[1]));
    let mut config: FullGameConfig = serde_json::from_str(&text).unwrap_or_else(|e| panic!("config: {e}"));
    let iterations: u32 = args[2].parse().expect("iterations");
    let every: u32 = args.get(3).map(|s| s.parse().expect("eval_every")).unwrap_or(50);
    if config.flops.is_empty() {
        let n = std::env::var("FULLGAME_PANEL").ok().and_then(|v| v.parse().ok()).unwrap_or(5);
        config.flops = canonical_flops_subset(n).into_iter().map(|(b, w)| (b, w as f64)).collect();
    }
    println!("flops: {}", config.flops.iter().map(|f| f.0.as_str()).collect::<Vec<_>>().join(" "));

    let vram_before = solver::gpu::vram_info_mb().map(|v| v.0);
    let start = Instant::now();
    let mut game = FullGame::build(config, &mut |m| println!("{m}")).unwrap_or_else(|e| {
        eprintln!("build failed: {e}");
        std::process::exit(1)
    });
    println!(
        "built {} flop lines, {} continuations, {:.2} GB on the GPU in {:.1}s",
        game.leaves.len(),
        game.continuations(),
        game.device_bytes() as f64 / 1e9,
        start.elapsed().as_secs_f64()
    );
    println!("  shared scratch {:.2} GB; {} continuations parked in {:.2} GB of host memory", game.scratch_bytes() as f64 / 1e9, game.parked(), game.host_bytes() as f64 / 1e9);
    if let (Some(before), Some((after, _))) = (vram_before, solver::gpu::vram_info_mb()) {
        println!("  device memory in use: {:.2} GB", before.saturating_sub(after) as f64 / 1e3);
    }
    for (i, l) in game.leaves.iter().enumerate() {
        println!(
            "  {:<44} pot {:>5.1} behind {:>5.1}  SB {:>3} / BB {:>3} classes  {:>6.2} GB",
            l.line, l.pot, l.behind,
            l.support[0].iter().filter(|&&x| x).count(),
            l.support[1].iter().filter(|&&x| x).count(),
            game.leaf_device_bytes(i) as f64 / 1e9
        );
    }

    let train = Instant::now();
    let mut last = None;
    for t in 1..=iterations {
        game.iterate().unwrap_or_else(|e| panic!("iteration {t}: {e}"));
        if let Some(seed) = game.config.support.clone() {
            if seed.expand_at.contains(&t) {
                let rebuilt = game.expand_support(seed.min_freq, &mut |m| println!("{m}"))
                    .unwrap_or_else(|e| panic!("expand support: {e}"));
                println!("iter {t:>5}  support grown on {} lines; {:.2} GB on the GPU, {} continuations parked in {:.2} GB of host memory", rebuilt.len(),
                    game.device_bytes() as f64 / 1e9, game.parked(), game.host_bytes() as f64 / 1e9);
            }
        }
        if t % every == 0 || t == iterations {
            let e0 = Instant::now();
            let ev = game.evaluate().unwrap_or_else(|e| panic!("evaluate: {e}"));
            println!(
                "iter {t:>5}  gap {:.5} bb (SB {:.5}, BB {:.5})  EV SB {:+.4} BB {:+.4}  outside {:.4}  [{:.1}s train, eval {:.1}s]",
                ev.gap_total, ev.gaps[0], ev.gaps[1], ev.evs[0], ev.evs[1], ev.outside_support,
                train.elapsed().as_secs_f64(), e0.elapsed().as_secs_f64()
            );
            last = Some(ev);
        }
    }

    let (actor, labels, sigma) = game.strategy(&[]).expect("root");
    let mut freq = vec![0.0; labels.len()];
    let mut combos = 0.0;
    for h in 0..NUM_CLASSES {
        let n = solver::preflop::equity::class_combos(h) as f64;
        combos += n;
        for a in 0..labels.len() {
            freq[a] += n * sigma[a * NUM_CLASSES + h];
        }
    }
    println!("seat {actor} first decision:");
    for (a, l) in labels.iter().enumerate() {
        println!("  {l:<12} {:.1}%", 100.0 * freq[a] / combos);
    }
    if let Some(path) = args.get(4) {
        let hands: Vec<_> = (0..NUM_CLASSES)
            .map(|h| serde_json::json!({
                "hand": class_label(h),
                "strategy": (0..labels.len()).map(|a| sigma[a * NUM_CLASSES + h]).collect::<Vec<_>>(),
            }))
            .collect();
        let out = serde_json::json!({
            "config": game.config, "evaluation": last, "root_actions": labels, "root": hands,
            "leaves": game.leaves.iter().map(|l| serde_json::json!({"line": l.line, "pot": l.pot, "behind": l.behind})).collect::<Vec<_>>(),
        });
        std::fs::write(path, serde_json::to_vec_pretty(&out).unwrap()).expect("write output");
    }
}
