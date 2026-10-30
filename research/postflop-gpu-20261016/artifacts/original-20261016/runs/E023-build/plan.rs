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

#[derive(Clone, Copy, Default)]
pub struct LevelSpan {
    pub start: u32,
    pub count: u32,
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
    /// Optional stable actor-partitioned training list; aggregate traversal stays unchanged.
    /// None means every original level is uniform and both actor spans use action_nodes.
    pub up_action_nodes: Option<Vec<u32>>,
    pub up_action_spans: [Vec<LevelSpan>; 2],
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
    /// Chance nodes: 1 / (46 - street).
    pub node_cdiv: Vec<f32>,
    /// Showdown nodes: dense river slot; -1 elsewhere.
    pub node_river_slot: Vec<i32>,
    /// reach_src[p][n] = node whose reach buffer holds n's reach for player p.
    pub reach_src: [Vec<u32>; 2],
    /// Dense physical reach slots, sharing storage exactly when owners match.
    pub reach_slot: [Vec<u32>; 2],
    pub reach_blocks: [usize; 2],
    /// CFV slots: persistent terminals plus alternating-level action/chance scratch.
    /// Unvisited nodes have no allocation.
    pub cfv_slot: Vec<u32>,
    pub cfv_blocks: usize,

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

// Every span uses one coordinate system: the optional list for mixed plans,
// otherwise the original aggregate list. No node or child order within an actor changes.
fn partition_up_actions(
    nodes: &[u32], spans: &[LevelSpan], player: &[i32],
) -> (Option<Vec<u32>>, [Vec<LevelSpan>; 2]) {
    let mixed = spans.iter().any(|sp| {
        let level = &nodes[sp.start as usize..(sp.start + sp.count) as usize];
        level.first().is_some_and(|&first| level.iter().any(|&n| player[n as usize] != player[first as usize]))
    });
    let mut partitioned = mixed.then(|| Vec::with_capacity(nodes.len()));
    let mut by_actor = [Vec::with_capacity(spans.len()), Vec::with_capacity(spans.len())];
    for sp in spans {
        let level = &nodes[sp.start as usize..(sp.start + sp.count) as usize];
        for p in 0..2 {
            let actor_span = if let Some(ids) = partitioned.as_mut() {
                let start = u32::try_from(ids.len()).expect("training action IDs exceed u32");
                ids.extend(level.iter().copied().filter(|&n| player[n as usize] == p as i32));
                LevelSpan { start, count: u32::try_from(ids.len()).expect("training action IDs exceed u32") - start }
            } else {
                LevelSpan { start: sp.start, count: if level.first().is_some_and(|&n| player[n as usize] == p as i32) { sp.count } else { 0 } }
            };
            by_actor[p].push(actor_span);
        }
    }
    if let Some(ids) = &partitioned { assert_eq!(ids.len(), nodes.len(), "every action must belong to one player"); }
    (partitioned, by_actor)
}

fn action_id_bytes(count: usize) -> u64 {
    (count as u64).checked_mul(4).expect("training action byte count exceeds u64")
}

impl GpuPlan {
    pub fn build(spot: &Spot, use_iso: bool) -> GpuPlan {
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

        // Terminal CFVs stay resident for repeated BR/average evaluations.
        // Action/chance CFVs live only from their up-sweep level until the
        // immediately preceding level consumes them. Reuse those scratch
        // slots between even levels and between odd levels, with root at 0.
        let mut widths = vec![0usize; max_level as usize + 1];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            if reached[ni] && (node.kind == KIND_ACTION || node.kind == KIND_CHANCE) {
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
            if node.kind == KIND_ACTION || node.kind == KIND_CHANCE {
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

        let (up_action_nodes, up_action_spans) = partition_up_actions(&action_nodes, &action_spans, &node_player);

        GpuPlan {
            num_levels,
            nh,
            nh_max: nh[0].max(nh[1]),
            num_nodes: n,
            iso_active,
            action_nodes,
            action_spans,
            up_action_nodes,
            up_action_spans,
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
            node_cdiv,
            node_river_slot,
            reach_src,
            reach_slot,
            reach_blocks,
            cfv_slot,
            cfv_blocks,
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

    /// Direct whole-arena transfers avoid host snapshots when VRAM is ample.
    pub(crate) fn use_full_action_arenas(&mut self, spot: &Spot) {
        self.arena_elements = [spot.tree.data_size[0] as usize, spot.tree.data_size[1] as usize];
        for (i, node) in spot.tree.nodes.iter().enumerate() {
            self.node_data_off[i] = node.data_offset;
        }
    }

    /// Extra immutable IDs used only by training-up dispatch.
    pub(crate) fn training_metadata_bytes(&self) -> u64 {
        self.up_action_nodes.as_ref().map_or(0, |ids| action_id_bytes(ids.len()))
    }

    /// Traversal working bytes: reach + CFV staging and optional training IDs.
    /// Exact-budget callers include this total once; continuation metadata accounts
    /// for the IDs separately from its individually counted mutable workspace buffers.
    pub fn staging_bytes(&self) -> u64 {
        let words = [(self.reach_blocks[0], self.nh[0]), (self.reach_blocks[1], self.nh[1]),
            (self.cfv_blocks, self.nh_max)].into_iter().fold(0u64, |sum, (n, width)| {
                (n as u64).checked_mul(width as u64).and_then(|v| sum.checked_add(v))
                    .expect("GPU traversal word count exceeds u64")
            });
        words.checked_mul(4).and_then(|bytes| bytes.checked_add(self.training_metadata_bytes()))
            .expect("GPU traversal byte count exceeds u64")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{parse_sizes, SpotConfig, StreetSizing, TreeConfig};

    fn assert_actor_partition(nodes: &[u32], spans: &[LevelSpan], player: &[i32],
        ids: &Option<Vec<u32>>, actors: &[Vec<LevelSpan>; 2]) {
        let selected = ids.as_deref().unwrap_or(nodes);
        let mut consumed = Vec::new();
        for (l, original) in spans.iter().enumerate() {
            let level = &nodes[original.start as usize..(original.start + original.count) as usize];
            for p in 0..2 {
                let sp = actors[p][l];
                let actual = &selected[sp.start as usize..(sp.start + sp.count) as usize];
                let expected: Vec<_> = level.iter().copied().filter(|&n| player[n as usize] == p as i32).collect();
                assert_eq!(actual, expected);
                consumed.extend_from_slice(actual);
            }
        }
        consumed.sort_unstable();
        let mut original = nodes.to_vec(); original.sort_unstable();
        assert_eq!(consumed, original, "exact union without omitted or repeated IDs");
    }

    #[test]
    fn training_actor_partition_preserves_stable_coverage_and_coordinates() {
        let player = [0, 1, 0, 1, 1, 0, 0];
        for (nodes, spans, mixed) in [
            (vec![], vec![LevelSpan::default()], false),
            (vec![5, 2, 4, 1, 3], vec![LevelSpan { start: 0, count: 2 }, LevelSpan { start: 2, count: 0 }, LevelSpan { start: 2, count: 3 }], false),
            (vec![0, 4, 2, 1, 6, 3, 5], vec![LevelSpan { start: 0, count: 0 }, LevelSpan { start: 0, count: 1 }, LevelSpan { start: 1, count: 4 }, LevelSpan { start: 5, count: 2 }], true),
        ] {
            let original = nodes.clone();
            let (ids, actors) = partition_up_actions(&nodes, &spans, &player);
            assert_eq!(ids.is_some(), mixed);
            assert_eq!(nodes, original, "aggregate traversal order is untouched");
            assert_actor_partition(&nodes, &spans, &player, &ids, &actors);
            if !mixed {
                for p in 0..2 { for (actual, original) in actors[p].iter().zip(&spans) {
                    assert_eq!(actual.start, original.start, "uniform spans address original IDs");
                } }
            }
        }
    }

    #[test]
    fn training_actor_metadata_bytes_are_exact_and_checked() {
        assert_eq!(action_id_bytes(0), 0);
        assert_eq!(action_id_bytes(523533), 2094132);
        #[cfg(target_pointer_width = "64")]
        assert!(std::panic::catch_unwind(|| action_id_bytes(usize::MAX)).is_err());
    }

    #[test]
    fn river_bounds_match_strength_comparisons() {
        let mut selection_seen = [false; 2];
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
            for iso in [false, true] {
                let plan = GpuPlan::build(&spot, iso);
                selection_seen[usize::from(plan.up_action_nodes.is_some())] = true;
                assert_actor_partition(&plan.action_nodes, &plan.action_spans, &plan.node_player,
                    &plan.up_action_nodes, &plan.up_action_spans);
                assert_eq!(plan.training_metadata_bytes(), plan.up_action_nodes.as_ref().map_or(0, |ids| ids.len() as u64 * 4));
                let original_staging = (plan.reach_blocks[0] * plan.nh[0] + plan.reach_blocks[1] * plan.nh[1] + plan.cfv_blocks * plan.nh_max) as u64 * 4;
                assert_eq!(plan.staging_bytes(), original_staging + plan.training_metadata_bytes());
                assert_eq!(plan.cfv_slot[0], 0);
                let mut used = vec![false; plan.cfv_blocks];
                let mut terminals = std::collections::HashSet::new();
                for &node in plan.fold_nodes.iter().chain(&plan.show_nodes) {
                    let slot = plan.cfv_slot[node as usize] as usize;
                    assert!(terminals.insert(slot), "terminal caches must remain distinct");
                    used[slot] = true;
                }
                let mut live = vec![std::collections::HashSet::new(); plan.num_levels];
                for l in 0..plan.num_levels {
                    for (nodes, spans) in [(&plan.action_nodes, &plan.action_spans),
                        (&plan.chance_nodes, &plan.chance_node_spans)] {
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
        assert_eq!(selection_seen, [true, true], "real plans cover uniform and mixed selection");
    }
}
