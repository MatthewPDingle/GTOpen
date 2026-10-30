//! Vectorized CFR for three-player postflop trees (CPU).
//!
//! Alternating updates: each iteration runs one traversal per player. A
//! traversal carries the traverser's reach and both opponents' reaches;
//! terminals use the exact three-player evaluators in `eval`. Chance nodes
//! parallelize over cards and fold suit-isomorphic cards onto one
//! representative, as the heads-up solver does.

use super::eval::terminal_cfv;
use super::game::MwSpot;
use super::tree::{MwNode, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, NP};
use crate::cfr::{regret_match, regret_match_inplace, regret_match_q, Algorithm, Discounts, RunOptions};
use crate::scratch::Buf;
use crate::store::{Storage, Store};
use crate::tree::SENTINEL;
use rayon::prelude::*;
use serde::Serialize;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

/// Cards dealt below the root board.
#[derive(Debug, Copy, Clone, Default)]
pub struct Dealt {
    pub cards: [u8; 2],
    pub len: u8,
}

impl Dealt {
    pub fn push(mut self, c: u8) -> Self {
        self.cards[self.len as usize] = c;
        self.len += 1;
        self
    }
    pub fn contains(&self, c: u8) -> bool {
        self.as_slice().contains(&c)
    }
    pub fn as_slice(&self) -> &[u8] {
        &self.cards[..self.len as usize]
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct MwProgress {
    pub iteration: u32,
    /// Each player's best-response gain over its current EV, in chips.
    pub gaps: [f64; NP],
    /// Each player's EV under the average profile, in chips.
    pub evs: [f64; NP],
    /// Mean gap (NashConv / 3), in chips and in % of the starting pot.
    pub exploit_chips: f64,
    pub exploit_pct_pot: f64,
    pub elapsed_secs: f64,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum EvalMode {
    BestResponse,
    Average,
}

pub struct MwSolver {
    pub spot: Arc<MwSpot>,
    pub storage: Storage,
    pub regrets: [Store; NP],
    pub strat: [Store; NP],
    pub preds: Option<Box<[Store; NP]>>,
    pub iteration: u32,
    pub algo: Algorithm,
    pub use_isomorphism: bool,
    /// Fixed strategies by node (na*nh, action-major).
    pub locks: std::collections::HashMap<u32, Vec<f32>>,
    sym_dirty: bool,
}

impl MwSolver {
    pub fn new(spot: Arc<MwSpot>, storage: Storage) -> MwSolver {
        let nn = spot.tree.nodes.len();
        let ds = spot.tree.data_size;
        let signed = |len: u64| match storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::i16(len, nn),
        };
        let unsigned = |len: u64| match storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::u16(len, nn),
        };
        MwSolver {
            regrets: std::array::from_fn(|p| signed(ds[p])),
            strat: std::array::from_fn(|p| unsigned(ds[p])),
            preds: None,
            spot,
            storage,
            iteration: 0,
            algo: Algorithm::Dcfr,
            use_isomorphism: true,
            locks: Default::default(),
            sym_dirty: false,
        }
    }

    pub fn arena_bytes(&self) -> u64 {
        let mut t: u64 = self.regrets.iter().chain(self.strat.iter()).map(Store::bytes).sum();
        if let Some(p) = &self.preds {
            t += p.iter().map(Store::bytes).sum::<u64>();
        }
        t
    }

    fn ensure_preds(&mut self) {
        if self.preds.is_some() {
            return;
        }
        let nn = self.spot.tree.nodes.len();
        let ds = self.spot.tree.data_size;
        let mk = |len: u64| match self.storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::i16(len, nn),
        };
        self.preds = Some(Box::new(std::array::from_fn(|p| mk(ds[p]))));
    }

    #[inline]
    fn node(&self, idx: u32) -> &MwNode {
        &self.spot.tree.nodes[idx as usize]
    }

    pub fn iterate(&mut self) {
        if self.algo == Algorithm::PcfrPlus {
            self.ensure_preds();
        }
        self.sym_dirty = true;
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        for p in 0..NP {
            let mut out = Buf::zeroed(self.spot.hands[p].len());
            let w = &self.spot.weights;
            self.cfr(0, p, [&w[0], &w[1], &w[2]], Dealt::default(), &disc, &mut out);
        }
    }

    pub fn current_strategy(&self, node_idx: u32, node: &MwNode, sigma: &mut [f32]) {
        if let Some(lock) = self.locks.get(&node_idx) {
            sigma.copy_from_slice(lock);
            return;
        }
        let p = node.player as usize;
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        let n = na * nh;
        let off = node.data_offset;
        let preds = if self.algo == Algorithm::PcfrPlus { self.preds.as_deref() } else { None };
        match (&self.regrets[p], preds) {
            (Store::F32(rb), None) => regret_match(unsafe { rb.slice(off, n) }, na, nh, sigma),
            (Store::F32(rb), Some(pr)) => {
                let r = unsafe { rb.slice(off, n) };
                let Store::F32(pb) = &pr[p] else { unreachable!() };
                let pv = unsafe { pb.slice(off, n) };
                for i in 0..n {
                    sigma[i] = r[i].max(0.0) + pv[i];
                }
                regret_match_inplace(sigma, na, nh);
            }
            (Store::I16 { q, .. }, None) => regret_match_q(unsafe { q.slice(off, n) }, na, nh, sigma),
            (Store::I16 { q, scale }, Some(pr)) => {
                let qr = unsafe { q.slice(off, n) };
                let kr = unsafe { scale.read_at(node_idx as usize) } / 32767.0;
                let Store::I16 { q: pq, scale: ps } = &pr[p] else { unreachable!() };
                let qp = unsafe { pq.slice(off, n) };
                let kp = unsafe { ps.read_at(node_idx as usize) } / 32767.0;
                for i in 0..n {
                    sigma[i] = qr[i].max(0) as f32 * kr + qp[i] as f32 * kp;
                }
                regret_match_inplace(sigma, na, nh);
            }
            _ => unreachable!("regret store mismatch"),
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn update_node(
        &self,
        node_idx: u32,
        node: &MwNode,
        p: usize,
        sigma: &[f32],
        vals: &[f32],
        out: &[f32],
        reach_p: &[f32],
        disc: &Discounts,
    ) {
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        let n = na * nh;
        let off = node.data_offset;
        let preds = if self.algo == Algorithm::PcfrPlus { self.preds.as_deref() } else { None };
        match self.storage {
            Storage::F32 => {
                let Store::F32(rb) = &self.regrets[p] else { unreachable!() };
                let Store::F32(sb) = &self.strat[p] else { unreachable!() };
                let regrets = unsafe { rb.slice(off, n) };
                let strat = unsafe { sb.slice(off, n) };
                for a in 0..na {
                    let base = a * nh;
                    for i in 0..nh {
                        let r = regrets[base + i];
                        let d = if r > 0.0 { disc.pos } else { disc.neg };
                        regrets[base + i] = r * d + (vals[base + i] - out[i]);
                        strat[base + i] = strat[base + i] * disc.strat + reach_p[i] * sigma[base + i];
                    }
                }
                if let Some(pr) = preds {
                    let Store::F32(pb) = &pr[p] else { unreachable!() };
                    let pv = unsafe { pb.slice(off, n) };
                    for a in 0..na {
                        for i in 0..nh {
                            pv[a * nh + i] = vals[a * nh + i] - out[i];
                        }
                    }
                }
            }
            Storage::Compressed => {
                let Store::I16 { q: rq, scale: rscale } = &self.regrets[p] else { unreachable!() };
                let Store::U16 { q: sq, scale: sscale } = &self.strat[p] else { unreachable!() };
                let rq = unsafe { rq.slice(off, n) };
                let sq = unsafe { sq.slice(off, n) };
                let kr = unsafe { rscale.read_at(node_idx as usize) } / 32767.0;
                let kss = unsafe { sscale.read_at(node_idx as usize) } / 65535.0 * disc.strat;
                let mut rbuf = Buf::for_overwrite(n);
                let mut sbuf = Buf::for_overwrite(n);
                let (mut rmax, mut smax) = (0f32, 0f32);
                for a in 0..na {
                    let base = a * nh;
                    for i in 0..nh {
                        let qv = rq[base + i];
                        let d = if qv > 0 { disc.pos } else { disc.neg };
                        let nr = qv as f32 * kr * d + (vals[base + i] - out[i]);
                        rbuf[base + i] = nr;
                        rmax = rmax.max(nr.abs());
                        let s = sq[base + i] as f32 * kss + reach_p[i] * sigma[base + i];
                        sbuf[base + i] = s;
                        smax = smax.max(s);
                    }
                }
                unsafe {
                    let seed = ((self.iteration as u64) << 32) | node_idx as u64;
                    rscale.write_at(node_idx as usize, crate::store::quantize_i16_unbiased(&rbuf, rmax, rq, seed));
                    sscale.write_at(
                        node_idx as usize,
                        crate::store::quantize_u16_unbiased(&sbuf, smax, sq, seed ^ 0xD1B5_4A32_D192_ED03),
                    );
                }
                if let Some(pr) = preds {
                    let mut pmax = 0f32;
                    for a in 0..na {
                        for i in 0..nh {
                            let d = vals[a * nh + i] - out[i];
                            rbuf[a * nh + i] = d;
                            pmax = pmax.max(d.abs());
                        }
                    }
                    let Store::I16 { q: pq, scale: ps } = &pr[p] else { unreachable!() };
                    unsafe {
                        ps.write_at(node_idx as usize, crate::store::quantize_i16(&rbuf, pmax, pq.slice(off, n)));
                    }
                }
            }
        }
    }

    /// Vector CFR traversal for traverser `p`; `out` must be zeroed.
    #[allow(clippy::too_many_arguments)]
    fn cfr(&self, node_idx: u32, p: usize, reach: [&[f32]; NP], dealt: Dealt, disc: &Discounts, out: &mut [f32]) {
        let node = self.node(node_idx);
        let spot = &*self.spot;
        match node.kind {
            KIND_TERM_FOLD | KIND_TERM_SHOWDOWN => {
                if opponents_dead(p, &reach) {
                    return;
                }
                terminal_cfv(spot, node, dealt.as_slice(), p, reach, out);
            }
            KIND_CHANCE => {
                self.chance_node(node, p, reach, dealt, out, &|s, c, r, d, o| s.cfr(c, p, r, d, disc, o));
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                let actor = node.player as usize;
                let nh_a = spot.hands[actor].len();
                let mut sigma = Buf::for_overwrite(na * nh_a);
                self.current_strategy(node_idx, node, &mut sigma);
                let mut rbuf = Buf::for_overwrite(nh_a);
                if actor == p {
                    let nh = nh_a;
                    let mut vals = Buf::zeroed(na * nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            rbuf[i] = reach[p][i] * sig[i];
                        }
                        let mut r = reach;
                        r[p] = &rbuf;
                        self.cfr(spot.tree.child(node, a), p, r, dealt, disc, &mut vals[a * nh..(a + 1) * nh]);
                    }
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        let v = &vals[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            out[i] += sig[i] * v[i];
                        }
                    }
                    if !self.locks.contains_key(&node_idx) {
                        self.update_node(node_idx, node, p, &sigma, &vals, out, reach[p], disc);
                    }
                } else {
                    let nh = spot.hands[p].len();
                    let mut child_out = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh_a..(a + 1) * nh_a];
                        for j in 0..nh_a {
                            rbuf[j] = reach[actor][j] * sig[j];
                        }
                        let mut r = reach;
                        r[actor] = &rbuf;
                        child_out.fill(0.0);
                        self.cfr(spot.tree.child(node, a), p, r, dealt, disc, &mut child_out);
                        for i in 0..nh {
                            out[i] += child_out[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Chance node shared by all traversals: zero hands holding the dealt
    /// card, recurse once per suit orbit, synthesize the rest by permuting
    /// hand indices, then divide by the number of possible cards.
    #[allow(clippy::type_complexity)]
    fn chance_node(
        &self,
        node: &MwNode,
        p: usize,
        reach: [&[f32]; NP],
        dealt: Dealt,
        out: &mut [f32],
        recurse: &(dyn Fn(&Self, u32, [&[f32]; NP], Dealt, &mut [f32]) + Sync),
    ) {
        let spot = &*self.spot;
        let nh = spot.hands[p].len();
        // 52 - board - 6 hole cards: turn 43, river 42.
        let divisor = (44 - node.street as i32) as f32;
        let cards: Vec<u8> = (0..52u8)
            .filter(|&c| spot.tree.children[node.children_start as usize + c as usize] != SENTINEL && !dealt.contains(c))
            .collect();
        let mut rep_of = [255u8; 52];
        let mut perm_of = [0usize; 52];
        if self.use_isomorphism && spot.suit_perms.len() > 1 {
            let valid = spot.perms_fixing(dealt.as_slice());
            for &c in &cards {
                let (mut rep, mut k_rep) = (c, 0);
                for &k in &valid {
                    let pc = crate::cards::permute_card(c, &spot.suit_perms[k]);
                    if pc < rep {
                        rep = pc;
                        k_rep = k;
                    }
                }
                rep_of[c as usize] = rep;
                perm_of[c as usize] = k_rep;
            }
        } else {
            for &c in &cards {
                rep_of[c as usize] = c;
            }
        }
        let reps: Vec<u8> = cards.iter().copied().filter(|&c| rep_of[c as usize] == c).collect();
        let run = |c: u8| -> (u8, Buf) {
            let child = spot.tree.children[node.children_start as usize + c as usize];
            let cm = 1u64 << c;
            let bufs: [Buf; NP] = std::array::from_fn(|o| {
                let mut b = Buf::for_overwrite(spot.hands[o].len());
                for (j, h) in spot.hands[o].iter().enumerate() {
                    b[j] = if h.mask & cm != 0 { 0.0 } else { reach[o][j] };
                }
                b
            });
            let mut co = Buf::zeroed(nh);
            recurse(self, child, [&bufs[0], &bufs[1], &bufs[2]], dealt.push(c), &mut co);
            (c, co)
        };
        let results: Vec<(u8, Buf)> = reps.par_iter().map(|&c| run(c)).collect();
        let mut by_card: [Option<&[f32]>; 52] = [None; 52];
        for (c, v) in &results {
            by_card[*c as usize] = Some(&v[..]);
        }
        for &c in &cards {
            let rep = rep_of[c as usize];
            let co = by_card[rep as usize].expect("orbit representative traversed");
            let cm = 1u64 << c;
            if c == rep {
                for (i, h) in spot.hands[p].iter().enumerate() {
                    if h.mask & cm == 0 {
                        out[i] += co[i];
                    }
                }
            } else {
                let tbl = &spot.hand_perm[p][perm_of[c as usize]];
                for (i, h) in spot.hands[p].iter().enumerate() {
                    if h.mask & cm == 0 {
                        out[i] += co[tbl[i] as usize];
                    }
                }
            }
        }
        let inv = 1.0 / divisor;
        for x in out.iter_mut() {
            *x *= inv;
        }
    }

    /// Normalized cumulative strategy (or the lock) for an action node.
    pub fn average_strategy_into(&self, node_idx: u32, node: &MwNode, sigma: &mut [f32]) {
        if let Some(lock) = self.locks.get(&node_idx) {
            sigma.copy_from_slice(lock);
            return;
        }
        let p = node.player as usize;
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        unsafe { self.strat[p].read_f32(node_idx, node.data_offset, na * nh, sigma) };
        for i in 0..nh {
            let s: f32 = (0..na).map(|a| sigma[a * nh + i]).sum();
            if s > 0.0 {
                for a in 0..na {
                    sigma[a * nh + i] /= s;
                }
            } else {
                let u = 1.0 / na as f32;
                for a in 0..na {
                    sigma[a * nh + i] = u;
                }
            }
        }
    }

    pub fn average_strategy(&self, node_idx: u32) -> Vec<f32> {
        let node = self.node(node_idx);
        let n = node.num_children as usize * self.spot.hands[node.player as usize].len();
        let mut v = vec![0f32; n];
        self.average_strategy_into(node_idx, node, &mut v);
        v
    }

    /// Read-only traversal: player `p` plays a best response (or the
    /// average strategy); the others play their average strategies.
    fn eval_into(&self, node_idx: u32, p: usize, reach: [&[f32]; NP], dealt: Dealt, mode: EvalMode, out: &mut [f32]) {
        if opponents_dead(p, &reach) {
            return;
        }
        let node = self.node(node_idx);
        let spot = &*self.spot;
        match node.kind {
            KIND_TERM_FOLD | KIND_TERM_SHOWDOWN => terminal_cfv(spot, node, dealt.as_slice(), p, reach, out),
            KIND_CHANCE => {
                self.chance_node(node, p, reach, dealt, out, &|s, c, r, d, o| s.eval_into(c, p, r, d, mode, o))
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                let actor = node.player as usize;
                let nh_a = spot.hands[actor].len();
                let nh = spot.hands[p].len();
                let mut sigma = Buf::for_overwrite(na * nh_a);
                self.average_strategy_into(node_idx, node, &mut sigma);
                let mut vals = Buf::for_overwrite(nh);
                if actor == p {
                    let free = mode == EvalMode::BestResponse && !self.locks.contains_key(&node_idx);
                    for a in 0..na {
                        vals.fill(0.0);
                        self.eval_into(spot.tree.child(node, a), p, reach, dealt, mode, &mut vals);
                        if free {
                            if a == 0 {
                                out.copy_from_slice(&vals);
                            } else {
                                for i in 0..nh {
                                    out[i] = out[i].max(vals[i]);
                                }
                            }
                        } else {
                            let sig = &sigma[a * nh..(a + 1) * nh];
                            for i in 0..nh {
                                out[i] += sig[i] * vals[i];
                            }
                        }
                    }
                } else {
                    let mut rbuf = Buf::for_overwrite(nh_a);
                    for a in 0..na {
                        let sig = &sigma[a * nh_a..(a + 1) * nh_a];
                        for j in 0..nh_a {
                            rbuf[j] = reach[actor][j] * sig[j];
                        }
                        let mut r = reach;
                        r[actor] = &rbuf;
                        vals.fill(0.0);
                        self.eval_into(spot.tree.child(node, a), p, r, dealt, mode, &mut vals);
                        for i in 0..nh {
                            out[i] += vals[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Per-hand counterfactual values for `p` from `node_idx` given reaches.
    pub fn node_values(&self, node_idx: u32, p: usize, reach: [&[f32]; NP], dealt: Dealt, best_response: bool) -> Vec<f32> {
        let mut out = vec![0f32; self.spot.hands[p].len()];
        let mode = if best_response { EvalMode::BestResponse } else { EvalMode::Average };
        self.eval_into(node_idx, p, reach, dealt, mode, &mut out);
        out
    }

    /// Root EVs and best-response gaps for all three players, in chips.
    pub fn exploitability(&self) -> ([f64; NP], [f64; NP]) {
        let w = &self.spot.weights;
        let reach = [&w[0][..], &w[1][..], &w[2][..]];
        let denom = self.spot.root_triple_mass();
        let mut evs = [0f64; NP];
        let mut gaps = [0f64; NP];
        for p in 0..NP {
            let dot = |v: &[f32]| w[p].iter().zip(v).map(|(&a, &b)| a as f64 * b as f64).sum::<f64>() / denom;
            let br = dot(&self.node_values(0, p, reach, Dealt::default(), true));
            let ev = dot(&self.node_values(0, p, reach, Dealt::default(), false));
            evs[p] = ev;
            gaps[p] = (br - ev).max(0.0);
        }
        (evs, gaps)
    }

    pub fn progress(&self, elapsed: f64) -> MwProgress {
        let (evs, gaps) = self.exploitability();
        let mean = gaps.iter().sum::<f64>() / NP as f64;
        MwProgress {
            iteration: self.iteration,
            gaps,
            evs,
            exploit_chips: mean,
            exploit_pct_pot: mean / self.spot.tree.config.starting_pot * 100.0,
            elapsed_secs: elapsed,
        }
    }

    pub fn run(&mut self, opts: &RunOptions, stop: &AtomicBool, mut on_progress: impl FnMut(&MwProgress)) -> Option<MwProgress> {
        let start = std::time::Instant::now();
        let mut last = None;
        while self.iteration < opts.max_iterations && !stop.load(Ordering::Relaxed) {
            self.iterate();
            if self.iteration % opts.check_every.max(1) == 0 || self.iteration >= opts.max_iterations {
                let pr = self.progress(start.elapsed().as_secs_f64());
                on_progress(&pr);
                let done = pr.exploit_pct_pot <= opts.target_exploit_pct;
                last = Some(pr);
                if done {
                    break;
                }
            }
        }
        last
    }

    /// Copy representative branches onto their suit-isomorphic siblings so
    /// every node holds its own data (needed before queries and saves).
    pub fn ensure_symmetric(&mut self) {
        if !self.sym_dirty || !self.use_isomorphism || self.spot.suit_perms.len() <= 1 {
            self.sym_dirty = false;
            return;
        }
        self.symmetrize(0, Dealt::default());
        self.sym_dirty = false;
    }

    pub fn mark_sym_dirty(&mut self) {
        self.sym_dirty = true;
    }

    fn symmetrize(&mut self, node_idx: u32, dealt: Dealt) {
        let spot = self.spot.clone();
        let node = &spot.tree.nodes[node_idx as usize];
        match node.kind {
            KIND_ACTION => {
                for a in 0..node.num_children as usize {
                    self.symmetrize(spot.tree.child(node, a), dealt);
                }
            }
            KIND_CHANCE => {
                let valid = spot.perms_fixing(dealt.as_slice());
                let mut orbit = Vec::new();
                for c in 0..52u8 {
                    if spot.tree.children[node.children_start as usize + c as usize] == SENTINEL || dealt.contains(c) {
                        continue;
                    }
                    let (mut rep, mut k_rep) = (c, 0);
                    for &k in &valid {
                        let pc = crate::cards::permute_card(c, &spot.suit_perms[k]);
                        if pc < rep {
                            rep = pc;
                            k_rep = k;
                        }
                    }
                    orbit.push((c, rep, k_rep));
                }
                for &(c, rep, _) in &orbit {
                    if c == rep {
                        self.symmetrize(spot.tree.children[node.children_start as usize + c as usize], dealt.push(c));
                    }
                }
                for &(c, rep, k) in &orbit {
                    if c != rep {
                        let src = spot.tree.children[node.children_start as usize + rep as usize];
                        let dst = spot.tree.children[node.children_start as usize + c as usize];
                        self.copy_branch(src, dst, k);
                    }
                }
            }
            _ => {}
        }
    }

    fn copy_branch(&mut self, src_idx: u32, dst_idx: u32, k: usize) {
        let spot = self.spot.clone();
        let src = &spot.tree.nodes[src_idx as usize];
        let dst = &spot.tree.nodes[dst_idx as usize];
        match src.kind {
            KIND_ACTION => {
                let p = src.player as usize;
                let nh = spot.hands[p].len();
                let na = src.num_children as usize;
                let n = na * nh;
                let tbl = &spot.hand_perm[p][k];
                let mut sr = Buf::zeroed(n);
                let mut ss = Buf::zeroed(n);
                unsafe {
                    self.regrets[p].read_f32(src_idx, src.data_offset, n, &mut sr);
                    self.strat[p].read_f32(src_idx, src.data_offset, n, &mut ss);
                }
                let lock = self.locks.get(&src_idx);
                let mut dr = Buf::zeroed(n);
                let mut ds = Buf::zeroed(n);
                for a in 0..na {
                    for i in 0..nh {
                        let j = tbl[i] as usize;
                        dr[a * nh + i] = sr[a * nh + j];
                        ds[a * nh + i] = match lock {
                            Some(l) => l[a * nh + j],
                            None => ss[a * nh + j],
                        };
                    }
                }
                unsafe {
                    self.regrets[p].write_f32(dst_idx, dst.data_offset, n, &dr);
                    self.strat[p].write_f32(dst_idx, dst.data_offset, n, &ds);
                }
                for a in 0..na {
                    self.copy_branch(spot.tree.child(src, a), spot.tree.child(dst, a), k);
                }
            }
            KIND_CHANCE => {
                for x in 0..52u8 {
                    let dc = spot.tree.children[dst.children_start as usize + x as usize];
                    if dc == SENTINEL {
                        continue;
                    }
                    let sx = crate::cards::permute_card(x, &spot.suit_perms[k]);
                    let sc = spot.tree.children[src.children_start as usize + sx as usize];
                    if sc != SENTINEL {
                        self.copy_branch(sc, dc, k);
                    }
                }
            }
            _ => {}
        }
    }
}

#[inline]
fn opponents_dead(p: usize, reach: &[&[f32]; NP]) -> bool {
    (0..NP).any(|o| o != p && reach[o].iter().all(|&x| x <= 0.0))
}
