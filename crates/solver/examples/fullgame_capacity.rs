//! CPU-only sizing for heads-up preflop-to-river continuations. No CUDA.
//! Prints one JSON line per (pot, menu, board): nodes and state bytes.
use serde_json::json;
use solver::preflop::equity::class_label;
use solver::{gpu::stored_capacity_plan, parse_sizes, Spot, SpotConfig, StreetSizing, TreeConfig};

fn sizing(bet: &str, raise: &str) -> StreetSizing {
    StreetSizing { bet: parse_sizes(bet).unwrap(), raise: parse_sizes(raise).unwrap(), donk: vec![] }
}

fn main() {
    let full = (0..169).map(class_label).collect::<Vec<_>>().join(",");
    let boards = ["Kh7d2c", "Ks9s4d", "Qh8h3h", "TdTc5s", "9h8d7c"];
    // (name, pot, stack) in bb for a 100bb SB-vs-BB game.
    let pots = [("limp", 2.0, 99.0), ("srp3x", 6.0, 97.0), ("3bet", 18.0, 91.0), ("4bet", 44.0, 78.0)];
    // (name, [flop, turn, river] bet, raise, max_raises)
    let menus: [(&str, [&str; 3], &str, u8); 7] = [
        ("mid", ["33", "66", "75"], "3x", 1),
        ("rec", ["33", "75", "75"], "3x|a|a", 1),
        ("mid_noai", ["33", "66", "75"], "3x", 1),
        ("tiny", ["33", "75", "75"], "a", 1),
        ("small", ["33", "66", "75"], "3x", 2),
        ("pilot", ["50", "50", "50"], "100", 1),
        ("two", ["33 75", "66", "75"], "3x", 2),
    ];
    let only: Option<String> = std::env::args().nth(1);
    for (pname, pot, stack) in pots {
        for (mname, bets, raise, max_raises) in menus {
            if let Some(o) = &only { if o != mname { continue; } }
            for board in boards {
                let s = |i: usize| sizing(bets[i], raise.split('|').nth(i).unwrap_or(raise));
                let cfg = SpotConfig {
                    board: board.into(),
                    range_oop: std::env::var("RANGE_OOP").unwrap_or(full.clone()),
                    range_ip: std::env::var("RANGE_IP").unwrap_or(full.clone()),
                    tree: TreeConfig {
                        starting_pot: pot, effective_stack: stack, rake_pct: 0.05, rake_cap: 3.0,
                        oop: [s(0), s(1), s(2)], ip: [s(0), s(1), s(2)],
                        max_raises, add_allin: !matches!(mname, "mid_noai" | "rec"), ..Default::default()
                    },
                };
                let t = std::time::Instant::now();
                match Spot::new_with_limit(cfg, Some(20_000_000)) {
                    Ok(spot) => {
                        let plan = stored_capacity_plan(&spot);
                        println!("{}", json!({
                            "pot": pname, "menu": mname, "board": board,
                            "nodes": spot.tree.nodes.len(), "nh": [spot.hands[0].len(), spot.hands[1].len()],
                            "explicit_gb": plan["explicit_state_bytes"].as_u64().unwrap() as f64 / 1e9,
                            "canonical_gb": plan["canonical_state_bytes"].as_u64().unwrap() as f64 / 1e9,
                            "gpu_meta_gb": plan["retained_gpu_payload_bytes"].as_u64().unwrap() as f64 / 1e9,
                            "workspace_gb": plan["workspace_components_bytes"].as_array().unwrap().iter()
                                .map(|v| v.as_u64().unwrap()).sum::<u64>() as f64 / 1e9,
                            "host_gb": plan["host_retained_payload_bytes"].as_u64().unwrap() as f64 / 1e9,
                            "iso": plan["iso_active"], "secs": t.elapsed().as_secs_f64(),
                        }));
                    }
                    Err(e) => println!("{}", json!({"pot": pname, "menu": mname, "board": board, "error": e})),
                }
            }
        }
    }
}
