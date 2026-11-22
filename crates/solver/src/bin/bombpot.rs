//! Command line for the bomb pot solver pilot.
//!
//!   bombpot solve <config.json> [--rounds N] [--deals N] [--threads N]
//!       [--seed N] [--check-every N] [--challenge DEALS] [--exact]
//!       [--report out.json] [--max-gb G]
//!
//! `config.json` is a `BpConfig`: boards, the betting tree and the hand
//! grouping. Progress goes to stdout as one JSON object per line.

use std::time::Instant;

use solver::bombpot::exact::Exact2;
use solver::bombpot::solver::{BpConfig, BpSolver, Challenger};
use solver::bombpot::tree::{KIND_ACTION, MAX_ACTIONS};
use solver::tree::Action;

fn arg<T: std::str::FromStr>(args: &[String], name: &str, default: T) -> T {
    args.iter()
        .position(|a| a == name)
        .and_then(|i| args.get(i + 1))
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

fn label(a: &Action) -> String {
    match a {
        Action::Fold => "fold".into(),
        Action::Check => "check".into(),
        Action::Call(x) => format!("call {x:.2}"),
        Action::Bet(x) => format!("bet {x:.2}"),
        Action::Raise(x) => format!("raise {x:.2}"),
    }
}

/// First decisions worth reading: each seat when checked to, and each seat
/// facing one bet after everyone in between has folded.
fn key_lines(s: &BpSolver) -> Vec<Vec<usize>> {
    let n = s.players();
    let mut lines = Vec::new();
    for k in 0..n {
        lines.push(vec![0; k]);
    }
    for bettor in 0..n {
        let at = s.walk(&vec![0; bettor]).unwrap();
        let node = &s.tree.nodes[at as usize];
        for a in 1..node.num_children as usize {
            // Everyone after the bettor folds until seat `k` (wrapping to the
            // seats that checked before the bet).
            for folds in 0..n - 1 {
                let mut line = vec![0; bettor];
                line.push(a);
                line.extend(std::iter::repeat(0).take(folds));
                if let Ok(idx) = s.walk(&line) {
                    if s.tree.nodes[idx as usize].kind == KIND_ACTION {
                        lines.push(line);
                    }
                }
            }
        }
    }
    lines
}

fn report(s: &BpSolver) -> serde_json::Value {
    let root_street = s.abs.root_street as usize;
    let mut nodes = Vec::new();
    for line in key_lines(s) {
        let idx = s.walk(&line).unwrap();
        let node = &s.tree.nodes[idx as usize];
        if node.street as usize != root_street {
            continue;
        }
        let mut names = Vec::new();
        let mut at = 0u32;
        for &a in &line {
            let nd = &s.tree.nodes[at as usize];
            names.push(format!("{}:{}", nd.player, label(&s.tree.node_actions(nd)[a])));
            at = s.tree.child(nd, a);
        }
        let na = node.num_children as usize;
        let mut strat = Vec::with_capacity(1326);
        let mut row = [0.0f32; MAX_ACTIONS];
        for h in 0..1326u32 {
            let (c1, c2) = solver::cards::combo_from_index(h as usize);
            if (1u64 << c1 | 1u64 << c2) & s.abs.dead != 0 {
                strat.push(serde_json::Value::Null);
                continue;
            }
            s.average(node, h, &mut row);
            strat.push(serde_json::json!(row[..na].iter().map(|x| (*x * 1e4).round() / 1e4).collect::<Vec<f32>>()));
        }
        nodes.push(serde_json::json!({
            "line": names,
            "seat": node.player,
            "pot": node.pot,
            "actions": s.tree.node_actions(node).iter().map(label).collect::<Vec<_>>(),
            "strategy": strat,
        }));
    }
    let hands: Vec<String> = (0..1326)
        .map(|h| {
            let (c1, c2) = solver::cards::combo_from_index(h);
            solver::cards::combo_to_string(c1, c2)
        })
        .collect();
    serde_json::json!({ "hands": hands, "nodes": nodes })
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 || args[1] != "solve" {
        eprintln!("usage: bombpot solve <config.json> [--rounds N] [--deals N] [--threads N] [--seed N] [--check-every N] [--challenge DEALS] [--exact] [--report out.json] [--max-gb G]");
        std::process::exit(2);
    }
    let text = std::fs::read_to_string(&args[2]).expect("read config");
    let cfg: BpConfig = serde_json::from_str(&text).expect("parse config");
    let rounds: u32 = arg(&args, "--rounds", 20);
    let deals: u64 = arg(&args, "--deals", 1_000_000);
    let threads: usize = arg(&args, "--threads", std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4));
    let seed: u64 = arg(&args, "--seed", 1);
    let check_every: u32 = arg(&args, "--check-every", 0);
    let challenge: u64 = arg(&args, "--challenge", 0);
    let max_gb: f64 = arg(&args, "--max-gb", 8.0);
    let exact = args.iter().any(|a| a == "--exact");
    let report_path: String = arg(&args, "--report", String::new());

    let t0 = Instant::now();
    let mut s = match BpSolver::new(&cfg, (max_gb * 1e9) as u64) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(1);
        }
    };
    let n = s.players();
    let bytes: usize = s.regret.iter().map(|t| t.len() * 8).sum();
    println!(
        "{}",
        serde_json::json!({
            "event": "built", "players": n, "boards": cfg.boards, "nodes": s.tree.nodes.len(),
            "decisions_by_street": s.tree.action_nodes, "slots_by_street": s.abs.slots,
            "table_gb": bytes as f64 / 1e9, "setup_s": t0.elapsed().as_secs_f64(), "threads": threads,
        })
    );
    let check = |s: &BpSolver, elapsed: f64| {
        let mut out = serde_json::json!({ "event": "check", "round": s.rounds, "deals": s.deals, "solve_s": elapsed });
        let base = s.sampled_values(2_000_000, threads, seed + 77, None);
        out["value"] = serde_json::json!(base.iter().map(|v| v.0).collect::<Vec<_>>());
        out["value_se"] = serde_json::json!(base.iter().map(|v| v.1).collect::<Vec<_>>());
        if exact && n == 2 {
            let v = Exact2::new(s).unwrap().values();
            out["exact_value"] = serde_json::json!(v.value);
            out["exact_gain"] = serde_json::json!([v.best[0] - v.value[0], v.best[1] - v.value[1]]);
        }
        if challenge > 0 {
            let mut gains = Vec::new();
            let mut ses = Vec::new();
            for seat in 0..n {
                let t = s.train_challenger(seat, challenge, threads, seed + 1000 + seat as u64);
                let c = Challenger { seat, regret: &t };
                let v = s.sampled_values(2_000_000, threads, seed + 77, Some(&c));
                gains.push(v[seat].0 - base[seat].0);
                ses.push((v[seat].1.powi(2) + base[seat].1.powi(2)).sqrt());
            }
            out["challenger_gain"] = serde_json::json!(gains);
            out["challenger_gain_se"] = serde_json::json!(ses);
        }
        println!("{out}");
    };
    let mut solve_s = 0.0;
    for r in 1..=rounds {
        let t = Instant::now();
        s.run_round(deals, threads, seed);
        let dt = t.elapsed().as_secs_f64();
        solve_s += dt;
        println!(
            "{}",
            serde_json::json!({ "event": "round", "round": r, "deals": s.deals, "round_s": dt, "deals_per_s": deals as f64 / dt })
        );
        if check_every > 0 && (r % check_every == 0 || r == rounds) {
            check(&s, solve_s);
        }
    }
    if check_every == 0 {
        check(&s, solve_s);
    }
    if !report_path.is_empty() {
        std::fs::write(&report_path, serde_json::to_string(&report(&s)).unwrap()).expect("write report");
    }
}
