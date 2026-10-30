use super::eval::{terminal_cfv, terminal_cfv_brute};
use super::game::{MwSpot, MwSpotConfig};
use super::solver::{Dealt, MwSolver};
use super::tree::*;
use crate::cfr::Algorithm;
use crate::store::Storage;
use crate::tree::{parse_sizes, Action};
use std::sync::Arc;

struct Rng(u64);
impl Rng {
    fn f(&mut self) -> f32 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        (self.0 >> 40) as f32 / (1u64 << 24) as f32
    }
}

fn cfg(board: &str, ranges: [&str; 3], pot: f64, stacks: [f64; 3], bets: &str, raises: &str) -> MwSpotConfig {
    let mut t = MwTreeConfig::uniform(pot, stacks[0], &parse_sizes(bets).unwrap(), &parse_sizes(raises).unwrap());
    t.stacks = stacks;
    MwSpotConfig { board: board.into(), ranges: ranges.map(String::from), tree: t }
}

const R0: &str = "AA,KK,QQ,JJ,TT,99,AK,AQ,KQ,QJ,JT,T9s,98s,87s,A5s";
const R1: &str = "QQ-77,AQ,AJ,KQ,KJs,QJs,JTs,T9s,98s,A4s,A3s";
const R2: &str = "AA-88,AK,AQ,AJs,KQs,KJs,QJs,JTs,65s,54s";

/// Walks the tree collecting (terminal node, dealt cards) pairs, sampling a
/// few cards per chance node.
fn collect_terminals(spot: &MwSpot, idx: u32, dealt: Dealt, out: &mut Vec<(u32, Dealt)>, budget: &mut usize) {
    let n = &spot.tree.nodes[idx as usize];
    match n.kind {
        KIND_ACTION => {
            for a in 0..n.num_children as usize {
                collect_terminals(spot, spot.tree.child(n, a), dealt, out, budget);
            }
        }
        KIND_CHANCE => {
            let mut taken = 0;
            for c in 0..52u8 {
                let ch = spot.tree.children[n.children_start as usize + c as usize];
                if ch == crate::tree::SENTINEL || dealt.contains(c) {
                    continue;
                }
                if c % 7 == 3 && taken < 2 {
                    taken += 1;
                    collect_terminals(spot, ch, dealt.push(c), out, budget);
                }
            }
        }
        _ => {
            if *budget > 0 {
                *budget -= 1;
                out.push((idx, dealt));
            }
        }
    }
}

fn check_terminals(c: MwSpotConfig, seed: u64) {
    let spot = MwSpot::new(c).unwrap();
    let mut terms = Vec::new();
    let mut budget = 400;
    collect_terminals(&spot, 0, Dealt::default(), &mut terms, &mut budget);
    assert!(terms.len() > 10);
    let mut rng = Rng(seed);
    let mut kinds = [0usize; 2];
    for (idx, dealt) in terms {
        let node = &spot.tree.nodes[idx as usize];
        kinds[(node.kind == KIND_TERM_SHOWDOWN) as usize] += 1;
        let mut dm = 0u64;
        for &c in dealt.as_slice() {
            dm |= 1u64 << c;
        }
        let reach: [Vec<f32>; 3] = std::array::from_fn(|o| {
            spot.hands[o].iter().map(|h| if h.mask & dm != 0 { 0.0 } else { rng.f() }).collect()
        });
        let rr = [&reach[0][..], &reach[1][..], &reach[2][..]];
        for p in 0..3 {
            let mut out = vec![0f32; spot.hands[p].len()];
            terminal_cfv(&spot, node, dealt.as_slice(), p, rr, &mut out);
            let want = terminal_cfv_brute(&spot, node, dealt.as_slice(), p, rr);
            for (i, h) in spot.hands[p].iter().enumerate() {
                if h.mask & dm != 0 {
                    continue;
                }
                let tol = 1e-3 * (1.0 + want[i].abs());
                assert!(
                    (out[i] as f64 - want[i]).abs() < tol,
                    "node {idx} kind {} live {:b} p {p} hand {i}: got {} want {}",
                    node.kind,
                    node.live,
                    out[i],
                    want[i]
                );
            }
        }
    }
    assert!(kinds[0] > 0 && kinds[1] > 0, "need fold and showdown terminals: {kinds:?}");
}

#[test]
fn river_terminals_match_brute_force() {
    check_terminals(cfg("Ks9d4c7h2s", [R0, R1, R2], 30.0, [100.0; 3], "50 100", "100"), 7);
}

#[test]
fn turn_terminals_match_brute_force_with_ties() {
    // Paired, connected board: many split pots.
    check_terminals(cfg("9h9d8c8s", [R0, R1, R2], 30.0, [60.0; 3], "75", "100"), 11);
}

#[test]
fn side_pot_terminals_match_brute_force() {
    check_terminals(cfg("Ks9d4c7h", [R0, R1, R2], 30.0, [20.0, 120.0, 60.0], "50 a", "a"), 13);
}

#[test]
fn raked_terminals_match_brute_force() {
    let mut c = cfg("Qs8d3c5h2d", [R0, R1, R2], 40.0, [100.0; 3], "33 75", "100");
    c.tree.rake_pct = 0.05;
    c.tree.rake_cap = 3.0;
    check_terminals(c, 17);
}

/// The three players' net results always sum to minus the rake.
#[test]
fn payoffs_are_zero_sum_up_to_rake() {
    let spot = MwSpot::new({
        let mut c = cfg("Ks9d4c7h2s", [R0, R1, R2], 30.0, [20.0, 120.0, 60.0], "50 a", "a");
        c.tree.rake_pct = 0.05;
        c
    })
    .unwrap();
    let mut rng = Rng(3);
    for node in spot.tree.nodes.iter().filter(|n| n.kind == KIND_TERM_SHOWDOWN || n.kind == KIND_TERM_FOLD) {
        for _ in 0..8 {
            let ranks: [u32; 3] = std::array::from_fn(|_| (rng.f() * 4.0) as u32);
            let mut sum = 0.0;
            for p in 0..3 {
                let (q, r) = others(p);
                let cat = |o: usize| if ranks[o] < ranks[p] { 0 } else if ranks[o] == ranks[p] { 1 } else { 2 };
                sum += payoff_table(node, p, 0.05, 0.0)[cat(q)][cat(r)];
            }
            let put: f64 = node.put.iter().map(|&x| x as f64).sum();
            assert!(sum <= 1e-4 && sum >= -0.05 * put - 1e-3, "sum {sum} put {put} live {:b}", node.live);
        }
    }
}

#[test]
fn tree_continues_heads_up_after_a_fold() {
    let spot = MwSpot::new(cfg("Ks9d4c7h2s", [R0, R1, R2], 30.0, [100.0; 3], "50", "100")).unwrap();
    let root = &spot.tree.nodes[0];
    let acts = spot.tree.node_actions(root);
    assert_eq!(acts[0], Action::Check);
    // Bet, then the next player folds: the third player still acts.
    let bet = spot.tree.child(root, 1);
    let n1 = &spot.tree.nodes[bet as usize];
    assert_eq!(n1.player, 1);
    let fold = spot.tree.child(n1, 0);
    let n2 = &spot.tree.nodes[fold as usize];
    assert_eq!(n2.kind, KIND_ACTION);
    assert_eq!(n2.player, 2);
    assert_eq!(n2.live, 0b101);
}

fn solve(c: MwSpotConfig, iters: u32, storage: Storage, iso: bool, algo: Algorithm) -> (MwSolver, f64) {
    let spot = Arc::new(MwSpot::new(c).unwrap());
    let mut s = MwSolver::new(spot, storage);
    s.use_isomorphism = iso;
    s.algo = algo;
    for _ in 0..iters {
        s.iterate();
    }
    let pr = s.progress(0.0);
    (s, pr.exploit_pct_pot)
}

#[test]
fn river_solve_converges() {
    let c = cfg("Ks9d4c7h2s", [R0, R1, R2], 30.0, [100.0; 3], "50 100", "100");
    let (_, e10) = solve(c.clone(), 10, Storage::F32, true, Algorithm::Dcfr);
    let (s, e) = solve(c, 300, Storage::F32, true, Algorithm::Dcfr);
    assert!(e < e10, "{e} !< {e10}");
    assert!(e < 0.5, "river exploitability {e}% pot");
    let (evs, _) = s.exploitability();
    let pot = 30.0;
    // EVs are net of the root contribution and sum to zero without rake.
    assert!(evs.iter().sum::<f64>().abs() < 0.02 * pot, "{evs:?}");
}

#[test]
fn isomorphism_matches_full_traversal() {
    // Monotone flop cards plus turn: the two off suits are symmetric.
    let r = "AA,KK,QQ,JJ,AKs,AKo,KQs,QJs";
    let c = cfg("AhKhQh2h", [r, r, r], 20.0, [40.0; 3], "75", "a");
    let (mut a, ea) = solve(c.clone(), 3, Storage::F32, true, Algorithm::Dcfr);
    let (b, eb) = solve(c, 3, Storage::F32, false, Algorithm::Dcfr);
    assert!(a.spot.suit_perms.len() > 1);
    assert!((ea - eb).abs() < 1e-3 * (1.0 + eb.abs()), "{ea} vs {eb}");
    // Regret matching is discontinuous near zero regrets, so float-order
    // differences eventually grow; compare early iterations exactly. Root
    // street nodes only: deeper nodes also hold (unused) values for hands
    // blocked by the dealt cards.
    a.ensure_symmetric();
    for (i, n) in a.spot.tree.nodes.iter().enumerate() {
        if n.kind == KIND_ACTION && n.street == a.spot.tree.root_street {
            let x = a.average_strategy(i as u32);
            let y = b.average_strategy(i as u32);
            for (u, v) in x.iter().zip(&y) {
                assert!((u - v).abs() < 1e-3, "node {i}: {u} vs {v}");
            }
        }
    }
}

#[test]
fn compressed_and_pcfr_turn_solves_converge() {
    let c = cfg("Ks9d4c7h", [R0, R1, R2], 30.0, [90.0; 3], "66", "a");
    let (_, e) = solve(c.clone(), 120, Storage::Compressed, true, Algorithm::PcfrPlus);
    assert!(e < 1.5, "compressed pcfr+ turn exploitability {e}% pot");
    let (_, e) = solve(c, 120, Storage::F32, true, Algorithm::Dcfr);
    assert!(e < 1.5, "dcfr turn exploitability {e}% pot");
}


#[test]
fn save_load_round_trip_and_browse() {
    use super::query::{class_index, class_label, node_view, MwStep};
    let c = cfg("Ks9d4c7h", [R0, R1, R2], 30.0, [90.0; 3], "66", "a");
    let (mut s, e) = solve(c, 20, Storage::Compressed, true, Algorithm::Dcfr);
    s.ensure_symmetric();
    let mut bytes = Vec::new();
    super::save::save(&s, Some(e), &mut bytes).unwrap();
    assert_eq!(super::save::peek(&bytes[..]).unwrap().iteration, 20);
    let (t, hdr) = super::save::load(&bytes[..], Storage::F32).unwrap();
    assert_eq!(hdr.exploit_pct_pot, Some(e));
    for (i, n) in s.spot.tree.nodes.iter().enumerate() {
        if n.kind == KIND_ACTION {
            let (x, y) = (s.average_strategy(i as u32), t.average_strategy(i as u32));
            for (u, v) in x.iter().zip(&y) {
                assert!((u - v).abs() < 1e-4);
            }
        }
    }
    assert_eq!(class_label(class_index(48, 49)), "AA");
    assert_eq!(class_label(class_index(51, 47)), "AKs");
    assert_eq!(class_label(class_index(50, 47)), "AKo");
    // Root, then check, check, check, then a river card.
    let root = node_view(&t, &[], true).unwrap();
    assert_eq!(root.kind, "action");
    let f: f64 = root.actions.iter().map(|a| a.freq).sum();
    assert!((f - 1.0).abs() < 1e-4, "{f}");
    assert!(root.hands.iter().all(|h| h.ev.map_or(true, |x| x.is_finite())));
    let path = [MwStep::Action(0), MwStep::Action(0), MwStep::Action(0)];
    let ch = node_view(&t, &path, false).unwrap();
    assert_eq!(ch.kind, "chance");
    let mut path = path.to_vec();
    path.push(MwStep::Card(ch.cards[0].clone()));
    let river = node_view(&t, &path, true).unwrap();
    assert_eq!(river.board.len(), 5);
    assert_eq!(river.actor, Some(0));
}

