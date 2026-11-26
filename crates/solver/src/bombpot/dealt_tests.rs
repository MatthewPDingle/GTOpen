//! Dealt self-play against whole-range play: over many deals the examples
//! at a spot must average to the exact advantages.

use super::abstraction::{AbsConfig, Rng};
use super::dealt::{play, Dealt};
use super::deepcfr::{GameCtx, SAMPLE_BYTES};
use super::net::{HAND, MENU};
use super::range::{At, Chance, NodeView, Policy, Recorder};
use super::range3::Walker3;
use super::solver::BpConfig;
use super::tree::*;
use crate::cards::{combo_index, NUM_COMBOS};
use crate::tree::parse_sizes;

/// Every hand mixes its actions by a scramble of the spot and the hand
/// (the same on every board, so flop spots can be compared).
struct Scramble<'a>(&'a BpTree);

impl Policy for Scramble<'_> {
    fn strategies(&self, at: &At, out: &mut [f32]) {
        let na = self.0.nodes[at.node_idx as usize].num_children as usize;
        for h in 0..NUM_COMBOS {
            let mut rng = Rng::new((at.node_idx as u64) << 20 ^ h as u64);
            let w: Vec<f32> = (0..na).map(|_| 0.1 + rng.f32()).collect();
            let total: f32 = w.iter().sum();
            for a in 0..na {
                out[a * NUM_COMBOS + h] = w[a] / total;
            }
        }
    }
}

/// Keeps what whole-range play works out at one spot.
struct Keep {
    node: u32,
    adv: Vec<Vec<f32>>,
    sigma: Vec<f32>,
    reach: Vec<f32>,
}

impl Recorder for Keep {
    fn node(&mut self, v: &NodeView) {
        if v.node_idx != self.node {
            return;
        }
        let pot = 6.0;
        self.adv = v
            .action_vals
            .iter()
            .map(|a| (0..NUM_COMBOS).map(|h| if v.opp_mass[h] > 0.0 { (a[h] - v.node_val[h]) / (v.opp_mass[h] * pot) } else { 0.0 }).collect())
            .collect();
        self.sigma = v.sigma.to_vec();
        self.reach = v.own_reach.to_vec();
    }
}

#[test]
fn dealt_examples_average_to_the_whole_range_advantages() {
    let cfg = BpConfig {
        boards: vec!["AsKd7c".into()],
        tree: BpTreeConfig::uniform(3, 2.0, 3.0, &parse_sizes("66").unwrap(), &parse_sizes("100").unwrap()),
        groups: AbsConfig::default(),
    };
    let game = GameCtx::new(&cfg).unwrap();
    let policy = Scramble(&game.tree);
    // The spot: seat 1 to act after seat 0's first action.
    let root = &game.tree.nodes[0];
    let spot = game.tree.child(root, 0);
    let node = &game.tree.nodes[spot as usize];
    assert_eq!((node.kind, node.player, node.street), (KIND_ACTION, 1, 0));
    let na = node.num_children as usize;
    let slots = game.pubf.slots[spot as usize];

    let walker = Walker3::new(&game.tree, &game.abs).unwrap();
    let mut exact = Keep { node: spot, adv: Vec::new(), sigma: Vec::new(), reach: Vec::new() };
    walker.run(&policy, Chance::All, false, Some(1), Some(&mut exact), &mut Rng::new(1));
    assert_eq!(exact.adv.len(), na);

    let d = Dealt { runouts: 5_000, hands: 4, strategy_runouts: 40, strategy_all: true, strategy_keep: Some([1.0, 0.0, 0.0]) };
    let (adv, strat) = play(&game, &policy, &d, [0.25, 0.0, 0.0], 1, 7).unwrap();
    let hand_of = |r: &[u8]| combo_index(r[0], r[1]);
    let target = |r: &[u8], slot: usize| {
        let o = 24 + HAND * 4 + slot * 4;
        f32::from_le_bytes(r[o..o + 4].try_into().unwrap())
    };
    let node_of = |r: &[u8]| u32::from_le_bytes(r[20..24].try_into().unwrap());
    let mut sum = vec![[0.0f64; MENU]; NUM_COMBOS];
    let mut count = vec![0u32; NUM_COMBOS];
    for r in adv.recs.chunks_exact(SAMPLE_BYTES) {
        if node_of(r) == spot {
            let h = hand_of(r);
            count[h] += 1;
            for (slot, s) in sum[h].iter_mut().enumerate() {
                *s += target(r, slot) as f64;
            }
        }
    }
    let reach = walker.root_reach();
    // Hand by hand the averages are still noisy: compare them with the
    // exact advantages over all hands at once.
    let (mut err, mut size, mut hands) = (0.0f64, 0.0f64, 0);
    let (mut xy, mut xx, mut yy) = (0.0f64, 0.0f64, 0.0f64);
    for h in 0..NUM_COMBOS {
        if reach[h] == 0.0 {
            assert_eq!(count[h], 0);
            continue;
        }
        assert!(count[h] > 300, "hand {h} seen {} times", count[h]);
        for a in 0..na {
            let got = sum[h][slots[a] as usize] / count[h] as f64;
            let want = exact.adv[a][h] as f64;
            err += (got - want).abs();
            size += want.abs();
            xy += got * want;
            xx += got * got;
            yy += want * want;
        }
        hands += 1;
    }
    let (err, size) = (err / (hands * na) as f64, size / (hands * na) as f64);
    let (alike, slope) = (xy / (xx * yy).sqrt(), xy / yy);
    eprintln!("dealt against exact at node {spot}: mean error {err:.4} on advantages of mean size {size:.4}, alike {alike:.4}, slope {slope:.4}, {hands} hands");
    assert!(alike > 0.97 && (slope - 1.0).abs() < 0.03, "alike {alike}, slope {slope}");

    // Strategy examples: the mix played, weighted by how often the hand
    // gets there, whatever the other seats do.
    let weight = |r: &[u8]| f32::from_le_bytes(r[16..20].try_into().unwrap());
    let mut seen = 0;
    for r in strat.recs.chunks_exact(SAMPLE_BYTES) {
        if node_of(r) == spot {
            let h = hand_of(r);
            assert!((weight(r) - exact.reach[h].max(0.05)).abs() < 1e-5);
            for a in 0..na {
                assert!((target(r, slots[a] as usize) - exact.sigma[a * NUM_COMBOS + h]).abs() < 1e-6);
            }
            seen += 1;
        }
    }
    assert!(seen > 20_000, "{seen} strategy examples");
}
