use super::abstraction::AbsConfig;
use super::exact::Exact2;
use super::solver::{BpConfig, BpSolver};
use super::tree::BpTreeConfig;
use crate::tree::parse_sizes;

fn config(players: usize, boards: &[&str], ante: f64, stack: f64, bets: &str, raises: &str, lossless: bool) -> BpConfig {
    BpConfig {
        boards: boards.iter().map(|s| s.to_string()).collect(),
        tree: BpTreeConfig::uniform(players, ante, stack, &parse_sizes(bets).unwrap(), &parse_sizes(raises).unwrap()),
        groups: AbsConfig { lossless, ..Default::default() },
    }
}

#[test]
fn two_player_river_self_play_becomes_hard_to_beat() {
    let cfg = config(2, &["AsKd7c4h2s"], 2.0, 20.0, "66", "100", false);
    let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
    let start = Exact2::new(&s).unwrap().values().exploitability();
    for r in 0..30 {
        s.run_round(100_000, 4, 11 + r);
    }
    let v = Exact2::new(&s).unwrap().values();
    eprintln!("river: start {start:.4}, now {:.4}, values {:?} best {:?}", v.exploitability(), v.value, v.best);
    // No rake: what one seat wins the other loses.
    assert!((v.value[0] + v.value[1]).abs() < 1e-3);
    assert!(v.exploitability() < 0.03 * 4.0, "exploitability {}", v.exploitability());
    assert!(v.exploitability() < start / 10.0);
}

/// Every two-card hand, in the exact solvers' range syntax.
fn any_two() -> String {
    let r = crate::cards::RANK_CHARS;
    let mut v = Vec::new();
    for i in 0..13 {
        v.push(format!("{}{}", r[i], r[i]));
        for j in 0..i {
            v.push(format!("{}{}", r[i], r[j]));
        }
    }
    v.join(",")
}

/// The heads-up exact solver on the same game: each seat's value.
fn heads_up_exact(board: &str, ante: f64, stack: f64, bets: &str, raises: &str, iters: u32) -> ([f64; 2], f64) {
    use crate::tree::{StreetSizing, TreeConfig};
    let s = StreetSizing { bet: parse_sizes(bets).unwrap(), raise: parse_sizes(raises).unwrap(), donk: Vec::new() };
    let tree: TreeConfig = serde_json::from_value(serde_json::json!({
        "starting_pot": 2.0 * ante,
        "effective_stack": stack,
        "oop": [s.clone(), s.clone(), s.clone()],
        "ip": [s.clone(), s.clone(), s.clone()],
    }))
    .unwrap();
    let spot = crate::Spot::new(crate::SpotConfig {
        board: board.into(),
        range_oop: any_two(),
        range_ip: any_two(),
        tree,
    })
    .unwrap();
    let spot = std::sync::Arc::new(spot);
    let mut solver = crate::Solver::new(spot.clone());
    for _ in 0..iters {
        solver.iterate();
    }
    let denom = solver.pair_weight_sum();
    let mut v = [0.0f64; 2];
    for p in 0..2 {
        let cfv = solver.traverse_avg(0, p, &spot.weights[1 - p], crate::game::Dealt::default());
        v[p] = spot.weights[p].iter().zip(&cfv).map(|(&w, &x)| w as f64 * x as f64).sum::<f64>() / denom;
    }
    (v, solver.exploitability())
}

#[test]
fn two_player_river_matches_the_exact_heads_up_solver() {
    let cfg = config(2, &["AsKd7c4h2s"], 2.0, 20.0, "66", "100", false);
    let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
    for r in 0..40 {
        s.run_round(100_000, 4, 5 + r);
    }
    let ours = Exact2::new(&s).unwrap().values();
    let (theirs, their_gap) = heads_up_exact("AsKd7c4h2s", 2.0, 20.0, "66", "100", 400);
    eprintln!("river values ours {:?} (gap {:.4}), exact solver {:?} (gap {:.4})", ours.value, ours.exploitability(), theirs, their_gap);
    for p in 0..2 {
        assert!((ours.value[p] - theirs[p]).abs() < 0.03, "seat {p}: {} vs {}", ours.value[p], theirs[p]);
    }
}

#[test]
fn two_player_turn_matches_the_exact_heads_up_solver() {
    // Every hand kept apart on every river card, so the only difference from
    // the exact solver is sampling.
    let cfg = config(2, &["AsKd7c4h"], 2.0, 20.0, "66", "100", true);
    let mut s = BpSolver::new(&cfg, 4 << 30).unwrap();
    for r in 0..40 {
        s.run_round(500_000, 4, 21 + r);
    }
    let ours = Exact2::new(&s).unwrap().values();
    let (theirs, their_gap) = heads_up_exact("AsKd7c4h", 2.0, 20.0, "66", "100", 300);
    eprintln!("turn values ours {:?} (gap {:.4}), exact solver {:?} (gap {:.4})", ours.value, ours.exploitability(), theirs, their_gap);
    for p in 0..2 {
        assert!((ours.value[p] - theirs[p]).abs() < 0.04, "seat {p}: {} vs {}", ours.value[p], theirs[p]);
    }
    assert!(ours.exploitability() < 0.25, "exploitability {}", ours.exploitability());
}
