//! The three-player walker against a slow calculation that lists every
//! pair of opposing hands and pays each deal by the rules.

use super::abstraction::{strengths, AbsConfig, Abstraction, Rng, Runout};
use super::range::{At, Chance, Policy, UniformPolicy};
use super::range3::Walker3;
use super::tree::*;
use crate::cards::{combo_from_index, parse_cards, Card, NUM_COMBOS};
use crate::tree::parse_sizes;

fn game(boards: &[&str], ante: f64, stack: f64, bets: &str, raises: &str) -> (BpTree, Abstraction) {
    let cards: Vec<Vec<Card>> = boards.iter().map(|b| parse_cards(b).unwrap()).collect();
    let abs = Abstraction::new(&cards, &AbsConfig::default()).unwrap();
    let cfg = BpTreeConfig::uniform(3, ante, stack, &parse_sizes(bets).unwrap(), &parse_sizes(raises).unwrap());
    let tree = BpTreeBuilder::build(&cfg, abs.root_street, 1_000_000).unwrap();
    (tree, abs)
}

/// A made-up strategy: every hand mixes its actions by a scramble of the
/// spot, the cards and the hand, and now and then never takes one.
struct Scramble<'a>(&'a BpTree);

impl Policy for Scramble<'_> {
    fn strategies(&self, at: &At, out: &mut [f32]) {
        let na = self.0.nodes[at.node_idx as usize].num_children as usize;
        let cards = at.runout.iter().flatten().fold(0u64, |m, &c| m * 64 + c as u64 + 1);
        for h in 0..NUM_COMBOS {
            let mut rng = Rng::new((at.node_idx as u64) << 40 ^ cards << 12 ^ h as u64);
            let mut w = [0.0f32; MAX_ACTIONS];
            for x in w.iter_mut().take(na) {
                *x = if rng.below(5) == 0 { 0.0 } else { 0.05 + rng.f32() };
            }
            w[rng.below(na as u32) as usize] += 0.1;
            let total: f32 = w[..na].iter().sum();
            for a in 0..na {
                out[a * NUM_COMBOS + h] = w[a] / total;
            }
        }
    }
}

struct Slow<'a> {
    tree: &'a BpTree,
    abs: &'a Abstraction,
    policy: &'a dyn Policy,
    /// The hands each seat can hold, with their starting weights.
    hands: [Vec<(usize, f64)>; 3],
}

fn cards_of(h: usize) -> u64 {
    let (a, b) = combo_from_index(h);
    1u64 << a | 1u64 << b
}

impl Slow<'_> {
    /// What seat `p` gets in one deal at the end of a line. `st` holds the
    /// showdown strengths on each board.
    fn pay(&self, node_idx: u32, p: usize, held: [usize; 3], st: &[Vec<u32>]) -> f64 {
        let node = &self.tree.nodes[node_idx as usize];
        let put = self.tree.put(node_idx, p) as f64;
        let live = |s: usize| node.live >> s & 1 != 0;
        if !live(p) {
            return -put;
        }
        if node.kind == KIND_FOLD {
            return node.pot_net as f64 - put;
        }
        let nb = self.abs.num_boards();
        let mut won = 0.0;
        for st in st {
            let mine = st[held[p]];
            let best = (0..3).filter(|&s| live(s)).map(|s| st[held[s]]).max().unwrap();
            if mine == best {
                let sharers = (0..3).filter(|&s| live(s) && st[held[s]] == best).count();
                won += node.pot_net as f64 / nb as f64 / sharers as f64;
            }
        }
        won - put
    }

    /// Seat `p`'s value per hand; `w[i * n + j]` is the weight of the other
    /// two seats holding their hands number i and j.
    #[allow(clippy::too_many_arguments)]
    fn walk(&self, p: usize, best: bool, node_idx: u32, have: usize, runout: &Runout, used: u64, w: &[f64]) -> Vec<f64> {
        let node = &self.tree.nodes[node_idx as usize];
        let (q, r) = ((p + 1) % 3, (p + 2) % 3);
        let (hp, hq, hr) = (&self.hands[p], &self.hands[q], &self.hands[r]);
        let need = if node.kind == KIND_SHOWDOWN { 2 } else { node.street as usize };
        if node.kind != KIND_FOLD && have < need {
            let nb = self.abs.num_boards();
            assert_eq!(nb, 1, "the slow walk deals one board");
            let free: Vec<Card> = (0..52u8).filter(|&c| used >> c & 1 == 0).collect();
            let mut out = vec![0.0; hp.len()];
            for &c in &free {
                let bit = 1u64 << c;
                let mut ro = *runout;
                ro[0][have] = c;
                let mut w2 = w.to_vec();
                for (i, &(h1, _)) in hq.iter().enumerate() {
                    for (j, &(h2, _)) in hr.iter().enumerate() {
                        if (cards_of(h1) | cards_of(h2)) & bit != 0 {
                            w2[i * hr.len() + j] = 0.0;
                        }
                    }
                }
                let v = self.walk(p, best, node_idx, have + 1, &ro, used | bit, &w2);
                for (k, &(h, _)) in hp.iter().enumerate() {
                    if cards_of(h) & bit == 0 {
                        out[k] += v[k] / (free.len() as f64 - 6.0);
                    }
                }
            }
            return out;
        }
        if node.kind != KIND_ACTION {
            let st: Vec<Vec<u32>> = match node.kind {
                KIND_SHOWDOWN => (0..self.abs.num_boards()).map(|b| strengths(&self.abs.full_board(b, runout), 0)).collect(),
                _ => Vec::new(),
            };
            return hp
                .iter()
                .map(|&(h, _)| {
                    let mut v = 0.0;
                    for (i, &(h1, _)) in hq.iter().enumerate() {
                        for (j, &(h2, _)) in hr.iter().enumerate() {
                            let (m0, m1, m2) = (cards_of(h), cards_of(h1), cards_of(h2));
                            if m0 & m1 != 0 || m0 & m2 != 0 || m1 & m2 != 0 {
                                continue;
                            }
                            let mut held = [0; 3];
                            held[p] = h;
                            held[q] = h1;
                            held[r] = h2;
                            v += w[i * hr.len() + j] * self.pay(node_idx, p, held, &st);
                        }
                    }
                    v
                })
                .collect();
        }
        let actor = node.player as usize;
        let na = node.num_children as usize;
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        self.policy.strategies(&At { node_idx, runout, used, range: None }, &mut sigma);
        let mut out = vec![if best && actor == p { f64::NEG_INFINITY } else { 0.0 }; hp.len()];
        for a in 0..na {
            let child = self.tree.child(node, a);
            if actor == p {
                let v = self.walk(p, best, child, have, runout, used, w);
                for (k, &(h, _)) in hp.iter().enumerate() {
                    if best {
                        out[k] = out[k].max(v[k]);
                    } else {
                        out[k] += sigma[a * NUM_COMBOS + h] as f64 * v[k];
                    }
                }
            } else {
                let mut w2 = w.to_vec();
                for (i, &(h1, _)) in hq.iter().enumerate() {
                    for (j, &(h2, _)) in hr.iter().enumerate() {
                        let h = if actor == q { h1 } else { h2 };
                        w2[i * hr.len() + j] *= sigma[a * NUM_COMBOS + h] as f64;
                    }
                }
                let v = self.walk(p, best, child, have, runout, used, &w2);
                for k in 0..hp.len() {
                    out[k] += v[k];
                }
            }
        }
        out
    }

    fn values(&self, p: usize, best: bool) -> Vec<f64> {
        let (q, r) = ((p + 1) % 3, (p + 2) % 3);
        let mut w = Vec::new();
        for &(_, a) in &self.hands[q] {
            for &(_, b) in &self.hands[r] {
                w.push(a * b);
            }
        }
        self.walk(p, best, 0, self.abs.root_street as usize, &[[0; 2]; 2], self.abs.dead, &w)
    }
}

/// A few hands per seat drawn from a small set of cards, so that seats
/// often hold the same cards or the same hand.
fn small_ranges(abs: &Abstraction, per_seat: usize, seed: u64) -> [Vec<(usize, f64)>; 3] {
    let mut rng = Rng::new(seed);
    let pool: Vec<usize> = (0..NUM_COMBOS)
        .filter(|&h| {
            let (a, b) = combo_from_index(h);
            cards_of(h) & abs.dead == 0 && a % 3 != 1 && b % 3 != 1
        })
        .collect();
    std::array::from_fn(|_| {
        let mut v: Vec<(usize, f64)> = Vec::new();
        while v.len() < per_seat {
            let h = pool[rng.below(pool.len() as u32) as usize];
            if v.iter().all(|&(x, _)| x != h) {
                v.push((h, 0.1 + rng.f32() as f64));
            }
        }
        v
    })
}

fn compare(boards: &[&str], ante: f64, stack: f64, per_seat: usize, seed: u64) {
    let (tree, abs) = game(boards, ante, stack, "66", "100");
    let policy = Scramble(&tree);
    let hands = small_ranges(&abs, per_seat, seed);
    let walker = Walker3::new(&tree, &abs).unwrap();
    let reach: [Vec<f32>; 3] = std::array::from_fn(|p| {
        let mut v = vec![0.0f32; NUM_COMBOS];
        for &(h, w) in &hands[p] {
            v[h] = w as f32;
        }
        v
    });
    // The slow walk reads the weights the walker reads.
    let hands: [Vec<(usize, f64)>; 3] = std::array::from_fn(|p| hands[p].iter().map(|&(h, _)| (h, reach[p][h] as f64)).collect());
    let slow = Slow { tree: &tree, abs: &abs, policy: &policy, hands };
    let fast = walker.run_from(&reach, &policy, Chance::All, true, None, None, &mut Rng::new(1));
    let kinds: std::collections::BTreeSet<(u8, u16)> =
        tree.nodes.iter().filter(|n| n.kind != KIND_ACTION).map(|n| (n.kind, n.live)).collect();
    let mut seen = 0;
    for p in 0..3 {
        let one = walker.run_from(&reach, &policy, Chance::All, false, Some(p), None, &mut Rng::new(1));
        assert!(one.avg[(p + 1) % 3].is_empty());
        for (best, got) in [(false, &fast.avg[p]), (true, &fast.best[0][p])] {
            let want = slow.values(p, best);
            let scale = want.iter().fold(1e-9f64, |m, v| m.max(v.abs()));
            for (k, &(h, _)) in slow.hands[p].iter().enumerate() {
                assert!(
                    (got[h] as f64 - want[k]).abs() < 2e-4 * scale,
                    "{boards:?} seat {p} hand {h} best {best}: {} against {} (largest {scale})",
                    got[h],
                    want[k]
                );
                if !best {
                    assert_eq!(one.avg[p][h], got[h]);
                }
                seen += 1;
            }
        }
    }
    eprintln!("{boards:?}: {} nodes, ends {kinds:?}, {seen} values agree", tree.nodes.len());
}

#[test]
fn three_player_river_values_match_the_slow_calculation() {
    compare(&["AsKd7c4h2s"], 2.0, 20.0, 14, 3);
    // A board that plays for many hands: big ties.
    compare(&["AsKsQsJsTs"], 2.0, 20.0, 14, 4);
    compare(&["8s8d8c3h3s"], 3.0, 10.0, 14, 5);
    // Two boards, half the pot each.
    compare(&["AsKd7c4h2s", "9h9d5c5s2d"], 2.0, 20.0, 12, 6);
}

#[test]
fn three_player_turn_values_match_the_slow_calculation() {
    compare(&["AsKd7c4h"], 2.0, 3.0, 7, 7);
    compare(&["Ts9s8d2c"], 3.0, 2.0, 7, 8);
}

#[test]
fn three_player_full_ranges_add_up() {
    let (tree, abs) = game(&["AsKd7c4h2s"], 2.0, 20.0, "66", "100");
    let walker = Walker3::new(&tree, &abs).unwrap();
    // 47 cards left: any hand faces C(45, 2) * C(43, 2) pairs of hands.
    let reach = walker.root_reach();
    let mass = walker.pair_mass(&reach, &reach);
    let pairs = 990.0 * 903.0;
    for h in 0..NUM_COMBOS {
        if reach[h] != 0.0 {
            assert!((mass[h] - pairs).abs() < 1e-3, "hand {h}: {}", mass[h]);
        }
    }
    assert!((walker.root_norm() as f64 - pairs).abs() < 1.0);
    // The quick way to a pair mass against the plain formula, on uneven ranges.
    let mut rng = Rng::new(9);
    let uneven: [Vec<f32>; 2] = std::array::from_fn(|_| reach.iter().map(|&r| if rng.below(3) == 0 { 0.0 } else { r * rng.f32() }).collect());
    let (quick, plain) = (walker.pair_mass(&uneven[0], &uneven[1]), walker.pair_mass_plain(&uneven[0], &uneven[1]));
    for h in 0..NUM_COMBOS {
        assert!((quick[h] - plain[h]).abs() < 1e-6 * plain[h].abs().max(1.0), "hand {h}: {} against {}", quick[h], plain[h]);
    }
    assert!((walker.root_triples() - 1081.0 * pairs).abs() < 1.0);
    // No rake: what the seats win and lose adds up to nothing, and a perfect
    // reply never does worse than the strategy it replaces.
    for policy in [&UniformPolicy(&tree) as &dyn Policy, &Scramble(&tree)] {
        let v = walker.run(policy, Chance::All, true, None, None, &mut Rng::new(1));
        let total = |x: &[f32]| (0..NUM_COMBOS).map(|h| reach[h] as f64 * x[h] as f64).sum::<f64>() / walker.root_triples();
        let value: Vec<f64> = (0..3).map(|p| total(&v.avg[p])).collect();
        let best: Vec<f64> = (0..3).map(|p| total(&v.best[0][p])).collect();
        eprintln!("values {value:?} best {best:?}");
        assert!(value.iter().sum::<f64>().abs() < 1e-3, "{value:?}");
        for p in 0..3 {
            assert!(best[p] >= value[p] - 1e-4);
            assert!(total(&v.best[2][p]) <= best[p] + 1e-4);
        }
    }
}
