//! Checks of the pieces a net needs: whole-range play with sampled cards,
//! the examples it records, the betting inputs, and the net reader.

use super::abstraction::{Abstraction, Rng};
use super::deepcfr::{canon_flop, generate, GameCtx, GenSpec, SAMPLE_BYTES};
use super::exact::score;
use super::net::*;
use super::range::{Chance, NodeView, Recorder, UniformPolicy, Walker};
use super::solver::BpConfig;
use super::tree::{BpTreeBuilder, BpTreeConfig};
use crate::cards::{parse_cards, NUM_COMBOS};
use crate::tree::{parse_sizes, Action};

fn game(boards: &[&str], ante: f64, stack: f64) -> BpConfig {
    BpConfig {
        boards: boards.iter().map(|s| s.to_string()).collect(),
        tree: BpTreeConfig::uniform(2, ante, stack, &parse_sizes("66").unwrap(), &parse_sizes("100").unwrap()),
        groups: Default::default(),
    }
}

#[test]
fn sampled_cards_average_to_the_exact_value() {
    // Turn root: every river card against a few drawn ones, many times.
    let cfg = game(&["AsKd7c4h"], 3.0, 20.0);
    let boards = vec![parse_cards("AsKd7c4h").unwrap()];
    let abs = Abstraction::new(&boards, &cfg.groups).unwrap();
    let tree = BpTreeBuilder::build(&cfg.tree, 1, 1_000_000).unwrap();
    let policy = Skew(&tree);
    let exact = score(&tree, &abs, &policy, Chance::All, 0).unwrap();
    // Asking for more cards than there are is the same as asking for all.
    let all = score(&tree, &abs, &policy, Chance::Sample { turn: 99, river: 99 }, 5).unwrap();
    assert!((exact.value[0] - all.value[0]).abs() < 1e-6);
    let runs = 300;
    let mut mean = 0.0;
    for seed in 0..runs {
        mean += score(&tree, &abs, &policy, Chance::Sample { turn: 1, river: 3 }, seed).unwrap().value[0];
    }
    mean /= runs as f64;
    eprintln!("exact {:.4}, sampled mean {mean:.4}", exact.value[0]);
    assert!((mean - exact.value[0]).abs() < 0.05, "exact {} sampled {mean}", exact.value[0]);
}

/// A lopsided strategy, so that results depend on the cards to come (when
/// every action is equally likely they do not: the seats mirror each other).
struct Skew<'a>(&'a super::tree::BpTree);

impl super::range::Policy for Skew<'_> {
    fn strategies(&self, at: &super::range::At, out: &mut [f32]) {
        let na = self.0.nodes[at.node_idx as usize].num_children as usize;
        for h in 0..NUM_COMBOS {
            let w = |a: usize| 1.0 + ((h + 7 * a + at.node_idx as usize) % 5) as f32;
            let total: f32 = (0..na).map(w).sum();
            for a in 0..na {
                out[a * NUM_COMBOS + h] = w(a) / total;
            }
        }
    }
}

#[test]
fn walks_that_share_the_cards_cover_them_exactly() {
    // 48 river cards, 8 walks of 6: together they are every card once.
    let cfg = game(&["AsKd7c4h"], 3.0, 20.0);
    let boards = vec![parse_cards("AsKd7c4h").unwrap()];
    let abs = Abstraction::new(&boards, &cfg.groups).unwrap();
    let tree = BpTreeBuilder::build(&cfg.tree, 1, 1_000_000).unwrap();
    let policy = Skew(&tree);
    let exact = score(&tree, &abs, &policy, Chance::All, 0).unwrap().value[0];
    let mut mean = 0.0;
    let mut off = 0.0f64;
    for walk in 0..8 {
        let v = score(&tree, &abs, &policy, Chance::Spread { turn: 6, river: 6, walk, deck: 77 }, walk as u64).unwrap().value[0];
        off = off.max((v - exact).abs());
        mean += v / 8.0;
    }
    eprintln!("exact {exact:.5}, shared mean {mean:.5}, one walk off by up to {off:.4}");
    assert!((mean - exact).abs() < 1e-4 && off > 1e-3, "exact {exact} shared {mean}");
}

struct Boards(std::collections::HashSet<[u8; 2]>);

impl Recorder for Boards {
    fn node(&mut self, v: &NodeView) {
        if v.runout[0][1] != 0 || v.used.count_ones() == 5 {
            self.0.insert(v.runout[0]);
        }
    }
}

#[test]
fn walks_that_share_the_cards_do_not_repeat_river_cards() {
    // 96 walks of 4 turn cards pass each turn card about 8 times; with 2
    // river cards each, every pass must bring new ones.
    let cfg = game(&["AsKd7c"], 3.0, 20.0);
    let g = GameCtx::new(&cfg).unwrap();
    let w = Walker::new(&g.tree, &g.abs).unwrap();
    let mut seen = Boards(Default::default());
    for walk in 0..96 {
        let chance = Chance::Spread { turn: 4, river: 2, walk, deck: 5 };
        w.run(&UniformPolicy(&g.tree), None, chance, false, Some(&mut seen), &mut Rng::new(walk as u64));
    }
    assert_eq!(seen.0.len(), 96 * 4 * 2);
}

#[test]
fn a_river_solved_on_the_spot_leaves_little_to_gain_there() {
    let cfg = game(&["AsKd7c"], 3.0, 20.0);
    let g = GameCtx::new(&cfg).unwrap();
    let policy = UniformPolicy(&g.tree);
    let chance = Chance::Sample { turn: 2, river: 2 };
    let pot = cfg.tree.starting_pot();
    let plain = score(&g.tree, &g.abs, &policy, chance, 3).unwrap();
    let solved = super::exact::score_solved(&g.tree, &g.abs, &policy, chance, 3, 200).unwrap();
    let (before, after) = (plain.gain_from()[2] / pot, solved.gain_from()[2] / pot);
    eprintln!("gain on the river, share of the pot: played at random {before:.4}, solved {after:.4}");
    assert!(before > 0.05 && after < 0.005, "{before} {after}");
    // The two seats' values still add up to the same pot.
    assert!((solved.value[0] + solved.value[1] - plain.value[0] - plain.value[1]).abs() < 1e-3);
}

struct Check {
    nodes: usize,
    worst: f32,
}

impl Recorder for Check {
    fn node(&mut self, v: &NodeView) {
        self.nodes += 1;
        let na = v.action_vals.len();
        for h in 0..NUM_COMBOS {
            // The mix's value is the actions' values weighted by the mix.
            let mix: f32 = (0..na).map(|a| v.sigma[a * NUM_COMBOS + h] * v.action_vals[a][h]).sum();
            self.worst = self.worst.max((mix - v.node_val[h]).abs() / (1.0 + v.opp_mass[h]));
        }
    }
}

#[test]
fn a_recorder_sees_every_decision_with_consistent_values() {
    let cfg = game(&["AsKd7c"], 3.0, 20.0);
    let g = GameCtx::new(&cfg).unwrap();
    let w = Walker::new(&g.tree, &g.abs).unwrap();
    let mut rec = Check { nodes: 0, worst: 0.0 };
    w.run(&UniformPolicy(&g.tree), None, Chance::Sample { turn: 2, river: 2 }, false, Some(&mut rec), &mut Rng::new(3));
    let d = g.tree.action_nodes;
    assert_eq!(rec.nodes as u64, d[0] + 2 * d[1] + 4 * d[2]);
    assert!(rec.worst < 1e-3, "{}", rec.worst);
}

#[test]
fn betting_inputs_and_action_slots() {
    let cfg = game(&["AsKd7c"], 6.0, 98.0);
    let g = GameCtx::new(&cfg).unwrap();
    let t = &g.tree;
    // First seat, checked to: check or bet.
    assert_eq!(&g.pubf.slots[0][..2], &[SLOT_CALL, SLOT_SIZE]);
    let r = g.pubf.row(0);
    assert_eq!(&r[..3], &[1.0, 0.0, 0.0]);
    assert_eq!(r[9], 0.0);
    assert!((r[7] - 12.0 / 110.0).abs() < 1e-6);
    assert!((r[14] - 0.2).abs() < 1e-6 && r[13] == 0.0);
    // Second seat facing the bet: fold, call, raise; it sees a bettor.
    let bet = t.child(&t.nodes[0], 1);
    let n = &t.nodes[bet as usize];
    assert_eq!(&g.pubf.slots[bet as usize][..n.num_children as usize], &[SLOT_FOLD, SLOT_CALL, SLOT_SIZE]);
    let r = g.pubf.row(bet);
    assert_eq!(r[9], 1.0);
    assert!((r[8] - 7.92 / (19.92 + 7.92)).abs() < 1e-4, "{}", r[8]);
    assert_eq!(&r[24..29], &[1.0, 0.0, 7.92 / 19.92, 1.0, 1.0]);
    assert_eq!(r[17], 1.0);
    // Somewhere a raise is all-in: it takes the last slot, with its size.
    let mut seen_allin = false;
    for (i, node) in t.nodes.iter().enumerate() {
        for (a, act) in t.node_actions(node).iter().enumerate() {
            let slot = g.pubf.slots[i][a];
            match act {
                Action::Fold => assert_eq!(slot, SLOT_FOLD),
                Action::Check | Action::Call(_) => assert_eq!(slot, SLOT_CALL),
                _ => {
                    let child = t.child(node, a);
                    let allin = t.put(child, node.player as usize) >= 104.0 - 1e-3;
                    assert_eq!(slot == SLOT_ALLIN, allin);
                    seen_allin |= allin;
                    if allin {
                        assert_eq!(g.pubf.rows[i * PUB + 55], 1.0);
                    }
                }
            }
        }
    }
    assert!(seen_allin);
}

/// A net file with every weight drawn from a fixed sequence.
fn net_bytes(h: usize, layers: usize, residual: bool, kind: u32) -> Vec<u8> {
    let mut out = b"BPN1".to_vec();
    for v in [1, h, layers, DENSE, EMB_ROWS, MENU, residual as usize, kind as usize] {
        out.extend_from_slice(&(v as u32).to_le_bytes());
    }
    let n = EMB_ROWS * h + h * DENSE + h + layers * (h * h + h) + MENU * h + MENU;
    let mut rng = Rng::new(9);
    for _ in 0..n {
        out.extend_from_slice(&((rng.f32() - 0.5) * 0.3).to_le_bytes());
    }
    out
}

#[test]
fn the_net_reader_computes_what_the_file_says() {
    let (h, layers) = (40, 2);
    let bytes = net_bytes(h, layers, true, KIND_ADVANTAGE);
    let net = Net::from_bytes(&bytes).unwrap();
    assert!(Net::from_bytes(&bytes[..bytes.len() - 4]).is_err());
    let f = |i: usize| f32::from_le_bytes(bytes[36 + i * 4..40 + i * 4].try_into().unwrap());
    let mut pub_row = vec![0.0f32; PUB];
    pub_row[0] = 1.0;
    pub_row[7] = 0.25;
    let mut hand = [0.0f32; HAND];
    hand[0] = 0.6;
    hand[1] = 0.1;
    hand[HAND - 1] = 0.4;
    let (c1, c2) = (50u8, 7u8);
    let board = [emb_board_row(0, 0, 3), emb_board_row(0, 0, 20), emb_board_row(0, 0, 44)];
    // By hand, straight from the file's layout.
    let dense: Vec<f32> = pub_row.iter().copied().chain(hand).collect();
    let (emb, wd) = (0, EMB_ROWS * h);
    let b0 = wd + h * DENSE;
    let mut x: Vec<f64> = (0..h)
        .map(|j| {
            let mut v = f(b0 + j) as f64;
            for r in board.iter().copied().chain([c1 as usize, c2 as usize]) {
                v += f(emb + r * h + j) as f64;
            }
            for d in 0..DENSE {
                v += f(wd + j * DENSE + d) as f64 * dense[d] as f64;
            }
            v.max(0.0)
        })
        .collect();
    let mut at = b0 + h;
    for _ in 0..layers {
        let y: Vec<f64> = (0..h)
            .map(|j| ((0..h).map(|i| f(at + j * h + i) as f64 * x[i]).sum::<f64>() + f(at + h * h + j) as f64).max(0.0))
            .collect();
        for j in 0..h {
            x[j] += y[j];
        }
        at += h * h + h;
    }
    let want: Vec<f64> =
        (0..MENU).map(|j| (0..h).map(|i| f(at + j * h + i) as f64 * x[i]).sum::<f64>() + f(at + MENU * h + j) as f64).collect();
    let raw = net.example(&pub_row, &board, c1, c2, &hand);
    for j in 0..MENU {
        assert!((raw[j] as f64 - want[j]).abs() < 1e-4, "{raw:?} {want:?}");
    }
}

/// A decision played for all hands at once must match the net asked one
/// hand at a time.
struct OneByOne<'a> {
    g: &'a GameCtx,
    net: &'a Net,
    seen: usize,
    worst: f32,
}

impl Recorder for OneByOne<'_> {
    fn node(&mut self, v: &NodeView) {
        let node = &self.g.tree.nodes[v.node_idx as usize];
        let (na, street) = (node.num_children as usize, node.street as usize);
        let rows = board_rows(&self.g.abs, street, v.runout);
        for h in (v.node_idx as usize % 7..NUM_COMBOS).step_by(97) {
            let (c1, c2) = crate::cards::combo_from_index(h);
            if (1u64 << c1 | 1u64 << c2) & v.used != 0 {
                continue;
            }
            let mut hf = [0.0f32; HAND];
            hand_feats(&self.g.abs, street, h, v.runout, None, &mut hf);
            let raw = self.net.example(self.g.pubf.row(v.node_idx), &rows, c1, c2, &hf);
            let mut p = [0.0f32; 8];
            outputs_to_probs(self.net.kind(), &raw, &self.g.pubf.slots[v.node_idx as usize], na, &mut p);
            for a in 0..na {
                self.worst = self.worst.max((p[a] - v.sigma[a * NUM_COMBOS + h]).abs());
            }
            self.seen += 1;
        }
    }
}

#[test]
fn a_two_sided_net_plays_all_hands_as_it_plays_each() {
    // A file of the two-sided layout with arbitrary weights.
    // The situation side has its own size (file version 2).
    let (h, layers, sh, sl, d) = (16usize, 2usize, 24usize, 1usize, 8usize);
    let mut bytes = b"BPN2".to_vec();
    for v in [2, h, layers, sh, sl, d, PUB, HAND, EMB_ROWS, MENU, KIND_POLICY as usize] {
        bytes.extend((v as u32).to_le_bytes());
    }
    let side = |h: usize, layers: usize, n_in: usize, n_out: usize| EMB_ROWS * h + h * n_in + h + layers * (h * h + h) + n_out * h + n_out;
    let mut rng = Rng::new(9);
    for _ in 0..side(h, layers, HAND, d) + side(sh, sl, PUB, MENU * (d + 1)) {
        bytes.extend(((rng.next_u64() % 2001) as f32 / 2000.0 - 0.5).to_le_bytes());
    }
    let net = Net::from_bytes(&bytes).unwrap();
    assert!(Net::from_bytes(&bytes[..bytes.len() - 4]).is_err());
    let cfg = game(&["AsKd7c"], 3.0, 20.0);
    let g = GameCtx::new(&cfg).unwrap();
    let w = Walker::new(&g.tree, &g.abs).unwrap();
    let policy = NetPolicy::new(&g.tree, &g.abs, &g.pubf, &net, false);
    let mut rec = OneByOne { g: &g, net: &net, seen: 0, worst: 0.0 };
    w.run(&policy, None, Chance::Sample { turn: 2, river: 2 }, false, Some(&mut rec), &mut Rng::new(3));
    assert!(rec.seen > 1000 && rec.worst < 1e-4, "{} hands, off by {}", rec.seen, rec.worst);
}

#[test]
fn outputs_become_probabilities_over_the_legal_actions() {
    let slots = [SLOT_FOLD, SLOT_CALL, SLOT_ALLIN, 0, 0, 0, 0, 0];
    let mut p = [0.0f32; 8];
    outputs_to_probs(KIND_ADVANTAGE, &[1.0, -2.0, 9.0, 9.0, 9.0, 3.0], &slots, 3, &mut p);
    assert_eq!(&p[..3], &[0.25, 0.0, 0.75]);
    // Nothing positive: the least bad action.
    outputs_to_probs(KIND_ADVANTAGE, &[-1.0, -2.0, 9.0, 9.0, 9.0, -0.5], &slots, 3, &mut p);
    assert_eq!(&p[..3], &[0.0, 0.0, 1.0]);
    outputs_to_probs(KIND_POLICY, &[0.0, 0.0, 50.0, 50.0, 50.0, (3.0f32).ln()], &slots, 3, &mut p);
    assert!((p[0] - 0.2).abs() < 1e-6 && (p[2] - 0.6).abs() < 1e-6);
}

#[test]
fn a_run_writes_examples_and_keeps_held_out_flops_out() {
    let mut cfg = game(&[], 3.0, 20.0);
    cfg.boards.clear();
    let spec = GenSpec {
        game: cfg,
        boards: 1,
        ante: Some([2.0, 4.0]),
        stack: Some([15.0, 25.0]),
        games: 3,
        walks: 1,
        turn_draws: 1,
        river_draws: 1,
        keep: [1.0, 0.2, 0.1],
        held_out: vec!["AsKd7c".into()],
        weight_power: 1.0,
        spread: false,
        fixed_cards: None,
        river_solve: 0,
    };
    let (adv, strat) = generate(&spec, None, None, true, None, 4).unwrap();
    assert!(adv.n > 1000 && strat.n > 1000);
    assert_eq!(adv.recs.len(), adv.n as usize * SAMPLE_BYTES);
    // Every example names a row of betting inputs that exists, and an
    // advantage example's targets, weighted by the mix, are not needed to
    // be zero here (uniform mix): their plain sum over legal actions is.
    let rows = adv.pub_rows.len() / PUB;
    for r in adv.recs.chunks_exact(SAMPLE_BYTES) {
        let idx = u32::from_le_bytes(r[20..24].try_into().unwrap()) as usize;
        assert!(idx < rows);
        let mask = r[12];
        let at = 24 + HAND * 4;
        let t: Vec<f32> =
            (0..MENU).map(|k| f32::from_le_bytes(r[at + k * 4..at + 4 + k * 4].try_into().unwrap())).collect();
        // Range inputs are shares between 0 and 1.
        for k in HAND_STATIC..HAND {
            let v = f32::from_le_bytes(r[24 + k * 4..28 + k * 4].try_into().unwrap());
            assert!((0.0..=1.0001).contains(&v), "range input {k} = {v}");
        }
        let legal = mask.count_ones() as f32;
        let sum: f32 = (0..MENU).filter(|&k| mask >> k & 1 != 0).map(|k| t[k]).sum();
        assert!(sum.abs() < 1e-2 * (1.0 + legal), "{t:?}");
    }
    // The same flop in other suits is the same flop.
    let a = canon_flop(&parse_cards("AsKd7c").unwrap());
    assert_eq!(a, canon_flop(&parse_cards("7hAcKs").unwrap()));
    assert_ne!(a, canon_flop(&parse_cards("AsKs7c").unwrap()));
    let mut rng = Rng::new(1);
    for _ in 0..3000 {
        let g = spec.draw_game(&mut rng).unwrap();
        assert_ne!(canon_flop(&parse_cards(&g.boards[0]).unwrap()), a);
        assert!((2.0..=4.0).contains(&g.tree.ante) && (15.0..=25.0).contains(&g.tree.stack));
    }
}

/// Plain tables fed by a recorder, one seat per pass: if what the recorder
/// is told is right, this is self-play that ends up hard to beat.
struct Tab {
    offs: Vec<usize>,
    regret: Vec<f32>,
    sum: Vec<f64>,
    round: f32,
    seat: usize,
}

struct TabPolicy<'a> {
    tree: &'a super::tree::BpTree,
    offs: &'a [usize],
    probs: Vec<f32>,
}

impl super::range::Policy for TabPolicy<'_> {
    fn strategies(&self, at: &super::range::At, out: &mut [f32]) {
        let na = self.tree.nodes[at.node_idx as usize].num_children as usize;
        let o = self.offs[at.node_idx as usize];
        out[..na * NUM_COMBOS].copy_from_slice(&self.probs[o..o + na * NUM_COMBOS]);
    }
}

impl Recorder for Tab {
    fn node(&mut self, v: &NodeView) {
        if v.actor != self.seat {
            return;
        }
        let na = v.action_vals.len();
        let o = self.offs[v.node_idx as usize];
        for a in 0..na {
            for h in 0..NUM_COMBOS {
                self.regret[o + a * NUM_COMBOS + h] += self.round * (v.action_vals[a][h] - v.node_val[h]);
                self.sum[o + a * NUM_COMBOS + h] += (self.round * v.own_reach[h] * v.sigma[a * NUM_COMBOS + h]) as f64;
            }
        }
    }
}

#[test]
fn self_play_from_recorded_values_becomes_hard_to_beat() {
    let cfg = game(&["AsKd7c4h2s"], 2.0, 20.0);
    let boards = vec![parse_cards("AsKd7c4h2s").unwrap()];
    let abs = Abstraction::new(&boards, &cfg.groups).unwrap();
    let tree = BpTreeBuilder::build(&cfg.tree, 2, 1_000_000).unwrap();
    let mut offs = vec![0usize; tree.nodes.len()];
    let mut size = 0;
    for (i, n) in tree.nodes.iter().enumerate() {
        offs[i] = size;
        size += n.num_children as usize * NUM_COMBOS;
    }
    let mut tab = Tab { offs: offs.clone(), regret: vec![0.0; size], sum: vec![0.0; size], round: 0.0, seat: 0 };
    let w = Walker::new(&tree, &abs).unwrap();
    let probs_of = |tab: &Tab, average: bool| -> Vec<f32> {
        let mut probs = vec![0.0f32; size];
        for (i, n) in tree.nodes.iter().enumerate() {
            let na = n.num_children as usize;
            for h in 0..NUM_COMBOS {
                let at = |a: usize| offs[i] + a * NUM_COMBOS + h;
                let raw: Vec<f64> =
                    (0..na).map(|a| if average { tab.sum[at(a)] } else { tab.regret[at(a)].max(0.0) as f64 }).collect();
                let total: f64 = raw.iter().sum();
                for a in 0..na {
                    probs[at(a)] = if total > 0.0 { (raw[a] / total) as f32 } else { 1.0 / na as f32 };
                }
            }
        }
        probs
    };
    let gap = |tab: &Tab| {
        let p = TabPolicy { tree: &tree, offs: &offs, probs: probs_of(tab, true) };
        score(&tree, &abs, &p, Chance::All, 0).unwrap().exploitability()
    };
    let start = gap(&tab);
    for round in 1..=60 {
        tab.round = round as f32;
        for seat in 0..2 {
            tab.seat = seat;
            let p = TabPolicy { tree: &tree, offs: &offs, probs: probs_of(&tab, false) };
            w.run(&p, None, Chance::All, false, Some(&mut tab), &mut Rng::new(0));
        }
    }
    let end = gap(&tab);
    eprintln!("whole-range self-play: a perfect opponent gains {start:.3} at the start, {end:.4} after 60 rounds (pot 4)");
    assert!(end < 0.005 * 4.0, "{end}");
}
