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
    pub node_data_off: Vec<u64>,
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
    /// 53 entries per slot: span of card c is [slot*53+c, slot*53+c+1).
    pub riv_card_off: [Vec<u32>; 2],
    /// Positions (into the slot's sorted order) of hands containing the card.
    pub riv_card_pos: [Vec<u32>; 2],
    /// Max sorted-list length across slots, per player (shared-mem sizing).
    pub riv_max_cnt: [usize; 2],
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
        let mut riv_card_off = [Vec::new(), Vec::new()];
        let mut riv_card_pos = [Vec::new(), Vec::new()];
        let mut riv_max_cnt = [0usize, 0usize];
        for p in 0..2 {
            for &key in &slots {
                let eval = spot.river.entries[key].as_deref().expect("river eval");
                let sorted = &eval.sorted[p];
                riv_off[p].push(riv_sorted_idx[p].len() as u32);
                riv_cnt[p].push(sorted.len() as u32);
                riv_max_cnt[p] = riv_max_cnt[p].max(sorted.len());
                let mut by_card: Vec<Vec<u32>> = vec![Vec::new(); 52];
                for (pos, &(stren, idx)) in sorted.iter().enumerate() {
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
        let mut node_data_off = vec![0u64; n];
        let mut node_children_start = vec![0u32; n];
        let mut node_twin = vec![0f32; n];
        let mut node_tlose = vec![0f32; n];
        let mut node_ttie = vec![0f32; n];
        let mut node_cdiv = vec![0f32; n];
        for (ni, node) in spot.tree.nodes.iter().enumerate() {
            node_player[ni] = node.player as i32;
            node_na[ni] = node.num_children as i32;
            node_data_off[ni] = node.data_offset;
            node_children_start[ni] = node.children_start;
            node_twin[ni] = node.t_win as f32;
            node_tlose[ni] = node.t_lose as f32;
            node_ttie[ni] = node.t_tie as f32;
            if node.kind == KIND_CHANCE {
                node_cdiv[ni] = 1.0 / (46 - node.street as i32) as f32;
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
            node_children_start,
            node_twin,
            node_tlose,
            node_ttie,
            node_cdiv,
            node_river_slot,
            reach_src,
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
            riv_card_off,
            riv_card_pos,
            riv_max_cnt,
        }
    }

    /// Total bytes of GPU staging (reach + cfv) this plan needs.
    pub fn staging_bytes(&self) -> u64 {
        self.num_nodes as u64 * (self.nh[0] + self.nh[1] + self.nh_max) as u64 * 4
    }
}
