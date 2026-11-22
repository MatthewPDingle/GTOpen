//! A net in place of strategy tables.
//!
//! The net reads one decision as a seat sees it (its two cards, the exact
//! board cards, how strong the hand is, and the betting so far) and returns
//! one number per action of a fixed menu. One net serves every seat, flop,
//! ante and stack size.
//!
//! This file holds the three things the trainer and the engine must agree
//! on: the inputs (`PublicFeats`, `hand_feats`, the card slots), the action
//! menu, and the net itself (`Mlp`, read from a file the trainer writes).

use super::abstraction::{Abstraction, Runout};
use super::range::Policy;
use super::tree::*;
use crate::cards::{combo_from_index, combo_index, NUM_COMBOS};
use crate::tree::Action;

/// Fixed action menu: fold, check or call, up to three bet or raise sizes
/// (smallest first), all-in.
pub const MENU: usize = 6;
pub const SLOT_FOLD: u8 = 0;
pub const SLOT_CALL: u8 = 1;
pub const SLOT_SIZE: u8 = 2;
pub const SLOT_ALLIN: u8 = 5;
/// Seats the inputs describe.
pub const NET_SEATS: usize = 6;
/// Inputs about the betting, the same for every hand at a node.
pub const PUB: usize = 57;
/// Inputs about the hand's strength: per board, the average share of other
/// hands beaten and its spread on the flop and on the turn, and the share
/// beaten on the river (0 until that street is dealt).
pub const HAND: usize = 10;
pub const DENSE: usize = PUB + HAND;
/// Card slots: the two hole cards share one table; each board has its own
/// for the flop, the turn card and the river card.
pub const EMB_ROWS: usize = 52 + 2 * 156;

#[inline]
pub fn emb_board_row(board: usize, street: usize, card: u8) -> usize {
    52 + board * 156 + street * 52 + card as usize
}

/// The betting inputs and action slots of every decision in a tree.
pub struct PublicFeats {
    /// `[node * PUB ..]`, zero for nodes that are not decisions.
    pub rows: Vec<f32>,
    /// Menu slot of each child action.
    pub slots: Vec<[u8; MAX_ACTIONS]>,
}

#[derive(Clone)]
struct PubState {
    street: u8,
    street_bet: [f32; MAX_PLAYERS],
    acted: u16,
    allin: u16,
    raises: [u8; 3],
    aggr: [i8; 3],
}

impl PublicFeats {
    pub fn build(tree: &BpTree, boards: usize) -> Result<PublicFeats, String> {
        if tree.players() > NET_SEATS {
            return Err(format!("the net describes at most {NET_SEATS} seats"));
        }
        let n = tree.nodes.len();
        let mut f = PublicFeats { rows: vec![0.0; n * PUB], slots: vec![[0; MAX_ACTIONS]; n] };
        let st = PubState {
            street: tree.root_street,
            street_bet: [0.0; MAX_PLAYERS],
            acted: 0,
            allin: 0,
            raises: [0; 3],
            aggr: [-1; 3],
        };
        f.visit(tree, boards, 0, st)?;
        Ok(f)
    }

    #[inline]
    pub fn row(&self, node_idx: u32) -> &[f32] {
        &self.rows[node_idx as usize * PUB..(node_idx as usize + 1) * PUB]
    }

    fn visit(&mut self, tree: &BpTree, boards: usize, idx: u32, st: PubState) -> Result<(), String> {
        let node = &tree.nodes[idx as usize];
        if node.kind != KIND_ACTION {
            return Ok(());
        }
        let n = tree.players();
        let cfg = &tree.config;
        let (ante, stack) = (cfg.ante as f32, cfg.stack as f32);
        let hero = node.player as usize;
        let street = node.street as usize;
        let pot = node.pot;
        let live = |p: usize| node.live >> p & 1 != 0;
        let hi = (0..n).filter(|&p| live(p)).map(|p| st.street_bet[p]).fold(0.0f32, f32::max);
        let facing = hi - st.street_bet[hero];
        let behind = stack - (tree.put(idx, hero) - ante);
        let acts = tree.node_actions(node);
        // Action slots: sizes that put the actor all-in take the last slot.
        let mut slots = [0u8; MAX_ACTIONS];
        let mut sized = 0u8;
        let mut size_feat = [0.0f32; 8];
        for (i, a) in acts.iter().enumerate() {
            slots[i] = match a {
                Action::Fold => SLOT_FOLD,
                Action::Check | Action::Call(_) => SLOT_CALL,
                Action::Bet(to) | Action::Raise(to) => {
                    let to = *to as f32;
                    let rel = (to - hi) / (pot + facing);
                    if to - st.street_bet[hero] >= behind - 1e-4 {
                        size_feat[6] = 1.0;
                        size_feat[7] = rel;
                        SLOT_ALLIN
                    } else {
                        if sized >= 3 {
                            return Err("the net's menu holds at most three bet or raise sizes below all-in".into());
                        }
                        size_feat[sized as usize * 2] = 1.0;
                        size_feat[sized as usize * 2 + 1] = rel;
                        sized += 1;
                        SLOT_SIZE + sized - 1
                    }
                }
            };
        }
        self.slots[idx as usize] = slots;
        let row = &mut self.rows[idx as usize * PUB..(idx as usize + 1) * PUB];
        row[street] = 1.0;
        row[3] = n as f32 / 6.0;
        row[4] = node.live.count_ones() as f32 / 6.0;
        row[5] = if boards == 2 { 1.0 } else { 0.0 };
        let start_pot = n as f32 * ante;
        row[6] = start_pot / (start_pot + stack);
        row[7] = pot / (pot + behind);
        row[8] = facing / (pot + facing);
        row[9] = if facing > 1e-6 { 1.0 } else { 0.0 };
        row[10] = behind / stack;
        row[11] = st.raises[street] as f32 / 4.0;
        row[12] = if st.acted >> hero & 1 != 0 { 1.0 } else { 0.0 };
        row[13] = (0..hero).filter(|&p| live(p)).count() as f32 / 5.0;
        row[14] = (hero + 1..n).filter(|&p| live(p)).count() as f32 / 5.0;
        for s in 0..3 {
            row[15 + s * 3] = st.raises[s] as f32 / 4.0;
            row[16 + s * 3] = if st.aggr[s] == hero as i8 { 1.0 } else { 0.0 };
            row[17 + s * 3] = if st.aggr[s] >= 0 && st.aggr[s] != hero as i8 { 1.0 } else { 0.0 };
        }
        for k in 1..n {
            let p = (hero + k) % n;
            let o = 24 + (k - 1) * 5;
            if !live(p) {
                continue;
            }
            row[o] = 1.0;
            row[o + 1] = if st.allin >> p & 1 != 0 { 1.0 } else { 0.0 };
            row[o + 2] = st.street_bet[p] / pot;
            row[o + 3] = if st.acted >> p & 1 != 0 { 1.0 } else { 0.0 };
            row[o + 4] = if st.aggr[street] == p as i8 { 1.0 } else { 0.0 };
        }
        row[49..57].copy_from_slice(&size_feat);
        for (i, a) in acts.iter().enumerate() {
            let child = tree.child(node, i);
            let cn = &tree.nodes[child as usize];
            if cn.kind != KIND_ACTION {
                continue;
            }
            let mut s2 = st.clone();
            match a {
                Action::Fold | Action::Check => s2.acted |= 1 << hero,
                Action::Call(to) => {
                    s2.street_bet[hero] = *to as f32;
                    s2.acted |= 1 << hero;
                }
                Action::Bet(to) | Action::Raise(to) => {
                    s2.street_bet[hero] = *to as f32;
                    s2.acted = 1 << hero;
                    s2.raises[street] += 1;
                    s2.aggr[street] = hero as i8;
                }
            }
            if tree.put(child, hero) >= ante + stack - 1e-4 {
                s2.allin |= 1 << hero;
            }
            if cn.street != s2.street {
                s2.street = cn.street;
                s2.street_bet = [0.0; MAX_PLAYERS];
                s2.acted = 0;
            }
            self.visit(tree, boards, child, s2)?;
        }
        Ok(())
    }
}

/// The hand-strength inputs of one hand on one street.
#[inline]
pub fn hand_feats(abs: &Abstraction, street: usize, hand: usize, runout: &Runout, out: &mut [f32; HAND]) {
    let f = abs.feats.as_ref().expect("built with_features");
    *out = [0.0; HAND];
    for b in 0..abs.num_boards() {
        let o = b * 5;
        out[o] = f.flop[b][hand * 2];
        out[o + 1] = f.flop[b][hand * 2 + 1];
        if street >= 1 {
            let t = runout[b][0] as usize;
            out[o + 2] = f.turn[b][(t * NUM_COMBOS + hand) * 2];
            out[o + 3] = f.turn[b][(t * NUM_COMBOS + hand) * 2 + 1];
        }
        if street >= 2 {
            out[o + 4] = f.river[b][combo_index(runout[b][0], runout[b][1]) * NUM_COMBOS + hand];
        }
    }
}

/// What the net's outputs mean.
pub const KIND_ADVANTAGE: u32 = 0;
pub const KIND_POLICY: u32 = 1;

/// The net: card tables and a dense layer summed into the first hidden
/// layer, further hidden layers (each added to its input when `residual`),
/// and one output per menu slot.
pub struct Mlp {
    pub h: usize,
    pub kind: u32,
    pub residual: bool,
    emb: Vec<f32>,
    /// One column of the dense layer per input.
    wd: Vec<f32>,
    b0: Vec<f32>,
    w: Vec<Vec<f32>>,
    b: Vec<Vec<f32>>,
    wo: Vec<f32>,
    bo: Vec<f32>,
    fast: bool,
}

const NET_MAGIC: &[u8; 4] = b"BPN1";

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2,fma")]
unsafe fn gemv_avx2(w: &[f32], x: &[f32], b: &[f32], out: &mut [f32]) {
    use std::arch::x86_64::*;
    let n = x.len();
    let chunks = n / 32;
    for (j, o) in out.iter_mut().enumerate() {
        let row = w.as_ptr().add(j * n);
        let xp = x.as_ptr();
        let (mut a0, mut a1, mut a2, mut a3) =
            (_mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps());
        for c in 0..chunks {
            let i = c * 32;
            a0 = _mm256_fmadd_ps(_mm256_loadu_ps(row.add(i)), _mm256_loadu_ps(xp.add(i)), a0);
            a1 = _mm256_fmadd_ps(_mm256_loadu_ps(row.add(i + 8)), _mm256_loadu_ps(xp.add(i + 8)), a1);
            a2 = _mm256_fmadd_ps(_mm256_loadu_ps(row.add(i + 16)), _mm256_loadu_ps(xp.add(i + 16)), a2);
            a3 = _mm256_fmadd_ps(_mm256_loadu_ps(row.add(i + 24)), _mm256_loadu_ps(xp.add(i + 24)), a3);
        }
        let s = _mm256_add_ps(_mm256_add_ps(a0, a1), _mm256_add_ps(a2, a3));
        let mut buf = [0.0f32; 8];
        _mm256_storeu_ps(buf.as_mut_ptr(), s);
        let mut acc = b[j] + buf.iter().sum::<f32>();
        for i in chunks * 32..n {
            acc += *row.add(i) * *xp.add(i);
        }
        *o = acc;
    }
}

fn gemv_plain(w: &[f32], x: &[f32], b: &[f32], out: &mut [f32]) {
    let n = x.len();
    for (j, o) in out.iter_mut().enumerate() {
        let row = &w[j * n..(j + 1) * n];
        *o = b[j] + row.iter().zip(x).map(|(a, c)| a * c).sum::<f32>();
    }
}

impl Mlp {
    pub fn load(path: &str) -> Result<Mlp, String> {
        let bytes = std::fs::read(path).map_err(|e| format!("{path}: {e}"))?;
        Mlp::from_bytes(&bytes).map_err(|e| format!("{path}: {e}"))
    }

    pub fn from_bytes(bytes: &[u8]) -> Result<Mlp, String> {
        if bytes.len() < 36 || &bytes[..4] != NET_MAGIC {
            return Err("not a bomb pot net file".into());
        }
        let u = |i: usize| u32::from_le_bytes(bytes[4 + i * 4..8 + i * 4].try_into().unwrap()) as usize;
        let (version, h, layers, dense, emb_rows, menu, residual, kind) = (u(0), u(1), u(2), u(3), u(4), u(5), u(6), u(7));
        if version != 1 || dense != DENSE || emb_rows != EMB_ROWS || menu != MENU {
            return Err(format!(
                "net file is for other inputs (version {version}, {dense} inputs, {emb_rows} card slots, {menu} actions)"
            ));
        }
        let floats = EMB_ROWS * h + h * DENSE + h + layers * (h * h + h) + MENU * h + MENU;
        if bytes.len() != 36 + floats * 4 {
            return Err("net file has the wrong length".into());
        }
        let mut at = 36;
        let mut take = |n: usize| -> Vec<f32> {
            let v = bytes[at..at + n * 4].chunks_exact(4).map(|c| f32::from_le_bytes(c.try_into().unwrap())).collect();
            at += n * 4;
            v
        };
        let emb = take(EMB_ROWS * h);
        let wd_rows = take(h * DENSE);
        let b0 = take(h);
        let mut w = Vec::new();
        let mut b = Vec::new();
        for _ in 0..layers {
            w.push(take(h * h));
            b.push(take(h));
        }
        let wo = take(MENU * h);
        let bo = take(MENU);
        let mut wd = vec![0.0f32; DENSE * h];
        for j in 0..h {
            for d in 0..DENSE {
                wd[d * h + j] = wd_rows[j * DENSE + d];
            }
        }
        #[cfg(target_arch = "x86_64")]
        let fast = std::is_x86_feature_detected!("avx2") && std::is_x86_feature_detected!("fma");
        #[cfg(not(target_arch = "x86_64"))]
        let fast = false;
        Ok(Mlp { h, kind: kind as u32, residual: residual != 0, emb, wd, b0, w, b, wo, bo, fast })
    }

    #[inline]
    fn gemv(&self, w: &[f32], x: &[f32], b: &[f32], out: &mut [f32]) {
        #[cfg(target_arch = "x86_64")]
        if self.fast {
            // SAFETY: the features were detected at load, and every slice
            // holds `out.len() * x.len()` weights and `out.len()` biases.
            unsafe { gemv_avx2(w, x, b, out) };
            return;
        }
        gemv_plain(w, x, b, out)
    }

    #[inline]
    fn add_scaled(&self, x: &mut [f32], col: &[f32], k: f32) {
        for (a, c) in x.iter_mut().zip(col) {
            *a += k * c;
        }
    }

    /// The part of the first layer that every hand at a node shares.
    pub fn node_base(&self, pub_row: &[f32], board_rows: &[usize]) -> Vec<f32> {
        let h = self.h;
        let mut x = self.b0.clone();
        for (d, &v) in pub_row.iter().enumerate() {
            if v != 0.0 {
                self.add_scaled(&mut x, &self.wd[d * h..(d + 1) * h], v);
            }
        }
        for &r in board_rows {
            self.add_scaled(&mut x, &self.emb[r * h..(r + 1) * h], 1.0);
        }
        x
    }

    /// Finish one hand: `x` starts as the node base and is used as scratch.
    pub fn forward(&self, x: &mut Vec<f32>, tmp: &mut Vec<f32>, c1: u8, c2: u8, hand: &[f32; HAND], out: &mut [f32; MENU]) {
        let h = self.h;
        for c in [c1 as usize, c2 as usize] {
            let row = &self.emb[c * h..(c + 1) * h];
            for (a, e) in x.iter_mut().zip(row) {
                *a += e;
            }
        }
        for (k, &v) in hand.iter().enumerate() {
            if v != 0.0 {
                let col = &self.wd[(PUB + k) * h..(PUB + k + 1) * h];
                for (a, c) in x.iter_mut().zip(col) {
                    *a += v * c;
                }
            }
        }
        x.iter_mut().for_each(|v| *v = v.max(0.0));
        tmp.resize(h, 0.0);
        for (w, b) in self.w.iter().zip(&self.b) {
            self.gemv(w, x, b, tmp);
            if self.residual {
                for (a, t) in x.iter_mut().zip(tmp.iter()) {
                    *a += t.max(0.0);
                }
            } else {
                for (a, t) in x.iter_mut().zip(tmp.iter()) {
                    *a = t.max(0.0);
                }
            }
        }
        self.gemv(&self.wo, x, &self.bo, out);
    }
}

/// Turn the net's outputs at one decision into probabilities over the
/// node's own actions.
#[inline]
pub fn outputs_to_probs(kind: u32, raw: &[f32; MENU], slots: &[u8; MAX_ACTIONS], na: usize, out: &mut [f32; MAX_ACTIONS]) {
    if kind == KIND_POLICY {
        let mut top = f32::NEG_INFINITY;
        for a in 0..na {
            top = top.max(raw[slots[a] as usize]);
        }
        let mut sum = 0.0;
        for a in 0..na {
            out[a] = (raw[slots[a] as usize] - top).exp();
            sum += out[a];
        }
        for o in out.iter_mut().take(na) {
            *o /= sum;
        }
        return;
    }
    // Advantages: play in proportion to the positive ones; with none, play
    // the least bad action.
    let mut sum = 0.0;
    let mut best = 0;
    for a in 0..na {
        let v = raw[slots[a] as usize];
        out[a] = v.max(0.0);
        sum += out[a];
        if v > raw[slots[best] as usize] {
            best = a;
        }
    }
    if sum > 0.0 {
        for o in out.iter_mut().take(na) {
            *o /= sum;
        }
    } else {
        out[..na].fill(0.0);
        out[best] = 1.0;
    }
}

/// The board cards a seat sees on a street, as card-table rows.
pub fn board_rows(abs: &Abstraction, street: usize, runout: &Runout) -> Vec<usize> {
    let mut rows = Vec::with_capacity(10);
    for b in 0..abs.num_boards() {
        for &c in &abs.boards[b] {
            rows.push(emb_board_row(b, 0, c));
        }
        for st in 1..=street {
            rows.push(emb_board_row(b, st, runout[b][st - 1]));
        }
    }
    rows
}

/// A net playing one game.
pub struct NetPolicy<'a> {
    pub tree: &'a BpTree,
    pub abs: &'a Abstraction,
    pub pubf: &'a PublicFeats,
    pub net: &'a Mlp,
}

impl NetPolicy<'_> {
    /// One hand at one decision.
    pub fn one(&self, node_idx: u32, hand: usize, runout: &Runout, out: &mut [f32; MAX_ACTIONS]) {
        let node = &self.tree.nodes[node_idx as usize];
        let street = node.street as usize;
        let mut x = self.net.node_base(self.pubf.row(node_idx), &board_rows(self.abs, street, runout));
        let mut tmp = Vec::new();
        let mut hf = [0.0f32; HAND];
        let mut raw = [0.0f32; MENU];
        let (c1, c2) = combo_from_index(hand);
        hand_feats(self.abs, street, hand, runout, &mut hf);
        self.net.forward(&mut x, &mut tmp, c1, c2, &hf, &mut raw);
        outputs_to_probs(self.net.kind, &raw, &self.pubf.slots[node_idx as usize], node.num_children as usize, out);
    }
}

impl Policy for NetPolicy<'_> {
    fn strategies(&self, node_idx: u32, runout: &Runout, used: u64, out: &mut [f32]) {
        let node = &self.tree.nodes[node_idx as usize];
        let na = node.num_children as usize;
        let street = node.street as usize;
        let slots = &self.pubf.slots[node_idx as usize];
        let base = self.net.node_base(self.pubf.row(node_idx), &board_rows(self.abs, street, runout));
        let mut x = Vec::with_capacity(base.len());
        let mut tmp = Vec::new();
        let mut hf = [0.0f32; HAND];
        let mut raw = [0.0f32; MENU];
        let mut probs = [0.0f32; MAX_ACTIONS];
        for h in 0..NUM_COMBOS {
            let (c1, c2) = combo_from_index(h);
            if (1u64 << c1 | 1u64 << c2) & used != 0 {
                continue;
            }
            x.clear();
            x.extend_from_slice(&base);
            hand_feats(self.abs, street, h, runout, &mut hf);
            self.net.forward(&mut x, &mut tmp, c1, c2, &hf, &mut raw);
            outputs_to_probs(self.net.kind, &raw, slots, na, &mut probs);
            for a in 0..na {
                out[a * NUM_COMBOS + h] = probs[a];
            }
        }
    }
}
