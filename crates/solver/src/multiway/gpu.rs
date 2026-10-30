//! CUDA three-player CFR: level-synchronous sweeps over the full public
//! tree with all arenas resident in VRAM (f32, no suit isomorphism).
//!
//! One iteration is three traversals. Before traversal p only the player
//! updated last, (p + 2) % 3, needs its reach recomputed; the up sweep then
//! evaluates terminals, chance averages and action nodes level by level.
//! Each traversal is captured into a CUDA graph after the first iteration.

use super::game::MwSpot;
use super::solver::{Dealt, MwProgress, MwSolver};
use super::tree::{others, payoff_table, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, NP};
use crate::cfr::{Algorithm, Discounts};
use crate::store::{Storage, Store};
use crate::tree::SENTINEL;
use cudarc::driver::{
    sys, CudaContext, CudaFunction, CudaGraph, CudaModule, CudaSlice, CudaStream, DevicePtr, LaunchConfig,
    PushKernelArg,
};
use std::collections::HashMap;
use std::sync::Arc;

const BLOCK: u32 = 128;
/// VRAM left free for the driver, graphs and fragmentation.
const HEADROOM: u64 = 384 << 20;

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

#[derive(Clone, Copy, Default)]
struct Span {
    start: i32,
    count: i32,
}

/// Host-side layout of the tree for the kernels.
struct Plan {
    num_levels: usize,
    action: Vec<u32>,
    action_spans: Vec<Span>,
    chance: Vec<u32>,
    chance_spans: Vec<Span>,
    edge_par: Vec<u32>,
    edge_chi: Vec<u32>,
    edge_card: Vec<u32>,
    edge_spans: Vec<Span>,
    fold: Vec<u32>,
    fold_spans: Vec<Span>,
    show: Vec<u32>,
    show_spans: Vec<Span>,
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
    // River boards by slot.
    srt_off: [Vec<u32>; NP],
    srt_str: [Vec<u32>; NP],
    srt_idx: [Vec<u32>; NP],
    cpos_off: [Vec<u32>; NP],
    cpos: [Vec<u32>; NP],
    rank_pair: Vec<u32>,
    max_sorted: [usize; NP],
}

impl Plan {
    fn build(spot: &MwSpot) -> Result<Plan, String> {
        let tree = &spot.tree;
        let nn = tree.nodes.len();
        let children_of = |n: usize, out: &mut Vec<(u32, u32)>| {
            out.clear();
            let node = &tree.nodes[n];
            match node.kind {
                KIND_ACTION => {
                    for a in 0..node.num_children as usize {
                        out.push((tree.child(node, a), u32::MAX));
                    }
                }
                KIND_CHANCE => {
                    for c in 0..52u32 {
                        let ch = tree.children[node.children_start as usize + c as usize];
                        if ch != SENTINEL {
                            out.push((ch, c));
                        }
                    }
                }
                _ => {}
            }
        };

        // Breadth-first order with levels; every node is reached once (the
        // tree is a tree).
        let mut level = vec![u32::MAX; nn];
        let mut dealt = vec![Dealt::default(); nn];
        let mut order: Vec<u32> = Vec::with_capacity(nn);
        level[0] = 0;
        order.push(0);
        let mut head = 0;
        let mut kids = Vec::new();
        let mut reach_slot: [Vec<u32>; NP] = std::array::from_fn(|_| vec![0u32; nn]);
        let mut reach_slots = [1usize; NP];
        let mut edge_lists: Vec<(u32, u32, u32, u32)> = Vec::new(); // (level, par, chi, card)
        while head < order.len() {
            let n = order[head] as usize;
            head += 1;
            children_of(n, &mut kids);
            let node = &tree.nodes[n];
            for &(c, card) in &kids {
                let c = c as usize;
                if level[c] != u32::MAX {
                    return Err("tree node reached twice".into());
                }
                level[c] = level[n] + 1;
                order.push(c as u32);
                if node.kind == KIND_CHANCE {
                    dealt[c] = dealt[n].push(card as u8);
                    for k in 0..NP {
                        reach_slot[k][c] = reach_slots[k] as u32;
                        reach_slots[k] += 1;
                    }
                    edge_lists.push((level[n], n as u32, c as u32, card));
                } else {
                    dealt[c] = dealt[n];
                    for k in 0..NP {
                        if node.kind == KIND_ACTION && node.player as usize == k {
                            reach_slot[k][c] = reach_slots[k] as u32;
                            reach_slots[k] += 1;
                        } else {
                            reach_slot[k][c] = reach_slot[k][n];
                        }
                    }
                }
            }
        }
        if order.len() != nn {
            return Err("tree has unreachable nodes".into());
        }
        let num_levels = level.iter().max().copied().unwrap_or(0) as usize + 1;

        // cfv slots: index within the level, halves alternate by parity.
        let mut width = vec![0u32; num_levels];
        let mut cfv_slot = vec![0u32; nn];
        for &n in &order {
            let l = level[n as usize] as usize;
            cfv_slot[n as usize] = width[l];
            width[l] += 1;
        }
        let w = *width.iter().max().unwrap() as usize;
        for n in 0..nn {
            if level[n] % 2 == 1 {
                cfv_slot[n] += w as u32;
            }
        }

        // Per-level work lists.
        let mut by_level: Vec<[Vec<u32>; 4]> = (0..num_levels).map(|_| Default::default()).collect();
        for &n in &order {
            let l = level[n as usize] as usize;
            let k = match tree.nodes[n as usize].kind {
                KIND_ACTION => 0,
                KIND_CHANCE => 1,
                KIND_TERM_FOLD => 2,
                KIND_TERM_SHOWDOWN => 3,
                _ => return Err("unknown node kind".into()),
            };
            by_level[l][k].push(n);
        }
        let flatten = |k: usize| -> (Vec<u32>, Vec<Span>) {
            let mut v = Vec::new();
            let mut spans = Vec::with_capacity(num_levels);
            for lv in &by_level {
                spans.push(Span { start: v.len() as i32, count: lv[k].len() as i32 });
                v.extend_from_slice(&lv[k]);
            }
            (v, spans)
        };
        let (action, action_spans) = flatten(0);
        let (chance, chance_spans) = flatten(1);
        let (fold, fold_spans) = flatten(2);
        let (show, show_spans) = flatten(3);
        edge_lists.sort_by_key(|x| x.0);
        let mut edge_spans = vec![Span::default(); num_levels];
        for (i, x) in edge_lists.iter().enumerate() {
            let s = &mut edge_spans[x.0 as usize];
            if s.count == 0 {
                s.start = i as i32;
            }
            s.count += 1;
        }

        // Per-node data.
        let cfg = &tree.config;
        let mut node_player = vec![-1i32; nn];
        let mut node_na = vec![0i32; nn];
        let mut node_off = vec![0u64; nn];
        let mut node_cs = vec![0u32; nn];
        let mut node_cdiv = vec![0f32; nn];
        let mut node_class = vec![-1i32; nn];
        let mut node_river = vec![-1i32; nn];
        let mut classes: HashMap<Vec<u32>, i32> = HashMap::new();
        let mut coef: Vec<f32> = Vec::new();
        let mut river_slots: HashMap<usize, i32> = HashMap::new();
        let mut river_keys: Vec<usize> = Vec::new();
        for (n, node) in tree.nodes.iter().enumerate() {
            node_cs[n] = node.children_start;
            match node.kind {
                KIND_ACTION => {
                    node_player[n] = node.player as i32;
                    node_na[n] = node.num_children as i32;
                    node_off[n] = node.data_offset;
                }
                KIND_CHANCE => node_cdiv[n] = 1.0 / (44 - node.street as i32) as f32,
                _ => {
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
                        let k = spot.river.key(dealt[n].as_slice());
                        let next = river_keys.len() as i32;
                        node_river[n] = *river_slots.entry(k).or_insert_with(|| {
                            river_keys.push(k);
                            next
                        });
                    }
                }
            }
        }

        // River boards.
        let mut srt_off: [Vec<u32>; NP] = Default::default();
        let mut srt_str: [Vec<u32>; NP] = Default::default();
        let mut srt_idx: [Vec<u32>; NP] = Default::default();
        let mut cpos_off: [Vec<u32>; NP] = Default::default();
        let mut cpos: [Vec<u32>; NP] = Default::default();
        let mut rank_pair = Vec::with_capacity(river_keys.len() * 2704);
        let mut max_sorted = [0usize; NP];
        for &key in &river_keys {
            let ev = spot.river.entries[key].as_deref().ok_or("river eval missing")?;
            rank_pair.extend_from_slice(&ev.rank_pair);
            for k in 0..NP {
                srt_off[k].push(srt_str[k].len() as u32);
                let list = &ev.sorted[k];
                max_sorted[k] = max_sorted[k].max(list.len());
                for &(s, i) in list {
                    srt_str[k].push(s);
                    srt_idx[k].push(i as u32);
                }
                for c in 0..52u8 {
                    cpos_off[k].push(cpos[k].len() as u32);
                    for (pos, &(_, i)) in list.iter().enumerate() {
                        let h = &spot.hands[k][i as usize];
                        if h.c1 == c || h.c2 == c {
                            cpos[k].push(pos as u32);
                        }
                    }
                }
                cpos_off[k].push(cpos[k].len() as u32);
            }
        }
        for k in 0..NP {
            srt_off[k].push(srt_str[k].len() as u32);
            // Kernels index cpos_off[slot * 53 + 52]; keep one dummy entry
            // so empty uploads stay valid.
            if cpos_off[k].is_empty() {
                cpos_off[k].push(0);
            }
            for v in [&mut srt_str[k], &mut srt_idx[k], &mut cpos[k]] {
                if v.is_empty() {
                    v.push(0);
                }
            }
        }
        if rank_pair.is_empty() {
            rank_pair.push(0);
        }
        if coef.is_empty() {
            coef.push(0.0);
        }

        Ok(Plan {
            num_levels,
            action,
            action_spans,
            chance,
            chance_spans,
            edge_par: edge_lists.iter().map(|x| x.1).collect(),
            edge_chi: edge_lists.iter().map(|x| x.2).collect(),
            edge_card: edge_lists.iter().map(|x| x.3).collect(),
            edge_spans,
            fold,
            fold_spans,
            show,
            show_spans,
            node_player,
            node_na,
            node_off,
            node_cs,
            node_cdiv,
            node_class,
            node_river,
            cfv_slot,
            cfv_slots: 2 * w,
            reach_slot,
            reach_slots,
            coef,
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

/// Device bytes a spot needs on the GPU (arenas, reach, values, tables).
pub fn estimate_device_bytes(spot: &MwSpot, algo: Algorithm) -> u64 {
    let arenas: u64 = spot.tree.data_size.iter().sum::<u64>() * if algo == Algorithm::PcfrPlus { 12 } else { 8 };
    // Rough non-arena share: reach + values + per-node data, measured on
    // turn trees at well under a quarter of the f32 arenas.
    arenas + arenas / 4 + spot.tree.nodes.len() as u64 * 64 + HEADROOM
}

pub struct MwGpuSolver {
    pub spot: Arc<MwSpot>,
    pub iteration: u32,
    pub algo: Algorithm,
    _ctx: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    _module: Arc<CudaModule>,
    f_copy_root: CudaFunction,
    f_down_action: CudaFunction,
    f_down_chance: CudaFunction,
    f_up_fold: CudaFunction,
    f_up_show: CudaFunction,
    f_up_chance: CudaFunction,
    f_up_action: CudaFunction,
    num_levels: usize,
    action_spans: Vec<Span>,
    chance_spans: Vec<Span>,
    edge_spans: Vec<Span>,
    fold_spans: Vec<Span>,
    show_spans: Vec<Span>,
    nh: [i32; NP],
    nh_max: i32,
    max_sorted: [usize; NP],
    /// Owned device buffers; kernels get raw pointers into them.
    bufs: Bufs,
    device_bytes: u64,
    /// Reach buffers hold current-strategy reaches for every player.
    reach_current: bool,
    graphs: Option<Vec<CudaGraph>>,
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
    disc: CudaSlice<f32>,
    regrets: [CudaSlice<f32>; NP],
    strat: [CudaSlice<f32>; NP],
    preds: Option<[CudaSlice<f32>; NP]>,
}

/// Raw device pointer of a buffer. Event tracking is disabled (everything
/// runs on one stream), so the guard carries no synchronization.
fn ptr<T>(s: &CudaSlice<T>, stream: &CudaStream) -> u64 {
    s.device_ptr(stream).0
}

impl MwGpuSolver {
    /// Fresh solver (zero regrets) for `spot`.
    pub fn new(spot: Arc<MwSpot>, algo: Algorithm) -> Result<MwGpuSolver, String> {
        Self::build(spot, algo, None)
    }

    /// Continue from a CPU solver's state (any storage; locks unsupported).
    pub fn from_solver(s: &MwSolver) -> Result<MwGpuSolver, String> {
        if !s.locks.is_empty() {
            return Err("the GPU solver does not support node locks yet".into());
        }
        let mut g = Self::build(s.spot.clone(), s.algo, Some(s))?;
        g.iteration = s.iteration;
        Ok(g)
    }

    fn build(spot: Arc<MwSpot>, algo: Algorithm, init: Option<&MwSolver>) -> Result<MwGpuSolver, String> {
        let plan = Plan::build(&spot)?;
        let ctx = CudaContext::new(0).map_err(e)?;
        let stream = ctx.new_stream().map_err(e)?;
        // One stream: cross-stream event tracking is unnecessary and its
        // events would break graph capture.
        unsafe { ctx.disable_event_tracking() };

        let nh: [usize; NP] = std::array::from_fn(|p| spot.hands[p].len());
        let nh_max = *nh.iter().max().unwrap();
        let ds = spot.tree.data_size;
        let arena_bytes: u64 = ds.iter().sum::<u64>() * 4 * if algo == Algorithm::PcfrPlus { 3 } else { 2 };
        let reach_bytes: u64 = (0..NP).map(|k| (plan.reach_slots[k] * nh[k] * 4) as u64).sum();
        let cfv_bytes = (plan.cfv_slots * nh_max * 4) as u64;
        let nn = spot.tree.nodes.len() as u64;
        let table_bytes = nn * 48
            + spot.tree.children.len() as u64 * 4
            + plan.rank_pair.len() as u64 * 4
            + (0..NP).map(|k| (plan.srt_str[k].len() * 8 + plan.cpos[k].len() * 4 + plan.cpos_off[k].len() * 4) as u64).sum::<u64>();
        let device_bytes = arena_bytes + reach_bytes + cfv_bytes + table_bytes;
        let (free, total) = ctx.mem_get_info().map_err(e)?;
        if device_bytes + HEADROOM > free as u64 {
            return Err(format!(
                "spot needs {:.2} GB of GPU memory ({:.2} GB arenas, {:.2} GB reach, {:.2} GB values); {:.2} of {:.2} GB free",
                device_bytes as f64 / 1e9,
                arena_bytes as f64 / 1e9,
                reach_bytes as f64 / 1e9,
                cfv_bytes as f64 / 1e9,
                free as f64 / 1e9,
                total as f64 / 1e9
            ));
        }

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
        let show_need = (0..NP).map(|p| Self::show_shared_bytes(&plan.max_sorted, p)).max().unwrap();
        if show_need > 48 * 1024 {
            f_up_show
                .set_attribute(
                    sys::CUfunction_attribute::CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES,
                    show_need as i32,
                )
                .map_err(|err| format!("showdown kernel needs {show_need} bytes of shared memory: {err:?}"))?;
        }

        let up32 = |v: &[u32]| stream.clone_htod(v).map_err(e);
        let upi = |v: &[i32]| stream.clone_htod(v).map_err(e);
        let up64 = |v: &[u64]| stream.clone_htod(v).map_err(e);
        let upf = |v: &[f32]| stream.clone_htod(v).map_err(e);
        let nonempty32 = |v: &[u32]| if v.is_empty() { vec![0u32] } else { v.to_vec() };

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

        let arena = |p: usize, which: usize| -> Result<CudaSlice<f32>, String> {
            let len = ds[p].max(1) as usize;
            match init {
                None => stream.alloc_zeros::<f32>(len).map_err(e),
                Some(s) => {
                    let store = match which {
                        0 => &s.regrets[p],
                        1 => &s.strat[p],
                        _ => match &s.preds {
                            Some(pr) => &pr[p],
                            None => return stream.alloc_zeros::<f32>(len).map_err(e),
                        },
                    };
                    let host = store_to_f32(&spot, p, store, len);
                    stream.clone_htod(&host).map_err(e)
                }
            }
        };
        let regrets = [arena(0, 0)?, arena(1, 0)?, arena(2, 0)?];
        let strat = [arena(0, 1)?, arena(1, 1)?, arena(2, 1)?];
        let preds = if algo == Algorithm::PcfrPlus { Some([arena(0, 2)?, arena(1, 2)?, arena(2, 2)?]) } else { None };

        let bufs = Bufs {
            action: up32(&nonempty32(&plan.action))?,
            chance: up32(&nonempty32(&plan.chance))?,
            edge_par: up32(&nonempty32(&plan.edge_par))?,
            edge_chi: up32(&nonempty32(&plan.edge_chi))?,
            edge_card: up32(&nonempty32(&plan.edge_card))?,
            fold: up32(&nonempty32(&plan.fold))?,
            show: up32(&nonempty32(&plan.show))?,
            node_player: upi(&plan.node_player)?,
            node_na: upi(&plan.node_na)?,
            node_off: up64(&plan.node_off)?,
            node_cs: up32(&plan.node_cs)?,
            node_cdiv: upf(&plan.node_cdiv)?,
            node_class: upi(&plan.node_class)?,
            node_river: upi(&plan.node_river)?,
            children: up32(&nonempty32(&spot.tree.children))?,
            cfv_slot: up32(&plan.cfv_slot)?,
            cfv: stream.alloc_zeros::<f32>(plan.cfv_slots * nh_max).map_err(e)?,
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
            lock_off: stream.clone_htod(&vec![-1i64; nn as usize]).map_err(e)?,
            lock_sigma: stream.alloc_zeros::<f32>(1).map_err(e)?,
            disc: stream.alloc_zeros::<f32>(3).map_err(e)?,
            regrets,
            strat,
            preds,
        };

        Ok(MwGpuSolver {
            iteration: 0,
            algo,
            f_copy_root: func("mw_copy_root")?,
            f_down_action: func("mw_down_action")?,
            f_down_chance: func("mw_down_chance")?,
            f_up_fold: func("mw_up_fold")?,
            f_up_show,
            f_up_chance: func("mw_up_chance")?,
            f_up_action: func("mw_up_action")?,
            num_levels: plan.num_levels,
            action_spans: plan.action_spans,
            chance_spans: plan.chance_spans,
            edge_spans: plan.edge_spans,
            fold_spans: plan.fold_spans,
            show_spans: plan.show_spans,
            nh: nh.map(|x| x as i32),
            nh_max: nh_max as i32,
            max_sorted: plan.max_sorted,
            bufs,
            device_bytes,
            reach_current: false,
            graphs: None,
            spot,
            _ctx: ctx,
            stream,
            _module: module,
        })
    }

    /// Dynamic shared memory of the showdown kernel for traverser p.
    fn show_shared_bytes(max_sorted: &[usize; NP], p: usize) -> usize {
        let (q, r) = others(p);
        (2 * 2704 + 4 * max_sorted[q] + 3 * max_sorted[r]) * 4
    }

    pub fn device_bytes(&self) -> u64 {
        self.device_bytes
    }

    fn cfg(blocks: i32, shared: usize) -> LaunchConfig {
        LaunchConfig { grid_dim: (blocks as u32, 1, 1), block_dim: (BLOCK, 1, 1), shared_mem_bytes: shared as u32 }
    }

    fn p<T>(&self, s: &CudaSlice<T>) -> u64 {
        ptr(s, &self.stream)
    }

    /// Down sweep. mode 0 uses current strategies, 1 average strategies.
    /// only >= 0 recomputes just that player's reach (root reach included).
    fn down(&self, mode: i32, only: i32) -> Result<(), String> {
        let b = &self.bufs;
        let [nh0, nh1, nh2] = self.nh;
        let reach = [self.p(&b.reach[0]), self.p(&b.reach[1]), self.p(&b.reach[2])];
        if only < 0 {
            launch!(self.stream, &self.f_copy_root, Self::cfg(8, 0), [
                self.p(&b.weights[0]), self.p(&b.weights[1]), self.p(&b.weights[2]),
                reach[0], reach[1], reach[2], nh0, nh1, nh2,
            ])?;
        }
        let null = 0u64;
        let preds = |k: usize| b.preds.as_ref().map(|pr| self.p(&pr[k])).unwrap_or(null);
        for l in 0..self.num_levels {
            let sp = self.action_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_down_action, Self::cfg(sp.count, 0), [
                    self.p(&b.action), sp.start, sp.count, mode, only,
                    self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                    self.p(&b.children),
                    self.p(&b.reach_slot[0]), self.p(&b.reach_slot[1]), self.p(&b.reach_slot[2]),
                    self.p(&b.regrets[0]), self.p(&b.regrets[1]), self.p(&b.regrets[2]),
                    preds(0), preds(1), preds(2),
                    self.p(&b.strat[0]), self.p(&b.strat[1]), self.p(&b.strat[2]),
                    self.p(&b.lock_sigma), self.p(&b.lock_off),
                    reach[0], reach[1], reach[2], nh0, nh1, nh2,
                ])?;
            }
            let sp = self.edge_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_down_chance, Self::cfg(sp.count, 0), [
                    self.p(&b.edge_par), self.p(&b.edge_chi), self.p(&b.edge_card), sp.start, sp.count, only,
                    self.p(&b.reach_slot[0]), self.p(&b.reach_slot[1]), self.p(&b.reach_slot[2]),
                    self.p(&b.mask[0]), self.p(&b.mask[1]), self.p(&b.mask[2]),
                    reach[0], reach[1], reach[2], nh0, nh1, nh2,
                ])?;
            }
        }
        Ok(())
    }

    /// Up sweep for traverser p. mode 0: CFR update, 1: best response,
    /// 2: average strategy. Leaves the root values in cfv slot 0.
    fn up(&self, p: usize, mode: i32) -> Result<(), String> {
        let b = &self.bufs;
        let (q, r) = others(p);
        let (pi, qi, ri) = (p as i32, q as i32, r as i32);
        let (nh_p, nh_q, nh_r, nh_max) = (self.nh[p], self.nh[q], self.nh[r], self.nh_max);
        let fold_shared = 2 * 2704 * 4;
        let show_shared = Self::show_shared_bytes(&self.max_sorted, p);
        let null = 0u64;
        let prd = b.preds.as_ref().map(|pr| self.p(&pr[p])).unwrap_or(null);
        for l in (0..self.num_levels).rev() {
            let sp = self.fold_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_up_fold, Self::cfg(sp.count, fold_shared), [
                    self.p(&b.fold), sp.start, sp.count, pi, qi, ri,
                    self.p(&b.node_class), self.p(&b.coef),
                    self.p(&b.reach_slot[q]), self.p(&b.reach_slot[r]),
                    self.p(&b.reach[q]), self.p(&b.reach[r]),
                    self.p(&b.c1[p]), self.p(&b.c2[p]), self.p(&b.c1[q]), self.p(&b.c2[q]),
                    self.p(&b.c1[r]), self.p(&b.c2[r]),
                    self.p(&b.same[p]),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_q, nh_r, nh_max,
                ])?;
            }
            let sp = self.show_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_up_show, Self::cfg(sp.count, show_shared), [
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
                ])?;
            }
            let sp = self.chance_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_up_chance, Self::cfg(sp.count, 0), [
                    self.p(&b.chance), sp.start, sp.count,
                    self.p(&b.node_cs), self.p(&b.children), self.p(&b.node_cdiv), self.p(&b.mask[p]),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_max,
                ])?;
            }
            let sp = self.action_spans[l];
            if sp.count > 0 {
                launch!(self.stream, &self.f_up_action, Self::cfg(sp.count, 0), [
                    self.p(&b.action), sp.start, sp.count, pi, mode,
                    self.p(&b.node_player), self.p(&b.node_na), self.p(&b.node_off), self.p(&b.node_cs),
                    self.p(&b.children),
                    self.p(&b.regrets[p]), prd, self.p(&b.strat[p]),
                    self.p(&b.lock_sigma), self.p(&b.lock_off),
                    self.p(&b.reach_slot[p]), self.p(&b.reach[p]),
                    self.p(&b.disc),
                    self.p(&b.cfv_slot), self.p(&b.cfv), nh_p, nh_max,
                ])?;
            }
        }
        Ok(())
    }

    /// Traversal p of one iteration: refresh the reach of the player updated
    /// last, then the CFR up sweep.
    fn traversal(&self, p: usize) -> Result<(), String> {
        self.down(0, ((p + 2) % NP) as i32)?;
        self.up(p, 0)
    }

    pub fn iterate(&mut self) -> Result<(), String> {
        self.iteration += 1;
        let d = Discounts::for_iteration(self.algo, self.iteration);
        self.stream.memcpy_htod(&[d.pos, d.neg, d.strat], &mut self.bufs.disc).map_err(e)?;
        if !self.reach_current {
            self.down(0, -1)?;
            self.reach_current = true;
        }
        if self.graphs.is_none() && self.iteration > 1 {
            // The first iteration ran eagerly (module JIT, lazy loading);
            // capture the three traversals. Kernels read the discounts from
            // device memory, so the graphs stay valid.
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

    /// Root EVs and best-response gaps (chips) under the average strategy,
    /// computed on the device. Matches `MwSolver::exploitability`.
    pub fn exploitability(&mut self) -> Result<([f64; NP], [f64; NP]), String> {
        self.down(1, -1)?;
        self.reach_current = false;
        let denom = self.spot.root_triple_mass();
        let mut evs = [0f64; NP];
        let mut gaps = [0f64; NP];
        for p in 0..NP {
            let w = &self.spot.weights[p];
            let dot = |v: &[f32]| w.iter().zip(v).map(|(&a, &b)| a as f64 * b as f64).sum::<f64>() / denom;
            self.up(p, 1)?;
            let br = dot(&self.root_values(p)?);
            self.up(p, 2)?;
            let ev = dot(&self.root_values(p)?);
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

    /// Downloads the arenas into a CPU solver (f32 storage) for queries,
    /// saves or further CPU iterations.
    pub fn to_cpu(&self) -> Result<MwSolver, String> {
        let mut s = MwSolver::new(self.spot.clone(), Storage::F32);
        s.algo = self.algo;
        s.iteration = self.iteration;
        let ds = self.spot.tree.data_size;
        for p in 0..NP {
            let len = ds[p] as usize;
            if len == 0 {
                continue;
            }
            for (dev, store) in [(&self.bufs.regrets[p], &mut s.regrets[p]), (&self.bufs.strat[p], &mut s.strat[p])] {
                let Store::F32(buf) = store else { unreachable!() };
                self.stream.memcpy_dtoh(&dev.slice(0..len), buf.as_mut_slice()).map_err(e)?;
            }
        }
        if let Some(pr) = &self.bufs.preds {
            let mut host: [Store; NP] = std::array::from_fn(|p| Store::f32(ds[p]));
            for p in 0..NP {
                let len = ds[p] as usize;
                if len > 0 {
                    let Store::F32(buf) = &mut host[p] else { unreachable!() };
                    self.stream.memcpy_dtoh(&pr[p].slice(0..len), buf.as_mut_slice()).map_err(e)?;
                }
            }
            s.preds = Some(Box::new(host));
        }
        Ok(s)
    }
}

/// Decodes one player's arena into f32 (node by node for compressed stores).
fn store_to_f32(spot: &MwSpot, p: usize, store: &Store, len: usize) -> Vec<f32> {
    let mut out = vec![0f32; len];
    match store {
        Store::F32(b) => out[..b.len()].copy_from_slice(b.as_slice()),
        _ => {
            let nh = spot.hands[p].len();
            for (i, n) in spot.tree.nodes.iter().enumerate() {
                if n.kind == KIND_ACTION && n.player as usize == p {
                    let k = n.num_children as usize * nh;
                    let off = n.data_offset as usize;
                    unsafe { store.read_f32(i as u32, n.data_offset, k, &mut out[off..off + k]) };
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::multiway::MwSpotConfig;
    use crate::tree::parse_sizes;
    use crate::multiway::MwTreeConfig;

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

    /// GPU iterations match full-traversal CPU iterations: strategies after a
    /// few iterations, and the device exploitability matches the CPU's on
    /// the downloaded arenas.
    fn check(spot: Arc<MwSpot>, algo: Algorithm, iters: u32) {
        let mut g = MwGpuSolver::new(spot.clone(), algo).expect("gpu init");
        let mut c = MwSolver::new(spot.clone(), Storage::F32);
        c.algo = algo;
        c.use_isomorphism = false;
        for _ in 0..iters {
            g.iterate().unwrap();
            c.iterate();
        }
        let d = g.to_cpu().unwrap();
        let mut worst = 0f32;
        for (i, n) in spot.tree.nodes.iter().enumerate() {
            if n.kind == KIND_ACTION && n.street == spot.tree.root_street {
                let x = d.average_strategy(i as u32);
                let y = c.average_strategy(i as u32);
                for (u, v) in x.iter().zip(&y) {
                    worst = worst.max((u - v).abs());
                }
            }
        }
        assert!(worst < 2e-3, "average strategies differ by {worst}");
        let (ev_g, gap_g) = g.exploitability().unwrap();
        let (ev_c, gap_c) = d.exploitability();
        for p in 0..NP {
            let tol = 1e-3 * spot.tree.config.starting_pot;
            assert!((ev_g[p] - ev_c[p]).abs() < tol, "ev p{p}: gpu {} cpu {}", ev_g[p], ev_c[p]);
            assert!((gap_g[p] - gap_c[p]).abs() < tol, "gap p{p}: gpu {} cpu {}", gap_g[p], gap_c[p]);
        }
        // Iterating after an evaluation keeps working (reach refresh).
        g.iterate().unwrap();
        c.iterate();
        let e_g = g.progress(0.0).unwrap().exploit_pct_pot;
        let e_c = c.progress(0.0).exploit_pct_pot;
        assert!((e_g - e_c).abs() < 0.05 * (1.0 + e_c), "after eval: gpu {e_g} cpu {e_c}");
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_river() {
        check(spot("Ks9d4c7h2s", [100.0; 3], "50 100", "100", 0.0), Algorithm::Dcfr, 3);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_turn_side_pots_rake() {
        check(spot("Ks9d4c7h", [20.0, 120.0, 60.0], "50 a", "a", 0.05), Algorithm::Dcfr, 3);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_turn_pcfr() {
        check(spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0), Algorithm::PcfrPlus, 3);
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_matches_cpu_paired_turn() {
        check(spot("9h9d8c8s", [60.0; 3], "75", "100", 0.0), Algorithm::Dcfr, 3);
    }

    /// Terminal and traversal math alone: random strategy sums, then BR and
    /// EV values on both engines (no CFR dynamics involved).
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_eval_matches_cpu_random_strategies() {
        let cases = [
            spot("9h9d8c8s", [60.0; 3], "75", "100", 0.0),
            spot("Ks9d4c7h", [20.0, 120.0, 60.0], "50 a", "a", 0.05),
            spot("Ks9d4c7h2s", [100.0; 3], "50 100", "100", 0.0),
            spot("QsQd3c3h", [100.0; 3], "33 a", "a", 0.05),
        ];
        for (ci, sp) in cases.into_iter().enumerate() {
            let mut c = MwSolver::new(sp.clone(), Storage::F32);
            c.use_isomorphism = false;
            let mut x = 0x9E37_79B9_7F4A_7C15u64 ^ ci as u64;
            for p in 0..NP {
                let Store::F32(b) = &mut c.strat[p] else { unreachable!() };
                for v in b.as_mut_slice() {
                    x ^= x << 13;
                    x ^= x >> 7;
                    x ^= x << 17;
                    *v = (x >> 40) as f32 / (1u64 << 24) as f32;
                }
            }
            let mut g = MwGpuSolver::from_solver(&c).unwrap();
            let (ev_g, gap_g) = g.exploitability().unwrap();
            let (ev_c, gap_c) = c.exploitability();
            for p in 0..NP {
                let tol = 2e-4 * sp.tree.config.starting_pot;
                assert!((ev_g[p] - ev_c[p]).abs() < tol, "case {ci} ev p{p}: gpu {} cpu {}", ev_g[p], ev_c[p]);
                assert!((gap_g[p] - gap_c[p]).abs() < tol, "case {ci} gap p{p}: gpu {} cpu {}", gap_g[p], gap_c[p]);
            }
        }
    }

    /// Dealt-card mask below the root for every node.
    fn dealt_masks(spot: &MwSpot) -> Vec<u64> {
        let mut m = vec![0u64; spot.tree.nodes.len()];
        for (i, n) in spot.tree.nodes.iter().enumerate() {
            match n.kind {
                KIND_ACTION => {
                    for a in 0..n.num_children as usize {
                        m[spot.tree.child(n, a) as usize] = m[i];
                    }
                }
                KIND_CHANCE => {
                    for c in 0..52usize {
                        let ch = spot.tree.children[n.children_start as usize + c];
                        if ch != SENTINEL {
                            m[ch as usize] = m[i] | 1u64 << c;
                        }
                    }
                }
                _ => {}
            }
        }
        m
    }

    /// Regrets and strategy sums of every unblocked hand after 1 and 2
    /// iterations, all streets. Prints the worst entry for diagnosis.
    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_arenas_match_cpu_early_iterations() {
        for (name, sp, algo) in [
            ("unpaired dcfr", spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0), Algorithm::Dcfr),
            ("paired dcfr", spot("9h9d8c8s", [60.0; 3], "75", "100", 0.0), Algorithm::Dcfr),
            ("unpaired pcfr", spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0), Algorithm::PcfrPlus),
        ] {
            let dm = dealt_masks(&sp);
            let mut g = MwGpuSolver::new(sp.clone(), algo).unwrap();
            let mut c = MwSolver::new(sp.clone(), Storage::F32);
            c.algo = algo;
            c.use_isomorphism = false;
            for it in 1..=2 {
                g.iterate().unwrap();
                c.iterate();
                let d = g.to_cpu().unwrap();
                for (which, label) in [(0, "regret"), (1, "strat")] {
                    let mut worst = (0f64, 0usize, 0usize, 0f32, 0f32);
                    for (i, n) in sp.tree.nodes.iter().enumerate() {
                        if n.kind != KIND_ACTION {
                            continue;
                        }
                        let p = n.player as usize;
                        let nh = sp.hands[p].len();
                        let k = n.num_children as usize * nh;
                        let (mut x, mut y) = (vec![0f32; k], vec![0f32; k]);
                        let (sx, sy) = if which == 0 { (&d.regrets[p], &c.regrets[p]) } else { (&d.strat[p], &c.strat[p]) };
                        unsafe {
                            sx.read_f32(i as u32, n.data_offset, k, &mut x);
                            sy.read_f32(i as u32, n.data_offset, k, &mut y);
                        }
                        for e in 0..k {
                            if sp.hands[p][e % nh].mask & dm[i] != 0 {
                                continue;
                            }
                            let rel = (x[e] - y[e]).abs() as f64 / (1.0 + y[e].abs() as f64);
                            if rel > worst.0 {
                                worst = (rel, i, e, x[e], y[e]);
                            }
                        }
                    }
                    let (rel, i, e, x, y) = worst;
                    let n = &sp.tree.nodes[i];
                    println!(
                        "{name} it {it} {label}: worst rel {rel:.3e} at node {i} (street {}, player {}, live {:b}, action {}, hand {}) gpu {x} cpu {y}",
                        n.street, n.player, n.live, e / sp.hands[n.player as usize].len(), e % sp.hands[n.player as usize].len()
                    );
                }
            }
        }
    }

    #[test]
    #[ignore = "needs a CUDA device"]
    fn gpu_turn_converges() {
        let s = spot("Ks9d4c7h", [90.0; 3], "66", "a", 0.0);
        let mut g = MwGpuSolver::new(s, Algorithm::Dcfr).unwrap();
        for _ in 0..150 {
            g.iterate().unwrap();
        }
        let e = g.progress(0.0).unwrap().exploit_pct_pot;
        assert!(e < 1.0, "gpu turn exploitability {e}% pot");
    }
}
