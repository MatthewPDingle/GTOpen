//! CUDA three-player CFR: level-synchronous sweeps over the full public
//! tree with the arenas resident in VRAM (no suit isomorphism).
//!
//! One iteration is three traversals. Before traversal p only the player
//! updated last, (p + 2) % 3, needs its reach recomputed; the up sweep then
//! evaluates terminals, chance averages and action nodes level by level.
//! Each traversal is captured into a CUDA graph after the first iteration.
//!
//! Large trees: the arenas can be stored compressed on the device (i16
//! regrets, u16 strategy sums, per-node scales, as in `Storage::Compressed`),
//! and the subtrees below the first chance layer (turn cards for a flop
//! root, river cards for a turn root) can be swept in groups that share one
//! scratch region for reaches and values. Only the root part's reaches and
//! the group roots' values stay resident.

use super::game::MwSpot;
use super::solver::{Dealt, MwProgress, MwSolver};
use super::tree::{others, payoff_table, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, NP};
use crate::cfr::{Algorithm, Discounts};
use crate::store::{Storage, Store};
use crate::tree::SENTINEL;
use cudarc::driver::{
    sys, CudaContext, CudaFunction, CudaGraph, CudaModule, CudaSlice, CudaStream, DevicePtr, DeviceRepr,
    LaunchConfig, PushKernelArg, ValidAsZeroBits,
};
use std::collections::HashMap;
use std::sync::Arc;

const BLOCK: u32 = 128;
/// VRAM left free for the driver, graphs and fragmentation.
const HEADROOM: u64 = 512 << 20;
/// Most actions a node may have on compressed arenas (kernel register array).
const MAX_ACTIONS_Q: usize = 16;

fn e(err: impl std::fmt::Debug) -> String {
    format!("cuda: {err:?}")
}

/// Pushes every argument (bound to a local so it outlives the launch) and
/// launches `$f` on `$stream`.
macro_rules! launch {
    ($stream:expr, $f:expr, $cfg:expr, [$($a:expr),* $(,)?]) => {{
        let mut b = $stream.launch_builder($f);
        $( let v = $a; b.arg(&v); )*
        unsafe { b.launch($cfg) }.map(|_| ()).map_err(e)
    }};
}

#[derive(Clone, Copy, Default, Debug)]
struct Span {
    start: i32,
    count: i32,
}

#[derive(Clone, Copy, Default, Debug)]
struct LevelSpans {
    action: Span,
    chance: Span,
    edge: Span,
    fold: Span,
    show: Span,
}

/// One level-synchronous sweep: the root part, or one group of subtrees
/// below the first chance layer (entered through `entry` chance edges).
#[derive(Clone, Default, Debug)]
struct Sweep {
    levels: Vec<LevelSpans>,
    entry: Span,
}

/// Tree structure shared by every grouping choice.
struct Layout {
    order: Vec<u32>,
    /// 0 = root part, 1 + c = below first-layer card c.
    seg: Vec<u8>,
    /// Level within the node's segment (group roots are level 0).
    level: Vec<u32>,
    dealt: Vec<Dealt>,
    /// Reach slots per player and level widths of the root part.
    root_slots: [usize; NP],
    root_width: Vec<u32>,
    /// Per first-layer card: reach slots per player and level widths
    /// (level 0, the group roots, excluded: their values are resident).
    card_slots: Vec<[usize; NP]>,
    card_width: Vec<Vec<u32>>,
    num_roots: usize,
}

impl Layout {
    fn build(spot: &MwSpot) -> Result<Layout, String> {
        let tree = &spot.tree;
        let nn = tree.nodes.len();
        let mut seg = vec![0u8; nn];
        let mut level = vec![u32::MAX; nn];
        let mut dealt = vec![Dealt::default(); nn];
        let mut order: Vec<u32> = Vec::with_capacity(nn);
        level[0] = 0;
        order.push(0);
        let mut head = 0;
        let mut root_slots = [1usize; NP];
        let mut card_slots = vec![[0usize; NP]; 52];
        let mut num_roots = 0;
        let mut kids: Vec<(usize, Option<u8>)> = Vec::new();
        while head < order.len() {
            let n = order[head] as usize;
            head += 1;
            let node = &tree.nodes[n];
            kids.clear();
            match node.kind {
                KIND_ACTION => kids.extend((0..node.num_children as usize).map(|a| (tree.child(node, a) as usize, None))),
                KIND_CHANCE => {
                    for c in 0..52u8 {
                        let ch = tree.children[node.children_start as usize + c as usize];
                        if ch != SENTINEL {
                            kids.push((ch as usize, Some(c)));
                        }
                    }
                }
                _ => {}
            }
            for &(c, card) in &kids {
                if level[c] != u32::MAX {
                    return Err("tree node reached twice".into());
                }
                if let (Some(k), 0) = (card, seg[n]) {
                    seg[c] = 1 + k;
                    level[c] = 0;
                    num_roots += 1;
                } else {
                    seg[c] = seg[n];
                    level[c] = level[n] + 1;
                }
                dealt[c] = match card {
                    Some(k) => dealt[n].push(k),
                    None => dealt[n],
                };
                let slots = if seg[c] == 0 { &mut root_slots } else { &mut card_slots[seg[c] as usize - 1] };
                for (k, s) in slots.iter_mut().enumerate() {
                    if card.is_some() || (node.kind == KIND_ACTION && node.player as usize == k) {
                        *s += 1;
                    }
                }
                order.push(c as u32);
            }
        }
        if order.len() != nn {
            return Err("tree has unreachable nodes".into());
        }
        let mut root_width = Vec::new();
        let mut card_width: Vec<Vec<u32>> = vec![Vec::new(); 52];
        for &n in &order {
            let (l, s) = (level[n as usize] as usize, seg[n as usize]);
            let w = if s == 0 { &mut root_width } else { &mut card_width[s as usize - 1] };
            if w.len() <= l {
                w.resize(l + 1, 0);
            }
            if s == 0 || l > 0 {
                w[l] += 1;
            }
        }
        Ok(Layout { order, seg, level, dealt, root_slots, root_width, card_slots, card_width, num_roots })
    }

    /// Reach bytes and widest level of one group of first-layer cards.
    fn group_bytes(&self, cards: &[u8], nh: &[usize; NP]) -> (u64, u32) {
        let mut reach = 0u64;
        let mut width: Vec<u32> = Vec::new();
        for &c in cards {
            let s = &self.card_slots[c as usize];
            reach += (0..NP).map(|k| (s[k] * nh[k] * 4) as u64).sum::<u64>();
            let w = &self.card_width[c as usize];
            if width.len() < w.len() {
                width.resize(w.len(), 0);
            }
            for (l, &x) in w.iter().enumerate() {
                width[l] += x;
            }
        }
        (reach, width.into_iter().max().unwrap_or(0))
    }

    fn cards_present(&self) -> Vec<u8> {
        (0..52u8).filter(|&c| self.card_slots[c as usize].iter().any(|&x| x > 0)).collect()
    }
}

/// Memory of a plan, by part.
#[derive(Clone, Copy, Debug, Default)]
pub struct GpuBytes {
    pub arenas: u64,
    pub reach: u64,
    pub values: u64,
    pub tables: u64,
}

impl GpuBytes {
    pub fn total(&self) -> u64 {
        self.arenas + self.reach + self.values + self.tables
    }
}

fn arena_bytes(spot: &MwSpot, storage: Storage, algo: Algorithm) -> u64 {
    let e: u64 = spot.tree.data_size.iter().sum();
    let nn = spot.tree.nodes.len() as u64;
    let pcfr = algo == Algorithm::PcfrPlus;
    match storage {
        Storage::F32 => e * if pcfr { 12 } else { 8 },
        Storage::Compressed => e * if pcfr { 6 } else { 4 } + nn * 4 * NP as u64 * if pcfr { 3 } else { 2 },
    }
}

fn table_bytes(spot: &MwSpot, river_slots: usize) -> u64 {
    let nn = spot.tree.nodes.len() as u64;
    // per node: player, na, offset (8), children start, cdiv, class, river,
    // cfv slot, 3 reach slots, lock offset (8); level lists; chance edges.
    nn * 72
        + spot.tree.children.len() as u64 * 4
        + river_slots as u64 * (2704 * 4 + 53 * 4 * NP as u64)
        + spot.hands.iter().map(|h| h.len() as u64 * 64).sum::<u64>()
}

/// Groups first-layer cards so each group's scratch fits `scratch` bytes.
/// None when even single cards do not fit.
fn group_cards(layout: &Layout, nh: &[usize; NP], scratch: u64) -> Option<Vec<Vec<u8>>> {
    let nh_max = *nh.iter().max().unwrap() as u64;
    let root_width = layout.root_width.iter().copied().max().unwrap_or(0) as u64;
    let cost = |cards: &[u8]| {
        let (reach, w) = layout.group_bytes(cards, nh);
        reach + 2 * (w as u64).max(root_width) * nh_max * 4
    };
    let mut groups: Vec<Vec<u8>> = Vec::new();
    let mut cur: Vec<u8> = Vec::new();
    for c in layout.cards_present() {
        cur.push(c);
        if cost(&cur) > scratch {
            cur.pop();
            if cur.is_empty() {
                return None;
            }
            groups.push(std::mem::take(&mut cur));
            cur.push(c);
            if cost(&cur) > scratch {
                return None;
            }
        }
    }
    if !cur.is_empty() {
        groups.push(cur);
    }
    Some(groups)
}

fn plan_bytes(spot: &MwSpot, layout: &Layout, groups: &[Vec<u8>], storage: Storage, algo: Algorithm, river_slots: usize) -> GpuBytes {
    let nh: [usize; NP] = std::array::from_fn(|k| spot.hands[k].len());
    let nh_max = *nh.iter().max().unwrap() as u64;
    let mut reach_slots = layout.root_slots;
    let mut width = layout.root_width.iter().copied().max().unwrap_or(0);
    let mut max_group = [0usize; NP];
    for g in groups {
        let mut s = [0usize; NP];
        for &c in g {
            for k in 0..NP {
                s[k] += layout.card_slots[c as usize][k];
            }
        }
        for k in 0..NP {
            max_group[k] = max_group[k].max(s[k]);
        }
        width = width.max(layout.group_bytes(g, &nh).1);
    }
    for k in 0..NP {
        reach_slots[k] += max_group[k];
    }
    GpuBytes {
        arenas: arena_bytes(spot, storage, algo),
        reach: (0..NP).map(|k| (reach_slots[k] * nh[k] * 4) as u64).sum(),
        values: (2 * width as u64 + layout.num_roots as u64) * nh_max * 4,
        tables: table_bytes(spot, river_slots),
    }
}

/// How a spot runs within `budget` device bytes: storage, first-layer card
/// groups and memory. Prefers f32 arenas, then as few groups as fit.
fn choose(
    spot: &MwSpot,
    layout: &Layout,
    algo: Algorithm,
    budget: u64,
    opts: &MwGpuOptions,
    river_slots: usize,
) -> Result<(Storage, Vec<Vec<u8>>, GpuBytes), String> {
    let nh: [usize; NP] = std::array::from_fn(|k| spot.hands[k].len());
    let nh_max = *nh.iter().max().unwrap() as u64;
    let all = layout.cards_present();
    let max_na = max_actions(spot);
    let storages: Vec<Storage> = match opts.storage {
        Some(Storage::Compressed) if max_na > MAX_ACTIONS_Q => {
            return Err(format!("compressed GPU arenas support at most {MAX_ACTIONS_Q} actions per node"))
        }
        Some(s) => vec![s],
        None if max_na > MAX_ACTIONS_Q => vec![Storage::F32],
        None => vec![Storage::F32, Storage::Compressed],
    };
    let mut smallest: Option<GpuBytes> = None;
    for &storage in &storages {
        let groups: Vec<Vec<u8>> = match opts.max_cards_per_group {
            Some(k) => all.chunks(k.max(1)).map(|c| c.to_vec()).collect(),
            None => {
                let single: Vec<Vec<u8>> = if all.is_empty() { vec![] } else { vec![all.clone()] };
                let b = plan_bytes(spot, layout, &single, storage, algo, river_slots);
                if b.total() <= budget {
                    single
                } else {
                    let resident = b.arenas
                        + b.tables
                        + layout.root_slots.iter().zip(&nh).map(|(&s, &h)| (s * h * 4) as u64).sum::<u64>()
                        + layout.num_roots as u64 * nh_max * 4;
                    match budget.checked_sub(resident).and_then(|scratch| group_cards(layout, &nh, scratch)) {
                        Some(g) => g,
                        None => {
                            let singles: Vec<Vec<u8>> = all.iter().map(|&c| vec![c]).collect();
                            let b = plan_bytes(spot, layout, &singles, storage, algo, river_slots);
                            if smallest.map_or(true, |x| b.total() < x.total()) {
                                smallest = Some(b);
                            }
                            continue;
                        }
                    }
                }
            }
        };
        let b = plan_bytes(spot, layout, &groups, storage, algo, river_slots);
        if b.total() <= budget {
            return Ok((storage, groups, b));
        }
        if smallest.map_or(true, |x| b.total() < x.total()) {
            smallest = Some(b);
        }
    }
    let b = smallest.unwrap_or_default();
    Err(format!(
        "spot needs at least {:.2} GB of GPU memory ({:.2} GB arenas, {:.2} GB reach, {:.2} GB values, {:.2} GB tables); {:.2} GB available",
        b.total() as f64 / 1e9,
        b.arenas as f64 / 1e9,
        b.reach as f64 / 1e9,
        b.values as f64 / 1e9,
        b.tables as f64 / 1e9,
        budget as f64 / 1e9
    ))
}

fn max_actions(spot: &MwSpot) -> usize {
    spot.tree.nodes.iter().filter(|n| n.kind == KIND_ACTION).map(|n| n.num_children as usize).max().unwrap_or(0)
}

/// Terminal payoff classes and river boards (independent of grouping).
struct Terminals {
    node_class: Vec<i32>,
    node_river: Vec<i32>,
    coef: Vec<f32>,
    river_keys: Vec<usize>,
}

fn terminals(spot: &MwSpot, layout: &Layout) -> Terminals {
    let tree = &spot.tree;
    let cfg = &tree.config;
    let nn = tree.nodes.len();
    let mut node_class = vec![-1i32; nn];
    let mut node_river = vec![-1i32; nn];
    let mut classes: HashMap<Vec<u32>, i32> = HashMap::new();
    let mut coef: Vec<f32> = Vec::new();
    let mut river_slots: HashMap<usize, i32> = HashMap::new();
    let mut river_keys: Vec<usize> = Vec::new();
    for (n, node) in tree.nodes.iter().enumerate() {
        if node.kind != KIND_TERM_FOLD && node.kind != KIND_TERM_SHOWDOWN {
            continue;
        }
        let mut c27 = [0f32; 27];
        for p in 0..NP {
            let cf = super::eval::basis_coeffs(&payoff_table(node, p, cfg.rake_pct, cfg.rake_cap));
            for x in 0..3 {
                for y in 0..3 {
                    c27[p * 9 + x * 3 + y] = cf[x][y] as f32;
                }
            }
        }
        let key: Vec<u32> = c27.iter().map(|v| v.to_bits()).collect();
        let next = classes.len() as i32;
        node_class[n] = *classes.entry(key).or_insert_with(|| {
            coef.extend_from_slice(&c27);
            next
        });
        if node.kind == KIND_TERM_SHOWDOWN {
            let k = spot.river.key(layout.dealt[n].as_slice());
            let next = river_keys.len() as i32;
            node_river[n] = *river_slots.entry(k).or_insert_with(|| {
                river_keys.push(k);
                next
            });
        }
    }
    if coef.is_empty() {
        coef.push(0.0);
    }
    Terminals { node_class, node_river, coef, river_keys }
}

/// Host-side layout of the tree for the kernels.
struct Plan {
    sweeps: Vec<Sweep>,
    action: Vec<u32>,
    chance: Vec<u32>,
    edge_par: Vec<u32>,
    edge_chi: Vec<u32>,
    edge_card: Vec<u32>,
    fold: Vec<u32>,
    show: Vec<u32>,
    node_player: Vec<i32>,
    node_na: Vec<i32>,
    node_off: Vec<u64>,
    node_cs: Vec<u32>,
    node_cdiv: Vec<f32>,
    node_class: Vec<i32>,
    node_river: Vec<i32>,
    cfv_slot: Vec<u32>,
    cfv_slots: usize,
    reach_slot: [Vec<u32>; NP],
    reach_slots: [usize; NP],
    coef: Vec<f32>,
    srt_off: [Vec<u32>; NP],
    srt_str: [Vec<u32>; NP],
    srt_idx: [Vec<u32>; NP],
    cpos_off: [Vec<u32>; NP],
    cpos: [Vec<u32>; NP],
    rank_pair: Vec<u32>,
    max_sorted: [usize; NP],
}

impl Plan {
    fn build(spot: &MwSpot, layout: &Layout, term: Terminals, groups: &[Vec<u8>]) -> Result<Plan, String> {
        let tree = &spot.tree;
        let nn = tree.nodes.len();
        let mut group_of = [usize::MAX; 52];
        for (g, cards) in groups.iter().enumerate() {
            for &c in cards {
                group_of[c as usize] = g;
            }
        }
        // Sweep of each node: 0 = root part, 1 + group.
        let sweep_of = |n: usize| -> usize {
            match layout.seg[n] {
                0 => 0,
                s => 1 + group_of[s as usize - 1],
            }
        };
        let num_sweeps = 1 + groups.len();
        let mut num_levels = vec![0usize; num_sweeps];
        for n in 0..nn {
            let s = sweep_of(n);
            num_levels[s] = num_levels[s].max(layout.level[n] as usize + 1);
        }

        // cfv slots: index within (sweep, level); halves alternate by level
        // parity; group roots get resident slots after both halves.
        let mut width: Vec<Vec<u32>> = num_levels.iter().map(|&l| vec![0u32; l]).collect();
        let mut cfv_slot = vec![0u32; nn];
        let mut root_idx = vec![u32::MAX; nn];
        let mut roots = 0u32;
        for &n in &layout.order {
            let n = n as usize;
            let s = sweep_of(n);
            let l = layout.level[n] as usize;
            if s > 0 && l == 0 {
                root_idx[n] = roots;
                roots += 1;
            } else {
                cfv_slot[n] = width[s][l];
                width[s][l] += 1;
            }
        }
        let w = width.iter().flat_map(|v| v.iter().copied()).max().unwrap_or(0);
        for n in 0..nn {
            if root_idx[n] != u32::MAX {
                cfv_slot[n] = 2 * w + root_idx[n];
            } else if layout.level[n] % 2 == 1 {
                cfv_slot[n] += w;
            }
        }

        // Reach slots (BFS order: parents first). The root part counts from
        // 0 with the owner trick; every group counts from the root part's
        // total, sharing one scratch region.
        let mut reach_slot: [Vec<u32>; NP] = std::array::from_fn(|_| vec![0u32; nn]);
        let mut next_slot: Vec<[usize; NP]> = vec![layout.root_slots; num_sweeps];
        next_slot[0] = [1; NP];
        let mut kids: Vec<(usize, bool)> = Vec::new();
        for &n in &layout.order {
            let n = n as usize;
            let node = &tree.nodes[n];
            kids.clear();
            match node.kind {
                KIND_ACTION => kids.extend((0..node.num_children as usize).map(|a| (tree.child(node, a) as usize, false))),
                KIND_CHANCE => kids.extend(
                    (0..52usize)
                        .map(|c| tree.children[node.children_start as usize + c])
                        .filter(|&ch| ch != SENTINEL)
                        .map(|ch| (ch as usize, true)),
                ),
                _ => {}
            }
            for &(c, chance) in &kids {
                let s = sweep_of(c);
                for k in 0..NP {
                    if chance || (node.kind == KIND_ACTION && node.player as usize == k) {
                        reach_slot[k][c] = next_slot[s][k] as u32;
                        next_slot[s][k] += 1;
                    } else {
                        reach_slot[k][c] = reach_slot[k][n];
                    }
                }
            }
        }
        let reach_slots: [usize; NP] = std::array::from_fn(|k| next_slot.iter().map(|x| x[k]).max().unwrap());

        // Work lists, sweep by sweep, level by level.
        let mut by: Vec<Vec<[Vec<u32>; 4]>> =
            num_levels.iter().map(|&l| (0..l).map(|_| Default::default()).collect()).collect();
        let mut edges: Vec<Vec<Vec<(u32, u32, u32)>>> = num_levels.iter().map(|&l| vec![Vec::new(); l]).collect();
        let mut entry: Vec<Vec<(u32, u32, u32)>> = vec![Vec::new(); num_sweeps];
        for &n in &layout.order {
            let nu = n as usize;
            let node = &tree.nodes[nu];
            let s = sweep_of(nu);
            let l = layout.level[nu] as usize;
            let k = match node.kind {
                KIND_ACTION => 0,
                KIND_CHANCE => 1,
                KIND_TERM_FOLD => 2,
                KIND_TERM_SHOWDOWN => 3,
                _ => return Err("unknown node kind".into()),
            };
            by[s][l][k].push(n);
            if node.kind == KIND_CHANCE {
                for c in 0..52u32 {
                    let ch = tree.children[node.children_start as usize + c as usize];
                    if ch == SENTINEL {
                        continue;
                    }
                    let cs = sweep_of(ch as usize);
                    if cs == s {
                        edges[s][l].push((n, ch, c));
                    } else {
                        entry[cs].push((n, ch, c));
                    }
                }
            }
        }
        let mut lists: [Vec<u32>; 4] = Default::default();
        let (mut edge_par, mut edge_chi, mut edge_card) = (Vec::new(), Vec::new(), Vec::new());
        let mut push_edges = |list: &[(u32, u32, u32)]| {
            let span = Span { start: edge_par.len() as i32, count: list.len() as i32 };
            for &(a, b, c) in list {
                edge_par.push(a);
                edge_chi.push(b);
                edge_card.push(c);
            }
            span
        };
        let mut sweeps = Vec::with_capacity(num_sweeps);
        for s in 0..num_sweeps {
            let mut sw = Sweep { entry: push_edges(&entry[s]), levels: Vec::new() };
            for l in 0..num_levels[s] {
                let mut spans = [Span::default(); 4];
                for (k, out) in lists.iter_mut().enumerate() {
                    spans[k] = Span { start: out.len() as i32, count: by[s][l][k].len() as i32 };
                    out.extend_from_slice(&by[s][l][k]);
                }
                sw.levels.push(LevelSpans {
                    action: spans[0],
                    chance: spans[1],
                    fold: spans[2],
                    show: spans[3],
                    edge: push_edges(&edges[s][l]),
                });
            }
            sweeps.push(sw);
        }
        let [action, chance, fold, show] = lists;

        let mut node_player = vec![-1i32; nn];
        let mut node_na = vec![0i32; nn];
        let mut node_off = vec![0u64; nn];
        let mut node_cs = vec![0u32; nn];
        let mut node_cdiv = vec![0f32; nn];
        for (n, node) in tree.nodes.iter().enumerate() {
            node_cs[n] = node.children_start;
            match node.kind {
                KIND_ACTION => {
                    node_player[n] = node.player as i32;
                    node_na[n] = node.num_children as i32;
                    node_off[n] = node.data_offset;
                }
                KIND_CHANCE => node_cdiv[n] = 1.0 / (44 - node.street as i32) as f32,
                _ => {}
            }
        }

        // River boards.
        let mut srt_off: [Vec<u32>; NP] = Default::default();
        let mut srt_str: [Vec<u32>; NP] = Default::default();
        let mut srt_idx: [Vec<u32>; NP] = Default::default();
        let mut cpos_off: [Vec<u32>; NP] = Default::default();
        let mut cpos: [Vec<u32>; NP] = Default::default();
        let mut rank_pair = Vec::with_capacity(term.river_keys.len() * 2704);
        let mut max_sorted = [0usize; NP];
        for &key in &term.river_keys {
            let ev = spot.river.entries[key].as_deref().ok_or("river eval missing")?;
            rank_pair.extend_from_slice(&ev.rank_pair);
            for k in 0..NP {
                srt_off[k].push(srt_str[k].len() as u32);
                let list = &ev.sorted[k];
                max_sorted[k] = max_sorted[k].max(list.len());
                let mut by_card: Vec<Vec<u32>> = vec![Vec::new(); 52];
                for (pos, &(s, i)) in list.iter().enumerate() {
                    srt_str[k].push(s);
                    srt_idx[k].push(i as u32);
                    let h = &spot.hands[k][i as usize];
                    by_card[h.c1 as usize].push(pos as u32);
                    by_card[h.c2 as usize].push(pos as u32);
                }
                for v in by_card {
                    cpos_off[k].push(cpos[k].len() as u32);
                    cpos[k].extend(v);
                }
                cpos_off[k].push(cpos[k].len() as u32);
            }
        }
        for k in 0..NP {
            srt_off[k].push(srt_str[k].len() as u32);
        }

        Ok(Plan {
            sweeps,
            action,
            chance,
            edge_par,
            edge_chi,
            edge_card,
            fold,
            show,
            node_player,
            node_na,
            node_off,
            node_cs,
            node_cdiv,
            node_class: term.node_class,
            node_river: term.node_river,
            cfv_slot,
            cfv_slots: 2 * w as usize + roots as usize,
            reach_slot,
            reach_slots,
            coef: term.coef,
            srt_off,
            srt_str,
            srt_idx,
            cpos_off,
            cpos,
            rank_pair,
            max_sorted,
        })
    }
}

/// Device memory a spot needs: (fully resident with f32 arenas, smallest
/// workable plan). The second decides whether the GPU can take it at all.
pub fn estimate_device_bytes(spot: &MwSpot, algo: Algorithm) -> (u64, u64) {
    let Ok(layout) = Layout::build(spot) else { return (0, 0) };
    let rivers = terminals(spot, &layout).river_keys.len();
    let all = layout.cards_present();
    let single: Vec<Vec<u8>> = if all.is_empty() { vec![] } else { vec![all.clone()] };
    let full = plan_bytes(spot, &layout, &single, Storage::F32, algo, rivers).total() + HEADROOM;
    let singles: Vec<Vec<u8>> = all.iter().map(|&c| vec![c]).collect();
    let max_na = max_actions(spot);
    let storage = if max_na > MAX_ACTIONS_Q { Storage::F32 } else { Storage::Compressed };
    let min = plan_bytes(spot, &layout, &singles, storage, algo, rivers).total() + HEADROOM;
    (full, min.min(full))
}

/// Device bytes a solve may plan for. `SOLVER_GPU_MEM_GB` overrides it.
/// On Windows (WDDM) the driver's free-memory figure ignores what the
/// desktop holds and allocations past physical VRAM succeed but page to
/// system RAM, so the budget also keeps 12% of the card free there.
fn device_budget(free: u64, total: u64) -> u64 {
    if let Some(gb) = std::env::var("SOLVER_GPU_MEM_GB").ok().and_then(|v| v.parse::<f64>().ok()) {
        return (gb * 1e9) as u64;
    }
    let cap = if cfg!(windows) { total - total / 8 } else { total };
    free.min(cap).saturating_sub(HEADROOM)
}

/// Overrides for tests and tuning.
#[derive(Clone, Debug, Default)]
pub struct MwGpuOptions {
    /// Arena storage on the device (default: f32 when it fits).
    pub storage: Option<Storage>,
    /// Device bytes to plan for (default: free memory minus headroom).
    pub budget_bytes: Option<u64>,
    /// Sweep the subtrees below the first chance layer in groups of at most
    /// this many cards (default: as few groups as fit).
    pub max_cards_per_group: Option<usize>,
}

enum DevArenas {
    F32 {
        reg: [CudaSlice<f32>; NP],
        str: [CudaSlice<f32>; NP],
        prd: Option<[CudaSlice<f32>; NP]>,
    },
    Q {
        reg: [CudaSlice<i16>; NP],
        str: [CudaSlice<u16>; NP],
        prd: Option<[CudaSlice<i16>; NP]>,
        rsc: [CudaSlice<f32>; NP],
        ssc: [CudaSlice<f32>; NP],
        psc: Option<[CudaSlice<f32>; NP]>,
    },
}

struct Bufs {
    action: CudaSlice<u32>,
    chance: CudaSlice<u32>,
    edge_par: CudaSlice<u32>,
    edge_chi: CudaSlice<u32>,
    edge_card: CudaSlice<u32>,
    fold: CudaSlice<u32>,
    show: CudaSlice<u32>,
    node_player: CudaSlice<i32>,
    node_na: CudaSlice<i32>,
    node_off: CudaSlice<u64>,
    node_cs: CudaSlice<u32>,
    node_cdiv: CudaSlice<f32>,
    node_class: CudaSlice<i32>,
    node_river: CudaSlice<i32>,
    children: CudaSlice<u32>,
    cfv_slot: CudaSlice<u32>,
    cfv: CudaSlice<f32>,
    reach_slot: [CudaSlice<u32>; NP],
    reach: [CudaSlice<f32>; NP],
    weights: [CudaSlice<f32>; NP],
    c1: [CudaSlice<u32>; NP],
    c2: [CudaSlice<u32>; NP],
    mask: [CudaSlice<u64>; NP],
    same: [CudaSlice<u32>; NP],
    coef: CudaSlice<f32>,
    srt_off: [CudaSlice<u32>; NP],
    srt_str: [CudaSlice<u32>; NP],
    srt_idx: [CudaSlice<u32>; NP],
    cpos_off: [CudaSlice<u32>; NP],
    cpos: [CudaSlice<u32>; NP],
    rank_pair: CudaSlice<u32>,
    lock_off: CudaSlice<i64>,
    lock_sigma: CudaSlice<f32>,
    /// {pos, neg, strat, iteration bits}
    disc: CudaSlice<f32>,
    arenas: DevArenas,
}

/// Raw device pointer of a buffer. Event tracking is disabled (everything
/// runs on one stream), so the guard carries no synchronization.
fn ptr<T>(s: &CudaSlice<T>, stream: &CudaStream) -> u64 {
    s.device_ptr(stream).0
}

/// Uploads `v`, or `len` zeros when it is empty (kernels never read the
/// arena of a player without decisions, but allocations must be non-empty).
fn upload<T: DeviceRepr + ValidAsZeroBits>(stream: &Arc<CudaStream>, v: &[T], len: usize) -> Result<CudaSlice<T>, String> {
    if v.is_empty() {
        stream.alloc_zeros::<T>(len.max(1)).map_err(e)
    } else {
        stream.clone_htod(v).map_err(e)
    }
}

pub struct MwGpuSolver {
    pub spot: Arc<MwSpot>,
    pub iteration: u32,
    pub algo: Algorithm,
    pub storage: Storage,
    _ctx: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    _module: Arc<CudaModule>,
    f_copy_root: CudaFunction,
    f_down_action: CudaFunction,
    f_down_action_q: CudaFunction,
    f_down_chance: CudaFunction,
    f_up_fold: CudaFunction,
    f_up_show: CudaFunction,
    f_up_chance: CudaFunction,
    f_up_action: CudaFunction,
    f_up_action_q: CudaFunction,
    sweeps: Vec<Sweep>,
    nh: [i32; NP],
    nh_max: i32,
    max_sorted: [usize; NP],
    show_threads: Option<u32>,
    bufs: Bufs,
    bytes: GpuBytes,
    /// Reach buffers hold current-strategy reaches for every player.
    reach_current: bool,
    graphs: Option<Vec<CudaGraph>>,
    /// Per-kernel wall time and launch count while profiling (no graphs).
    prof: Option<std::cell::RefCell<HashMap<&'static str, (f64, u64)>>>,
}

impl MwGpuSolver {
    /// Fresh solver (zero regrets) for `spot`.
    pub fn new(spot: Arc<MwSpot>, algo: Algorithm) -> Result<MwGpuSolver, String> {
        Self::build(spot, algo, None, &MwGpuOptions::default())
    }

    pub fn with_options(spot: Arc<MwSpot>, algo: Algorithm, opts: &MwGpuOptions) -> Result<MwGpuSolver, String> {
        Self::build(spot, algo, None, opts)
    }

    /// Continue from a CPU solver's state (any storage; locks unsupported).
    pub fn from_solver(s: &MwSolver) -> Result<MwGpuSolver, String> {
        Self::from_solver_with(s, &MwGpuOptions::default())
    }

    pub fn from_solver_with(s: &MwSolver, opts: &MwGpuOptions) -> Result<MwGpuSolver, String> {
        if !s.locks.is_empty() {
            return Err("the GPU solver does not support node locks yet".into());
        }
        let mut g = Self::build(s.spot.clone(), s.algo, Some(s), opts)?;
        g.iteration = s.iteration;
        Ok(g)
    }

    fn build(spot: Arc<MwSpot>, algo: Algorithm, init: Option<&MwSolver>, opts: &MwGpuOptions) -> Result<MwGpuSolver, String> {
        let layout = Layout::build(&spot)?;
        let term = terminals(&spot, &layout);
        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
        // One stream: cross-stream event tracking is unnecessary and its
        // events would break graph capture.
        unsafe { ctx.disable_event_tracking() };
        let budget = match opts.budget_bytes {
            Some(b) => b,
            None => {
                let (free, total) = ctx.mem_get_info().map_err(e)?;
                device_budget(free as u64, total as u64)
            }
        };
        let (storage, groups, bytes) = choose(&spot, &layout, algo, budget, opts, term.river_keys.len())?;
        let plan = Plan::build(&spot, &layout, term, &groups)?;
        drop(layout);

        let (cc_maj, cc_min) = ctx.compute_capability().map_err(e)?;
        let arch: &'static str = Box::leak(format!("compute_{cc_maj}{cc_min}").into_boxed_str());
        static PTX: std::sync::OnceLock<Result<cudarc::nvrtc::Ptx, String>> = std::sync::OnceLock::new();
        let ptx = PTX
            .get_or_init(|| {
                cudarc::nvrtc::compile_ptx_with_opts(
                    include_str!("kernels.cu"),
                    cudarc::nvrtc::CompileOptions { arch: Some(arch), ..Default::default() },
                )
                .map_err(e)
            })
            .clone()?;
        let module = ctx.load_module(ptx).map_err(e)?;
        let func = |name: &str| module.load_function(name).map_err(e);
        let f_up_show = func("mw_up_show")?;
        // Always opt in: the kernel's static shared memory counts toward the
        // 48 KB default too.
        let show_need = (0..NP).map(|p| Self::show_shared_bytes(&plan.max_sorted, p)).max().unwrap();
        f_up_show
            .set_attribute(sys::CUfunction_attribute::CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES, show_need as i32)
            .map_err(|err| format!("showdown kernel needs {show_need} bytes of shared memory: {err:?}"))?;

        let up32 = |v: &[u32]| upload(&stream, v, 1);
        let upi = |v: &[i32]| upload(&stream, v, 1);
        let up64 = |v: &[u64]| upload(&stream, v, 1);
        let upf = |v: &[f32]| upload(&stream, v, 1);

        let nh: [usize; NP] = std::array::from_fn(|p| spot.hands[p].len());
        let nh_max = *nh.iter().max().unwrap();
        let hands = &spot.hands;
        let c1: [Vec<u32>; NP] = std::array::from_fn(|k| hands[k].iter().map(|h| h.c1 as u32).collect());
        let c2: [Vec<u32>; NP] = std::array::from_fn(|k| hands[k].iter().map(|h| h.c2 as u32).collect());
        let mask: [Vec<u64>; NP] = std::array::from_fn(|k| hands[k].iter().map(|h| h.mask).collect());
        // same[p][j]: hand j of q (first opponent) as a hand of r, if held.
        let same: [Vec<u32>; NP] = std::array::from_fn(|p| {
            let (q, r) = others(p);
            spot.hand_combo[q]
                .iter()
                .map(|&k| {
                    let j = spot.combo_hand[r][k as usize];
                    if j == super::game::NO_HAND {
                        u32::MAX
                    } else {
                        j as u32
                    }
                })
                .collect()
        });

        let arenas = upload_arenas(&stream, &spot, storage, algo, init)?;
        let nn = spot.tree.nodes.len();
        let bufs = Bufs {
            action: up32(&plan.action)?,
            chance: up32(&plan.chance)?,
            edge_par: up32(&plan.edge_par)?,
            edge_chi: up32(&plan.edge_chi)?,
            edge_card: up32(&plan.edge_card)?,
            fold: up32(&plan.fold)?,
            show: up32(&plan.show)?,
            node_player: upi(&plan.node_player)?,
            node_na: upi(&plan.node_na)?,
            node_off: up64(&plan.node_off)?,
            node_cs: up32(&plan.node_cs)?,
            node_cdiv: upf(&plan.node_cdiv)?,
            node_class: upi(&plan.node_class)?,
            node_river: upi(&plan.node_river)?,
            children: up32(&spot.tree.children)?,
            cfv_slot: up32(&plan.cfv_slot)?,
            cfv: stream.alloc_zeros::<f32>(plan.cfv_slots.max(1) * nh_max).map_err(e)?,
            reach_slot: [up32(&plan.reach_slot[0])?, up32(&plan.reach_slot[1])?, up32(&plan.reach_slot[2])?],
            reach: [
                stream.alloc_zeros::<f32>(plan.reach_slots[0] * nh[0]).map_err(e)?,
                stream.alloc_zeros::<f32>(plan.reach_slots[1] * nh[1]).map_err(e)?,
                stream.alloc_zeros::<f32>(plan.reach_slots[2] * nh[2]).map_err(e)?,
            ],
            weights: [upf(&spot.weights[0])?, upf(&spot.weights[1])?, upf(&spot.weights[2])?],
            c1: [up32(&c1[0])?, up32(&c1[1])?, up32(&c1[2])?],
            c2: [up32(&c2[0])?, up32(&c2[1])?, up32(&c2[2])?],
            mask: [up64(&mask[0])?, up64(&mask[1])?, up64(&mask[2])?],
            same: [up32(&same[0])?, up32(&same[1])?, up32(&same[2])?],
            coef: upf(&plan.coef)?,
            srt_off: [up32(&plan.srt_off[0])?, up32(&plan.srt_off[1])?, up32(&plan.srt_off[2])?],
            srt_str: [up32(&plan.srt_str[0])?, up32(&plan.srt_str[1])?, up32(&plan.srt_str[2])?],
            srt_idx: [up32(&plan.srt_idx[0])?, up32(&plan.srt_idx[1])?, up32(&plan.srt_idx[2])?],
            cpos_off: [up32(&plan.cpos_off[0])?, up32(&plan.cpos_off[1])?, up32(&plan.cpos_off[2])?],
            cpos: [up32(&plan.cpos[0])?, up32(&plan.cpos[1])?, up32(&plan.cpos[2])?],
            rank_pair: up32(&plan.rank_pair)?,
            lock_off: stream.clone_htod(&vec![-1i64; nn]).map_err(e)?,
            lock_sigma: stream.alloc_zeros::<f32>(1).map_err(e)?,
            disc: stream.alloc_zeros::<f32>(4).map_err(e)?,
            arenas,
        };

        Ok(MwGpuSolver {
            iteration: 0,
            algo,
            storage,
            f_copy_root: func("mw_copy_root")?,
            f_down_action: func("mw_down_action")?,
            f_down_action_q: func("mw_down_action_q")?,
            f_down_chance: func("mw_down_chance")?,
            f_up_fold: func("mw_up_fold")?,
            f_up_show,
            f_up_chance: func("mw_up_chance")?,
            f_up_action: func("mw_up_action")?,
            f_up_action_q: func("mw_up_action_q")?,
            sweeps: plan.sweeps,
            nh: nh.map(|x| x as i32),
            nh_max: nh_max as i32,
            max_sorted: plan.max_sorted,
            show_threads: std::env::var("SOLVER_SHOW_THREADS")
                .ok()
                .and_then(|v| v.parse::<u32>().ok())
                .map(|t| (t + 31) / 32 * 32)
                .filter(|&t| (32..=1024).contains(&t)),
            bufs,
            bytes,
            reach_current: false,
            graphs: None,
            prof: None,
            spot,
            _ctx: ctx,
            stream,
            _module: module,
        })
    }

    /// Dynamic shared memory of the showdown kernel for traverser p.
    fn show_shared_bytes(max_sorted: &[usize; NP], p: usize) -> usize {
        let (q, r) = others(p);
        (3 * 2704 + 6 * max_sorted[q] + 5 * max_sorted[r]) * 4
    }

    pub fn device_bytes(&self) -> u64 {
        self.bytes.total()
    }

    /// Groups the subtrees below the first chance layer are swept in.
    pub fn num_groups(&self) -> usize {
        self.sweeps.len() - 1
    }

    pub fn describe(&self) -> String {
        let s = match self.storage {
            Storage::F32 => "f32",
            Storage::Compressed => "16-bit",
        };
        let groups = match self.num_groups() {
            0 | 1 => String::new(),
            g => format!(", {g} card groups"),
        };
        format!("CUDA, {s} arenas, {:.2} GB on the GPU{groups}", self.device_bytes() as f64 / 1e9)
    }

    /// Time every kernel (synchronizing around each launch; CUDA graphs
    /// are dropped while on). For tuning only.
    pub fn set_profiling(&mut self, on: bool) {
        self.prof = on.then(Default::default);
        self.graphs = None;
    }

    /// Kernel name, seconds and launches since profiling started, slowest
    /// first.
    pub fn profile(&self) -> Vec<(&'static str, f64, u64)> {
        let mut v: Vec<_> = match &self.prof {
            Some(p) => p.borrow().iter().map(|(&k, &(t, n))| (k, t, n)).collect(),
            None => Vec::new(),
        };
        v.sort_by(|a, b| b.1.total_cmp(&a.1));
        v
    }

    fn timed(&self, name: &'static str, f: impl FnOnce() -> Result<(), String>) -> Result<(), String> {
        let Some(prof) = &self.prof else { return f() };
        self.stream.synchronize().map_err(e)?;
        let t = std::time::Instant::now();
        f()?;
        self.stream.synchronize().map_err(e)?;
        let mut p = prof.borrow_mut();
        let x = p.entry(name).or_insert((0.0, 0));
        x.0 += t.elapsed().as_secs_f64();
        x.1 += 1;
        Ok(())
    }

    fn cfg(blocks: i32, shared: usize) -> LaunchConfig {
        LaunchConfig { grid_dim: (blocks as u32, 1, 1), block_dim: (BLOCK, 1, 1), shared_mem_bytes: shared as u32 }
    }

    fn p<T>(&self, s: &CudaSlice<T>) -> u64 {
        ptr(s, &self.stream)
    }

    fn copy_root(&self) -> Result<(), String> {
        let b = &self.bufs;
        let [nh0, nh1, nh2] = self.nh;
        self.timed("copy_root", || launch!(self.stream, &self.f_copy_root, Self::cfg(8, 0), [
            self.p(&b.weights[0]), self.p(&b.weights[1]), self.p(&b.weights[2]),
            self.p(&b.reach[0]), self.p(&b.reach[1]), self.p(&b.reach[2]), nh0, nh1, nh2,
        ]))
    }

    fn down_edges(&self, sp: Span, only: i32) -> Result<(), String> {
        if sp.count == 0 {
            return Ok(());
        }
        let b = &self.bufs;
        let [nh0, nh1, nh2] = self.nh;
        self.timed("down_chance", || launch!(self.stream, &self.f_down_chance, Self::cfg(sp.count, 0), [
            self.p(&b.edge_par), self.p(&b.edge_chi), self.p(&b.edge_card), sp.start, sp.count, only,
            self.p(&b.reach_slot[0]), self.p(&b.reach_slot[1]), self.p(&b.reach_slot[2]),
            self.p(&b.mask[0]), self.p(&b.mask[1]), self.p(&b.mask[2]),
            self.p(&b.reach[0]), self.p(&b.reach[1]), self.p(&b.reach[2]), nh0, nh1, nh2,
        ]))
    }

    /// Down sweep of one sweep. mode 0 uses current strategies, 1 average
    /// strategies. only >= 0 recomputes just that player's reach.
    fn down(&self, s: usize, mode: i32, only: i32) -> Result<(), String> {
        let b = &self.bufs;
        let [nh0, nh1, nh2] = self.nh;
        let reach = [self.p(&b.reach[0]), self.p(&b.reach[1]), self.p(&b.reach[2])];
        let null = 0u64;
        let sw = &self.sweeps[s];
        self.down_edges(sw.entry, only)?;
        for ls in &sw.levels {
            let sp = ls.action;
            if sp.count > 0 {
                match &b.arenas {
                    DevArenas::F32 { reg, str, prd } => {
                        let pr = |k: usize| prd.as_ref().map(|x| self.p(&x[k])).unwrap_or(null);
                        self.timed("down_action", || launch!(self.stream, &self.f_down_action, Self::cfg(sp.count, 0), [
                            self.p(&b.action), sp.start, sp.count, mode, only,
                            self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                            self.p(&b.children),
                            self.p(&b.reach_slot[0]), self.p(&b.reach_slot[1]), self.p(&b.reach_slot[2]),
                            self.p(&reg[0]), self.p(&reg[1]), self.p(&reg[2]),
                            pr(0), pr(1), pr(2),
                            self.p(&str[0]), self.p(&str[1]), self.p(&str[2]),
                            self.p(&b.lock_sigma), self.p(&b.lock_off),
                            reach[0], reach[1], reach[2], nh0, nh1, nh2,
                        ]))?;
                    }
                    DevArenas::Q { reg, str, prd, rsc, psc, .. } => {
                        let pr = |k: usize| prd.as_ref().map(|x| self.p(&x[k])).unwrap_or(null);
                        let ps = |k: usize| psc.as_ref().map(|x| self.p(&x[k])).unwrap_or(null);
                        self.timed("down_action_q", || launch!(self.stream, &self.f_down_action_q, Self::cfg(sp.count, 0), [
                            self.p(&b.action), sp.start, sp.count, mode, only,
                            self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                            self.p(&b.children),
                            self.p(&b.reach_slot[0]), self.p(&b.reach_slot[1]), self.p(&b.reach_slot[2]),
                            self.p(&reg[0]), self.p(&reg[1]), self.p(&reg[2]),
                            pr(0), pr(1), pr(2),
                            self.p(&str[0]), self.p(&str[1]), self.p(&str[2]),
                            self.p(&rsc[0]), self.p(&rsc[1]), self.p(&rsc[2]),
                            ps(0), ps(1), ps(2),
                            reach[0], reach[1], reach[2], nh0, nh1, nh2,
                        ]))?;
                    }
                }
            }
            self.down_edges(ls.edge, only)?;
        }
        Ok(())
    }

    /// Up sweep of one sweep for traverser p. mode 0: CFR update, 1: best
    /// response, 2: average strategy. The root's values end in cfv slot 0.
    fn up(&self, s: usize, p: usize, mode: i32) -> Result<(), String> {
        let b = &self.bufs;
        let (q, r) = others(p);
        let (pi, qi, ri) = (p as i32, q as i32, r as i32);
        let (nh_p, nh_q, nh_r, nh_max) = (self.nh[p], self.nh[q], self.nh[r], self.nh_max);
        let fold_shared = 2 * 2704 * 4;
        let show_shared = Self::show_shared_bytes(&self.max_sorted, p);
        // About one thread per hand of p, in whole warps (SOLVER_SHOW_THREADS
        // overrides, for tuning).
        let show_threads = self.show_threads.unwrap_or(((nh_p as u32 + 31) / 32 * 32).clamp(64, 512));
        let null = 0u64;
        for ls in self.sweeps[s].levels.iter().rev() {
            let sp = ls.fold;
            if sp.count > 0 {
                self.timed("up_fold", || launch!(self.stream, &self.f_up_fold, Self::cfg(sp.count, fold_shared), [
                    self.p(&b.fold), sp.start, sp.count, pi, qi, ri,
                    self.p(&b.node_class), self.p(&b.coef),
                    self.p(&b.reach_slot[q]), self.p(&b.reach_slot[r]),
                    self.p(&b.reach[q]), self.p(&b.reach[r]),
                    self.p(&b.c1[p]), self.p(&b.c2[p]), self.p(&b.c1[q]), self.p(&b.c2[q]),
                    self.p(&b.c1[r]), self.p(&b.c2[r]),
                    self.p(&b.same[p]),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_q, nh_r, nh_max,
                ]))?;
            }
            let sp = ls.show;
            if sp.count > 0 {
                let cfg = LaunchConfig {
                    grid_dim: (sp.count as u32, 1, 1),
                    block_dim: (show_threads, 1, 1),
                    shared_mem_bytes: show_shared as u32,
                };
                self.timed("up_show", || launch!(self.stream, &self.f_up_show, cfg, [
                    self.p(&b.show), sp.start, sp.count, pi, qi, ri,
                    self.p(&b.node_class), self.p(&b.coef), self.p(&b.node_river),
                    self.p(&b.reach_slot[q]), self.p(&b.reach_slot[r]),
                    self.p(&b.reach[q]), self.p(&b.reach[r]),
                    self.p(&b.srt_off[p]), self.p(&b.srt_str[p]), self.p(&b.srt_idx[p]),
                    self.p(&b.srt_off[q]), self.p(&b.srt_str[q]), self.p(&b.srt_idx[q]),
                    self.p(&b.srt_off[r]), self.p(&b.srt_str[r]), self.p(&b.srt_idx[r]),
                    self.p(&b.cpos_off[q]), self.p(&b.cpos[q]),
                    self.p(&b.cpos_off[r]), self.p(&b.cpos[r]),
                    self.p(&b.rank_pair),
                    self.p(&b.c1[p]), self.p(&b.c2[p]), self.p(&b.c1[q]), self.p(&b.c2[q]),
                    self.p(&b.c1[r]), self.p(&b.c2[r]),
                    self.p(&b.same[p]),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_q, nh_r, nh_max,
                ]))?;
            }
            let sp = ls.chance;
            if sp.count > 0 {
                self.timed("up_chance", || launch!(self.stream, &self.f_up_chance, Self::cfg(sp.count, 0), [
                    self.p(&b.chance), sp.start, sp.count,
                    self.p(&b.node_cs), self.p(&b.children), self.p(&b.node_cdiv), self.p(&b.mask[p]),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_max,
                ]))?;
            }
            let sp = ls.action;
            if sp.count > 0 {
                match &b.arenas {
                    DevArenas::F32 { reg, str, prd } => {
                        let prd = prd.as_ref().map(|x| self.p(&x[p])).unwrap_or(null);
                        self.timed("up_action", || launch!(self.stream, &self.f_up_action, Self::cfg(sp.count, 0), [
                            self.p(&b.action), sp.start, sp.count, pi, mode,
                            self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                            self.p(&b.children),
                            self.p(&reg[p]), prd, self.p(&str[p]),
                            self.p(&b.lock_sigma), self.p(&b.lock_off),
                            self.p(&b.reach_slot[p]), self.p(&b.reach[p]),
                            self.p(&b.disc),
                            self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_max,
                        ]))?;
                    }
                    DevArenas::Q { reg, str, prd, rsc, ssc, psc } => {
                        let prd = prd.as_ref().map(|x| self.p(&x[p])).unwrap_or(null);
                        let psc = psc.as_ref().map(|x| self.p(&x[p])).unwrap_or(null);
                        self.timed("up_action_q", || launch!(self.stream, &self.f_up_action_q, Self::cfg(sp.count, 0), [
                            self.p(&b.action), sp.start, sp.count, pi, mode,
                            self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                            self.p(&b.children),
                            self.p(&reg[p]), prd, self.p(&str[p]), self.p(&rsc[p]), psc, self.p(&ssc[p]),
                            self.p(&b.reach_slot[p]), self.p(&b.reach[p]),
                            self.p(&b.disc),
                            self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_max,
                        ]))?;
                    }
                }
            }
        }
        Ok(())
    }

    /// Group reaches persist between traversals only with a single group.
    fn groups_resident(&self) -> bool {
        self.sweeps.len() <= 2
    }

    /// Whole-tree down sweep for every player.
    fn down_all(&self, mode: i32) -> Result<(), String> {
        self.copy_root()?;
        for s in 0..self.sweeps.len() {
            self.down(s, mode, -1)?;
        }
        Ok(())
    }

    /// Traversal p of one iteration: refresh the reach of the player updated
    /// last, then the CFR up sweep (groups first, then the root part).
    fn traversal(&self, p: usize) -> Result<(), String> {
        let refresh = ((p + 2) % NP) as i32;
        self.down(0, 0, refresh)?;
        let group_only = if self.groups_resident() { refresh } else { -1 };
        for s in 1..self.sweeps.len() {
            self.down(s, 0, group_only)?;
            self.up(s, p, 0)?;
        }
        self.up(0, p, 0)
    }

    pub fn iterate(&mut self) -> Result<(), String> {
        self.iteration += 1;
        let d = Discounts::for_iteration(self.algo, self.iteration);
        self.stream
            .memcpy_htod(&[d.pos, d.neg, d.strat, f32::from_bits(self.iteration)], &mut self.bufs.disc)
            .map_err(e)?;
        if !self.reach_current {
            self.down_all(0)?;
            self.reach_current = true;
        }
        if self.graphs.is_none() && self.iteration > 1 && self.prof.is_none() {
            // The first iteration ran eagerly (module JIT, lazy loading);
            // capture the three traversals. Kernels read the discounts and
            // the iteration from device memory, so the graphs stay valid.
            let mut graphs = Vec::with_capacity(NP);
            for p in 0..NP {
                self.stream
                    .begin_capture(sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL)
                    .map_err(e)?;
                let res = self.traversal(p);
                let g = self
                    .stream
                    .end_capture(sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH)
                    .map_err(e)?;
                res?;
                graphs.push(g.ok_or("graph capture failed")?);
            }
            self.graphs = Some(graphs);
        }
        match &self.graphs {
            Some(gs) => {
                for g in gs {
                    g.launch().map_err(e)?;
                }
            }
            None => {
                for p in 0..NP {
                    self.traversal(p)?;
                }
            }
        }
        Ok(())
    }

    /// Waits for queued work.
    pub fn synchronize(&self) -> Result<(), String> {
        self.stream.synchronize().map_err(e)
    }

    fn root_values(&self, p: usize) -> Result<Vec<f32>, String> {
        let nh = self.nh[p] as usize;
        // The root is level 0, slot 0.
        let view = self.bufs.cfv.slice(0..nh);
        let mut out = vec![0f32; nh];
        self.stream.memcpy_dtoh(&view, &mut out).map_err(e)?;
        Ok(out)
    }

    /// Root values for traverser p under the average strategies (mode 1: p
    /// best responds, 2: p plays its average).
    fn eval_values(&self, p: usize, mode: i32) -> Result<Vec<f32>, String> {
        for s in 1..self.sweeps.len() {
            if !self.groups_resident() {
                self.down(s, 1, -1)?;
            }
            self.up(s, p, mode)?;
        }
        self.up(0, p, mode)?;
        self.root_values(p)
    }

    /// Root EVs and best-response gaps (chips) under the average strategy,
    /// computed on the device. Matches `MwSolver::exploitability`.
    pub fn exploitability(&mut self) -> Result<([f64; NP], [f64; NP]), String> {
        self.reach_current = false;
        self.copy_root()?;
        self.down(0, 1, -1)?;
        if self.groups_resident() {
            for s in 1..self.sweeps.len() {
                self.down(s, 1, -1)?;
            }
        }
        let denom = self.spot.root_triple_mass();
        let mut evs = [0f64; NP];
        let mut gaps = [0f64; NP];
        for p in 0..NP {
            let w = &self.spot.weights[p];
            let dot = |v: &[f32]| w.iter().zip(v).map(|(&a, &b)| a as f64 * b as f64).sum::<f64>() / denom;
            let br = dot(&self.eval_values(p, 1)?);
            let ev = dot(&self.eval_values(p, 2)?);
            evs[p] = ev;
            gaps[p] = (br - ev).max(0.0);
        }
        Ok((evs, gaps))
    }

    pub fn progress(&mut self, elapsed: f64) -> Result<MwProgress, String> {
        let (evs, gaps) = self.exploitability()?;
        let mean = gaps.iter().sum::<f64>() / NP as f64;
        Ok(MwProgress {
            iteration: self.iteration,
            gaps,
            evs,
            exploit_chips: mean,
            exploit_pct_pot: mean / self.spot.tree.config.starting_pot * 100.0,
            elapsed_secs: elapsed,
        })
    }

    /// Downloads the arenas into a CPU solver (same storage as the device)
    /// for queries, saves or further CPU iterations.
    pub fn to_cpu(&self) -> Result<MwSolver, String> {
        let mut s = MwSolver::new(self.spot.clone(), self.storage);
        s.algo = self.algo;
        s.iteration = self.iteration;
        let ds = self.spot.tree.data_size;
        let nn = self.spot.tree.nodes.len();
        let st = &self.stream;
        let mut preds: Option<[Store; NP]> = None;
        match &self.bufs.arenas {
            DevArenas::F32 { reg, str, prd } => {
                for p in 0..NP {
                    let len = ds[p] as usize;
                    if len == 0 {
                        continue;
                    }
                    for (dev, store) in [(&reg[p], &mut s.regrets[p]), (&str[p], &mut s.strat[p])] {
                        let Store::F32(buf) = store else { unreachable!() };
                        st.memcpy_dtoh(&dev.slice(0..len), buf.as_mut_slice()).map_err(e)?;
                    }
                }
                if let Some(pr) = prd {
                    let mut host: [Store; NP] = std::array::from_fn(|p| Store::f32(ds[p]));
                    for p in 0..NP {
                        let len = ds[p] as usize;
                        if len > 0 {
                            let Store::F32(buf) = &mut host[p] else { unreachable!() };
                            st.memcpy_dtoh(&pr[p].slice(0..len), buf.as_mut_slice()).map_err(e)?;
                        }
                    }
                    preds = Some(host);
                }
            }
            DevArenas::Q { reg, str, prd, rsc, ssc, psc } => {
                for p in 0..NP {
                    let len = ds[p] as usize;
                    let Store::I16 { q, scale } = &mut s.regrets[p] else { unreachable!() };
                    if len > 0 {
                        st.memcpy_dtoh(&reg[p].slice(0..len), q.as_mut_slice()).map_err(e)?;
                    }
                    st.memcpy_dtoh(&rsc[p].slice(0..nn), scale.as_mut_slice()).map_err(e)?;
                    let Store::U16 { q, scale } = &mut s.strat[p] else { unreachable!() };
                    if len > 0 {
                        st.memcpy_dtoh(&str[p].slice(0..len), q.as_mut_slice()).map_err(e)?;
                    }
                    st.memcpy_dtoh(&ssc[p].slice(0..nn), scale.as_mut_slice()).map_err(e)?;
                }
                if let (Some(pr), Some(ps)) = (prd, psc) {
                    let mut host: [Store; NP] = std::array::from_fn(|p| Store::i16(ds[p], nn));
                    for p in 0..NP {
                        let Store::I16 { q, scale } = &mut host[p] else { unreachable!() };
                        if ds[p] > 0 {
                            st.memcpy_dtoh(&pr[p].slice(0..ds[p] as usize), q.as_mut_slice()).map_err(e)?;
                        }
                        st.memcpy_dtoh(&ps[p].slice(0..nn), scale.as_mut_slice()).map_err(e)?;
                    }
                    preds = Some(host);
                }
            }
        }
        s.preds = preds.map(Box::new);
        Ok(s)
    }
}

/// Device arenas: zeros, or uploaded from a CPU solver (converted to the
/// device storage when the modes differ).
fn upload_arenas(
    stream: &Arc<CudaStream>,
    spot: &MwSpot,
    storage: Storage,
    algo: Algorithm,
    init: Option<&MwSolver>,
) -> Result<DevArenas, String> {
    let ds = spot.tree.data_size;
    let nn = spot.tree.nodes.len();
    let pcfr = algo == Algorithm::PcfrPlus;
    // which: 0 regrets, 1 strategy sums, 2 predictions
    let source = |p: usize, which: usize| -> Option<&Store> {
        let s = init?;
        match which {
            0 => Some(&s.regrets[p]),
            1 => Some(&s.strat[p]),
            _ => s.preds.as_ref().map(|pr| &pr[p]),
        }
    };
    match storage {
        Storage::F32 => {
            let arena = |p: usize, which: usize| -> Result<CudaSlice<f32>, String> {
                let len = ds[p] as usize;
                match source(p, which) {
                    None => upload::<f32>(stream, &[], len),
                    Some(store) => upload(stream, &store_to_f32(spot, p, store, len), len),
                }
            };
            let three = |which: usize| -> Result<[CudaSlice<f32>; NP], String> {
                Ok([arena(0, which)?, arena(1, which)?, arena(2, which)?])
            };
            Ok(DevArenas::F32 { reg: three(0)?, str: three(1)?, prd: if pcfr { Some(three(2)?) } else { None } })
        }
        Storage::Compressed => {
            let signed = |p: usize, which: usize| -> Result<(CudaSlice<i16>, CudaSlice<f32>), String> {
                let len = ds[p] as usize;
                match source(p, which) {
                    None => Ok((upload::<i16>(stream, &[], len)?, upload::<f32>(stream, &[], nn)?)),
                    Some(Store::I16 { q, scale }) => Ok((upload(stream, q.as_slice(), len)?, upload(stream, scale.as_slice(), nn)?)),
                    Some(store) => {
                        let (q, sc) = encode_signed(spot, p, store);
                        Ok((upload(stream, &q, len)?, upload(stream, &sc, nn)?))
                    }
                }
            };
            let unsigned = |p: usize| -> Result<(CudaSlice<u16>, CudaSlice<f32>), String> {
                let len = ds[p] as usize;
                match source(p, 1) {
                    None => Ok((upload::<u16>(stream, &[], len)?, upload::<f32>(stream, &[], nn)?)),
                    Some(Store::U16 { q, scale }) => Ok((upload(stream, q.as_slice(), len)?, upload(stream, scale.as_slice(), nn)?)),
                    Some(store) => {
                        let (q, sc) = encode_unsigned(spot, p, store);
                        Ok((upload(stream, &q, len)?, upload(stream, &sc, nn)?))
                    }
                }
            };
            let [r0, r1, r2] = [signed(0, 0)?, signed(1, 0)?, signed(2, 0)?];
            let [s0, s1, s2] = [unsigned(0)?, unsigned(1)?, unsigned(2)?];
            let (prd, psc) = if pcfr {
                let [p0, p1, p2] = [signed(0, 2)?, signed(1, 2)?, signed(2, 2)?];
                (Some([p0.0, p1.0, p2.0]), Some([p0.1, p1.1, p2.1]))
            } else {
                (None, None)
            };
            Ok(DevArenas::Q {
                reg: [r0.0, r1.0, r2.0],
                rsc: [r0.1, r1.1, r2.1],
                str: [s0.0, s1.0, s2.0],
                ssc: [s0.1, s1.1, s2.1],
                prd,
                psc,
            })
        }
    }
}

/// Decodes one player's arena into f32 (node by node for compressed stores).
fn store_to_f32(spot: &MwSpot, p: usize, store: &Store, len: usize) -> Vec<f32> {
    let mut out = vec![0f32; len];
    match store {
        Store::F32(b) => out[..b.len()].copy_from_slice(b.as_slice()),
        _ => for_nodes(spot, p, |i, off, k| unsafe { store.read_f32(i, off as u64, k, &mut out[off..off + k]) }),
    }
    out
}

fn for_nodes(spot: &MwSpot, p: usize, mut f: impl FnMut(u32, usize, usize)) {
    let nh = spot.hands[p].len();
    for (i, n) in spot.tree.nodes.iter().enumerate() {
        if n.kind == KIND_ACTION && n.player as usize == p {
            f(i as u32, n.data_offset as usize, n.num_children as usize * nh);
        }
    }
}

fn encode_signed(spot: &MwSpot, p: usize, store: &Store) -> (Vec<i16>, Vec<f32>) {
    let mut q = vec![0i16; spot.tree.data_size[p] as usize];
    let mut sc = vec![0f32; spot.tree.nodes.len()];
    let mut buf = Vec::new();
    for_nodes(spot, p, |i, off, k| {
        buf.resize(k, 0f32);
        unsafe { store.read_f32(i, off as u64, k, &mut buf) };
        sc[i as usize] = crate::store::encode_i16(&buf, &mut q[off..off + k]);
    });
    (q, sc)
}

fn encode_unsigned(spot: &MwSpot, p: usize, store: &Store) -> (Vec<u16>, Vec<f32>) {
    let mut q = vec![0u16; spot.tree.data_size[p] as usize];
    let mut sc = vec![0f32; spot.tree.nodes.len()];
    let mut buf = Vec::new();
    for_nodes(spot, p, |i, off, k| {
        buf.resize(k, 0f32);
        unsafe { store.read_f32(i, off as u64, k, &mut buf) };
        sc[i as usize] = crate::store::encode_u16(&buf, &mut q[off..off + k]);
    });
    (q, sc)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::multiway::{MwSpotConfig, MwTreeConfig};
    use crate::tree::parse_sizes;

    /// PTX compiles (needs libnvrtc, not a device).
    #[test]
    fn kernels_compile() {
        cudarc::nvrtc::compile_ptx_with_opts(
            include_str!("kernels.cu"),
            cudarc::nvrtc::CompileOptions { arch: Some("compute_86"), ..Default::default() },
        )
        .expect("multiway kernels compile");
    }

    const R0: &str = "AA,KK,QQ,JJ,TT,99,AK,AQ,KQ,QJ,JT,T9s,98s,87s,A5s";
    const R1: &str = "QQ-77,AQ,AJ,KQ,KJs,QJs,JTs,T9s,98s,A4s,A3s";
    const R2: &str = "AA-88,AK,AQ,AJs,KQs,KJs,QJs,JTs,65s,54s";

    fn spot(board: &str, stacks: [f64; 3], bets: &str, raises: &str, rake: f64) -> Arc<MwSpot> {
        let mut t = MwTreeConfig::uniform(30.0, stacks[0], &parse_sizes(bets).unwrap(), &parse_sizes(raises).unwrap());
        t.stacks = stacks;
        t.rake_pct = rake;
        t.rake_cap = if rake > 0.0 { 3.0 } else { 0.0 };
        let c = MwSpotConfig { board: board.into(), ranges: [R0, R1, R2].map(String::from), tree: t };
        Arc::new(MwSpot::new(c).unwrap())
    }

    fn opts(storage: Storage, group: Option<usize>) -> MwGpuOptions {
        MwGpuOptions { storage: Some(storage), budget_bytes: None, max_cards_per_group: group }
    }

    /// Device exploitability equals the CPU's on the downloaded arenas.
    fn assert_eval_matches(g: &mut MwGpuSolver, label: &str) {
        let tol = 2e-4 * g.spot.tree.config.starting_pot;
        let (ev_g, gap_g) = g.exploitability().unwrap();
        let (ev_c, gap_c) = g.to_cpu().unwrap().exploitability();
        for p in 0..NP {
            assert!((ev_g[p] - ev_c[p]).abs() < tol, "{label} ev p{p}: gpu {} cpu {}", ev_g[p], ev_c[p]);
            assert!((gap_g[p] - gap_c[p]).abs() < tol, "{label} gap p{p}: gpu {} cpu {}", gap_g[p], gap_c[p]);
        }
    }

    /// A CPU solver with random strategy sums (regrets zero).
    fn random_strategies(sp: &Arc<MwSpot>, seed: u64) -> MwSolver {
        let mut c = MwSolver::new(sp.clone(), Storage::F32);
        c.use_isomorphism = false;
        let mut x = 0x9E37_79B9_7F4A_7C15u64 ^ seed;
        for p in 0..NP {
            let Store::F32(b) = &mut c.strat[p] else { unreachable!() };
            for v in b.as_mut_slice() {
                x ^= x << 13;
                x ^= x >> 7;
                x ^= x << 17;
                *v = (x >> 40) as f32 / (1u64 << 24) as f32;
            }
        }
        c
    }

    fn eval_cases() -> Vec<Arc<MwSpot>> {
        vec![
            spot("9h9d8c8s", [60.0; 3], "75", "100", 0.0),
            spot("Ks9d4c7h", [20.0, 120.0, 60.0], "50 a", "a", 0.05),
            spot("Ks9d4c7h2s", [100.0; 3], "50 100", "100", 0.0),
            spot("QsQd3c3h", [100.0; 3], "33 a", "a", 0.05),
        ]
    }

    /// Terminal and traversal math alone: random strategy sums, then BR and
    /// EV values on both engines (no CFR dynamics involved), for every
    /// storage and with the river cards swept in groups.
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_eval_matches_cpu_random_strategies() {
        for (ci, sp) in eval_cases().into_iter().enumerate() {
            let c = random_strategies(&sp, ci as u64);
            let (ev_c, gap_c) = c.exploitability();
            let tol = 2e-4 * sp.tree.config.starting_pot;
            let mut g = MwGpuSolver::from_solver_with(&c, &opts(Storage::F32, None)).unwrap();
            let (ev_g, gap_g) = g.exploitability().unwrap();
            for p in 0..NP {
                assert!((ev_g[p] - ev_c[p]).abs() < tol, "case {ci} ev p{p}: gpu {} cpu {}", ev_g[p], ev_c[p]);
                assert!((gap_g[p] - gap_c[p]).abs() < tol, "case {ci} gap p{p}: gpu {} cpu {}", gap_g[p], gap_c[p]);
            }
            for (storage, group) in [(Storage::F32, Some(5)), (Storage::Compressed, None), (Storage::Compressed, Some(3))] {
                let mut g = MwGpuSolver::from_solver_with(&c, &opts(storage, group)).unwrap();
                let label = format!("case {ci} {storage:?} groups {}", g.num_groups());
                assert_eval_matches(&mut g, &label);
            }
        }
    }

    /// Iterations: for each storage and grouping, the device's
    /// exploitability matches the CPU's on its arenas, before and after
    /// further iterations (reach refresh after an evaluation), and the run
    /// tracks the CPU solver's convergence.
    fn check(sp: Arc<MwSpot>, algo: Algorithm, iters: u32) {
        let mut c = MwSolver::new(sp.clone(), Storage::F32);
        c.algo = algo;
        c.use_isomorphism = false;
        for _ in 0..iters {
            c.iterate();
        }
        let e_c = c.progress(0.0).exploit_pct_pot;
        for (storage, group) in [(Storage::F32, None), (Storage::F32, Some(4)), (Storage::Compressed, None), (Storage::Compressed, Some(4))] {
            let mut g = MwGpuSolver::with_options(sp.clone(), algo, &opts(storage, group)).unwrap();
            let label = format!("{algo:?} {storage:?} groups {}", g.num_groups());
            for _ in 0..iters {
                g.iterate().unwrap();
            }
            assert_eval_matches(&mut g, &label);
            let e_g = g.progress(0.0).unwrap().exploit_pct_pot;
            println!("{label}: gpu {e_g:.4}% cpu {e_c:.4}% after {iters}");
            // Same dynamics, different rounding: runs drift apart where regrets
            // are exactly zero, so only the convergence level is compared.
            assert!((e_g - e_c).abs() < 0.2 * e_c + 0.05, "{label}: gpu {e_g}% cpu {e_c}% pot");
            g.iterate().unwrap();
            assert_eval_matches(&mut g, &format!("{label} after eval"));
        }
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_river() {
        check(spot("Ks9d4c7h2s", [100.0; 3], "50 100", "100", 0.0), Algorithm::Dcfr, 30);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_turn_side_pots_rake() {
        check(spot("Ks9d4c7h", [20.0, 120.0, 60.0], "50 a", "a", 0.05), Algorithm::Dcfr, 30);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_turn_pcfr() {
        check(spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0), Algorithm::PcfrPlus, 30);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_paired_turn() {
        check(spot("9h9d8c8s", [60.0; 3], "75", "100", 0.0), Algorithm::Dcfr, 30);
    }

    /// Grouped sweeps do the same arithmetic as resident ones: first-iteration
    /// regrets agree to rounding (later iterations drift apart chaotically,
    /// like GPU and CPU runs, where regrets sit at exactly zero), and both
    /// runs converge alike.
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_groups_match_resident() {
        let sp = spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0);
        let mut a = MwGpuSolver::with_options(sp.clone(), Algorithm::Dcfr, &opts(Storage::F32, None)).unwrap();
        let mut b = MwGpuSolver::with_options(sp.clone(), Algorithm::Dcfr, &opts(Storage::F32, Some(3))).unwrap();
        assert!(a.num_groups() == 1 && b.num_groups() > 1);
        a.iterate().unwrap();
        b.iterate().unwrap();
        let (x, y) = (a.to_cpu().unwrap(), b.to_cpu().unwrap());
        for p in 0..NP {
            let (Store::F32(u), Store::F32(v)) = (&x.regrets[p], &y.regrets[p]) else { unreachable!() };
            let nh = sp.hands[p].len();
            for n in sp.tree.nodes.iter().filter(|n| n.kind == KIND_ACTION && n.player as usize == p) {
                let r = n.data_offset as usize..n.data_offset as usize + n.num_children as usize * nh;
                let (u, v) = (&u.as_slice()[r.clone()], &v.as_slice()[r]);
                let scale = u.iter().fold(1e-3f32, |m, x| m.max(x.abs()));
                for (s, t) in u.iter().zip(v) {
                    assert!((s - t).abs() <= 1e-4 * scale, "p{p} regret {s} vs {t} (node scale {scale})");
                }
            }
        }
        for _ in 1..150 {
            a.iterate().unwrap();
            b.iterate().unwrap();
        }
        let ea = a.progress(0.0).unwrap().exploit_pct_pot;
        let eb = b.progress(0.0).unwrap().exploit_pct_pot;
        assert!((ea - eb).abs() < 0.2 * ea.max(eb) + 0.02, "resident {ea}% vs grouped {eb}% pot");
    }

    /// Compressed arenas move between host and device unchanged.
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_compressed_round_trip() {
        let sp = spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0);
        let mut c = MwSolver::new(sp.clone(), Storage::Compressed);
        c.algo = Algorithm::PcfrPlus;
        for _ in 0..5 {
            c.iterate();
        }
        let g = MwGpuSolver::from_solver_with(&c, &opts(Storage::Compressed, Some(6))).unwrap();
        let d = g.to_cpu().unwrap();
        let same = |x: &Store, y: &Store| match (x, y) {
            (Store::I16 { q: a, scale: s }, Store::I16 { q: b, scale: t }) => a.as_slice() == b.as_slice() && s.as_slice() == t.as_slice(),
            (Store::U16 { q: a, scale: s }, Store::U16 { q: b, scale: t }) => a.as_slice() == b.as_slice() && s.as_slice() == t.as_slice(),
            _ => false,
        };
        for p in 0..NP {
            assert!(same(&c.regrets[p], &d.regrets[p]), "regrets p{p}");
            assert!(same(&c.strat[p], &d.strat[p]), "strat p{p}");
            assert!(same(&c.preds.as_ref().unwrap()[p], &d.preds.as_ref().unwrap()[p]), "preds p{p}");
        }
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_turn_converges() {
        let s = spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0);
        for (storage, group) in [(Storage::F32, None), (Storage::Compressed, Some(5))] {
            let mut g = MwGpuSolver::with_options(s.clone(), Algorithm::Dcfr, &opts(storage, group)).unwrap();
            for _ in 0..150 {
                g.iterate().unwrap();
            }
            let e = g.progress(0.0).unwrap().exploit_pct_pot;
            assert!(e < 1.0, "{storage:?}: gpu turn exploitability {e}% pot");
        }
    }

    /// A small flop: turn cards swept in groups on compressed arenas, the
    /// layout big trees use.
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_flop_grouped_compressed() {
        let sp = spot("Ks9d4c", [60.0; 3], "50", "a", 0.0);
        let mut g = MwGpuSolver::with_options(sp.clone(), Algorithm::Dcfr, &opts(Storage::Compressed, Some(8))).unwrap();
        println!("{}", g.describe());
        assert!(g.num_groups() > 1);
        for _ in 0..40 {
            g.iterate().unwrap();
        }
        assert_eval_matches(&mut g, "flop");
        let e = g.progress(0.0).unwrap().exploit_pct_pot;
        println!("flop after 40: {e:.3}% pot");
        assert!(e < 5.0, "flop exploitability {e}% pot");
    }

    /// Planning alone (no device): grouping kicks in under a small budget
    /// and fails cleanly under a tiny one.
    #[test]
    fn plan_groups_under_budget() {
        let sp = spot("Ks9d4c", [60.0; 3], "50", "a", 0.0);
        let layout = Layout::build(&sp).unwrap();
        let rivers = terminals(&sp, &layout).river_keys.len();
        let o = MwGpuOptions::default();
        let (full, min) = estimate_device_bytes(&sp, Algorithm::Dcfr);
        assert!(min < full);
        let (s, g, b) = choose(&sp, &layout, Algorithm::Dcfr, full, &o, rivers).unwrap();
        assert_eq!((s, g.len()), (Storage::F32, 1));
        assert!(b.total() <= full);
        let (s, g, b) = choose(&sp, &layout, Algorithm::Dcfr, min, &o, rivers).unwrap();
        println!("full {full}, min {min}: {s:?}, {} groups, {b:?}", g.len());
        assert!(g.len() > 1 && b.total() <= min, "{} groups, {} > {}", g.len(), b.total(), min);
        let plan = Plan::build(&sp, &layout, terminals(&sp, &layout), &g).unwrap();
        assert_eq!(plan.sweeps.len(), g.len() + 1);
        let c = MwGpuOptions { storage: Some(Storage::Compressed), ..Default::default() };
        let (_, g, b) = choose(&sp, &layout, Algorithm::Dcfr, min, &c, rivers).unwrap();
        assert!(b.total() <= min && g.len() <= 49);
        assert!(choose(&sp, &layout, Algorithm::Dcfr, min / 4, &o, rivers).is_err());
    }
}
