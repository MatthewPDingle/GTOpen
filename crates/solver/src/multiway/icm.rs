//! Tournament (ICM) payoffs for three-player postflop spots.
//!
//! Every terminal pays each player the change in its Malmuth–Harville prize
//! equity, in big-blind equivalents, measured from the root with the pot
//! split evenly (see `icm::postflop`). The terminal evaluator works with
//! payoff tables indexed by how each opponent's hand compares with the
//! traverser's (`payoff_table`), which fixes every player's chips. Under ICM
//! a player's prize also depends on the other players' stacks, so two cases
//! also need the order of the opponents' hands: both opponents beat the
//! traverser (or both lose to it, which matters when they contest a side
//! pot it is not in), and the traverser has folded while the other two show
//! down. For those the table holds the value when the second opponent wins,
//! and `order` the corrections when the first wins or they tie, which the
//! evaluator weights with exact ordered pair masses (`eval::order_masses`).

use super::tree::{others, MwNode, MwTree, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, NP};
use crate::icm::postflop::{IcmPricer, PostflopIcm};
use std::collections::HashMap;

/// Net chips (won minus put) for every player at a terminal, given each
/// player's hand strength (higher wins). Pots are settled layer by layer;
/// folded players contribute but cannot win. No rake.
pub fn chip_results(node: &MwNode, strength: [i32; NP]) -> [f64; NP] {
    let put = node.put.map(|x| x as f64);
    let mut levels: Vec<f64> = put.to_vec();
    levels.sort_by(f64::total_cmp);
    levels.dedup_by(|a, b| (*a - *b).abs() < 1e-7);
    let mut won = [0f64; NP];
    let mut prev = 0.0;
    for &lv in &levels {
        let payers: Vec<usize> = (0..NP).filter(|&i| put[i] >= lv - 1e-7).collect();
        let amount = (lv - prev) * payers.len() as f64;
        prev = lv;
        if amount <= 0.0 {
            continue;
        }
        let contenders: Vec<usize> = payers.iter().copied().filter(|&i| node.live & (1 << i) != 0).collect();
        if contenders.is_empty() {
            // Only folded players paid this layer: give it back.
            for &i in &payers {
                won[i] += amount / payers.len() as f64;
            }
            continue;
        }
        let best = contenders.iter().map(|&i| strength[i]).max().unwrap();
        let winners: Vec<usize> = contenders.into_iter().filter(|&i| strength[i] == best).collect();
        for &i in &winners {
            won[i] += amount / winners.len() as f64;
        }
    }
    std::array::from_fn(|i| won[i] - put[i])
}

/// Per-terminal ICM payoff tables for a three-player tree.
pub struct MwIcm {
    pricer: IcmPricer,
    reference: [f64; NP],
    /// (live, put bits) -> per-player 3x3 table, as `payoff_table`, and
    /// order corrections (see `MwIcm::order`).
    tables: HashMap<(u8, [u32; NP]), [([[f64; 3]; 3], [f64; 4]); NP]>,
}

impl MwIcm {
    pub fn build(tree: &MwTree, icm: &PostflopIcm) -> Self {
        let cfg = &tree.config;
        let share = cfg.starting_pot / NP as f64;
        let reference: [f64; NP] = std::array::from_fn(|i| cfg.stacks[i] + share);
        let pricer = IcmPricer::new(icm, reference.to_vec());
        let mut me = MwIcm { pricer, reference, tables: HashMap::new() };
        let mut cache: HashMap<[u64; NP], [f64; NP]> = HashMap::new();
        for node in &tree.nodes {
            if node.kind != KIND_TERM_FOLD && node.kind != KIND_TERM_SHOWDOWN {
                continue;
            }
            let key = (node.live, node.put.map(f32::to_bits));
            if me.tables.contains_key(&key) {
                continue;
            }
            let t: [([[f64; 3]; 3], [f64; 4]); NP] = std::array::from_fn(|p| me.table_for(node, p, &mut cache));
            me.tables.insert(key, t);
        }
        me
    }

    /// Big blinds per unit of prize.
    pub fn scale(&self) -> f64 {
        self.pricer.scale
    }

    pub fn start_equity(&self) -> &[f64] {
        self.pricer.start_equity()
    }

    /// Every player's ICM value for given hand strengths (higher wins).
    pub fn values(&self, node: &MwNode, strength: [i32; NP], cache: &mut HashMap<[u64; NP], [f64; NP]>) -> [f64; NP] {
        let net = chip_results(node, strength);
        let after: [f64; NP] = std::array::from_fn(|i| self.reference[i] + net[i]);
        *cache.entry(after.map(f64::to_bits)).or_insert_with(|| {
            let v = self.pricer.value(&after);
            [v[0], v[1], v[2]]
        })
    }

    fn table_for(&self, node: &MwNode, p: usize, cache: &mut HashMap<[u64; NP], [f64; NP]>) -> ([[f64; 3]; 3], [f64; 4]) {
        let (q, r) = others(p);
        let live = |i: usize| node.live & (1 << i) != 0;
        let both = live(q) && live(r);
        let mut value = |sq: i32, sr: i32| {
            let mut s = [0i32; NP];
            s[p] = 10;
            s[q] = sq;
            s[r] = sr;
            self.values(node, s, cache)[p]
        };
        let mut pay = [[0f64; 3]; 3];
        let mut order = [0f64; 4];
        if both && !live(p) {
            // Folded: only q against r matters. Table: r wins.
            let base = value(1, 2);
            pay = [[base; 3]; 3];
            order[0] = value(2, 1) - base;
            order[1] = value(1, 1) - base;
            return (pay, order);
        }
        // An opponent weaker than p sits at 5, tied at 10, stronger at 15.
        let at = |c: usize| 5 * (c as i32 + 1);
        for cq in 0..3 {
            for cr in 0..3 {
                let (x, y) = (at(cq), at(cr));
                if both && cq == cr && cq != 1 {
                    // Both above or both below p: r wins in the table.
                    let base = value(x, x + 1);
                    pay[cq][cr] = base;
                    let slot = if cq == 2 { 0 } else { 2 };
                    order[slot] = value(x + 1, x) - base;
                    order[slot + 1] = value(x, x) - base;
                } else {
                    pay[cq][cr] = value(x, y);
                }
            }
        }
        (pay, order)
    }

    /// Player p's payoff table at a terminal of the tree this was built for.
    pub fn table(&self, node: &MwNode, p: usize) -> [[f64; 3]; 3] {
        self.tables[&(node.live, node.put.map(f32::to_bits))][p].0
    }

    /// Player p's corrections for the opponents' order, added to the table
    /// value where it holds the second opponent (r) winning: [q beats r, q
    /// ties r] when both beat p, then the same when both lose to p. With p
    /// folded only the first pair is used, over all hands.
    pub fn order(&self, node: &MwNode, p: usize) -> [f64; 4] {
        self.tables[&(node.live, node.put.map(f32::to_bits))][p].1
    }
}
