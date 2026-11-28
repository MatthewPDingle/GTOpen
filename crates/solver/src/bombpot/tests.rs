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

#[test]
fn three_player_river_matches_the_exact_three_way_solver() {
    use crate::multiway::{MwSolver, MwSpot, MwSpotConfig, MwTreeConfig};
    let (board, ante, stack, bets, raises) = ("AsKd7c4h2s", 2.0, 20.0, "66", "100");
    let cfg = config(3, &[board], ante, stack, bets, raises, false);
    let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
    for r in 0..40 {
        s.run_round(1_000_000, 4, 31 + r);
    }
    let ours = s.sampled_values(4_000_000, 4, 3, None);

    let tree = MwTreeConfig::uniform(3.0 * ante, stack, &parse_sizes(bets).unwrap(), &parse_sizes(raises).unwrap());
    let spot = MwSpot::new(MwSpotConfig { board: board.into(), ranges: std::array::from_fn(|_| any_two()), tree }).unwrap();
    let spot = std::sync::Arc::new(spot);
    let mut exact = MwSolver::new(spot.clone(), crate::store::Storage::F32);
    for _ in 0..300 {
        exact.iterate();
    }
    let (evs, gaps) = exact.exploitability();
    eprintln!("3-way river: ours {ours:?}; exact values {evs:?} gaps {gaps:?}");
    // The whole-range walk of the same tables: the values that the dealt
    // hands above estimate, and little left for any one seat to gain.
    let walked = super::exact::score(&s.tree, &s.abs, &super::range::TablePolicy(&s), super::range::Chance::All, 0).unwrap();
    eprintln!("walked values {:?} gains {:?}", walked.value, walked.gain());
    for p in 0..3 {
        assert!((walked.value[p] - ours[p].0).abs() < 0.01 + 4.0 * ours[p].1, "seat {p}: {} vs {}", walked.value[p], ours[p].0);
    }
    assert!(walked.exploitability() < 0.05 * 3.0 * ante, "gain {}", walked.exploitability());
    // The exact solver reports each seat's share of the pot; ours is the
    // result after the ante.
    for p in 0..3 {
        let theirs = evs[p] - if evs.iter().sum::<f64>() > 1.0 { ante } else { 0.0 };
        assert!((ours[p].0 - theirs).abs() < 0.05 + 4.0 * ours[p].1, "seat {p}: {} vs {theirs}", ours[p].0);
    }
    // First seat's opening action, hand by hand.
    let root = &s.tree.nodes[0];
    let na = root.num_children as usize;
    let sig = exact.average_strategy(0);
    let nh = spot.hands[0].len();
    let mut diff = 0.0f64;
    let mut freq = [vec![0.0f64; na], vec![0.0f64; na]];
    for i in 0..nh {
        let combo = spot.hand_combo[0][i] as u32;
        let mut row = [0.0f32; super::tree::MAX_ACTIONS];
        s.average(root, combo, &mut row);
        for a in 0..na {
            diff += (row[a] as f64 - sig[a * nh + i] as f64).abs() / 2.0;
            freq[0][a] += row[a] as f64 / nh as f64;
            freq[1][a] += sig[a * nh + i] as f64 / nh as f64;
        }
    }
    eprintln!("first seat opening: ours {:?} exact {:?}, mean difference per hand {:.3}", freq[0], freq[1], diff / nh as f64);
    for a in 0..na {
        assert!((freq[0][a] - freq[1][a]).abs() < 0.03);
    }
}

#[test]
fn a_challenger_finds_little_to_gain_after_self_play_and_a_lot_before() {
    let cfg = config(2, &["AsKd7c4h2s"], 2.0, 20.0, "66", "100", false);
    let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
    let gain = |s: &BpSolver| {
        let base = s.sampled_values(2_000_000, 4, 1, None);
        let exact = Exact2::new(s).unwrap().values();
        let mut out = Vec::new();
        for seat in 0..2 {
            let c = s.train_challenger(seat, None, 2_000_000, 4, 9, 1 << 30).unwrap();
            let v = s.sampled_values(2_000_000, 4, 2, Some(&c));
            out.push((v[seat].0 - base[seat].0, exact.best[seat] - exact.value[seat]));
        }
        out
    };
    // One round of self-play is still far from good.
    s.run_round(2_000, 4, 1);
    let before = gain(&s);
    for r in 0..40 {
        s.run_round(100_000, 4, 50 + r);
    }
    let after = gain(&s);
    eprintln!("challenger gain (sampled, exact): before {before:?} after {after:?}");
    for seat in 0..2 {
        // The challenger never beats a perfect reply, and comes close to it.
        assert!(before[seat].0 < before[seat].1 + 0.03);
        assert!(before[seat].0 > 0.8 * before[seat].1);
        assert!(after[seat].0 < after[seat].1 + 0.03);
        assert!(after[seat].0 < 0.1);
    }
}

#[test]
fn two_boards_split_the_pot_the_same_way_in_playouts_and_exact_scoring() {
    // Two independent pieces of code pay out a two-board showdown: the
    // playout (one dealt hand at a time) and the exact scorer (every hand at
    // once). On an untrained strategy they must give each seat the same value.
    for boards in [["AsKd7c4h2s", "9h8h2dQcJc"], ["AsKd7c4h", "9h8h2dQc"]] {
        let mut cfg = config(2, &boards, 3.0, 30.0, "66", "100", false);
        cfg.groups = AbsConfig { river_groups: 8, ..Default::default() };
        let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
        // A little self-play so the strategy is not symmetric noise.
        s.run_round(20_000, 4, 3);
        let exact = Exact2::new(&s).unwrap().values();
        let sampled = s.sampled_values(6_000_000, 4, 8, None);
        eprintln!("two boards {boards:?}: exact {:?} sampled {sampled:?}", exact.value);
        for p in 0..2 {
            assert!((exact.value[p] - sampled[p].0).abs() < 4.0 * sampled[p].1 + 0.005, "seat {p}");
        }
        assert!((exact.value[0] + exact.value[1]).abs() < 1e-3);
        assert!(exact.best[0] >= exact.value[0] - 1e-4 && exact.best[1] >= exact.value[1] - 1e-4);
    }
}

#[test]
fn two_player_two_board_river_self_play_becomes_hard_to_beat() {
    let cfg = config(2, &["AsKd7c4h2s", "9h8h2dQcJc"], 3.0, 30.0, "66", "100", false);
    let mut s = BpSolver::new(&cfg, 1 << 30).unwrap();
    let start = Exact2::new(&s).unwrap().values().exploitability();
    for r in 0..30 {
        s.run_round(100_000, 4, 70 + r);
    }
    let v = Exact2::new(&s).unwrap().values();
    eprintln!("two-board river: start {start:.4}, now {:.4}", v.exploitability());
    assert!(v.exploitability() < 0.03 * 6.0, "exploitability {}", v.exploitability());
}

#[test]
fn six_players_two_boards_run_and_the_money_adds_up() {
    let mut cfg = config(6, &["AsKd7c", "9h8h2d"], 2.0, 98.0, "66", "100", false);
    cfg.tree.max_raises = 1;
    cfg.tree.rake_pct = 0.05;
    cfg.tree.rake_cap = 3.0;
    cfg.groups = AbsConfig { river_groups: 6, turn_strength_groups: 4, turn_draw_groups: 2, ..Default::default() };
    let mut s = BpSolver::new(&cfg, 2 << 30).unwrap();
    s.run_round(20_000, 4, 5);
    let v = s.sampled_values(200_000, 4, 6, None);
    let total: f64 = v.iter().map(|x| x.0).sum();
    eprintln!("six players, two boards: values {v:?}");
    // With rake the seats lose between them exactly what the house takes:
    // more than nothing, never more than the cap.
    assert!(total < 0.0 && total > -3.0, "total {total}");
}
