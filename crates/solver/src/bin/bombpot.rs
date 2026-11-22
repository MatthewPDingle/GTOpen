//! Command line for the bomb pot solver pilot.
//!
//!   bombpot solve <config.json> [--rounds N] [--deals N] [--threads N]
//!       [--seed N] [--check-every N] [--challenge DEALS] [--exact]
//!       [--report out.json] [--max-gb G] [--fine river,turn_strength,turn_draw,top]
//!
//!   bombpot gen <spec.json> --out PREFIX --iter N [--net net.bin] [--seat N] [--seed N] [--threads N]
//!   bombpot score <config.json> --net net.bin [--turns N --rivers N] [--threads N]
//!   bombpot netcheck <examples.bps> --net net.bin [--rows N]
//!
//! `config.json` is a `BpConfig`: boards, the betting tree and the hand
//! grouping. Progress goes to stdout as one JSON object per line.
//!
//! `gen` plays one run of self-play with a net (or, without one, with every
//! action equally likely) and writes PREFIX.adv.bps and PREFIX.strat.bps for
//! the trainer in tools/bombpot, for one seat's decisions (`--seat`) or all. `score` measures a two-player net exactly
//! on one game. `netcheck` prints the net's outputs on stored examples, so
//! the trainer can confirm both sides compute the same thing.

use std::time::Instant;

use solver::bombpot::exact::Exact2;
use solver::bombpot::net::Mlp;
use solver::bombpot::AbsConfig;
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

fn fail(e: String) -> ! {
    eprintln!("{e}");
    std::process::exit(1);
}

fn pool(threads: usize) {
    rayon::ThreadPoolBuilder::new().num_threads(threads).build_global().ok();
}

fn gen(args: &[String], threads: usize) {
    use solver::bombpot::deepcfr::{generate, GenSpec};
    let text = std::fs::read_to_string(&args[2]).unwrap_or_else(|e| fail(format!("{}: {e}", args[2])));
    let spec: GenSpec = serde_json::from_str(&text).unwrap_or_else(|e| fail(format!("{}: {e}", args[2])));
    let out: String = arg(args, "--out", String::new());
    let iter: u32 = arg(args, "--iter", 1);
    let seed: u64 = arg(args, "--seed", 1);
    let net_path: String = arg(args, "--net", String::new());
    if out.is_empty() {
        fail("gen needs --out PREFIX".into());
    }
    pool(threads);
    let net = if net_path.is_empty() { None } else { Some(Mlp::load(&net_path).unwrap_or_else(|e| fail(e))) };
    let t = Instant::now();
    let seat: i64 = arg(args, "--seat", -1);
    let only = if seat >= 0 { Some(seat as usize) } else { None };
    let seed = seed ^ (iter as u64) << 32 ^ ((seat + 1) as u64) << 56;
    let (adv, strat) = generate(&spec, net.as_ref(), only, seed).unwrap_or_else(|e| fail(e));
    adv.write(&format!("{out}.adv.bps"), iter).unwrap_or_else(|e| fail(e));
    strat.write(&format!("{out}.strat.bps"), iter).unwrap_or_else(|e| fail(e));
    println!(
        "{}",
        serde_json::json!({ "event": "gen", "iter": iter, "seat": seat, "games": spec.games, "walks": spec.walks,
            "advantages": adv.n, "strategies": strat.n, "gen_s": t.elapsed().as_secs_f64() })
    );
}

fn score_net(args: &[String], threads: usize) {
    use solver::bombpot::deepcfr::GameCtx;
    use solver::bombpot::exact::score;
    use solver::bombpot::net::NetPolicy;
    use solver::bombpot::range::Chance;
    let text = std::fs::read_to_string(&args[2]).unwrap_or_else(|e| fail(format!("{}: {e}", args[2])));
    let cfg: BpConfig = serde_json::from_str(&text).unwrap_or_else(|e| fail(format!("{}: {e}", args[2])));
    let net_path: String = arg(args, "--net", String::new());
    let turns: usize = arg(args, "--turns", 0);
    let rivers: usize = arg(args, "--rivers", 0);
    let seed: u64 = arg(args, "--seed", 1);
    pool(threads);
    let net = Mlp::load(&net_path).unwrap_or_else(|e| fail(e));
    let t = Instant::now();
    let game = GameCtx::new(&cfg).unwrap_or_else(|e| fail(e));
    let policy = NetPolicy { tree: &game.tree, abs: &game.abs, pubf: &game.pubf, net: &net };
    let chance = if turns == 0 && rivers == 0 {
        Chance::All
    } else {
        Chance::Sample { turn: if turns == 0 { 52 } else { turns }, river: if rivers == 0 { 52 } else { rivers } }
    };
    let v = score(&game.tree, &game.abs, &policy, chance, seed).unwrap_or_else(|e| fail(e));
    let pot = cfg.tree.starting_pot();
    let gain = [v.best[0] - v.value[0], v.best[1] - v.value[1]];
    println!(
        "{}",
        serde_json::json!({ "event": "score", "boards": cfg.boards, "pot": pot, "exact": turns == 0 && rivers == 0,
            "value": v.value, "gain": gain, "gain_avg": v.exploitability(),
            "gain_pct_of_pot": 100.0 * v.exploitability() / pot, "score_s": t.elapsed().as_secs_f64() })
    );
}

/// Print the net's raw outputs for the first rows of an examples file.
fn netcheck(args: &[String]) {
    use solver::bombpot::net::{emb_board_row, HAND, MENU, PUB};
    let net_path: String = arg(args, "--net", String::new());
    let rows: usize = arg(args, "--rows", 64);
    let net = Mlp::load(&net_path).unwrap_or_else(|e| fail(e));
    let bytes = std::fs::read(&args[2]).unwrap_or_else(|e| fail(format!("{}: {e}", args[2])));
    let n = u64::from_le_bytes(bytes[16..24].try_into().unwrap()) as usize;
    let n_pub = u64::from_le_bytes(bytes[24..32].try_into().unwrap()) as usize;
    let rec = u32::from_le_bytes(bytes[44..48].try_into().unwrap()) as usize;
    let f = |at: usize| f32::from_le_bytes(bytes[at..at + 4].try_into().unwrap());
    let recs = 48 + n_pub * PUB * 4;
    let mut out = Vec::new();
    for i in 0..rows.min(n) {
        let r = recs + i * rec;
        let cards = &bytes[r..r + 12];
        let pub_idx = u32::from_le_bytes(bytes[r + 20..r + 24].try_into().unwrap()) as usize;
        let pub_row: Vec<f32> = (0..PUB).map(|k| f(48 + (pub_idx * PUB + k) * 4)).collect();
        let mut board = Vec::new();
        for b in 0..2 {
            for k in 0..5 {
                let c = cards[2 + b * 5 + k];
                if c != 255 {
                    board.push(emb_board_row(b, k.saturating_sub(2), c));
                }
            }
        }
        let mut hand = [0.0f32; HAND];
        for (k, h) in hand.iter_mut().enumerate() {
            *h = f(r + 24 + k * 4);
        }
        let mut x = net.node_base(&pub_row, &board);
        let mut raw = [0.0f32; MENU];
        net.forward(&mut x, &mut Vec::new(), cards[0], cards[1], &hand, &mut raw);
        out.push(raw.to_vec());
    }
    println!("{}", serde_json::json!(out));
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let threads: usize = arg(&args, "--threads", std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4));
    match args.get(1).map(|s| s.as_str()) {
        Some("gen") if args.len() >= 3 => return gen(&args, threads),
        Some("score") if args.len() >= 3 => return score_net(&args, threads),
        Some("netcheck") if args.len() >= 3 => return netcheck(&args),
        _ => {}
    }
    if args.len() < 3 || args[1] != "solve" {
        eprintln!("usage: bombpot solve <config.json> [--rounds N] [--deals N] [--threads N] [--seed N] [--check-every N] [--challenge DEALS] [--exact] [--report out.json] [--max-gb G] [--fine river,turn_strength,turn_draw,top]");
        std::process::exit(2);
    }
    let text = std::fs::read_to_string(&args[2]).expect("read config");
    let cfg: BpConfig = serde_json::from_str(&text).expect("parse config");
    let rounds: u32 = arg(&args, "--rounds", 20);
    let deals: u64 = arg(&args, "--deals", 1_000_000);
    let seed: u64 = arg(&args, "--seed", 1);
    let check_every: u32 = arg(&args, "--check-every", 0);
    let challenge: u64 = arg(&args, "--challenge", 0);
    let max_gb: f64 = arg(&args, "--max-gb", 8.0);
    let exact = args.iter().any(|a| a == "--exact");
    let report_path: String = arg(&args, "--report", String::new());
    // `--fine river,turn_strength,turn_draw,top`: the challenger tells hands
    // apart this finely instead of using the solve's own grouping.
    let fine: Option<AbsConfig> = args.iter().position(|a| a == "--fine").and_then(|i| args.get(i + 1)).map(|v| {
        let p: Vec<f64> = v.split(',').map(|x| x.parse().expect("--fine takes four numbers")).collect();
        AbsConfig {
            river_groups: p[0] as usize,
            turn_strength_groups: p[1] as usize,
            turn_draw_groups: p[2] as usize,
            top: p[3],
            per_board: false,
            lossless: false,
        }
    });

    let t0 = Instant::now();
    let mut s = match BpSolver::new(&cfg, (max_gb * 1e9) as u64) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(1);
        }
    };
    let n = s.players();
    let bytes: usize = s.regret.iter().map(|t| t.len() * 12).sum();
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
                let c: Challenger = s
                    .train_challenger(seat, fine.as_ref(), challenge, threads, seed + 1000 + seat as u64, (max_gb * 1e9) as u64)
                    .expect("challenger");
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
            if !report_path.is_empty() && r != rounds {
                // Keep a report per check so two runs can be compared as they go.
                let path = format!("{report_path}.round{r}");
                std::fs::write(&path, serde_json::to_string(&report(&s)).unwrap()).expect("write report");
            }
        }
    }
    if check_every == 0 {
        check(&s, solve_s);
    }
    if !report_path.is_empty() {
        std::fs::write(&report_path, serde_json::to_string(&report(&s)).unwrap()).expect("write report");
    }
}
