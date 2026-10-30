//! A three-player postflop spot: board, the three ranges, the tree and the
//! per-river-board hand strengths every terminal evaluation needs.

use super::tree::{MwTree, MwTreeBuilder, MwTreeConfig, NP};
use crate::cards::*;
use crate::evaluator::evaluate7;
use crate::game::HandInfo;
use crate::range::Range;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};

pub const NO_HAND: u16 = u16::MAX;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MwSpotConfig {
    pub board: String,
    /// Ranges in postflop action order (first to act first).
    pub ranges: [String; NP],
    pub tree: MwTreeConfig,
}

/// Hand strengths on one complete five-card board.
pub struct MwRiverEval {
    /// Strength by combo index (0 for combos touching the board).
    pub rank: Vec<u32>,
    /// Strength by ordered card pair, rank_pair[a*52+b] (dense lookups).
    pub rank_pair: Vec<u32>,
    /// Each player's valid hands as (strength, hand index), ascending.
    pub sorted: [Vec<(u32, u16)>; NP],
}

pub struct MwRiverTable {
    pub root_street: u8,
    pub entries: Vec<Option<Box<MwRiverEval>>>,
}

impl MwRiverTable {
    /// Same keying as the heads-up table: flop root lo*52+hi, turn root by
    /// the river card, river root 0. `dealt` holds the cards below the root.
    pub fn key(&self, dealt: &[u8]) -> usize {
        match self.root_street {
            2 => 0,
            1 => dealt[0] as usize,
            _ => {
                let (a, b) = (dealt[0].min(dealt[1]), dealt[0].max(dealt[1]));
                a as usize * 52 + b as usize
            }
        }
    }

    pub fn get(&self, dealt: &[u8]) -> &MwRiverEval {
        self.entries[self.key(dealt)].as_deref().expect("river eval missing")
    }
}

pub struct MwSpot {
    pub config: MwSpotConfig,
    pub board: Vec<Card>,
    pub board_mask: u64,
    pub tree: MwTree,
    pub hands: [Vec<HandInfo>; NP],
    pub weights: [Vec<f32>; NP],
    /// combo index -> hand index for each player (NO_HAND if absent).
    pub combo_hand: [Vec<u16>; NP],
    /// combo index of every hand.
    pub hand_combo: [Vec<u16>; NP],
    /// combo index of each unordered card pair: pair_combo[a*52+b].
    pub pair_combo: Vec<u16>,
    pub river: MwRiverTable,
    /// Suit permutations fixing the board pointwise and all three ranges.
    pub suit_perms: Vec<[u8; 4]>,
    pub hand_perm: [Vec<Vec<u16>>; NP],
}

impl MwSpot {
    pub fn new(config: MwSpotConfig) -> Result<MwSpot, String> {
        MwSpot::new_with_limit(config, None)
    }

    pub fn new_with_limit(config: MwSpotConfig, max_nodes: Option<usize>) -> Result<MwSpot, String> {
        let board = parse_cards(&config.board)?;
        if !(3..=5).contains(&board.len()) {
            return Err("board must have 3 to 5 cards".into());
        }
        let board_mask = board.iter().fold(0u64, |m, &c| m | card_mask(c));
        let mut hands: [Vec<HandInfo>; NP] = Default::default();
        for p in 0..NP {
            let range = Range::parse(&config.ranges[p])?;
            for idx in 0..NUM_COMBOS {
                let w = range.weights[idx];
                if w <= 0.0 {
                    continue;
                }
                let (c1, c2) = combo_from_index(idx);
                let mask = card_mask(c1) | card_mask(c2);
                if mask & board_mask != 0 {
                    continue;
                }
                hands[p].push(HandInfo { c1, c2, weight: w, mask });
            }
            if hands[p].is_empty() {
                return Err(format!("player {} range has no combos left after board removal", p + 1));
            }
            if hands[p].len() >= NO_HAND as usize {
                return Err("range too large".into());
            }
        }
        let mut combo_hand: [Vec<u16>; NP] = Default::default();
        let mut hand_combo: [Vec<u16>; NP] = Default::default();
        for p in 0..NP {
            combo_hand[p] = vec![NO_HAND; NUM_COMBOS];
            for (i, h) in hands[p].iter().enumerate() {
                let k = combo_index(h.c1, h.c2);
                combo_hand[p][k] = i as u16;
                hand_combo[p].push(k as u16);
            }
        }
        let mut pair_combo = vec![u16::MAX; 52 * 52];
        for a in 0..52u8 {
            for b in 0..52u8 {
                if a != b {
                    pair_combo[a as usize * 52 + b as usize] = combo_index(a, b) as u16;
                }
            }
        }
        // Every deal needs three mutually disjoint hands.
        let triple = triple_mass(&hands);
        if triple <= 0.0 {
            return Err("the three ranges are mutually impossible after card removal".into());
        }
        let weights: [Vec<f32>; NP] = std::array::from_fn(|p| hands[p].iter().map(|h| h.weight).collect());
        let root_street = (board.len() - 3) as u8;
        let tree = MwTreeBuilder::build(
            &config.tree,
            board_mask,
            root_street,
            std::array::from_fn(|p| hands[p].len()),
            max_nodes,
        )?;
        let river = build_river_table(&board, board_mask, &hands);
        let (suit_perms, hand_perm) = suit_symmetries(&board, &hands, &combo_hand);
        Ok(MwSpot {
            config,
            board,
            board_mask,
            tree,
            hands,
            weights,
            combo_hand,
            hand_combo,
            pair_combo,
            river,
            suit_perms,
            hand_perm,
        })
    }

    /// Solver arena bytes (regrets + strategy sums).
    pub fn arena_bytes(&self, storage: crate::store::Storage) -> u64 {
        let e: u64 = self.tree.data_size.iter().sum();
        match storage {
            crate::store::Storage::F32 => e * 8,
            crate::store::Storage::Compressed => e * 4 + self.tree.nodes.len() as u64 * 16,
        }
    }

    pub fn perms_fixing(&self, dealt: &[u8]) -> Vec<usize> {
        self.suit_perms
            .iter()
            .enumerate()
            .filter(|(_, pm)| dealt.iter().all(|&c| permute_card(c, pm) == c))
            .map(|(k, _)| k)
            .collect()
    }

    /// Total weight of mutually compatible hand triples at the root.
    pub fn root_triple_mass(&self) -> f64 {
        triple_mass(&self.hands)
    }

    pub fn num_action_nodes(&self) -> usize {
        self.tree.nodes.iter().filter(|n| n.kind == super::tree::KIND_ACTION).count()
    }
}

fn triple_mass(hands: &[Vec<HandInfo>; NP]) -> f64 {
    // O(n0 * n1) with per-card sums for the third range.
    let mut s2 = [0f64; 52];
    let mut t2 = 0f64;
    let mut combo2 = vec![0f64; NUM_COMBOS];
    for h in &hands[2] {
        let w = h.weight as f64;
        t2 += w;
        s2[h.c1 as usize] += w;
        s2[h.c2 as usize] += w;
        combo2[combo_index(h.c1, h.c2)] += w;
    }
    let mut total = 0f64;
    for h0 in &hands[0] {
        for h1 in &hands[1] {
            if h0.mask & h1.mask != 0 {
                continue;
            }
            let cs = [h0.c1, h0.c2, h1.c1, h1.c2];
            let mut v = t2;
            for &c in &cs {
                v -= s2[c as usize];
            }
            for i in 0..4 {
                for j in i + 1..4 {
                    v += combo2[combo_index(cs[i], cs[j])];
                }
            }
            total += h0.weight as f64 * h1.weight as f64 * v;
        }
    }
    total
}

fn build_river_table(board: &[Card], board_mask: u64, hands: &[Vec<HandInfo>; NP]) -> MwRiverTable {
    let root_street = (board.len() - 3) as u8;
    let eval_board = |extra: &[Card]| -> Box<MwRiverEval> {
        let mut full = [0u8; 7];
        full[..board.len()].copy_from_slice(board);
        full[board.len()..5].copy_from_slice(extra);
        let mask = full[..5].iter().fold(0u64, |m, &c| m | card_mask(c));
        let mut rank = vec![0u32; NUM_COMBOS];
        for (k, r) in rank.iter_mut().enumerate() {
            let (c1, c2) = combo_from_index(k);
            if (card_mask(c1) | card_mask(c2)) & mask != 0 {
                continue;
            }
            full[5] = c1;
            full[6] = c2;
            *r = evaluate7(&full);
        }
        let sorted = std::array::from_fn(|p| {
            let mut v: Vec<(u32, u16)> = hands[p]
                .iter()
                .enumerate()
                .filter(|(_, h)| h.mask & mask == 0)
                .map(|(i, h)| (rank[combo_index(h.c1, h.c2)], i as u16))
                .collect();
            v.sort_unstable();
            v
        });
        let mut rank_pair = vec![0u32; 52 * 52];
        for a in 0..52usize {
            for b in 0..52usize {
                if a != b {
                    rank_pair[a * 52 + b] = rank[combo_index(a as u8, b as u8)];
                }
            }
        }
        Box::new(MwRiverEval { rank, rank_pair, sorted })
    };
    let entries = match root_street {
        2 => vec![Some(eval_board(&[]))],
        1 => {
            let mut slots: Vec<Option<Box<MwRiverEval>>> = (0..52).map(|_| None).collect();
            let done: Vec<_> = (0..52u8)
                .into_par_iter()
                .filter(|&c| board_mask & card_mask(c) == 0)
                .map(|c| (c as usize, eval_board(&[c])))
                .collect();
            for (i, e) in done {
                slots[i] = Some(e);
            }
            slots
        }
        _ => {
            let mut slots: Vec<Option<Box<MwRiverEval>>> = (0..52 * 52).map(|_| None).collect();
            let mut pairs = Vec::new();
            for a in 0..52u8 {
                for b in a + 1..52 {
                    if board_mask & (card_mask(a) | card_mask(b)) == 0 {
                        pairs.push((a, b));
                    }
                }
            }
            let done: Vec<_> = pairs
                .into_par_iter()
                .map(|(a, b)| (a as usize * 52 + b as usize, eval_board(&[a, b])))
                .collect();
            for (i, e) in done {
                slots[i] = Some(e);
            }
            slots
        }
    };
    MwRiverTable { root_street, entries }
}

#[allow(clippy::type_complexity)]
fn suit_symmetries(
    board: &[Card],
    hands: &[Vec<HandInfo>; NP],
    combo_hand: &[Vec<u16>; NP],
) -> (Vec<[u8; 4]>, [Vec<Vec<u16>>; NP]) {
    let mut perms = Vec::new();
    let mut tables: [Vec<Vec<u16>>; NP] = Default::default();
    for a in 0..4u8 {
        for b in 0..4u8 {
            for c in 0..4u8 {
                for d in 0..4u8 {
                    let pm = [a, b, c, d];
                    let mut seen = [false; 4];
                    if !pm.iter().all(|&s| !std::mem::replace(&mut seen[s as usize], true)) {
                        continue;
                    }
                    if board.iter().any(|&c| permute_card(c, &pm) != c) {
                        continue;
                    }
                    let mut tb: [Vec<u16>; NP] = Default::default();
                    let mut ok = true;
                    'p: for p in 0..NP {
                        for h in &hands[p] {
                            let k = combo_index(permute_card(h.c1, &pm), permute_card(h.c2, &pm));
                            let j = combo_hand[p][k];
                            if j == NO_HAND || (hands[p][j as usize].weight - h.weight).abs() >= 1e-6 {
                                ok = false;
                                break 'p;
                            }
                            tb[p].push(j);
                        }
                    }
                    if ok {
                        perms.push(pm);
                        for p in 0..NP {
                            tables[p].push(std::mem::take(&mut tb[p]));
                        }
                    }
                }
            }
        }
    }
    if let Some(id) = perms.iter().position(|pm| *pm == [0, 1, 2, 3]) {
        perms.swap(0, id);
        for t in tables.iter_mut() {
            t.swap(0, id);
        }
    }
    (perms, tables)
}
