//! Aggregated flop reports: one traversal of a solved board that records, at
//! every action node, the pair-mass-weighted strategy, per-player EV / EQ /
//! EQR and (at the nodes people actually study) a hand-category breakdown.
//! Turn and river nodes are keyed by the LINE SHAPE — chance steps are
//! abstracted to `c` — and pooled over every card that can be dealt, so
//! "IP's first turn decision after check / bet 33% / call" is ONE entry per
//! board no matter which turn came. The REPORTS tab aggregates these entries
//! across boards at any node without re-solving (the full solves would be
//! gigabytes per board; these summaries are a couple of MB).
//!
//! Weighting is the pair mass (reach × card-removal-adjusted opponent mass)
//! everywhere: it is the probability the situation actually arises with the
//! hand, and the only weighting under which EV_OOP + EV_IP = pot.

use crate::cards::{rank, suit, Card};
use crate::cfr::Solver;
use crate::game::{fold_cfv, showdown_cfv, Dealt};
use crate::tree::{KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, SENTINEL};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

// ---------------------------------------------------------------------------
// Hand categories (mirrors web/js/classify.js — keep the two in lockstep)
// ---------------------------------------------------------------------------

pub const MADE: [&str; 17] = [
    "sf", "quads", "boat", "flush", "straight", "set", "trips", "two_pair", "overpair",
    "top_pair", "underpair", "second_pair", "third_pair", "weak_pair", "ace_high",
    "king_high", "no_made",
];
pub const DRAW: [&str; 8] =
    ["combo", "nut_fd", "fd", "oesd", "gutshot", "bdfd2", "bdfd1", "no_draw"];
pub const EQA: [&str; 7] = ["eqa_90", "eqa_80", "eqa_70", "eqa_60", "eqa_50", "eqa_25", "eqa_0"];

fn has_straight(rank_mask: u32) -> bool {
    let m = (rank_mask << 1) | ((rank_mask >> 12) & 1); // ace low
    let mut run = 0;
    for i in 0..14 {
        if m & (1 << i) != 0 {
            run += 1;
            if run >= 5 {
                return true;
            }
        } else {
            run = 0;
        }
    }
    false
}

/// (made, draw) category indices of a hand on `board` (all cards dealt so
/// far). Exactly classify.js's rules.
pub fn classify(board: &[Card], c1: Card, c2: Card) -> (u8, u8) {
    let hr = [rank(c1) as usize, rank(c2) as usize];
    let hs = [suit(c1), suit(c2)];
    let pocket = hr[0] == hr[1];
    let mut all: Vec<Card> = board.to_vec();
    all.push(c1);
    all.push(c2);

    let mut cnt_all = [0u8; 13];
    let mut cnt_board = [0u8; 13];
    let (mut mask_all, mut mask_board) = (0u32, 0u32);
    for &c in board {
        cnt_board[rank(c) as usize] += 1;
        mask_board |= 1 << rank(c);
    }
    for &c in &all {
        cnt_all[rank(c) as usize] += 1;
        mask_all |= 1 << rank(c);
    }
    let mut suit_all = [0u8; 4];
    for &c in &all {
        suit_all[suit(c) as usize] += 1;
    }
    let board_top = board.iter().map(|&c| rank(c) as usize).max().unwrap_or(0);
    // distinct board ranks, descending
    let mut board_ranks: Vec<usize> = board.iter().map(|&c| rank(c) as usize).collect();
    board_ranks.sort_unstable_by(|a, b| b.cmp(a));
    board_ranks.dedup();

    let mut made: Option<&str> = None;
    let mut flush_suit: i32 = -1;
    for s in 0..4 {
        if suit_all[s] >= 5 {
            flush_suit = s as i32;
        }
    }
    if flush_suit >= 0 {
        let mut sf_mask = 0u32;
        for &c in &all {
            if suit(c) as i32 == flush_suit {
                sf_mask |= 1 << rank(c);
            }
        }
        if has_straight(sf_mask) {
            made = Some("sf");
        }
    }
    let quad = cnt_all.iter().position(|&n| n == 4);
    let mut trip_ranks: Vec<usize> = Vec::new();
    let mut pair_ranks: Vec<usize> = Vec::new();
    for r in (0..13).rev() {
        if cnt_all[r] == 3 {
            trip_ranks.push(r);
        }
        if cnt_all[r] == 2 {
            pair_ranks.push(r);
        }
    }
    if made.is_none() && quad.is_some() {
        made = Some("quads");
    }
    if made.is_none() && !trip_ranks.is_empty() && (trip_ranks.len() > 1 || !pair_ranks.is_empty())
    {
        made = Some("boat");
    }
    if made.is_none() && flush_suit >= 0 {
        made = Some("flush");
    }
    if made.is_none() && has_straight(mask_all) {
        made = Some("straight");
    }
    if made.is_none() && !trip_ranks.is_empty() {
        let r = trip_ranks[0];
        if cnt_board[r] < 3 {
            made = Some(if pocket && hr[0] == r { "set" } else { "trips" });
        }
    }
    if made.is_none() {
        let hole_pairs: Vec<usize> = pair_ranks
            .iter()
            .copied()
            .filter(|&r| (hr[0] == r || hr[1] == r) && cnt_board[r] < 2)
            .collect();
        if hole_pairs.len() >= 2 {
            made = Some("two_pair");
        } else if hole_pairs.len() == 1 || (pocket && cnt_board[hr[0]] == 0) {
            if pocket {
                made = Some(if hr[0] > board_top { "overpair" } else { "underpair" });
            } else {
                let r = hole_pairs[0];
                let pos = board_ranks.iter().position(|&x| x == r);
                made = Some(match pos {
                    Some(0) => "top_pair",
                    Some(1) => "second_pair",
                    Some(2) => "third_pair",
                    _ => "weak_pair",
                });
            }
        }
    }
    let made = made.unwrap_or_else(|| {
        let hi = hr[0].max(hr[1]);
        if hi == 12 {
            "ace_high"
        } else if hi == 11 {
            "king_high"
        } else {
            "no_made"
        }
    });

    let mut draw = "no_draw";
    if board.len() < 5 {
        let strong = matches!(made, "sf" | "quads" | "boat" | "flush" | "straight");
        let mut fd_suit: i32 = -1;
        for s in 0..4u8 {
            let hole_of = (hs[0] == s) as u8 + (hs[1] == s) as u8;
            if suit_all[s as usize] == 4 && hole_of >= 1 {
                fd_suit = s as i32;
            }
        }
        let mut outs = 0;
        if !strong && made != "straight" {
            for r in 0..13 {
                let with_r = mask_all | (1 << r);
                let board_with_r = mask_board | (1 << r);
                if has_straight(with_r) && !has_straight(board_with_r) {
                    outs += 1;
                }
            }
        }
        let nut_fd = if fd_suit < 0 {
            false
        } else {
            let fs = fd_suit as u8;
            let mut res = false;
            for r in (0..13).rev() {
                let on_board = board.iter().any(|&c| suit(c) == fs && rank(c) as usize == r);
                if on_board {
                    continue;
                }
                res = (hs[0] == fs && hr[0] == r) || (hs[1] == fs && hr[1] == r);
                break;
            }
            res
        };
        if strong {
            draw = "no_draw";
        } else if fd_suit >= 0 && outs >= 1 {
            draw = "combo";
        } else if nut_fd {
            draw = "nut_fd";
        } else if fd_suit >= 0 {
            draw = "fd";
        } else if outs >= 2 {
            draw = "oesd";
        } else if outs == 1 {
            draw = "gutshot";
        } else if board.len() == 3 {
            for s in 0..4u8 {
                let hole_of = (hs[0] == s) as u8 + (hs[1] == s) as u8;
                if suit_all[s as usize] == 3 && hole_of == 2 {
                    draw = "bdfd2";
                    break;
                }
                if suit_all[s as usize] == 3 && hole_of == 1 {
                    draw = "bdfd1";
                }
            }
        }
    }
    let mi = MADE.iter().position(|&m| m == made).unwrap() as u8;
    let di = DRAW.iter().position(|&d| d == draw).unwrap() as u8;
    (mi, di)
}

fn eqa_bucket(eq: f32) -> usize {
    if eq >= 0.9 {
        0
    } else if eq >= 0.8 {
        1
    } else if eq >= 0.7 {
        2
    } else if eq >= 0.6 {
        3
    } else if eq >= 0.5 {
        4
    } else if eq >= 0.25 {
        5
    } else {
        6
    }
}

// ---------------------------------------------------------------------------
// Output types (what a per-board report file holds)
// ---------------------------------------------------------------------------

/// One hand category's share of a player's range at a node, with its
/// pair-mass-weighted EV / EQ and (actor only) action frequencies.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatStat {
    pub w: f32,
    pub ev: f32,
    pub eq: f32,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub freqs: Vec<f32>,
}

/// Category breakdowns, indexed like `MADE` / `DRAW` / `EQA`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CatBreakdown {
    pub made: Vec<CatStat>,
    pub draw: Vec<CatStat>,
    pub eqa: Vec<CatStat>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlayerStat {
    /// Pair mass at this node (Σ reach × valid): how much of the situation
    /// this player's range represents; the weight for cross-board pooling.
    pub w: f32,
    pub ev: f32,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub eq: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub eqr: Option<f32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cats: Option<CatBreakdown>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LineSummary {
    /// "action" | "chance" | "terminal_fold" | "terminal_showdown"
    pub kind: String,
    pub street: u8,
    pub pot: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub actor: Option<u8>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub actions: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub kinds: Vec<String>,
    /// Actor's pair-mass-weighted action frequencies.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub freqs: Vec<f32>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub players: Vec<PlayerStat>,
}

// ---------------------------------------------------------------------------
// Accumulators (pooled over cards for turn/river shapes)
// ---------------------------------------------------------------------------

#[derive(Clone, Default)]
struct Acc1 {
    w: f64,
    wev: f64,
    weq: f64,
    fsum: Vec<f64>,
}

#[derive(Clone, Default)]
struct PAcc {
    w: f64,
    wev: f64,
    weq: f64,
    has_eq: bool,
    cats: Option<[Vec<Acc1>; 3]>,
}

#[derive(Clone)]
struct LineAcc {
    kind: &'static str,
    street: u8,
    pot: f64,
    actor: Option<u8>,
    actions: Vec<String>,
    kinds: Vec<String>,
    fsum: Vec<f64>,
    fw: f64,
    players: [PAcc; 2],
}

fn merge_acc1(a: &mut Acc1, b: &Acc1) {
    a.w += b.w;
    a.wev += b.wev;
    a.weq += b.weq;
    if a.fsum.len() < b.fsum.len() {
        a.fsum.resize(b.fsum.len(), 0.0);
    }
    for (x, y) in a.fsum.iter_mut().zip(&b.fsum) {
        *x += y;
    }
}

fn merge_line(a: &mut LineAcc, b: &LineAcc) {
    for (x, y) in a.fsum.iter_mut().zip(&b.fsum) {
        *x += y;
    }
    a.fw += b.fw;
    for p in 0..2 {
        let (pa, pb) = (&mut a.players[p], &b.players[p]);
        pa.w += pb.w;
        pa.wev += pb.wev;
        pa.weq += pb.weq;
        pa.has_eq |= pb.has_eq;
        match (&mut pa.cats, &pb.cats) {
            (Some(ca), Some(cb)) => {
                for d in 0..3 {
                    for (x, y) in ca[d].iter_mut().zip(&cb[d]) {
                        merge_acc1(x, y);
                    }
                }
            }
            (None, Some(cb)) => pa.cats = Some(cb.clone()),
            _ => {}
        }
    }
}

fn merge_maps(into: &mut BTreeMap<String, LineAcc>, from: BTreeMap<String, LineAcc>) {
    for (k, v) in from {
        match into.get_mut(&k) {
            Some(a) => merge_line(a, &v),
            None => {
                into.insert(k, v);
            }
        }
    }
}

fn r4(x: f64) -> f32 {
    ((x * 1e4).round() / 1e4) as f32
}

fn finish(acc: LineAcc) -> LineSummary {
    let players = if acc.kind == "action" || acc.kind == "chance" {
        acc.players
            .iter()
            .map(|pa| {
                let ev = if pa.w > 1e-12 { pa.wev / pa.w } else { 0.0 };
                let eq = if pa.has_eq && pa.w > 1e-12 { Some(pa.weq / pa.w) } else { None };
                let eqr = eq.filter(|&e| e > 0.02).map(|e| ev / (acc.pot * e));
                let cats = pa.cats.as_ref().map(|c| {
                    let conv = |v: &Vec<Acc1>| -> Vec<CatStat> {
                        v.iter()
                            .map(|a| CatStat {
                                w: r4(a.w),
                                ev: if a.w > 1e-12 { r4(a.wev / a.w) } else { 0.0 },
                                eq: if a.w > 1e-12 { r4(a.weq / a.w) } else { 0.0 },
                                freqs: a
                                    .fsum
                                    .iter()
                                    .map(|&f| if a.w > 1e-12 { r4(f / a.w) } else { 0.0 })
                                    .collect(),
                            })
                            .collect()
                    };
                    CatBreakdown { made: conv(&c[0]), draw: conv(&c[1]), eqa: conv(&c[2]) }
                });
                PlayerStat {
                    w: r4(pa.w),
                    ev: r4(ev),
                    eq: eq.map(r4),
                    eqr: eqr.map(r4),
                    cats,
                }
            })
            .collect()
    } else {
        Vec::new()
    };
    LineSummary {
        kind: acc.kind.to_string(),
        street: acc.street,
        pot: acc.pot,
        actor: acc.actor,
        actions: acc.actions,
        kinds: acc.kinds,
        freqs: acc
            .fsum
            .iter()
            .map(|&f| if acc.fw > 1e-12 { r4(f / acc.fw) } else { 0.0 })
            .collect(),
        players,
    }
}

/// Which nodes are written, by street and by how many actions into the
/// street the node sits (0 = the street's first decision): flop and turn
/// nodes all, river nodes up to the first response. Category breakdowns
/// (the expensive part: an equity pass + classification per player) go on
/// every flop node, the turn's first decision + responses, and the river's
/// first decision.
const RECORD_DEPTH: [u8; 3] = [255, 255, 1];
const FULL_DEPTH: [u8; 3] = [255, 1, 0];

/// Per-hand (made, draw) categories on one board, for both players.
struct BoardCats {
    cats: [Vec<(u8, u8)>; 2],
}

impl Solver {
    /// Line summaries for every recorded node of this solved board (see the
    /// module docs). Call `ensure_symmetric()` first so every card branch —
    /// not only the orbit representatives — carries its strategy.
    pub fn report_lines(&self) -> BTreeMap<String, LineSummary> {
        let spot = &*self.spot;
        let reach: [Vec<f32>; 2] = [spot.weights[0].clone(), spot.weights[1].clone()];
        let cats = self.board_cats(Dealt::default());
        let mut out = BTreeMap::new();
        self.sweep(0, [&reach[0], &reach[1]], Dealt::default(), "", 0, &cats, &mut out);
        out.into_iter().map(|(k, v)| (k, finish(v))).collect()
    }

    fn board_cats(&self, dealt: Dealt) -> BoardCats {
        let spot = &*self.spot;
        let mut board: Vec<Card> = spot.board.clone();
        for i in 0..dealt.len as usize {
            board.push(dealt.cards[i]);
        }
        let cats = [0usize, 1].map(|p| {
            spot.hands[p].iter().map(|h| classify(&board, h.c1, h.c2)).collect()
        });
        BoardCats { cats }
    }

    /// Both players' counterfactual values below `node_idx` under the average
    /// strategies (the `traverse_avg` convention: per-hand cfv normalized by
    /// the opponent's valid mass gives the pot-share EV), recording summaries
    /// on the way. Line keys: `a<i>` per action step, `c` per chance step.
    fn sweep(
        &self,
        node_idx: u32,
        reach: [&[f32]; 2],
        dealt: Dealt,
        key: &str,
        since_chance: u8,
        cats: &BoardCats,
        out: &mut BTreeMap<String, LineAcc>,
    ) -> [Vec<f32>; 2] {
        let spot = &*self.spot;
        let node = &spot.tree.nodes[node_idx as usize];
        let nh = [spot.hands[0].len(), spot.hands[1].len()];
        // a chance node's `street` is the one being dealt INTO; the actions
        // that led to it were on the previous street, whose cap applies
        let street = if node.kind == KIND_CHANCE {
            (node.street as usize).saturating_sub(1)
        } else {
            node.street as usize
        };
        let record = since_chance <= RECORD_DEPTH[street.min(2)];
        let full = since_chance <= FULL_DEPTH[street.min(2)];
        let pot = node.put[0] + node.put[1];

        match node.kind {
            KIND_TERM_FOLD | KIND_TERM_SHOWDOWN => {
                let mut cfv = [vec![0f32; nh[0]], vec![0f32; nh[1]]];
                for p in 0..2 {
                    if node.kind == KIND_TERM_FOLD {
                        let amount =
                            if node.player as usize == p { node.t_lose } else { node.t_win } as f32;
                        fold_cfv(
                            &spot.hands[p],
                            &spot.hands[1 - p],
                            reach[1 - p],
                            &spot.same_combo[p],
                            amount,
                            &mut cfv[p],
                        );
                    } else {
                        showdown_cfv(
                            spot.river.get(&dealt),
                            p,
                            &spot.hands[p],
                            &spot.hands[1 - p],
                            reach[1 - p],
                            &spot.same_combo[p],
                            node.t_win as f32,
                            node.t_lose as f32,
                            node.t_tie as f32,
                            &mut cfv[p],
                        );
                    }
                }
                if record {
                    let kind = if node.kind == KIND_TERM_FOLD {
                        "terminal_fold"
                    } else {
                        "terminal_showdown"
                    };
                    out.entry(key.to_string()).or_insert_with(|| LineAcc {
                        kind,
                        street: node.street,
                        pot,
                        actor: None,
                        actions: Vec::new(),
                        kinds: Vec::new(),
                        fsum: Vec::new(),
                        fw: 0.0,
                        players: [PAcc::default(), PAcc::default()],
                    });
                }
                cfv
            }
            KIND_CHANCE => {
                let divisor = (46 - node.street as i32) as f32;
                let mut cards: Vec<Card> = Vec::new();
                for c in 0..52u8 {
                    if spot.tree.children[node.children_start as usize + c as usize] != SENTINEL
                        && !dealt.contains(c)
                    {
                        cards.push(c);
                    }
                }
                let child_key = format!("{key}{}c", if key.is_empty() { "" } else { "," });
                let run = |&c: &Card| -> ([Vec<f32>; 2], BTreeMap<String, LineAcc>) {
                    let child = spot.tree.children[node.children_start as usize + c as usize];
                    let cm = 1u64 << c;
                    let r: [Vec<f32>; 2] = [0usize, 1].map(|p| {
                        spot.hands[p]
                            .iter()
                            .zip(reach[p])
                            .map(|(h, &x)| if h.mask & cm != 0 { 0.0 } else { x })
                            .collect()
                    });
                    let d2 = dealt.push(c);
                    let bc = self.board_cats(d2);
                    let mut local = BTreeMap::new();
                    let mut cfv =
                        self.sweep(child, [&r[0], &r[1]], d2, &child_key, 0, &bc, &mut local);
                    // a hand holding the dealt card does not exist on this
                    // runout: its value here is zero (as in chance_node)
                    for p in 0..2 {
                        for (i, h) in spot.hands[p].iter().enumerate() {
                            if h.mask & cm != 0 {
                                cfv[p][i] = 0.0;
                            }
                        }
                    }
                    (cfv, local)
                };
                // parallel when the children open a betting round (the same
                // rule as the CFR traversal); bare runouts stay sequential
                let parallel = cards.first().map_or(false, |&c| {
                    let child = spot.tree.children[node.children_start as usize + c as usize];
                    spot.tree.nodes[child as usize].kind == KIND_ACTION
                });
                let results: Vec<([Vec<f32>; 2], BTreeMap<String, LineAcc>)> = if parallel {
                    cards.par_iter().map(run).collect()
                } else {
                    cards.iter().map(run).collect()
                };
                let mut cfv = [vec![0f32; nh[0]], vec![0f32; nh[1]]];
                for (ccfv, local) in results {
                    for p in 0..2 {
                        for i in 0..nh[p] {
                            cfv[p][i] += ccfv[p][i];
                        }
                    }
                    merge_maps(out, local);
                }
                let inv = 1.0 / divisor;
                for p in 0..2 {
                    for x in cfv[p].iter_mut() {
                        *x *= inv;
                    }
                }
                if record {
                    // EV going INTO the street, for the ribbon
                    let mut acc = LineAcc {
                        kind: "chance",
                        street: node.street,
                        pot,
                        actor: None,
                        actions: Vec::new(),
                        kinds: Vec::new(),
                        fsum: Vec::new(),
                        fw: 0.0,
                        players: [PAcc::default(), PAcc::default()],
                    };
                    for p in 0..2 {
                        let valid = self.valid_opp_sum(p, reach[1 - p]);
                        let pa = &mut acc.players[p];
                        for i in 0..nh[p] {
                            if valid[i] > 1e-9 && reach[p][i] > 0.0 {
                                let w = reach[p][i] as f64 * valid[i];
                                let ev = cfv[p][i] as f64 / valid[i] + node.put[p];
                                pa.w += w;
                                pa.wev += w * ev;
                            }
                        }
                    }
                    match out.get_mut(key) {
                        Some(a) => merge_line(a, &acc),
                        None => {
                            out.insert(key.to_string(), acc);
                        }
                    }
                }
                cfv
            }
            KIND_ACTION => {
                let q = node.player as usize;
                let o = 1 - q;
                let na = node.num_children as usize;
                let sigma = self.average_strategy(node_idx, node);
                let mut cfv = [vec![0f32; nh[0]], vec![0f32; nh[1]]];
                let mut rq = vec![0f32; nh[q]];
                for a in 0..na {
                    let sig = &sigma[a * nh[q]..(a + 1) * nh[q]];
                    for i in 0..nh[q] {
                        rq[i] = reach[q][i] * sig[i];
                    }
                    let child = spot.tree.children[node.children_start as usize + a];
                    let child_key = format!("{key}{}a{a}", if key.is_empty() { "" } else { "," });
                    let child_reach: [&[f32]; 2] =
                        if q == 0 { [rq.as_slice(), reach[1]] } else { [reach[0], rq.as_slice()] };
                    let ccfv =
                        self.sweep(child, child_reach, dealt, &child_key, since_chance + 1, cats, out);
                    for i in 0..nh[q] {
                        cfv[q][i] += sig[i] * ccfv[q][i];
                    }
                    for i in 0..nh[o] {
                        cfv[o][i] += ccfv[o][i];
                    }
                }
                if record {
                    let views = self.action_views(node_idx);
                    let mut acc = LineAcc {
                        kind: "action",
                        street: node.street,
                        pot,
                        actor: Some(node.player),
                        actions: views.iter().map(|v| v.label.clone()).collect(),
                        kinds: views.iter().map(|v| v.kind.clone()).collect(),
                        fsum: vec![0f64; na],
                        fw: 0.0,
                        players: [PAcc::default(), PAcc::default()],
                    };
                    for p in 0..2 {
                        let valid = self.valid_opp_sum(p, reach[1 - p]);
                        let eq = if full { Some(self.equity(p, reach[1 - p], dealt)) } else { None };
                        let pa = &mut acc.players[p];
                        pa.has_eq = eq.is_some();
                        if full {
                            let mk = |n: usize, na: usize| -> Vec<Acc1> {
                                (0..n).map(|_| Acc1 { fsum: vec![0.0; na], ..Default::default() }).collect()
                            };
                            let fna = if p == q { na } else { 0 };
                            pa.cats = Some([mk(MADE.len(), fna), mk(DRAW.len(), fna), mk(EQA.len(), fna)]);
                        }
                        for i in 0..nh[p] {
                            if valid[i] <= 1e-9 || reach[p][i] <= 0.0 {
                                continue;
                            }
                            let w = reach[p][i] as f64 * valid[i];
                            let ev = cfv[p][i] as f64 / valid[i] + node.put[p];
                            let e = eq.as_ref().map(|v| v[i]).filter(|x| !x.is_nan());
                            pa.w += w;
                            pa.wev += w * ev;
                            if let Some(e) = e {
                                pa.weq += w * e as f64;
                            }
                            if p == q {
                                acc.fw += w;
                                for a in 0..na {
                                    acc.fsum[a] += w * sigma[a * nh[q] + i] as f64;
                                }
                            }
                            if let Some(c) = pa.cats.as_mut() {
                                let (mi, di) = cats.cats[p][i];
                                let ei = e.map(eqa_bucket);
                                let slots: [Option<usize>; 3] =
                                    [Some(mi as usize), Some(di as usize), ei];
                                for d in 0..3 {
                                    let Some(k) = slots[d] else { continue };
                                    let a1 = &mut c[d][k];
                                    a1.w += w;
                                    a1.wev += w * ev;
                                    if let Some(e) = e {
                                        a1.weq += w * e as f64;
                                    }
                                    if p == q {
                                        for a in 0..na {
                                            a1.fsum[a] += w * sigma[a * nh[q] + i] as f64;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    match out.get_mut(key) {
                        Some(a) => merge_line(a, &acc),
                        None => {
                            out.insert(key.to_string(), acc);
                        }
                    }
                }
                cfv
            }
            _ => unreachable!(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cards::card_from_str;

    fn c(s: &str) -> Card {
        card_from_str(s).unwrap()
    }
    fn made(board: &str, hand: &str) -> &'static str {
        let b: Vec<Card> = (0..board.len() / 2).map(|i| c(&board[2 * i..2 * i + 2])).collect();
        MADE[classify(&b, c(&hand[0..2]), c(&hand[2..4])).0 as usize]
    }
    fn draw(board: &str, hand: &str) -> &'static str {
        let b: Vec<Card> = (0..board.len() / 2).map(|i| c(&board[2 * i..2 * i + 2])).collect();
        DRAW[classify(&b, c(&hand[0..2]), c(&hand[2..4])).1 as usize]
    }

    #[test]
    fn classifier_matches_the_js_rules() {
        assert_eq!(made("Ks7h2d", "AhAd"), "overpair");
        assert_eq!(made("Ks7h2d", "KhQd"), "top_pair");
        assert_eq!(made("Ks7h2d", "7s8s"), "second_pair");
        assert_eq!(made("Ks7h2d", "2s3s"), "third_pair");
        assert_eq!(made("Ks7h2d", "7d7c"), "set");
        assert_eq!(made("Ks7h2d", "5h5c"), "underpair");
        assert_eq!(made("Ks7h2d", "AhQd"), "ace_high");
        assert_eq!(made("Ks7h2d", "Kc7d"), "two_pair");
        assert_eq!(made("KsKh2d", "AhAd"), "overpair"); // board pair is everyone's
        assert_eq!(made("KsKh2d", "KdQc"), "trips");
        assert_eq!(made("9s8s7s", "6s5s"), "sf");
        assert_eq!(made("9s8s7d", "6h5c"), "straight");
        assert_eq!(made("Ks7s2s", "AsQs"), "flush");
        assert_eq!(made("Ks7s2s", "AsQd"), "ace_high"); // four to a flush is not a flush
        assert_eq!(draw("Ks7s2d", "AsQs"), "nut_fd");
        assert_eq!(draw("Ks7s2d", "QsJs"), "fd");
        assert_eq!(draw("Ks7h2d", "AsQs"), "bdfd2"); // two hole spades + Ks
        assert_eq!(draw("Ks7s2d", "AsQc"), "bdfd1"); // one hole spade + two on board
        assert_eq!(draw("Ks7h2d", "AsQc"), "no_draw");
        assert_eq!(draw("Js7h2d", "9c8d"), "gutshot"); // only a T fills J-7
        assert_eq!(draw("Js7h2d", "Tc9d"), "gutshot"); // only an 8
        assert_eq!(draw("9s7h2d", "8cTd"), "oesd"); // 6 or J
        assert_eq!(draw("Js7s2d", "Ts9s"), "combo");
    }
}
