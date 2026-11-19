//! CPU-side restructuring of a Spot's tree into level-ordered flat arrays for
//! level-synchronous GPU traversal.
//!
//! Levels are node depths (every edge, action or chance, adds one). The GPU
//! processes one level at a time: a down sweep propagating reach vectors from
//! parents to children, then an up sweep accumulating counterfactual values
//! from children to parents and applying regret/strategy updates.
//!
//! Reach buffers use the "owner" trick: an action edge only changes the
//! actor's reach, so the child reads the other player's reach from the
//! nearest ancestor that wrote it (`reach_src`), halving down-sweep traffic.
//!
//! Suit isomorphism: with `use_iso`, only orbit-representative chance
//! branches enter the work lists. Each chance node carries a card table
//! (card, representative child, suit-perm index) so the up sweep can
//! synthesize non-representative branches by hand-index permutation,
//! mirroring the CPU's `chance_node` exactly. Without isomorphism the same
//! tables degenerate to identity orbits.

use crate::game::{Dealt, Spot};
use crate::tree::{KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, SENTINEL};

/// Plan layout options (see [`GpuPlan::build_with`]).
#[derive(Clone, Copy, Debug, Default)]
pub struct PlanOptions {
    /// Give terminal (fold / showdown) nodes slots in the per-level parity
    /// scratch instead of one resident slot each. Terminal values then live
    /// only until their parent level consumes them, so an evaluation that
    /// reuses them (mode 1 after mode 0 under rake, "trust the read") must
    /// recompute them; `GpuSolver` does so whenever the plan has this set.
    pub terminal_scratch: bool,
}

#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct LevelSpan {
    pub start: u32,
    pub count: u32,
}

/// Work-list spans of one level of one sweep.
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct LevelSpans {
    pub action: LevelSpan,
    /// Chance edges whose parent is at this level (`chance_parents/children/cards`).
    pub edge: LevelSpan,
    /// Chance nodes (`chance_nodes`).
    pub chance: LevelSpan,
    pub fold: LevelSpan,
    pub show: LevelSpan,
}

/// One level-synchronous sweep: the whole tree (resident plan), or in a
/// grouped plan the root part or one group of first-layer subtrees. A group
/// is entered through its `entry` chance edges (parents in the root part).
#[derive(Clone, Default, Debug, PartialEq, Eq)]
pub struct SweepSpans {
    pub levels: Vec<LevelSpans>,
    pub entry: LevelSpan,
}

pub struct GpuPlan {
    pub num_levels: usize,
    pub nh: [usize; 2],
    pub nh_max: usize,
    pub num_nodes: usize,
    /// Whether orbit folding is active (use_iso && >1 suit perm).
    pub iso_active: bool,

    // Level-ordered work lists (flat arrays + one span per level).
    pub action_nodes: Vec<u32>,
    pub action_spans: Vec<LevelSpan>,
    pub chance_parents: Vec<u32>,
    pub chance_children: Vec<u32>,
    pub chance_cards: Vec<u32>,
    pub chance_spans: Vec<LevelSpan>,
    pub chance_nodes: Vec<u32>,
    pub chance_node_spans: Vec<LevelSpan>,
    pub fold_nodes: Vec<u32>,
    pub fold_spans: Vec<LevelSpan>,
    pub show_nodes: Vec<u32>,
    pub show_spans: Vec<LevelSpan>,

    // Per-chance-node card tables: span [cc_start[n], cc_start[n]+cc_count[n])
    // into the cc_* arrays.
    pub cc_start: Vec<u32>,
    pub cc_count: Vec<u32>,
    pub cc_card: Vec<u32>,
    /// Representative child traversed for this card's orbit.
    pub cc_child: Vec<u32>,
    /// suit_perms index mapping this card onto its representative.
    pub cc_perm: Vec<u32>,
    /// hand_perm[p] flattened: perm k occupies [k*nh_p, (k+1)*nh_p).
    pub hand_perm_flat: [Vec<u32>; 2],

    // Per-node arrays (length num_nodes).
    pub node_player: Vec<i32>,
    pub node_na: Vec<i32>,
    /// Arena offsets; compact plans use u64::MAX for inactive action nodes.
    pub node_data_off: Vec<u64>,
    pub arena_elements: [usize; 2],
    pub node_children_start: Vec<u32>,
    pub node_twin: Vec<f32>,
    pub node_tlose: Vec<f32>,
    pub node_ttie: Vec<f32>,
    /// Offset of player 1's terminal payoffs in node_twin/tlose/ttie: 0
    /// when both players share the chip payoffs, the node count under ICM.
    pub payoff_stride: usize,
    /// Chance nodes: 1 / (46 - street).
    pub node_cdiv: Vec<f32>,
    /// Showdown nodes: dense river slot; -1 elsewhere.
    pub node_river_slot: Vec<i32>,
    /// reach_src[p][n] = node whose reach buffer holds n's reach for player p.
    pub reach_src: [Vec<u32>; 2],
    /// Dense physical reach slots, sharing storage exactly when owners match.
    pub reach_slot: [Vec<u32>; 2],
    pub reach_blocks: [usize; 2],
    /// CFV slots: persistent terminals plus alternating-level action/chance scratch
    /// (with `terminal_scratch`, terminals share the scratch too).
    /// Unvisited nodes have no allocation.
    pub cfv_slot: Vec<u32>,
    pub cfv_blocks: usize,
    /// Terminal cfvs live in the per-level scratch (`PlanOptions::terminal_scratch`).
    pub terminal_scratch: bool,
    /// Length of the tree's child-slot array (uploaded as is).
    pub children_len: usize,
    /// Sweeps in traversal order. Resident plans: one sweep over the whole
    /// tree, whose levels are the per-level spans above. Grouped plans
    /// (`regroup`): the root part, then one sweep per group; the per-level
    /// span vectors above are empty there.
    pub sweeps: Vec<SweepSpans>,
    /// First-layer card groups of a grouped plan, in sweep order (empty when
    /// resident).
    pub groups: Vec<Vec<u8>>,

    // Per-hand arrays.
    pub hand_c1: [Vec<u32>; 2],
    pub hand_c2: [Vec<u32>; 2],
    pub hand_mask: [Vec<u64>; 2],
    pub same_combo: [Vec<u32>; 2],
    pub weights: [Vec<f32>; 2],

    // Flattened river evaluation tables, indexed by dense slot.
    pub num_slots: usize,
    pub riv_off: [Vec<u32>; 2],
    pub riv_cnt: [Vec<u32>; 2],
    pub riv_sorted_idx: [Vec<u32>; 2],
    pub riv_sorted_str: [Vec<u32>; 2],
    /// Opponent sorted-list boundaries for each entry in riv_sorted_idx[p]:
    /// first strength >= ours, and first strength > ours. Board-dependent,
    /// so compute once rather than binary-searching at every terminal visit.
    pub riv_lower: [Vec<u32>; 2],
    pub riv_upper: [Vec<u32>; 2],
    /// 53 entries per slot: span of card c is [slot*53+c, slot*53+c+1).
    pub riv_card_off: [Vec<u32>; 2],
    /// Positions (into the slot's sorted order) of hands containing the card.
    pub riv_card_pos: [Vec<u32>; 2],
    /// Max sorted-list length across slots, per player (shared-mem sizing).
    pub riv_max_cnt: [usize; 2],
}

impl GpuPlan {
    /// The upstream layout: one resident cfv slot per terminal.
    pub fn build(spot: &Spot, use_iso: bool) -> GpuPlan {
        GpuPlan::build_with(spot, use_iso, &PlanOptions::default())
    }

    pub fn build_with(spot: &Spot, use_iso: bool, opts: &PlanOptions) -> GpuPlan {
        let n = spot.tree.nodes.len();
        let nh = [spot.hands[0].len(), spot.hands[1].len()];
        let iso_active = use_iso && spot.suit_perms.len() > 1;

        // --- DFS over representative branches: levels, river keys, owners,
        // --- chance card tables ---------------------------------------------
        let mut level = vec![0u32; n];
        let mut reached = vec![false; n];
        let mut river_key = vec![usize::MAX; n];
        let mut reach_src = [vec![0u32; n], vec![0u32; n]];
        let mut cc_start = vec![0u32; n];
        let mut cc_count = vec![0u32; n];
        let mut cc_card: Vec<u32> = Vec::new();
        let mut cc_child: Vec<u32> = Vec::new();
        let mut cc_perm: Vec<u32> = Vec::new();
        let mut rep_edges: Vec<(u32, u32, u32)> = Vec::new(); // parent, child, card
        let mut max_level = 0u32;

        struct Item {
            node: u32,
            level: u32,
            dealt: Dealt,
            src: [u32; 2],
        }
        let mut stack = vec![Item {
            node: 0,
            level: 0,
            dealt: Dealt::default(),
            src: [0, 0],
        }];
        while let Some(it) = stack.pop() {
            let ni = it.node as usize;
            reached[ni] = true;
            level[ni] = it.level;
            reach_src[0][ni] = it.src[0];
            reach_src[1][ni] = it.src[1];
            max_level = max_level.max(it.level);
            let node = &spot.tree.nodes[ni];
            match node.kind {
                KIND_ACTION => {
                    let actor = node.player as usize;
                    for a in 0..node.num_children as usize {
                        let child = spot.tree.children[node.children_start as usize + a];
                        let mut src = it.src;
                        src[actor] = child; // actor's reach is rewritten on this edge
                        stack.push(Item {
                            node: child,
                            level: it.level + 1,
                            dealt: it.dealt,
                            src,
                        });
                    }
                }
                KIND_CHANCE => {
                    let valid_perms: Vec<usize> = if iso_active {
                        spot.perms_fixing(&it.dealt)
                    } else {
                        vec![0]
                    };
                    cc_start[ni] = cc_card.len() as u32;
                    for c in 0..52u8 {
                        let child =
                            spot.tree.children[node.children_start as usize + c as usize];
                        if child == SENTINEL || it.dealt.contains(c) {
                            continue;
                        }
                        let mut rep = c;
                        let mut k_rep = 0usize;
                        for &k in &valid_perms {
                            let pc = crate::cards::permute_card(c, &spot.suit_perms[k]);
                            if pc < rep {
                                rep = pc;
                                k_rep = k;
                            }
                        }
                        let rep_child =
                            spot.tree.children[node.children_start as usize + rep as usize];
                        cc_card.push(c as u32);
                        cc_child.push(rep_child);
                        cc_perm.push(k_rep as u32);
                        if c == rep {
                            rep_edges.push((it.node, child, c as u32));
                            stack.push(Item {
                                node: child,
                                level: it.level + 1,
                                dealt: it.dealt.push(c),
                                src: [child, child], // chance edges rewrite both
                            });
                        }
                    }
                    cc_count[ni] = cc_card.len() as u32 - cc_start[ni];
                }
                KIND_TERM_SHOWDOWN => {
                    river_key[ni] = spot.river.key(&it.dealt);
                }
                _ => {}
            }
        }

        // Terminal CFVs stay resident for repeated BR/average evaluations
        // (unless `terminal_scratch`: then they are scratch like the rest).
        // Action/chance CFVs live only from their up-sweep level until the
        // immediately preceding level consumes them. Reuse those scratch
        // slots between even levels and between odd levels, with root at 0.
        let in_scratch = |kind: u8| {
            kind == KIND_ACTION || kind == KIND_CHANCE
                || (opts.terminal_scratch && (kind == KIND_TERM_FOLD || kind == KIND_TERM_SHOWDOWN))
        };
        let mut widths = vec![0usize; max_level as usize + 1];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            if reached[ni] && in_scratch(node.kind) {
                widths[level[ni] as usize] += 1;
            }
        }
        let mut parity_max = [0usize; 2];
        for (l, &width) in widths.iter().enumerate() {
            parity_max[l % 2] = parity_max[l % 2].max(width);
        }
        let base = [0usize, parity_max[0]];
        let mut used = vec![0usize; widths.len()];
        let mut cfv_slot = vec![u32::MAX; n];
        let mut cfv_blocks = parity_max[0] + parity_max[1];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            if !reached[ni] { continue; }
            if in_scratch(node.kind) {
                let l = level[ni] as usize;
                cfv_slot[ni] = (base[l % 2] + used[l]) as u32;
                used[l] += 1;
            } else {
                cfv_slot[ni] = cfv_blocks as u32;
                cfv_blocks += 1;
            }
        }

        // --- Level-ordered work lists (representative branches only) --------
        let num_levels = max_level as usize + 1;
        let mut action_by_level: Vec<Vec<u32>> = vec![Vec::new(); num_levels];
        let mut fold_by_level: Vec<Vec<u32>> = vec![Vec::new(); num_levels];
        let mut show_by_level: Vec<Vec<u32>> = vec![Vec::new(); num_levels];
        let mut cnode_by_level: Vec<Vec<u32>> = vec![Vec::new(); num_levels];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            if !reached[ni] {
                continue;
            }
            let l = level[ni] as usize;
            match node.kind {
                KIND_ACTION => action_by_level[l].push(ni as u32),
                KIND_TERM_FOLD => fold_by_level[l].push(ni as u32),
                KIND_TERM_SHOWDOWN => show_by_level[l].push(ni as u32),
                KIND_CHANCE => cnode_by_level[l].push(ni as u32),
                _ => unreachable!(),
            }
        }
        let flatten_nodes = |by: Vec<Vec<u32>>| -> (Vec<u32>, Vec<LevelSpan>) {
            let mut flat = Vec::new();
            let mut spans = Vec::with_capacity(num_levels);
            for lst in by {
                spans.push(LevelSpan {
                    start: flat.len() as u32,
                    count: lst.len() as u32,
                });
                flat.extend(lst);
            }
            (flat, spans)
        };
        let (action_nodes, action_spans) = flatten_nodes(action_by_level);
        let (fold_nodes, fold_spans) = flatten_nodes(fold_by_level);
        let (show_nodes, show_spans) = flatten_nodes(show_by_level);
        let (chance_nodes, chance_node_spans) = flatten_nodes(cnode_by_level);

        let mut edge_by_level: Vec<Vec<(u32, u32, u32)>> = vec![Vec::new(); num_levels];
        for (p, c, card) in rep_edges {
            edge_by_level[level[p as usize] as usize].push((p, c, card));
        }
        let mut chance_parents = Vec::new();
        let mut chance_children = Vec::new();
        let mut chance_cards = Vec::new();
        let mut chance_spans = Vec::with_capacity(num_levels);
        for lst in edge_by_level {
            chance_spans.push(LevelSpan {
                start: chance_parents.len() as u32,
                count: lst.len() as u32,
            });
            for (p, c, card) in lst {
                chance_parents.push(p);
                chance_children.push(c);
                chance_cards.push(card);
            }
        }

        // --- River slot assignment + flattened tables ----------------------
        let mut slot_of_key = std::collections::HashMap::new();
        let mut node_river_slot = vec![-1i32; n];
        let mut slots: Vec<usize> = Vec::new();
        for ni in 0..n {
            if river_key[ni] != usize::MAX {
                let next = slot_of_key.len();
                let s = *slot_of_key.entry(river_key[ni]).or_insert(next);
                if s == slots.len() {
                    slots.push(river_key[ni]);
                }
                node_river_slot[ni] = s as i32;
            }
        }
        let num_slots = slots.len();
        let mut riv_off = [Vec::new(), Vec::new()];
        let mut riv_cnt = [Vec::new(), Vec::new()];
        let mut riv_sorted_idx = [Vec::new(), Vec::new()];
        let mut riv_sorted_str = [Vec::new(), Vec::new()];
        let mut riv_lower = [Vec::new(), Vec::new()];
        let mut riv_upper = [Vec::new(), Vec::new()];
        let mut riv_card_off = [Vec::new(), Vec::new()];
        let mut riv_card_pos = [Vec::new(), Vec::new()];
        let mut riv_max_cnt = [0usize, 0usize];
        for p in 0..2 {
            for &key in &slots {
                let eval = spot.river.entries[key].as_deref().expect("river eval");
                let sorted = &eval.sorted[p];
                let opponent = &eval.sorted[1 - p];
                let (mut lower, mut upper) = (0, 0);
                riv_off[p].push(riv_sorted_idx[p].len() as u32);
                riv_cnt[p].push(sorted.len() as u32);
                riv_max_cnt[p] = riv_max_cnt[p].max(sorted.len());
                let mut by_card: Vec<Vec<u32>> = vec![Vec::new(); 52];
                for (pos, &(stren, idx)) in sorted.iter().enumerate() {
                    while lower < opponent.len() && opponent[lower].0 < stren {
                        lower += 1;
                    }
                    upper = upper.max(lower);
                    while upper < opponent.len() && opponent[upper].0 <= stren {
                        upper += 1;
                    }
                    riv_lower[p].push(lower as u32);
                    riv_upper[p].push(upper as u32);
                    riv_sorted_str[p].push(stren);
                    riv_sorted_idx[p].push(idx as u32);
                    let h = &spot.hands[p][idx as usize];
                    by_card[h.c1 as usize].push(pos as u32);
                    by_card[h.c2 as usize].push(pos as u32);
                }
                for c in 0..52 {
                    riv_card_off[p].push(riv_card_pos[p].len() as u32);
                    riv_card_pos[p].extend(&by_card[c]);
                }
                riv_card_off[p].push(riv_card_pos[p].len() as u32); // 53rd: end
            }
        }

        // --- Per-node scalar arrays -----------------------------------------
        let mut node_player = vec![0i32; n];
        let mut node_na = vec![0i32; n];
        let mut node_data_off = vec![u64::MAX; n];
        let mut arena_elements = [0usize; 2];
        let mut node_children_start = vec![0u32; n];
        let mut node_twin = vec![0f32; n];
        let mut node_tlose = vec![0f32; n];
        let mut node_ttie = vec![0f32; n];
        let mut node_cdiv = vec![0f32; n];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            node_player[ni] = node.player as i32;
            node_na[ni] = node.num_children as i32;
            if node.kind == KIND_ACTION && reached[ni] {
                let p = node.player as usize;
                node_data_off[ni] = arena_elements[p] as u64;
                arena_elements[p] += node.num_children as usize * nh[p];
            }
            node_children_start[ni] = node.children_start;
            node_twin[ni] = node.t_win as f32;
            node_tlose[ni] = node.t_lose as f32;
            node_ttie[ni] = node.t_tie as f32;
            if node.kind == KIND_CHANCE {
                node_cdiv[ni] = 1.0 / (46 - node.street as i32) as f32;
            }
        }
        // ICM: each player has its own payoffs, player 0's block first.
        let mut payoff_stride = 0;
        if let Some(icm) = &spot.icm {
            node_twin = icm.win.concat();
            node_tlose = icm.lose.concat();
            node_ttie = icm.tie.concat();
            payoff_stride = n;
        }

        // Packing adds host copy/restore work. Keep direct whole-arena DMA
        // when unreachable blocks save less than 5% of action storage.
        let full_elements = spot.tree.data_size[0] + spot.tree.data_size[1];
        let packed_elements = (arena_elements[0] + arena_elements[1]) as u64;
        if full_elements - packed_elements < full_elements / 20 {
            arena_elements = [spot.tree.data_size[0] as usize, spot.tree.data_size[1] as usize];
            for (ni, node) in spot.tree.nodes.iter().enumerate() {
                node_data_off[ni] = node.data_offset;
            }
        }

        // --- Per-hand arrays + flattened permutation tables ------------------
        let mut hand_c1 = [Vec::new(), Vec::new()];
        let mut hand_c2 = [Vec::new(), Vec::new()];
        let mut hand_mask = [Vec::new(), Vec::new()];
        let mut hand_perm_flat = [Vec::new(), Vec::new()];
        for p in 0..2 {
            for h in &spot.hands[p] {
                hand_c1[p].push(h.c1 as u32);
                hand_c2[p].push(h.c2 as u32);
                hand_mask[p].push(h.mask);
            }
            for tbl in &spot.hand_perm[p] {
                hand_perm_flat[p].extend(tbl.iter().map(|&i| i as u32));
            }
        }

        // Node IDs describe ownership; only distinct owners need storage.
        // Visiting node zero first reserves physical slot zero for root weights.
        let mut reach_slot = [Vec::with_capacity(n), Vec::with_capacity(n)];
        let mut reach_blocks = [0usize; 2];
        for p in 0..2 {
            let mut owner_slot = vec![u32::MAX; n];
            for &owner in &reach_src[p] {
                let slot = &mut owner_slot[owner as usize];
                if *slot == u32::MAX {
                    *slot = reach_blocks[p] as u32;
                    reach_blocks[p] += 1;
                }
                reach_slot[p].push(*slot);
            }
        }

        let sweeps = vec![SweepSpans {
            levels: (0..num_levels)
                .map(|l| LevelSpans {
                    action: action_spans[l],
                    edge: chance_spans[l],
                    chance: chance_node_spans[l],
                    fold: fold_spans[l],
                    show: show_spans[l],
                })
                .collect(),
            entry: LevelSpan::default(),
        }];

        GpuPlan {
            num_levels,
            nh,
            nh_max: nh[0].max(nh[1]),
            num_nodes: n,
            iso_active,
            action_nodes,
            action_spans,
            chance_parents,
            chance_children,
            chance_cards,
            chance_spans,
            chance_nodes,
            chance_node_spans,
            fold_nodes,
            fold_spans,
            show_nodes,
            show_spans,
            cc_start,
            cc_count,
            cc_card,
            cc_child,
            cc_perm,
            hand_perm_flat,
            node_player,
            node_na,
            node_data_off,
            arena_elements,
            node_children_start,
            node_twin,
            node_tlose,
            node_ttie,
            payoff_stride,
            node_cdiv,
            node_river_slot,
            reach_src,
            reach_slot,
            reach_blocks,
            cfv_slot,
            cfv_blocks,
            terminal_scratch: opts.terminal_scratch,
            children_len: spot.tree.children.len(),
            sweeps,
            groups: Vec::new(),
            hand_c1,
            hand_c2,
            hand_mask,
            same_combo: [spot.same_combo[0].clone(), spot.same_combo[1].clone()],
            weights: [spot.weights[0].clone(), spot.weights[1].clone()],
            num_slots,
            riv_off,
            riv_cnt,
            riv_sorted_idx,
            riv_sorted_str,
            riv_lower,
            riv_upper,
            riv_card_off,
            riv_card_pos,
            riv_max_cnt,
        }
    }

    /// Turn the resident plan into a grouped one (multiway `Plan::build`,
    /// heads-up form): the subtrees below the first chance layer (turn cards
    /// for a flop root, river cards for a turn root) are swept one group of
    /// cards at a time, sharing one reach and cfv scratch region. Only the
    /// root part's reaches and the group roots' cfvs stay resident; terminals
    /// always live in the per-level scratch. Arena offsets, river tables and
    /// per-node scalars do not depend on the grouping and stay as built.
    ///
    /// `groups` must partition `layout.cards` (the layout of this plan). The
    /// per-level span vectors are cleared: the kernels walk `sweeps`.
    pub fn regroup(&mut self, spot: &Spot, layout: &HuLayout, groups: &[Vec<u8>]) -> Result<(), String> {
        if !self.groups.is_empty() || self.sweeps.len() != 1 {
            return Err("regroup needs a resident plan".into());
        }
        let mut group_of = [usize::MAX; 52];
        for (g, cards) in groups.iter().enumerate() {
            if cards.is_empty() {
                return Err("empty card group".into());
            }
            for &c in cards {
                if c >= 52 || group_of[c as usize] != usize::MAX {
                    return Err(format!("card {c} is in two groups or out of range"));
                }
                group_of[c as usize] = g;
            }
        }
        let mut grouped: Vec<u8> = groups.iter().flatten().copied().collect();
        grouped.sort_unstable();
        if grouped != layout.cards {
            return Err(format!("groups {groups:?} do not partition the first-layer cards {:?}", layout.cards));
        }
        let n = self.num_nodes;
        let reached = |ni: usize| layout.level[ni] != u32::MAX;
        let sweep_of = |ni: usize| -> usize {
            match layout.seg[ni] {
                0 => 0,
                s => 1 + group_of[s as usize - 1],
            }
        };
        let num_sweeps = 1 + groups.len();
        let mut num_levels = vec![0usize; num_sweeps];
        for ni in 0..n {
            if reached(ni) {
                let s = sweep_of(ni);
                num_levels[s] = num_levels[s].max(layout.level[ni] as usize + 1);
            }
        }

        // cfv: per (sweep, level) scratch alternating between the two parity
        // halves (sized by the widest level of either parity over all sweeps:
        // sweeps run one after another), group roots resident after them.
        let is_root = |ni: usize| layout.seg[ni] != 0 && layout.level[ni] == 0;
        let mut width: Vec<Vec<usize>> = num_levels.iter().map(|&l| vec![0; l]).collect();
        for ni in 0..n {
            if reached(ni) && !is_root(ni) {
                width[sweep_of(ni)][layout.level[ni] as usize] += 1;
            }
        }
        let mut parity_max = [0usize; 2];
        for w in &width {
            for (l, &x) in w.iter().enumerate() {
                parity_max[l % 2] = parity_max[l % 2].max(x);
            }
        }
        let base = [0usize, parity_max[0]];
        let mut used: Vec<Vec<usize>> = num_levels.iter().map(|&l| vec![0; l]).collect();
        let mut cfv_slot = vec![u32::MAX; n];
        let mut roots = 0usize;
        for ni in 0..n {
            if !reached(ni) {
                continue;
            }
            if is_root(ni) {
                cfv_slot[ni] = (parity_max[0] + parity_max[1] + roots) as u32;
                roots += 1;
            } else {
                let (s, l) = (sweep_of(ni), layout.level[ni] as usize);
                cfv_slot[ni] = (base[l % 2] + used[s][l]) as u32;
                used[s][l] += 1;
            }
        }
        debug_assert_eq!(roots, layout.num_roots);

        // reach: the root part's owners count from 0 (node 0 first: slot 0
        // holds the root weights); every group's from the root part's total,
        // so all groups share one region. Owners of a group's nodes lie in
        // that group (its entry edges rewrite both players' reach).
        let mut reach_slot = [vec![0u32; n], vec![0u32; n]];
        let mut reach_blocks = [0usize; 2];
        for p in 0..2 {
            let mut next = vec![layout.root_owners[p]; num_sweeps];
            next[0] = 0;
            let mut owner_slot = vec![u32::MAX; n];
            for ni in 0..n {
                if reached(ni) && self.reach_src[p][ni] as usize == ni {
                    let s = sweep_of(ni);
                    owner_slot[ni] = next[s] as u32;
                    next[s] += 1;
                }
            }
            for ni in 0..n {
                let slot = owner_slot[self.reach_src[p][ni] as usize];
                debug_assert!(slot != u32::MAX);
                reach_slot[p][ni] = slot;
            }
            reach_blocks[p] = next.into_iter().max().unwrap_or(0);
        }

        // Work lists, sweep by sweep, level by level (node order within).
        let mut by: Vec<Vec<[Vec<u32>; 4]>> =
            num_levels.iter().map(|&l| (0..l).map(|_| Default::default()).collect()).collect();
        for ni in 0..n {
            if !reached(ni) {
                continue;
            }
            let k = match spot.tree.nodes[ni].kind {
                KIND_ACTION => 0,
                KIND_CHANCE => 1,
                KIND_TERM_FOLD => 2,
                KIND_TERM_SHOWDOWN => 3,
                _ => return Err("unknown node kind".into()),
            };
            by[sweep_of(ni)][layout.level[ni] as usize][k].push(ni as u32);
        }
        let mut edges: Vec<Vec<Vec<(u32, u32, u32)>>> = num_levels.iter().map(|&l| vec![Vec::new(); l]).collect();
        let mut entry: Vec<Vec<(u32, u32, u32)>> = vec![Vec::new(); num_sweeps];
        for i in 0..self.chance_parents.len() {
            let (par, child, card) = (self.chance_parents[i], self.chance_children[i], self.chance_cards[i]);
            let e = (par, child, card);
            if layout.seg[par as usize] == 0 {
                entry[sweep_of(child as usize)].push(e);
            } else {
                edges[sweep_of(par as usize)][layout.level[par as usize] as usize].push(e);
            }
        }
        let mut lists: [Vec<u32>; 4] = Default::default();
        let (mut cp, mut cc, mut ck) = (Vec::new(), Vec::new(), Vec::new());
        let mut push_edges = |list: &[(u32, u32, u32)]| {
            let span = LevelSpan { start: cp.len() as u32, count: list.len() as u32 };
            for &(a, b, c) in list {
                cp.push(a);
                cc.push(b);
                ck.push(c);
            }
            span
        };
        let span_of = |out: &mut Vec<u32>, v: &[u32]| {
            let span = LevelSpan { start: out.len() as u32, count: v.len() as u32 };
            out.extend_from_slice(v);
            span
        };
        let mut sweeps = Vec::with_capacity(num_sweeps);
        for s in 0..num_sweeps {
            let mut sw = SweepSpans { entry: push_edges(&entry[s]), levels: Vec::with_capacity(num_levels[s]) };
            for l in 0..num_levels[s] {
                let [a, c, f, sh] = &by[s][l];
                sw.levels.push(LevelSpans {
                    action: span_of(&mut lists[0], a),
                    chance: span_of(&mut lists[1], c),
                    fold: span_of(&mut lists[2], f),
                    show: span_of(&mut lists[3], sh),
                    edge: push_edges(&edges[s][l]),
                });
            }
            sweeps.push(sw);
        }
        let [action_nodes, chance_nodes, fold_nodes, show_nodes] = lists;
        debug_assert_eq!(action_nodes.len(), self.action_nodes.len());
        debug_assert_eq!(cp.len(), self.chance_parents.len());

        self.action_nodes = action_nodes;
        self.chance_nodes = chance_nodes;
        self.fold_nodes = fold_nodes;
        self.show_nodes = show_nodes;
        self.chance_parents = cp;
        self.chance_children = cc;
        self.chance_cards = ck;
        for v in [&mut self.action_spans, &mut self.chance_spans, &mut self.chance_node_spans,
                  &mut self.fold_spans, &mut self.show_spans] {
            v.clear();
        }
        self.num_levels = num_levels.iter().copied().max().unwrap_or(0);
        self.cfv_slot = cfv_slot;
        self.cfv_blocks = parity_max[0] + parity_max[1] + roots;
        self.reach_slot = reach_slot;
        self.reach_blocks = reach_blocks;
        self.terminal_scratch = true;
        self.sweeps = sweeps;
        self.groups = groups.to_vec();
        Ok(())
    }

    /// `build_with` + `regroup` with the plan's own layout.
    pub fn build_grouped(spot: &Spot, use_iso: bool, opts: &PlanOptions, groups: &[Vec<u8>]) -> Result<GpuPlan, String> {
        let mut plan = GpuPlan::build_with(spot, use_iso, opts);
        let layout = HuLayout::from_plan(spot, &plan);
        plan.regroup(spot, &layout, groups)?;
        Ok(plan)
    }

    /// Direct whole-arena transfers avoid host snapshots when VRAM is ample.
    pub(crate) fn use_full_action_arenas(&mut self, spot: &Spot) {
        self.arena_elements = [spot.tree.data_size[0] as usize, spot.tree.data_size[1] as usize];
        for (i, node) in spot.tree.nodes.iter().enumerate() {
            self.node_data_off[i] = node.data_offset;
        }
    }

    /// Total bytes of GPU staging (reach + cfv) this plan needs.
    pub fn staging_bytes(&self) -> u64 {
        (self.reach_blocks[0] as u64 * self.nh[0] as u64
            + self.reach_blocks[1] as u64 * self.nh[1] as u64
            + self.cfv_blocks as u64 * self.nh_max as u64) * 4
    }

    /// Device bytes of the read-only tables `GpuSolver` uploads for this plan
    /// (everything except arenas, reach and cfv), without locks and fits:
    /// per-node arrays (76 B/node, payoffs ×2 under ICM), work lists, child
    /// slots, chance card tables, hand tables, river tables, scalars.
    pub fn table_bytes(&self) -> u64 {
        let n = self.num_nodes as u64;
        let w = |len: usize| len as u64 * 4;
        // player, na, data offset (8), children start, cdiv, river slot,
        // cc span (2), reach slot (2), cfv slot, lock offsets (2 × 8)
        let per_node = n * (4 + 4 + 8 + 4 + 4 + 4 + 8 + 8 + 4 + 16)
            + w(self.node_twin.len() + self.node_tlose.len() + self.node_ttie.len());
        let lists = w(self.action_nodes.len() + self.chance_parents.len() + self.chance_children.len()
            + self.chance_cards.len() + self.chance_nodes.len() + self.fold_nodes.len()
            + self.show_nodes.len() + self.children_len
            + self.cc_card.len() + self.cc_child.len() + self.cc_perm.len()
            + self.hand_perm_flat[0].len() + self.hand_perm_flat[1].len());
        let mut hands = 0;
        let mut river = 0;
        for p in 0..2 {
            // c1, c2, mask (8), same combo, weight; fold index: 53 offsets + 2 per hand
            hands += self.nh[p] as u64 * 24 + w(53 + 2 * self.nh[p]);
            river += w(self.riv_off[p].len() + self.riv_cnt[p].len() + self.riv_sorted_idx[p].len()
                + self.riv_lower[p].len() + self.riv_upper[p].len()
                + self.riv_card_off[p].len() + self.riv_card_pos[p].len());
        }
        // lock sigma placeholder, fit stride + 2 index words, discounts, eval roots
        let scalars = w(1 + 48 + 2 + 3 + 4 * self.nh_max);
        per_node + lists + hands + river + scalars
    }
}

/// Segments of a resident plan's reached nodes for first-layer grouping
/// (multiway `Layout`, heads-up form): the root part (segment 0) and the
/// subtrees below each first-layer card c (segment 1 + c): turn cards under
/// a flop root, river cards under a turn root. With suit isomorphism only
/// representative cards have subtrees (the others are synthesized from them
/// at the first-layer chance nodes, which belong to the root part).
pub struct HuLayout {
    /// 0 = root part, 1 + c = below first-layer card c.
    pub seg: Vec<u8>,
    /// Level within the node's segment (group roots, the children of the
    /// first chance layer, are level 0); u32::MAX for unreached nodes.
    pub level: Vec<u32>,
    /// First-layer cards with subtrees, ascending.
    pub cards: Vec<u8>,
    /// Reach owners (= reach slots) of the root part, per player.
    pub root_owners: [usize; 2],
    /// Scratch cfv width of each root-part level.
    pub root_width: Vec<usize>,
    /// Per card 0..52: reach owners per player, and the scratch cfv width of
    /// each level of its subtrees (level 0, the group roots, is resident).
    pub card_owners: Vec<[usize; 2]>,
    pub card_width: Vec<Vec<usize>>,
    /// Group roots: one resident cfv slot each.
    pub num_roots: usize,
    pub nh: [usize; 2],
}

fn parity_max(widths: &[usize]) -> [usize; 2] {
    let mut m = [0usize; 2];
    for (l, &w) in widths.iter().enumerate() {
        m[l % 2] = m[l % 2].max(w);
    }
    m
}

impl HuLayout {
    /// Layout of a resident plan (`build` / `build_with`) of `spot`.
    pub fn from_plan(spot: &Spot, plan: &GpuPlan) -> HuLayout {
        let tree = &spot.tree;
        let n = plan.num_nodes;
        let mut seg = vec![0u8; n];
        let mut level = vec![u32::MAX; n];
        let mut card_owners = vec![[0usize; 2]; 52];
        let mut card_width: Vec<Vec<usize>> = vec![Vec::new(); 52];
        let mut root_width: Vec<usize> = Vec::new();
        let mut root_owners = [0usize; 2];
        let mut num_roots = 0usize;
        // reached = has a cfv slot (resident plans give every reached node one)
        let reached = |ni: usize| plan.cfv_slot[ni] != u32::MAX;
        level[0] = 0;
        let mut stack = vec![0u32];
        while let Some(ni) = stack.pop() {
            let ni = ni as usize;
            let node = &tree.nodes[ni];
            let (s, l) = (seg[ni], level[ni]);
            let mut visit = |child: u32, first_layer_card: Option<u8>| {
                let c = child as usize;
                match first_layer_card {
                    Some(card) => {
                        seg[c] = 1 + card;
                        level[c] = 0;
                    }
                    None => {
                        seg[c] = s;
                        level[c] = l + 1;
                    }
                }
                stack.push(child);
            };
            match node.kind {
                KIND_ACTION => {
                    for a in 0..node.num_children as usize {
                        visit(tree.children[node.children_start as usize + a], None);
                    }
                }
                KIND_CHANCE => {
                    for card in 0..52u8 {
                        let child = tree.children[node.children_start as usize + card as usize];
                        if child == SENTINEL || !reached(child as usize) {
                            continue; // dealt, or a non-representative card
                        }
                        visit(child, (s == 0).then_some(card));
                    }
                }
                _ => {}
            }
        }
        for ni in 0..n {
            if level[ni] == u32::MAX {
                continue;
            }
            let (s, l) = (seg[ni] as usize, level[ni] as usize);
            if s == 0 {
                if root_width.len() <= l {
                    root_width.resize(l + 1, 0);
                }
                root_width[l] += 1;
            } else if l == 0 {
                num_roots += 1;
            } else {
                let w = &mut card_width[s - 1];
                if w.len() <= l {
                    w.resize(l + 1, 0);
                }
                w[l] += 1;
            }
            for p in 0..2 {
                if plan.reach_src[p][ni] as usize == ni {
                    if s == 0 {
                        root_owners[p] += 1;
                    } else {
                        card_owners[s - 1][p] += 1;
                    }
                }
            }
        }
        let cards = (0..52u8).filter(|&c| card_owners[c as usize] != [0, 0]).collect();
        HuLayout { seg, level, cards, root_owners, root_width, card_owners, card_width, num_roots, nh: plan.nh }
    }

    /// Reach slots per player and cfv slots of the plan `regroup` builds
    /// for `groups`.
    pub fn grouped_blocks(&self, groups: &[Vec<u8>]) -> ([usize; 2], usize) {
        let mut reach = [0usize; 2];
        let mut pm = parity_max(&self.root_width);
        for g in groups {
            let mut own = [0usize; 2];
            let mut w: Vec<usize> = Vec::new();
            for &c in g {
                let c = c as usize;
                for p in 0..2 {
                    own[p] += self.card_owners[c][p];
                }
                let cw = &self.card_width[c];
                if w.len() < cw.len() {
                    w.resize(cw.len(), 0);
                }
                for (l, &x) in cw.iter().enumerate() {
                    w[l] += x;
                }
            }
            let gm = parity_max(&w);
            for k in 0..2 {
                reach[k] = reach[k].max(own[k]);
                pm[k] = pm[k].max(gm[k]);
            }
        }
        ([self.root_owners[0] + reach[0], self.root_owners[1] + reach[1]], pm[0] + pm[1] + self.num_roots)
    }

    /// Device bytes of reach and cfv under `groups` (f32).
    pub fn grouped_staging(&self, groups: &[Vec<u8>]) -> (u64, u64) {
        let (r, c) = self.grouped_blocks(groups);
        let nh_max = self.nh[0].max(self.nh[1]) as u64;
        ((r[0] * self.nh[0] + r[1] * self.nh[1]) as u64 * 4, c as u64 * nh_max * 4)
    }

    /// Groups of at most `k` cards, in card order.
    pub fn chunks(&self, k: usize) -> Vec<Vec<u8>> {
        self.cards.chunks(k.max(1)).map(|c| c.to_vec()).collect()
    }

    /// Fewest groups the greedy pass (cards in order, a new group whenever
    /// the next card would overflow) finds whose reach + cfv fit `scratch`
    /// bytes; None when not even single cards do (multiway `group_cards`).
    pub fn group_cards(&self, scratch: u64) -> Option<Vec<Vec<u8>>> {
        let fits = |g: &[Vec<u8>]| {
            let (r, c) = self.grouped_staging(g);
            r + c <= scratch
        };
        let mut groups: Vec<Vec<u8>> = Vec::new();
        let mut cur: Vec<u8> = Vec::new();
        for &c in &self.cards {
            let mut next = cur.clone();
            next.push(c);
            let mut cand = groups.clone();
            cand.push(next.clone());
            if fits(&cand) {
                cur = next;
                continue;
            }
            if cur.is_empty() {
                return None;
            }
            groups.push(std::mem::take(&mut cur));
            let mut cand = groups.clone();
            cand.push(vec![c]);
            if !fits(&cand) {
                return None;
            }
            cur = vec![c];
        }
        if !cur.is_empty() {
            groups.push(cur);
        }
        Some(groups)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{parse_sizes, SpotConfig, StreetSizing, TreeConfig};

    fn group_spot(board: &str, stack: f64) -> Spot {
        let sizing = || StreetSizing {
            bet: parse_sizes("50").unwrap(), raise: parse_sizes("2.5x").unwrap(), donk: vec![],
        };
        Spot::new(SpotConfig {
            board: board.into(),
            range_oop: "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
            range_ip: "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
            tree: TreeConfig {
                starting_pot: 10.0, effective_stack: stack,
                oop: [sizing(), sizing(), sizing()],
                ip: [sizing(), sizing(), sizing()],
                ..Default::default()
            },
        }).unwrap()
    }

    /// Turn-grouped plans (no device): slot invariants of every sweep, the
    /// layout's byte account equals the plan's, and everything except the
    /// reach/cfv slots and work-list order matches the resident plan.
    #[test]
    fn plan_groups_hu_slots() {
        // flop with flop all-in runouts (stack 40), a deeper flop, a turn root
        for (board, stack) in [("KsQs2d", 40.0), ("Td9d6h", 90.0), ("Qs7h2dKh", 40.0)] {
            let spot = group_spot(board, stack);
            for iso in [false, true] {
                let resident = GpuPlan::build_with(&spot, iso, &PlanOptions { terminal_scratch: true });
                let layout = HuLayout::from_plan(&spot, &resident);
                assert!(!layout.cards.is_empty());
                if !iso {
                    assert_eq!(layout.cards.len(), 52 - spot.board.len());
                }
                for p in 0..2 {
                    let owners: usize = layout.root_owners[p] + layout.card_owners.iter().map(|o| o[p]).sum::<usize>();
                    assert_eq!(owners, resident.reach_blocks[p], "{board} iso={iso}: owners partition");
                }
                let all = layout.chunks(52);
                for groups in [layout.chunks(1), layout.chunks(3), all.clone()] {
                    let label = format!("{board} iso={iso} {} groups", groups.len());
                    let plan = GpuPlan::build_grouped(&spot, iso, &PlanOptions { terminal_scratch: true }, &groups).unwrap();
                    assert_eq!(plan.groups, groups);
                    assert_eq!(plan.sweeps.len(), 1 + groups.len(), "{label}");
                    assert!(plan.terminal_scratch);
                    assert_eq!(layout.grouped_blocks(&groups), (plan.reach_blocks, plan.cfv_blocks), "{label}");
                    let (r, c) = layout.grouped_staging(&groups);
                    assert_eq!(r + c, plan.staging_bytes(), "{label}");
                    assert_eq!(plan.arena_elements, resident.arena_elements);
                    assert_eq!(plan.node_data_off, resident.node_data_off);
                    assert_eq!(plan.table_bytes(), resident.table_bytes());
                    assert!(plan.reach_blocks[0] <= resident.reach_blocks[0] && plan.reach_blocks[1] <= resident.reach_blocks[1]);
                    assert_eq!(plan.cfv_slot[0], 0);
                    for p in 0..2 {
                        assert_eq!(plan.reach_slot[p][0], 0);
                    }
                    let sweep_of = |n: usize| match layout.seg[n] {
                        0 => 0,
                        sg => 1 + groups.iter().position(|g| g.contains(&(sg - 1))).unwrap(),
                    };
                    let scratch_end = plan.cfv_blocks - layout.num_roots;
                    // every reached node is listed once, in its sweep at its level
                    let mut seen = vec![false; plan.num_nodes];
                    let mut roots = std::collections::HashSet::new();
                    for (s, sw) in plan.sweeps.iter().enumerate() {
                        let mut prev: std::collections::HashSet<usize> = Default::default();
                        for (l, ls) in sw.levels.iter().enumerate() {
                            let mut live = std::collections::HashSet::new();
                            for (nodes, sp) in [(&plan.action_nodes, ls.action), (&plan.chance_nodes, ls.chance),
                                                (&plan.fold_nodes, ls.fold), (&plan.show_nodes, ls.show)] {
                                for &n in &nodes[sp.start as usize..(sp.start + sp.count) as usize] {
                                    let n = n as usize;
                                    assert!(!std::mem::replace(&mut seen[n], true), "{label}: node {n} listed twice");
                                    assert_eq!((sweep_of(n), layout.level[n] as usize), (s, l), "{label}: node {n}");
                                    let slot = plan.cfv_slot[n] as usize;
                                    if s > 0 && l == 0 {
                                        assert!(slot >= scratch_end && slot < plan.cfv_blocks, "{label}: group root resident");
                                        assert!(roots.insert(slot), "{label}: group roots distinct");
                                    } else {
                                        assert!(slot < scratch_end, "{label}: scratch below the resident roots");
                                        assert!(live.insert(slot), "{label}: same-level outputs cannot alias");
                                    }
                                }
                            }
                            assert!(live.is_disjoint(&prev), "{label}: a parent cannot overwrite child input storage");
                            prev = live;
                            for (&par, &child) in plan.chance_parents[ls.edge.start as usize..(ls.edge.start + ls.edge.count) as usize]
                                .iter().zip(&plan.chance_children[ls.edge.start as usize..(ls.edge.start + ls.edge.count) as usize])
                            {
                                assert_eq!((sweep_of(par as usize), layout.level[par as usize] as usize), (s, l), "{label}: edge level");
                                assert_eq!(sweep_of(child as usize), s);
                            }
                        }
                        let e = sw.entry;
                        assert_eq!(e.count == 0, s == 0, "{label}: groups and only groups are entered");
                        for i in e.start as usize..(e.start + e.count) as usize {
                            let (par, child) = (plan.chance_parents[i] as usize, plan.chance_children[i] as usize);
                            assert_eq!(sweep_of(par), 0);
                            assert_eq!((sweep_of(child), layout.level[child]), (s, 0), "{label}: entry child is a group root");
                        }
                    }
                    assert_eq!(roots.len(), layout.num_roots);
                    for n in 0..plan.num_nodes {
                        assert_eq!(seen[n], resident.cfv_slot[n] != u32::MAX, "{label}: node {n} reached");
                    }
                    for &child in &plan.cc_child {
                        assert_ne!(plan.cfv_slot[child as usize], u32::MAX);
                    }
                    // reach: owners inside the node's sweep; one owner per slot and sweep
                    for p in 0..2 {
                        let mut owner_of: std::collections::HashMap<(usize, u32), u32> = Default::default();
                        for n in 0..plan.num_nodes {
                            if !seen[n] {
                                continue;
                            }
                            let owner = plan.reach_src[p][n];
                            assert_eq!(sweep_of(owner as usize), sweep_of(n), "{label}: owner in the node's sweep");
                            let slot = plan.reach_slot[p][n];
                            assert!((slot as usize) < plan.reach_blocks[p]);
                            assert_eq!(slot, plan.reach_slot[p][owner as usize]);
                            let prev = owner_of.insert((sweep_of(n), slot), owner);
                            assert!(prev.is_none_or(|o| o == owner), "{label}: slot {slot} has two owners");
                            if sweep_of(n) > 0 {
                                assert!(slot as usize >= layout.root_owners[p], "{label}: groups above the root part");
                            }
                        }
                    }
                }
                // a partition is required
                let mut bad = layout.chunks(1);
                bad.pop();
                assert!(GpuPlan::build_grouped(&spot, iso, &PlanOptions { terminal_scratch: true }, &bad).is_err());
                // the greedy grouping honours its budget and is never worse than single cards
                let single = { let (r, c) = layout.grouped_staging(&layout.chunks(1)); r + c };
                let whole = { let (r, c) = layout.grouped_staging(&all); r + c };
                assert!(layout.group_cards(single - 1).is_none_or(|g| { let (r, c) = layout.grouped_staging(&g); r + c < single }));
                assert_eq!(layout.group_cards(whole).map(|g| g.len()), Some(1));
                let mid = (single + whole) / 2;
                if let Some(g) = layout.group_cards(mid) {
                    let (r, c) = layout.grouped_staging(&g);
                    assert!(r + c <= mid);
                    let mut cards: Vec<u8> = g.concat();
                    cards.sort_unstable();
                    assert_eq!(cards, layout.cards);
                }
            }
        }
    }

    #[test]
    fn river_bounds_match_strength_comparisons() {
        for board in ["KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"] {
            let sizing = || StreetSizing {
                bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![],
            };
            let spot = Spot::new(SpotConfig {
                board: board.into(),
                range_oop: "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),
                range_ip: "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
                tree: TreeConfig {
                    starting_pot: 10.0, effective_stack: 20.0,
                    oop: [sizing(), sizing(), sizing()],
                    ip: [sizing(), sizing(), sizing()],
                    ..Default::default()
                },
            }).unwrap();
            for (iso, terminal_scratch) in [(false, false), (true, false), (false, true), (true, true)] {
                let plan = GpuPlan::build_with(&spot, iso, &PlanOptions { terminal_scratch });
                assert_eq!(plan.terminal_scratch, terminal_scratch);
                assert_eq!(plan.cfv_slot[0], 0);
                let mut used = vec![false; plan.cfv_blocks];
                let mut terminals = std::collections::HashSet::new();
                if !terminal_scratch {
                    for &node in plan.fold_nodes.iter().chain(&plan.show_nodes) {
                        let slot = plan.cfv_slot[node as usize] as usize;
                        assert!(terminals.insert(slot), "terminal caches must remain distinct");
                        used[slot] = true;
                    }
                }
                let mut live = vec![std::collections::HashSet::new(); plan.num_levels];
                for l in 0..plan.num_levels {
                    let mut lists = vec![(&plan.action_nodes, &plan.action_spans),
                        (&plan.chance_nodes, &plan.chance_node_spans)];
                    if terminal_scratch {
                        // terminals are scratch outputs of their level like everything else
                        lists.push((&plan.fold_nodes, &plan.fold_spans));
                        lists.push((&plan.show_nodes, &plan.show_spans));
                    }
                    for (nodes, spans) in lists {
                        let span = spans[l];
                        for &node in &nodes[span.start as usize..(span.start + span.count) as usize] {
                            let slot = plan.cfv_slot[node as usize] as usize;
                            assert!(live[l].insert(slot), "same-level outputs cannot alias");
                            assert!(!terminals.contains(&slot), "scratch cannot overwrite cached terminals");
                            used[slot] = true;
                        }
                    }
                    if l > 0 {
                        assert!(live[l].is_disjoint(&live[l - 1]), "a parent cannot overwrite child input storage");
                    }
                }
                let resident = GpuPlan::build(&spot, iso);
                if terminal_scratch {
                    assert!(plan.cfv_blocks <= resident.cfv_blocks);
                    // only the cfv layout differs
                    assert_eq!(plan.reach_blocks, resident.reach_blocks);
                    assert_eq!(plan.arena_elements, resident.arena_elements);
                    assert_eq!(plan.table_bytes(), resident.table_bytes());
                }
                assert!(used.iter().all(|&used| used));
                for &child in &plan.cc_child {
                    assert_ne!(plan.cfv_slot[child as usize], u32::MAX);
                }
                for p in 0..2 {
                    assert_eq!(plan.reach_slot[p][0], 0);
                    let mut owner_for_slot = vec![u32::MAX; plan.reach_blocks[p]];
                    let mut slot_for_owner = vec![u32::MAX; plan.num_nodes];
                    for (&owner, &slot) in plan.reach_src[p].iter().zip(&plan.reach_slot[p]) {
                        let previous = &mut owner_for_slot[slot as usize];
                        assert!(*previous == u32::MAX || *previous == owner);
                        *previous = owner;
                        let previous = &mut slot_for_owner[owner as usize];
                        assert!(*previous == u32::MAX || *previous == slot);
                        *previous = slot;
                    }
                    assert!(owner_for_slot.iter().all(|&owner| owner != u32::MAX));
                    for slot in 0..plan.num_slots {
                        let start = plan.riv_off[p][slot] as usize;
                        let end = start + plan.riv_cnt[p][slot] as usize;
                        let ob = plan.riv_off[1 - p][slot] as usize;
                        let oe = ob + plan.riv_cnt[1 - p][slot] as usize;
                        let opponents = &plan.riv_sorted_str[1 - p][ob..oe];
                        for i in start..end {
                            let strength = plan.riv_sorted_str[p][i];
                            let lower = plan.riv_lower[p][i] as usize;
                            let upper = plan.riv_upper[p][i] as usize;
                            assert_eq!(lower, opponents.iter().filter(|&&s| s < strength).count());
                            assert_eq!(upper, opponents.iter().filter(|&&s| s <= strength).count());
                            for (pos, &other) in opponents.iter().enumerate() {
                                assert_eq!(pos < lower, other < strength);
                                assert_eq!(pos >= upper, other > strength);
                            }
                        }
                    }
                }
            }
        }
    }
}
