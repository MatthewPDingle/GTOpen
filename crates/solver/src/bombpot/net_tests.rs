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
    let policy = UniformPolicy(&tree);
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
    w.run(&UniformPolicy(&g.tree), Chance::Sample { turn: 2, river: 2 }, false, Some(&mut rec), &mut Rng::new(3));
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
    let net = Mlp::from_bytes(&bytes).unwrap();
    assert!(Mlp::from_bytes(&bytes[..bytes.len() - 4]).is_err());
    let f = |i: usize| f32::from_le_bytes(bytes[36 + i * 4..40 + i * 4].try_into().unwrap());
    let mut pub_row = vec![0.0f32; PUB];
    pub_row[0] = 1.0;
    pub_row[7] = 0.25;
    let hand: [f32; HAND] = [0.6, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
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
    let mut base = net.node_base(&pub_row, &board);
    let mut raw = [0.0f32; MENU];
    net.forward(&mut base, &mut Vec::new(), c1, c2, &hand, &mut raw);
    for j in 0..MENU {
        assert!((raw[j] as f64 - want[j]).abs() < 1e-4, "{raw:?} {want:?}");
    }
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
    };
    let (adv, strat) = generate(&spec, None, 4).unwrap();
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
        let t: Vec<f32> = (0..MENU).map(|k| f32::from_le_bytes(r[64 + k * 4..68 + k * 4].try_into().unwrap())).collect();
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
