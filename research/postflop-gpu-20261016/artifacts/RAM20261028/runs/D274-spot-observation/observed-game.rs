//! A `Spot` bundles everything needed to solve one postflop scenario:
//! the built tree, both players' hand lists, and precomputed river strengths.

use crate::cards::*;
use crate::evaluator::evaluate7;
use crate::range::Range;
use crate::store::Storage;
use crate::tree::{Strictness, Tree, TreeBuilder, TreeConfig, SENTINEL};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone)]
pub struct HandInfo {
    pub c1: Card,
    pub c2: Card,
    pub weight: f32,
    pub mask: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpotConfig {
    pub board: String,
    pub range_oop: String,
    pub range_ip: String,
    pub tree: TreeConfig,
}

/// Per-river-board sorted hand strengths for both players.
/// Hands conflicting with the full 5-card board are excluded.
pub struct RiverBoardEval {
    /// (strength, index into Spot::hands[p]) sorted ascending by strength.
    pub sorted: [Vec<(u32, u16)>; 2],
}

pub struct RiverTable {
    pub(crate) root_street: u8,
    /// root_street 0: indexed lo*52+hi (lo < hi); 1: indexed by river card; 2: index 0.
    pub(crate) entries: Vec<Option<Box<RiverBoardEval>>>,
}

impl RiverTable {
    /// Linear key for a set of dealt cards (see `entries` indexing).
    pub(crate) fn key(&self, dealt: &Dealt) -> usize {
        match self.root_street {
            2 => 0,
            1 => {
                debug_assert_eq!(dealt.len, 1);
                dealt.cards[0] as usize
            }
            _ => {
                debug_assert_eq!(dealt.len, 2);
                let (a, b) = (dealt.cards[0].min(dealt.cards[1]), dealt.cards[0].max(dealt.cards[1]));
                a as usize * 52 + b as usize
            }
        }
    }

    pub fn get(&self, dealt: &Dealt) -> &RiverBoardEval {
        self.entries[self.key(dealt)].as_deref().expect("river eval missing")
    }
}

/// Board cards dealt during traversal (beyond the initial board).
#[derive(Debug, Copy, Clone, Default)]
pub struct Dealt {
    pub cards: [Card; 2],
    pub len: u8,
}

impl Dealt {
    pub fn push(mut self, c: Card) -> Self {
        self.cards[self.len as usize] = c;
        self.len += 1;
        self
    }
    pub fn contains(&self, c: Card) -> bool {
        (0..self.len as usize).any(|i| self.cards[i] == c)
    }
}

pub struct Spot {
    pub config: SpotConfig,
    pub board: Vec<Card>,
    pub board_mask: u64,
    pub tree: Tree,
    pub hands: [Vec<HandInfo>; 2],
    /// Initial range weights per hand (reach vector at the root).
    pub weights: [Vec<f32>; 2],
    /// For each hand of player p, index in the opponent's list holding the
    /// identical combo (SENTINEL if the opponent range lacks it).
    pub same_combo: [Vec<u32>; 2],
    pub river: RiverTable,
    /// Suit permutations under which the board (pointwise) and both ranges
    /// are invariant. Entry 0 is always the identity.
    pub suit_perms: Vec<[u8; 4]>,
    /// hand_perm[p][k][i] = index in hands[p] of suit_perms[k] applied to
    /// hands[p][i] (the permuted combo is guaranteed to exist in range).
    pub hand_perm: [Vec<Vec<u16>>; 2],
}

impl Spot {
    pub fn new(config: SpotConfig) -> Result<Spot, String> {
        Spot::new_with_limit(config, None)
    }

    /// [`Spot::new`] with a tree node budget: construction aborts with an
    /// error once the tree grows past `max_nodes` nodes (None = no cap), so
    /// an oversized config errors out early instead of OOMing before the
    /// caller can size-check the finished spot.
    pub fn new_with_limit(config: SpotConfig, max_nodes: Option<usize>) -> Result<Spot, String> {
        Spot::new_impl(config, max_nodes, Strictness::Strict)
    }

    /// [`Spot::new`] in [`Strictness::LenientLoad`] mode, for rebuilding a
    /// spot from a SAVED config only (never for new builds): sizing quirks
    /// the pre-validation tree builder silently dropped (a raise-only "2.5x"
    /// in a bet/donk list) are dropped again instead of rejected, so the
    /// rebuilt tree layout is byte-identical to the one the save's arenas
    /// were written against and old .gto files keep loading.
    pub fn new_lenient(config: SpotConfig) -> Result<Spot, String> {
        Spot::new_impl(config, None, Strictness::LenientLoad)
    }

    /// [`Spot::new_lenient`] with a tree node budget (see
    /// [`Spot::new_with_limit`]); for save-vetting paths that rebuild the
    /// tree under a memory cap.
    pub fn new_lenient_with_limit(
        config: SpotConfig,
        max_nodes: Option<usize>,
    ) -> Result<Spot, String> {
        Spot::new_impl(config, max_nodes, Strictness::LenientLoad)
    }

    fn new_impl(
        mut config: SpotConfig,
        max_nodes: Option<usize>,
        strictness: Strictness,
    ) -> Result<Spot, String> {
        // Record the tree shape explicitly: every new build (and therefore
        // every new save header) says Some(false); only the save loaders
        // turn an ABSENT value into Some(true) for pre-fix files.
        config.tree.carry_aggressor_through_checks.get_or_insert(false);
        // fraction-vs-percent confusion charges the full cap on every pot
        if config.tree.rake_pct >= 1.0 {
            return Err(format!(
                "rake_pct is a FRACTION of the pot (0.05 = 5%), got {} — did you pass a percent?",
                config.tree.rake_pct
            ));
        }
        // negative rake would mint chips: every terminal would pay the
        // winner more than the opponent ever put in
        if config.tree.rake_pct < 0.0 {
            return Err(format!(
                "rake_pct must be >= 0, got {}",
                config.tree.rake_pct
            ));
        }
        if config.tree.rake_cap < 0.0 {
            return Err(format!(
                "rake_cap must be >= 0, got {}",
                config.tree.rake_cap
            ));
        }
        let board = parse_cards(&config.board)?;
        if !(3..=5).contains(&board.len()) {
            return Err("board must have 3 to 5 cards".to_string());
        }
        let mut board_mask = 0u64;
        for &c in &board {
            board_mask |= card_mask(c);
        }

        let ranges = [
            Range::parse(&config.range_oop)?,
            Range::parse(&config.range_ip)?,
        ];
        let mut hands: [Vec<HandInfo>; 2] = [Vec::new(), Vec::new()];
        for p in 0..2 {
            for idx in 0..NUM_COMBOS {
                let w = ranges[p].weights[idx];
                if w <= 0.0 {
                    continue;
                }
                let (c1, c2) = combo_from_index(idx);
                let mask = card_mask(c1) | card_mask(c2);
                if mask & board_mask != 0 {
                    continue;
                }
                hands[p].push(HandInfo {
                    c1,
                    c2,
                    weight: w,
                    mask,
                });
            }
            if hands[p].is_empty() {
                return Err(format!(
                    "{} range has no combos left after board card removal",
                    if p == 0 { "OOP" } else { "IP" }
                ));
            }
            if hands[p].len() > u16::MAX as usize {
                return Err("range too large".to_string());
            }
        }

        // Ranges that pass the per-player checks can still be MUTUALLY
        // impossible: every OOP combo shares a card with every IP combo
        // (e.g. OOP=AsKs vs IP=AsQs — the As blocks the lot), so no deal
        // exists and every downstream aggregate — equity, EV, exploitability
        // — is a 0/0 that surfaces as null. Compute the compatible pair mass
        // with the terminals' blocker logic (disjoint card masks) and reject
        // it here, where the config is still on hand to fix.
        let mut pair_mass = 0f64;
        for h0 in &hands[0] {
            for h1 in &hands[1] {
                if h0.mask & h1.mask == 0 {
                    pair_mass += h0.weight as f64 * h1.weight as f64;
                }
            }
        }
        if pair_mass <= 0.0 {
            return Err(
                "OOP and IP ranges are mutually impossible: every OOP combo shares a card \
                 with every IP combo after board removal, so no deal exists (zero compatible \
                 pair mass) — every equity and EV would be 0/0"
                    .to_string(),
            );
        }

        // Cross-index identical combos.
        let mut same_combo: [Vec<u32>; 2] = [Vec::new(), Vec::new()];
        for p in 0..2 {
            let opp = &hands[1 - p];
            let mut map = std::collections::HashMap::with_capacity(opp.len());
            for (j, h) in opp.iter().enumerate() {
                map.insert(combo_index(h.c1, h.c2), j as u32);
            }
            same_combo[p] = hands[p]
                .iter()
                .map(|h| {
                    map.get(&combo_index(h.c1, h.c2))
                        .copied()
                        .unwrap_or(SENTINEL)
                })
                .collect();
        }

        let weights = [
            hands[0].iter().map(|h| h.weight).collect::<Vec<f32>>(),
            hands[1].iter().map(|h| h.weight).collect::<Vec<f32>>(),
        ];

        let tree = TreeBuilder::build_with_options(
            &config.tree,
            &board,
            [hands[0].len(), hands[1].len()],
            max_nodes,
            strictness,
        )?;
        let river = build_river_table(&board, board_mask, &hands);

        // Suit symmetry group: permutations fixing the board pointwise and
        // leaving both ranges invariant (equal weights for permuted combos).
        let mut suit_perms: Vec<[u8; 4]> = Vec::new();
        let mut hand_perm: [Vec<Vec<u16>>; 2] = [Vec::new(), Vec::new()];
        let idx_of: [std::collections::HashMap<usize, u16>; 2] = [0, 1].map(|p| {
            hands[p]
                .iter()
                .enumerate()
                .map(|(i, h)| (combo_index(h.c1, h.c2), i as u16))
                .collect()
        });
        let mut perm4 = Vec::new();
        for a in 0..4u8 {
            for b in 0..4u8 {
                for c in 0..4u8 {
                    for d in 0..4u8 {
                        let pm = [a, b, c, d];
                        let mut seen = [false; 4];
                        if pm.iter().all(|&s| {
                            let f = !seen[s as usize];
                            seen[s as usize] = true;
                            f
                        }) {
                            perm4.push(pm);
                        }
                    }
                }
            }
        }
        'perm: for pm in perm4 {
            // board fixed pointwise (each board card maps to itself)
            for &c in &board {
                if permute_card(c, &pm) != c {
                    continue 'perm;
                }
            }
            let mut tables: [Vec<u16>; 2] = [Vec::new(), Vec::new()];
            for p in 0..2 {
                for h in hands[p].iter() {
                    let pc = combo_index(permute_card(h.c1, &pm), permute_card(h.c2, &pm));
                    match idx_of[p].get(&pc) {
                        Some(&j) if (hands[p][j as usize].weight - h.weight).abs() < 1e-6 => {
                            tables[p].push(j)
                        }
                        _ => continue 'perm,
                    }
                }
            }
            suit_perms.push(pm);
            hand_perm[0].push(tables[0].clone());
            hand_perm[1].push(tables[1].clone());
        }
        // ensure identity is entry 0
        if let Some(id) = suit_perms.iter().position(|pm| *pm == [0, 1, 2, 3]) {
            suit_perms.swap(0, id);
            hand_perm[0].swap(0, id);
            hand_perm[1].swap(0, id);
        }

        Ok(Spot {
            config,
            board,
            board_mask,
            tree,
            hands,
            weights,
            same_combo,
            river,
            suit_perms,
            hand_perm,
        })
    }

    /// Indices into suit_perms that fix every dealt card (the stabilizer of
    /// the cards revealed so far).
    pub fn perms_fixing(&self, dealt: &Dealt) -> Vec<usize> {
        self.suit_perms
            .iter()
            .enumerate()
            .filter(|(_, pm)| {
                (0..dealt.len as usize).all(|i| permute_card(dealt.cards[i], pm) == dealt.cards[i])
            })
            .map(|(k, _)| k)
            .collect()
    }

    /// Estimated memory for solver arenas, in bytes (f32 storage).
    pub fn arena_bytes(&self) -> u64 {
        self.arena_bytes_for(Storage::F32)
    }

    /// Estimated memory for solver arenas under a given storage mode
    /// (regrets + strategy sums — what DCFR and CFR+ hold).
    pub fn arena_bytes_for(&self, storage: Storage) -> u64 {
        let entries = self.tree.data_size[0] + self.tree.data_size[1];
        match storage {
            Storage::F32 => entries * 2 * 4,
            // 2 bytes per entry plus four per-node f32 scale arrays
            Storage::Compressed => entries * 2 * 2 + self.tree.nodes.len() as u64 * 16,
        }
    }

    /// Extra bytes the PCFR+ prediction arenas add on top of
    /// `arena_bytes_for` (a third, regret-sized pair, allocated lazily on
    /// the first PCFR+ iteration); 0 for the other algorithms.
    pub fn pred_bytes_for(&self, storage: Storage, algo: crate::cfr::Algorithm) -> u64 {
        if algo != crate::cfr::Algorithm::PcfrPlus {
            return 0;
        }
        let entries = self.tree.data_size[0] + self.tree.data_size[1];
        match storage {
            Storage::F32 => entries * 4,
            // 2 bytes per entry plus two per-node f32 scale arrays
            Storage::Compressed => entries * 2 + self.tree.nodes.len() as u64 * 8,
        }
    }

    /// Arena memory for a given algorithm: `arena_bytes_for` plus the
    /// PCFR+ prediction arenas when applicable (1.5x the DCFR estimate).
    pub fn arena_bytes_for_algo(&self, storage: Storage, algo: crate::cfr::Algorithm) -> u64 {
        self.arena_bytes_for(storage) + self.pred_bytes_for(storage, algo)
    }

    /// Bytes held by the tree itself (nodes, child slots, actions) — the
    /// part of a spot's memory that exists before any arena is allocated.
    pub fn tree_bytes(&self) -> u64 {
        self.tree.bytes()
    }

    /// Rough VRAM needed to solve this spot on the GPU: per-node hand staging
    /// buffers, f32 regret+strategy arenas, and slack for river/lock tables.
    /// CPU-only (no CUDA), so the UI can show the estimate up front even
    /// when the `gpu` feature is off. Mirrors `gpu::GpuSolver`'s allocations.
    pub fn vram_estimate_bytes(&self) -> u64 {
        let n = self.tree.nodes.len() as u64;
        let nh0 = self.hands[0].len() as u64;
        let nh1 = self.hands[1].len() as u64;
        let nh_max = nh0.max(nh1);
        // Count every potential writer, including non-representative chance
        // branches. This conservatively covers either isomorphism setting.
        let mut reach_blocks = [1u64; 2];
        for node in &self.tree.nodes {
            match node.kind {
                crate::tree::KIND_ACTION => {
                    reach_blocks[node.player as usize] += node.num_children as u64;
                }
                crate::tree::KIND_CHANCE => {
                    let start = node.children_start as usize;
                    let children = self.tree.children[start..start + 52].iter()
                        .filter(|&&child| child != crate::tree::SENTINEL).count() as u64;
                    reach_blocks[0] += children;
                    reach_blocks[1] += children;
                }
                _ => {}
            }
        }
        let staging = (reach_blocks[0] * nh0 + reach_blocks[1] * nh1 + n * nh_max) * 4;
        let arenas = (self.tree.data_size[0] + self.tree.data_size[1]) * 2 * 4;
        staging + arenas + 512 * 1024 * 1024
    }

    pub fn num_action_nodes(&self) -> usize {
        self.tree
            .nodes
            .iter()
            .filter(|n| n.kind == crate::tree::KIND_ACTION)
            .count()
    }
}

fn build_river_table(board: &[Card], board_mask: u64, hands: &[Vec<HandInfo>; 2]) -> RiverTable {
    let root_street = (board.len() - 3) as u8;

    let eval_board = |extra: &[Card]| -> Box<RiverBoardEval> {
        let mut full = [0u8; 5];
        full[..board.len()].copy_from_slice(board);
        full[board.len()..board.len() + extra.len()].copy_from_slice(extra);
        debug_assert_eq!(board.len() + extra.len(), 5);
        let mut extra_mask = 0u64;
        for &c in extra {
            extra_mask |= card_mask(c);
        }
        let mut sorted: [Vec<(u32, u16)>; 2] = [Vec::new(), Vec::new()];
        let mut cards7 = [0u8; 7];
        cards7[..5].copy_from_slice(&full);
        for p in 0..2 {
            let mut v: Vec<(u32, u16)> = Vec::with_capacity(hands[p].len());
            for (i, h) in hands[p].iter().enumerate() {
                if h.mask & extra_mask != 0 {
                    continue;
                }
                cards7[5] = h.c1;
                cards7[6] = h.c2;
                v.push((evaluate7(&cards7), i as u16));
            }
            v.sort_unstable();
            sorted[p] = v;
        }
        Box::new(RiverBoardEval { sorted })
    };

    let entries: Vec<Option<Box<RiverBoardEval>>> = match root_street {
        2 => vec![Some(eval_board(&[]))],
        1 => {
            let mut slots: Vec<Option<Box<RiverBoardEval>>> = (0..52).map(|_| None).collect();
            let computed: Vec<(usize, Box<RiverBoardEval>)> = (0..52u8)
                .into_par_iter()
                .filter(|&c| board_mask & card_mask(c) == 0)
                .map(|c| (c as usize, eval_board(&[c])))
                .collect();
            for (i, e) in computed {
                slots[i] = Some(e);
            }
            slots
        }
        _ => {
            let mut slots: Vec<Option<Box<RiverBoardEval>>> =
                (0..52 * 52).map(|_| None).collect();
            let pairs: Vec<(u8, u8)> = {
                let mut v = Vec::new();
                for a in 0..52u8 {
                    if board_mask & card_mask(a) != 0 {
                        continue;
                    }
                    for b in (a + 1)..52 {
                        if board_mask & card_mask(b) != 0 {
                            continue;
                        }
                        v.push((a, b));
                    }
                }
                v
            };
            let computed: Vec<(usize, Box<RiverBoardEval>)> = pairs
                .into_par_iter()
                .map(|(a, b)| (a as usize * 52 + b as usize, eval_board(&[a, b])))
                .collect();
            for (i, e) in computed {
                slots[i] = Some(e);
            }
            slots
        }
    };

    RiverTable {
        root_street,
        entries,
    }
}

// ---------------------------------------------------------------------------
// Terminal node evaluation
// ---------------------------------------------------------------------------

/// Counterfactual value at a fold terminal: `amount` per unit of compatible
/// opponent reach.
pub fn fold_cfv(
    hands_me: &[HandInfo],
    hands_opp: &[HandInfo],
    reach_opp: &[f32],
    same_combo_me: &[u32],
    amount: f32,
    out: &mut [f32],
) {
    let mut t = 0f64;
    let mut s = [0f64; 52];
    for (j, h) in hands_opp.iter().enumerate() {
        let r = reach_opp[j] as f64;
        t += r;
        s[h.c1 as usize] += r;
        s[h.c2 as usize] += r;
    }
    for (i, h) in hands_me.iter().enumerate() {
        let same = same_combo_me[i];
        let same_r = if same != SENTINEL {
            reach_opp[same as usize]
        } else {
            0.0
        };
        let valid = (t - s[h.c1 as usize] - s[h.c2 as usize]) as f32 + same_r;
        out[i] = amount * valid;
    }
}

/// Counterfactual value at a showdown. `out` must be zeroed by the caller;
/// only hands valid on this river board are written.
#[allow(clippy::too_many_arguments)]
pub fn showdown_cfv(
    eval: &RiverBoardEval,
    me: usize,
    hands_me: &[HandInfo],
    hands_opp: &[HandInfo],
    reach_opp: &[f32],
    same_combo_me: &[u32],
    win: f32,
    lose: f32,
    tie: f32,
    out: &mut [f32],
) {
    let mine = &eval.sorted[me];
    let opps = &eval.sorted[1 - me];

    let mut t_all = 0f64;
    let mut s_all = [0f64; 52];
    for &(_, j) in opps {
        let r = reach_opp[j as usize] as f64;
        let h = &hands_opp[j as usize];
        t_all += r;
        s_all[h.c1 as usize] += r;
        s_all[h.c2 as usize] += r;
    }

    // Pass 1 (ascending): strictly weaker opponent reach for each of my hands.
    // Each valid hand appears once in mine. Its output slot can hold the
    // intermediate lower mass until the reverse pass overwrites that slot.
    {
        let mut t = 0f64;
        let mut s = [0f64; 52];
        let mut j = 0usize;
        for &(stren, i) in mine {
            while j < opps.len() && opps[j].0 < stren {
                let jj = opps[j].1 as usize;
                let r = reach_opp[jj] as f64;
                let h = &hands_opp[jj];
                t += r;
                s[h.c1 as usize] += r;
                s[h.c2 as usize] += r;
                j += 1;
            }
            let h = &hands_me[i as usize];
            out[i as usize] = (t - s[h.c1 as usize] - s[h.c2 as usize]) as f32;
        }
    }

    // Pass 2 (descending): strictly stronger opponent reach, then finalize.
    {
        let mut t = 0f64;
        let mut s = [0f64; 52];
        let mut j = opps.len();
        for k in (0..mine.len()).rev() {
            let (stren, i) = mine[k];
            while j > 0 && opps[j - 1].0 > stren {
                j -= 1;
                let jj = opps[j].1 as usize;
                let r = reach_opp[jj] as f64;
                let h = &hands_opp[jj];
                t += r;
                s[h.c1 as usize] += r;
                s[h.c2 as usize] += r;
            }
            let h = &hands_me[i as usize];
            let higher = (t - s[h.c1 as usize] - s[h.c2 as usize]) as f32;
            let same = same_combo_me[i as usize];
            let same_r = if same != SENTINEL {
                reach_opp[same as usize]
            } else {
                0.0
            };
            let valid = (t_all - s_all[h.c1 as usize] - s_all[h.c2 as usize]) as f32 + same_r;
            let lo = out[i as usize];
            let ti = valid - lo - higher;
            out[i as usize] = win * lo + lose * higher + tie * ti;
        }
    }
}

/// Accumulate win/tie/valid opponent reach per hand for equity calculation.
pub fn sweep_buckets(
    eval: &RiverBoardEval,
    me: usize,
    hands_me: &[HandInfo],
    hands_opp: &[HandInfo],
    reach_opp: &[f32],
    same_combo_me: &[u32],
    acc_win: &mut [f64],
    acc_tie: &mut [f64],
    acc_valid: &mut [f64],
) {
    let mine = &eval.sorted[me];
    let opps = &eval.sorted[1 - me];

    let mut t_all = 0f64;
    let mut s_all = [0f64; 52];
    for &(_, j) in opps {
        let r = reach_opp[j as usize] as f64;
        let h = &hands_opp[j as usize];
        t_all += r;
        s_all[h.c1 as usize] += r;
        s_all[h.c2 as usize] += r;
    }

    let mut lower = vec![0f64; mine.len()];
    {
        let mut t = 0f64;
        let mut s = [0f64; 52];
        let mut j = 0usize;
        for (k, &(stren, i)) in mine.iter().enumerate() {
            while j < opps.len() && opps[j].0 < stren {
                let jj = opps[j].1 as usize;
                let r = reach_opp[jj] as f64;
                let h = &hands_opp[jj];
                t += r;
                s[h.c1 as usize] += r;
                s[h.c2 as usize] += r;
                j += 1;
            }
            let h = &hands_me[i as usize];
            lower[k] = t - s[h.c1 as usize] - s[h.c2 as usize];
        }
    }
    {
        let mut t = 0f64;
        let mut s = [0f64; 52];
        let mut j = opps.len();
        for k in (0..mine.len()).rev() {
            let (stren, i) = mine[k];
            while j > 0 && opps[j - 1].0 > stren {
                j -= 1;
                let jj = opps[j].1 as usize;
                let r = reach_opp[jj] as f64;
                let h = &hands_opp[jj];
                t += r;
                s[h.c1 as usize] += r;
                s[h.c2 as usize] += r;
            }
            let h = &hands_me[i as usize];
            let higher = t - s[h.c1 as usize] - s[h.c2 as usize];
            let same = same_combo_me[i as usize];
            let same_r = if same != SENTINEL {
                reach_opp[same as usize] as f64
            } else {
                0.0
            };
            let valid = t_all - s_all[h.c1 as usize] - s_all[h.c2 as usize] + same_r;
            let i = i as usize;
            acc_win[i] += lower[k];
            acc_tie[i] += valid - lower[k] - higher;
            acc_valid[i] += valid;
        }
    }
}
#[cfg(test)]
#[derive(Clone,Copy,Default)]
struct D274Marks {tree_ns:u64,river_ns:u64,symmetry_ns:u64,total_ns:u64,tree_started:bool,river_started:bool,symmetry_started:bool}
#[cfg(test)]
thread_local! { static D274_MARKS: std::cell::Cell<D274Marks> = std::cell::Cell::new(D274Marks::default()); }
#[cfg(test)]
impl Spot {
    fn d274_profiled_new_impl(
        mut config: SpotConfig,
        max_nodes: Option<usize>,
        strictness: Strictness,
    ) -> Result<Spot, String> {
        let d274_total=std::time::Instant::now();
        // Record the tree shape explicitly: every new build (and therefore
        // every new save header) says Some(false); only the save loaders
        // turn an ABSENT value into Some(true) for pre-fix files.
        config.tree.carry_aggressor_through_checks.get_or_insert(false);
        // fraction-vs-percent confusion charges the full cap on every pot
        if config.tree.rake_pct >= 1.0 {
            return Err(format!(
                "rake_pct is a FRACTION of the pot (0.05 = 5%), got {} — did you pass a percent?",
                config.tree.rake_pct
            ));
        }
        // negative rake would mint chips: every terminal would pay the
        // winner more than the opponent ever put in
        if config.tree.rake_pct < 0.0 {
            return Err(format!(
                "rake_pct must be >= 0, got {}",
                config.tree.rake_pct
            ));
        }
        if config.tree.rake_cap < 0.0 {
            return Err(format!(
                "rake_cap must be >= 0, got {}",
                config.tree.rake_cap
            ));
        }
        let board = parse_cards(&config.board)?;
        if !(3..=5).contains(&board.len()) {
            return Err("board must have 3 to 5 cards".to_string());
        }
        let mut board_mask = 0u64;
        for &c in &board {
            board_mask |= card_mask(c);
        }

        let ranges = [
            Range::parse(&config.range_oop)?,
            Range::parse(&config.range_ip)?,
        ];
        let mut hands: [Vec<HandInfo>; 2] = [Vec::new(), Vec::new()];
        for p in 0..2 {
            for idx in 0..NUM_COMBOS {
                let w = ranges[p].weights[idx];
                if w <= 0.0 {
                    continue;
                }
                let (c1, c2) = combo_from_index(idx);
                let mask = card_mask(c1) | card_mask(c2);
                if mask & board_mask != 0 {
                    continue;
                }
                hands[p].push(HandInfo {
                    c1,
                    c2,
                    weight: w,
                    mask,
                });
            }
            if hands[p].is_empty() {
                return Err(format!(
                    "{} range has no combos left after board card removal",
                    if p == 0 { "OOP" } else { "IP" }
                ));
            }
            if hands[p].len() > u16::MAX as usize {
                return Err("range too large".to_string());
            }
        }

        // Ranges that pass the per-player checks can still be MUTUALLY
        // impossible: every OOP combo shares a card with every IP combo
        // (e.g. OOP=AsKs vs IP=AsQs — the As blocks the lot), so no deal
        // exists and every downstream aggregate — equity, EV, exploitability
        // — is a 0/0 that surfaces as null. Compute the compatible pair mass
        // with the terminals' blocker logic (disjoint card masks) and reject
        // it here, where the config is still on hand to fix.
        let mut pair_mass = 0f64;
        for h0 in &hands[0] {
            for h1 in &hands[1] {
                if h0.mask & h1.mask == 0 {
                    pair_mass += h0.weight as f64 * h1.weight as f64;
                }
            }
        }
        if pair_mass <= 0.0 {
            return Err(
                "OOP and IP ranges are mutually impossible: every OOP combo shares a card \
                 with every IP combo after board removal, so no deal exists (zero compatible \
                 pair mass) — every equity and EV would be 0/0"
                    .to_string(),
            );
        }

        // Cross-index identical combos.
        let mut same_combo: [Vec<u32>; 2] = [Vec::new(), Vec::new()];
        for p in 0..2 {
            let opp = &hands[1 - p];
            let mut map = std::collections::HashMap::with_capacity(opp.len());
            for (j, h) in opp.iter().enumerate() {
                map.insert(combo_index(h.c1, h.c2), j as u32);
            }
            same_combo[p] = hands[p]
                .iter()
                .map(|h| {
                    map.get(&combo_index(h.c1, h.c2))
                        .copied()
                        .unwrap_or(SENTINEL)
                })
                .collect();
        }

        let weights = [
            hands[0].iter().map(|h| h.weight).collect::<Vec<f32>>(),
            hands[1].iter().map(|h| h.weight).collect::<Vec<f32>>(),
        ];

        let d274_tree=std::time::Instant::now();
        D274_MARKS.with(|m|{let mut x=m.get();x.tree_started=true;m.set(x);});
        let tree = TreeBuilder::build_with_options(
            &config.tree,
            &board,
            [hands[0].len(), hands[1].len()],
            max_nodes,
            strictness,
        )?;
        D274_MARKS.with(|m|{let mut x=m.get();x.tree_ns=d274_tree.elapsed().as_nanos()as u64;m.set(x);});
        let d274_river=std::time::Instant::now();
        D274_MARKS.with(|m|{let mut x=m.get();x.river_started=true;m.set(x);});
        let river = build_river_table(&board, board_mask, &hands);
        D274_MARKS.with(|m|{let mut x=m.get();x.river_ns=d274_river.elapsed().as_nanos()as u64;m.set(x);});

        let d274_symmetry=std::time::Instant::now();
        D274_MARKS.with(|m|{let mut x=m.get();x.symmetry_started=true;m.set(x);});
        // Suit symmetry group: permutations fixing the board pointwise and
        // leaving both ranges invariant (equal weights for permuted combos).
        let mut suit_perms: Vec<[u8; 4]> = Vec::new();
        let mut hand_perm: [Vec<Vec<u16>>; 2] = [Vec::new(), Vec::new()];
        let idx_of: [std::collections::HashMap<usize, u16>; 2] = [0, 1].map(|p| {
            hands[p]
                .iter()
                .enumerate()
                .map(|(i, h)| (combo_index(h.c1, h.c2), i as u16))
                .collect()
        });
        let mut perm4 = Vec::new();
        for a in 0..4u8 {
            for b in 0..4u8 {
                for c in 0..4u8 {
                    for d in 0..4u8 {
                        let pm = [a, b, c, d];
                        let mut seen = [false; 4];
                        if pm.iter().all(|&s| {
                            let f = !seen[s as usize];
                            seen[s as usize] = true;
                            f
                        }) {
                            perm4.push(pm);
                        }
                    }
                }
            }
        }
        'perm: for pm in perm4 {
            // board fixed pointwise (each board card maps to itself)
            for &c in &board {
                if permute_card(c, &pm) != c {
                    continue 'perm;
                }
            }
            let mut tables: [Vec<u16>; 2] = [Vec::new(), Vec::new()];
            for p in 0..2 {
                for h in hands[p].iter() {
                    let pc = combo_index(permute_card(h.c1, &pm), permute_card(h.c2, &pm));
                    match idx_of[p].get(&pc) {
                        Some(&j) if (hands[p][j as usize].weight - h.weight).abs() < 1e-6 => {
                            tables[p].push(j)
                        }
                        _ => continue 'perm,
                    }
                }
            }
            suit_perms.push(pm);
            hand_perm[0].push(tables[0].clone());
            hand_perm[1].push(tables[1].clone());
        }
        // ensure identity is entry 0
        if let Some(id) = suit_perms.iter().position(|pm| *pm == [0, 1, 2, 3]) {
            suit_perms.swap(0, id);
            hand_perm[0].swap(0, id);
            hand_perm[1].swap(0, id);
        }

        let d274_result=Ok(Spot {
            config,
            board,
            board_mask,
            tree,
            hands,
            weights,
            same_combo,
            river,
            suit_perms,
            hand_perm,
        });
        D274_MARKS.with(|m|{let mut x=m.get();x.symmetry_ns=d274_symmetry.elapsed().as_nanos()as u64;x.total_ns=d274_total.elapsed().as_nanos()as u64;m.set(x);});
        d274_result
    }


}

#[cfg(test)]
mod d274_observer {
use super::*;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::Path,time::Instant};
use serde_json::{json,Value};
trait Encode {fn size(&self)->u64;fn encode(&self,w:&mut impl Write);}
macro_rules! primitive {($t:ty,$n:expr,$f:expr)=>{impl Encode for $t {fn size(&self)->u64{$n}fn encode(&self,w:&mut impl Write){w.write_all(&($f)(*self)).unwrap();}}};}
primitive!(u8,1,|x:u8|[x]);primitive!(u16,2,|x:u16|x.to_le_bytes());primitive!(u32,4,|x:u32|x.to_le_bytes());primitive!(u64,8,|x:u64|x.to_le_bytes());
primitive!(f32,4,|x:f32|x.to_bits().to_le_bytes());primitive!(f64,8,|x:f64|x.to_bits().to_le_bytes());
impl<T:Encode> Encode for Vec<T>{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(self.len()as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode,const N:usize> Encode for[T;N]{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(N as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode> Encode for Option<T>{fn size(&self)->u64{1+self.as_ref().map(Encode::size).unwrap_or(0)}fn encode(&self,w:&mut impl Write){match self{None=>0u8.encode(w),Some(x)=>{1u8.encode(w);x.encode(w);}}}}
impl<T:Encode> Encode for Box<T>{fn size(&self)->u64{self.as_ref().size()}fn encode(&self,w:&mut impl Write){self.as_ref().encode(w);}}
impl Encode for(u32,u16){fn size(&self)->u64{6}fn encode(&self,w:&mut impl Write){self.0.encode(w);self.1.encode(w);}}
impl Encode for crate::tree::Node{
 fn size(&self)->u64{68}
 fn encode(&self,w:&mut impl Write){self.kind.encode(w);self.player.encode(w);self.street.encode(w);self.num_children.encode(w);self.children_start.encode(w);self.actions_start.encode(w);self.data_offset.encode(w);self.put.encode(w);self.t_win.encode(w);self.t_lose.encode(w);self.t_tie.encode(w);}
}
impl Encode for crate::tree::Action{
 fn size(&self)->u64{match self{Self::Fold|Self::Check=>1,_=>9}}
 fn encode(&self,w:&mut impl Write){use crate::tree::Action::*;match self{Fold=>0u8.encode(w),Check=>1u8.encode(w),Call(x)=>{2u8.encode(w);x.encode(w);},Bet(x)=>{3u8.encode(w);x.encode(w);},Raise(x)=>{4u8.encode(w);x.encode(w);}}}
}
impl Encode for HandInfo{fn size(&self)->u64{14}fn encode(&self,w:&mut impl Write){self.c1.encode(w);self.c2.encode(w);self.weight.encode(w);self.mask.encode(w);}}
impl Encode for RiverBoardEval{fn size(&self)->u64{self.sorted.size()}fn encode(&self,w:&mut impl Write){self.sorted.encode(w);}}
fn field(w:&mut impl Write,name:&str,v:&impl Encode){(name.len()as u32).encode(w);w.write_all(name.as_bytes()).unwrap();v.size().encode(w);v.encode(w);}
fn dump(s:&Spot,path:&Path){
 let mut w=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());w.write_all(b"D274-SPOT-v1\0\0\0\0").unwrap();
 field(&mut w,"config_json",&serde_json::to_vec(&s.config).unwrap());field(&mut w,"board",&s.board);field(&mut w,"board_mask",&s.board_mask);
 field(&mut w,"tree_config_json",&serde_json::to_vec(&s.tree.config).unwrap());field(&mut w,"tree_root_street",&s.tree.root_street);
 field(&mut w,"tree_nodes",&s.tree.nodes);field(&mut w,"tree_children",&s.tree.children);field(&mut w,"tree_actions",&s.tree.actions);field(&mut w,"tree_data_size",&s.tree.data_size);
 field(&mut w,"hands",&s.hands);field(&mut w,"weights",&s.weights);field(&mut w,"same_combo",&s.same_combo);
 field(&mut w,"river_root_street",&s.river.root_street);field(&mut w,"river_entries",&s.river.entries);field(&mut w,"suit_perms",&s.suit_perms);field(&mut w,"hand_perm",&s.hand_perm);
 let mut capacities=vec![s.board.capacity()as u64,s.tree.nodes.capacity()as u64,s.tree.children.capacity()as u64,s.tree.actions.capacity()as u64,s.river.entries.capacity()as u64,s.suit_perms.capacity()as u64];
 for p in 0..2{capacities.extend([s.hands[p].capacity()as u64,s.weights[p].capacity()as u64,s.same_combo[p].capacity()as u64,s.hand_perm[p].capacity()as u64]);for perm in&s.hand_perm[p]{capacities.push(perm.capacity()as u64);}}
 for entry in&s.river.entries{if let Some(entry)=entry{for p in 0..2{capacities.push(entry.sorted[p].capacity()as u64);}}}
 field(&mut w,"data_vector_capacities",&capacities);w.flush().unwrap();w.get_ref().sync_all().unwrap();
}
fn compare_data(a:&Spot,b:&Spot){
 assert_eq!(serde_json::to_vec(&a.config).unwrap(),serde_json::to_vec(&b.config).unwrap());
 assert_eq!(serde_json::to_vec(&a.tree.config).unwrap(),serde_json::to_vec(&b.tree.config).unwrap());
 assert_eq!(a.tree.nodes.len(),b.tree.nodes.len());assert_eq!(a.tree.children,b.tree.children);assert_eq!(a.tree.data_size,b.tree.data_size);
 for(x,y)in a.tree.nodes.iter().zip(&b.tree.nodes){
  assert_eq!((x.kind,x.player,x.street,x.num_children,x.children_start,x.actions_start,x.data_offset),(y.kind,y.player,y.street,y.num_children,y.children_start,y.actions_start,y.data_offset));
  assert_eq!([x.put[0],x.put[1],x.t_win,x.t_lose,x.t_tie].map(f64::to_bits),[y.put[0],y.put[1],y.t_win,y.t_lose,y.t_tie].map(f64::to_bits));
 }
 assert_eq!(a.tree.actions.len(),b.tree.actions.len());for(x,y)in a.tree.actions.iter().zip(&b.tree.actions){
  use crate::tree::Action::*;match(x,y){(Fold,Fold)|(Check,Check)=>{},(Call(x),Call(y))|(Bet(x),Bet(y))|(Raise(x),Raise(y))=>assert_eq!(x.to_bits(),y.to_bits()),_=>panic!("action variant")}
 }
 assert_eq!(a.board,b.board);assert_eq!(a.board_mask,b.board_mask);assert_eq!(a.tree.root_street,b.tree.root_street);assert_eq!(a.river.root_street,b.river.root_street);assert_eq!(a.suit_perms,b.suit_perms);assert_eq!(a.hand_perm,b.hand_perm);
 for p in 0..2{
  assert_eq!(a.hands[p].len(),b.hands[p].len());for(x,y)in a.hands[p].iter().zip(&b.hands[p]){assert_eq!((x.c1,x.c2,x.weight.to_bits(),x.mask),(y.c1,y.c2,y.weight.to_bits(),y.mask));}
  assert_eq!(a.weights[p].iter().map(|x|x.to_bits()).collect::<Vec<_>>(),b.weights[p].iter().map(|x|x.to_bits()).collect::<Vec<_>>());assert_eq!(a.same_combo[p],b.same_combo[p]);
 }
 assert_eq!(a.river.entries.len(),b.river.entries.len());for(x,y)in a.river.entries.iter().zip(&b.river.entries){match(x,y){(None,None)=>{},(Some(x),Some(y))=>assert_eq!(x.sorted,y.sorted),_=>panic!("river slot")}}
}

#[test]
fn observe(){
 let fixtures:Vec<Value>=serde_json::from_str(include_str!(r"X:\Dev\GTOpen-research\postflop-gpu-20261028\runs\D274-spot-observation\fixtures.json")).unwrap();assert_eq!(fixtures.len(),3);
 let output=std::path::PathBuf::from(std::env::var("D274_OUTPUT").unwrap());std::fs::create_dir(&output).unwrap();
 let order=std::env::var("D274_ORDER").unwrap();assert!(order=="BO"||order=="OB");assert_eq!(rayon::current_num_threads(),16);
 for f in&fixtures{
  let id=f["fixture"].as_str().unwrap();let cfg:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();
  let mut built: [Option<Spot>;2]=[None,None];let mut elapsed=[0u64;2];let mut marks=D274Marks::default();
  for arm in if order=="BO"{[0usize,1]}else{[1usize,0]}{
   D274_MARKS.with(|m|m.set(D274Marks::default()));let start=Instant::now();
   let spot=if arm==0{Spot::new(cfg.clone())}else{Spot::d274_profiled_new_impl(cfg.clone(),None,Strictness::Strict)}.unwrap();
   elapsed[arm]=start.elapsed().as_nanos()as u64;if arm==1{marks=D274_MARKS.with(|m|m.get());}built[arm]=Some(spot);
  }
  let a=built[0].as_ref().unwrap();let b=built[1].as_ref().unwrap();assert_eq!(a.tree.nodes.len()as u64,f["expected_nodes"].as_u64().unwrap());compare_data(a,b);
  assert!(marks.tree_started&&marks.river_started&&marks.symmetry_started);
  assert!(marks.tree_ns+marks.river_ns+marks.symmetry_ns<=marks.total_ns&&marks.total_ns<=elapsed[1]);
  dump(a,&output.join(format!("{id}-baseline.spot.bin")));dump(b,&output.join(format!("{id}-observed.spot.bin")));
  println!("\nD274_SPOT {}",json!({"fixture":id,"order":order,"nodes":a.tree.nodes.len(),"hands":a.hands.each_ref().map(|v|v.len()),"baseline_ns":elapsed[0],"observed_ns":elapsed[1],"tree_ns":marks.tree_ns,"river_ns":marks.river_ns,"symmetry_ns":marks.symmetry_ns,"profiled_constructor_ns":marks.total_ns,"full_data_native_exact":true,"worker_count":rayon::current_num_threads(),"CPU_only":true,"CFR_iterations_GPU_calls":0}));std::io::stdout().flush().unwrap();
 }
 let base:SpotConfig=serde_json::from_value(fixtures[0]["config"].clone()).unwrap();let mut errors=0;
 for tag in["budget0","budget1","budget100","bad_stack","bad_bet","bad_board","empty_range","impossible_ranges"]{
  let mut cfg=base.clone();let limit=match tag{"budget0"=>Some(0),"budget1"=>Some(1),"budget100"=>Some(100),_=>None};
  match tag{"bad_stack"=>cfg.tree.effective_stack=0.,"bad_bet"=>cfg.tree.oop[0].bet=vec![crate::tree::BetSize::PrevMult(2.5)],"bad_board"=>cfg.board="Ks7h".into(),"empty_range"=>cfg.range_oop="".into(),"impossible_ranges"=>{cfg.range_oop="AcKc".into();cfg.range_ip="AcQc".into();},_=>{}}
  let baseline=match Spot::new_with_limit(cfg.clone(),limit){Ok(_)=>panic!("expected error {tag}"),Err(e)=>e};D274_MARKS.with(|m|m.set(D274Marks::default()));
  let observed=match Spot::d274_profiled_new_impl(cfg,limit,Strictness::Strict){Ok(_)=>panic!("expected profiled error {tag}"),Err(e)=>e};let marks=D274_MARKS.with(|m|m.get());
  assert_eq!(baseline,observed);assert!(!marks.river_started&&!marks.symmetry_started);
  println!("D274_ERROR {}",json!({"case":tag,"same_error":baseline,"river_not_started":true,"symmetry_not_started":true}));errors+=1;
 }
 assert_eq!(errors,8);println!("D274_COMPLETE {}",json!({"fixtures":3,"full_Spot_pairs":3,"error_cases":8,"CFR_iterations_GPU_calls":0}));
}
}
