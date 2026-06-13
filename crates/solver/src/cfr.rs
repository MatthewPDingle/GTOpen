//! Discounted CFR engine with alternating updates, vectorized over hands and
//! parallelized over chance-node branches.

use crate::game::{fold_cfv, showdown_cfv, Dealt, Spot};
use crate::scratch::Buf;
use crate::store::{Storage, Store};
use crate::tree::{Node, KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, SENTINEL};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum Algorithm {
    /// Discounted CFR (Brown & Sandholm): alpha=1.5, beta=0, gamma=2.
    Dcfr,
    /// CFR+ style: regrets floored at zero, quadratic strategy averaging.
    CfrPlus,
    /// Predictive CFR+ (Farina, Kroer & Sandholm): CFR+ regret flooring, with
    /// the last instantaneous regret added as a prediction when computing the
    /// current strategy.
    PcfrPlus,
}

impl Algorithm {
    pub fn parse(s: &str) -> Result<Algorithm, String> {
        match s.to_ascii_lowercase().replace(['-', '_', '+'], "").as_str() {
            "dcfr" => Ok(Algorithm::Dcfr),
            "cfr" | "cfrplus" => Ok(Algorithm::CfrPlus),
            "pcfr" | "pcfrplus" => Ok(Algorithm::PcfrPlus),
            _ => Err(format!("unknown algorithm {s:?} (use dcfr, cfr+ or pcfr+)")),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Discounts {
    pub pos: f32,
    pub neg: f32,
    pub strat: f32,
}

impl Discounts {
    pub fn for_iteration(algo: Algorithm, t: u32) -> Discounts {
        let t = t as f64;
        match algo {
            Algorithm::Dcfr => {
                let ta = t.powf(1.5);
                Discounts {
                    pos: (ta / (ta + 1.0)) as f32,
                    neg: 0.5,
                    strat: (t / (t + 1.0)).powi(2) as f32,
                }
            }
            // RM+ flooring: multiplying a negative cumulative regret by 0
            // before adding the new delta equals max(R + r, 0) over time.
            Algorithm::CfrPlus | Algorithm::PcfrPlus => Discounts {
                pos: 1.0,
                neg: 0.0,
                strat: (t / (t + 1.0)).powi(2) as f32,
            },
        }
    }
}

pub struct Solver {
    pub spot: Arc<Spot>,
    /// Arena storage mode (f32 or 16-bit compressed with per-node scaling).
    pub storage: Storage,
    /// Cumulative regrets per player (indexed by node data_offset).
    pub regrets: [Store; 2],
    /// Cumulative (weighted) strategy per player.
    pub strat: [Store; 2],
    /// PCFR+ prediction arenas (last instantaneous regrets), lazily allocated
    /// on the first PCFR+ iteration.
    pub preds: Option<Box<[Store; 2]>>,
    pub iteration: u32,
    pub algo: Algorithm,
    /// Locked strategies: node index -> fixed sigma (na*nh). Locked nodes are
    /// excluded from regret/strategy updates and play the fixed strategy.
    pub locks: std::collections::HashMap<u32, Vec<f32>>,
    /// Display labels for locked nodes (path descriptions), node index keyed.
    pub lock_labels: std::collections::HashMap<u32, String>,
    /// Exploit suit symmetries by traversing one chance branch per orbit.
    pub use_isomorphism: bool,
    /// Non-representative branches hold stale data until symmetrize() runs.
    sym_dirty: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct Progress {
    pub iteration: u32,
    pub exploit_chips: f64,
    pub exploit_pct_pot: f64,
    pub elapsed_secs: f64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RunOptions {
    pub max_iterations: u32,
    /// Target exploitability as a percentage of the starting pot (e.g. 0.3).
    pub target_exploit_pct: f64,
    /// How often (in iterations) to measure exploitability.
    pub check_every: u32,
}

impl Default for RunOptions {
    fn default() -> Self {
        RunOptions {
            max_iterations: 1000,
            target_exploit_pct: 0.3,
            check_every: 25,
        }
    }
}

impl Solver {
    pub fn new(spot: Arc<Spot>) -> Solver {
        Solver::with_storage(spot, Storage::F32)
    }

    pub fn with_storage(spot: Arc<Spot>, storage: Storage) -> Solver {
        let num_nodes = spot.tree.nodes.len();
        let ds = spot.tree.data_size;
        let signed = |len: u64| match storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::i16(len, num_nodes),
        };
        let unsigned = |len: u64| match storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::u16(len, num_nodes),
        };
        Solver {
            spot,
            storage,
            regrets: [signed(ds[0]), signed(ds[1])],
            strat: [unsigned(ds[0]), unsigned(ds[1])],
            preds: None,
            iteration: 0,
            algo: Algorithm::Dcfr,
            locks: std::collections::HashMap::new(),
            lock_labels: std::collections::HashMap::new(),
            use_isomorphism: true,
            sym_dirty: false,
        }
    }

    /// Actual bytes held by the solver data arenas.
    pub fn arena_bytes(&self) -> u64 {
        let mut total: u64 = self.regrets.iter().chain(self.strat.iter()).map(Store::bytes).sum();
        if let Some(preds) = &self.preds {
            total += preds.iter().map(Store::bytes).sum::<u64>();
        }
        total
    }

    fn ensure_preds(&mut self) {
        if self.preds.is_some() {
            return;
        }
        let num_nodes = self.spot.tree.nodes.len();
        let ds = self.spot.tree.data_size;
        let mk = |len: u64| match self.storage {
            Storage::F32 => Store::f32(len),
            Storage::Compressed => Store::i16(len, num_nodes),
        };
        self.preds = Some(Box::new([mk(ds[0]), mk(ds[1])]));
    }

    pub fn iterate(&mut self) {
        if self.algo == Algorithm::PcfrPlus && self.preds.is_none() {
            self.ensure_preds();
        }
        self.sym_dirty = true;
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        for p in 0..2usize {
            let nh = self.spot.hands[p].len();
            let mut out = Buf::zeroed(nh);
            self.cfr(
                0,
                p,
                &self.spot.weights[p],
                &self.spot.weights[1 - p],
                Dealt::default(),
                &disc,
                &mut out,
            );
        }
    }

    /// Run until convergence or stop. The callback receives progress after each
    /// exploitability check; returning `false` stops the run.
    pub fn run(
        &mut self,
        opts: &RunOptions,
        stop: &AtomicBool,
        mut on_progress: impl FnMut(&Progress),
    ) -> Progress {
        let start = std::time::Instant::now();
        let mut last = Progress {
            iteration: self.iteration,
            exploit_chips: f64::NAN,
            exploit_pct_pot: f64::NAN,
            elapsed_secs: 0.0,
        };
        while self.iteration < opts.max_iterations && !stop.load(Ordering::Relaxed) {
            self.iterate();
            let check = self.iteration % opts.check_every.max(1) == 0
                || self.iteration >= opts.max_iterations;
            if check {
                let e = self.exploitability();
                last = Progress {
                    iteration: self.iteration,
                    exploit_chips: e,
                    exploit_pct_pot: e / self.spot.tree.config.starting_pot * 100.0,
                    elapsed_secs: start.elapsed().as_secs_f64(),
                };
                on_progress(&last);
                if last.exploit_pct_pot <= opts.target_exploit_pct {
                    break;
                }
            }
        }
        last
    }

    #[inline]
    fn node(&self, idx: u32) -> &Node {
        &self.spot.tree.nodes[idx as usize]
    }

    #[inline]
    fn child_of(&self, node: &Node, i: usize) -> u32 {
        self.spot.tree.children[node.children_start as usize + i]
    }

    /// Current strategy from regret matching (or the locked strategy),
    /// written into `sigma` (na*nh).
    fn current_strategy(&self, node_idx: u32, node: &Node, sigma: &mut [f32]) {
        if let Some(lock) = self.locks.get(&node_idx) {
            sigma.copy_from_slice(lock);
            return;
        }
        let p = node.player as usize;
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        let n = na * nh;
        let off = node.data_offset;
        let preds = if self.algo == Algorithm::PcfrPlus {
            self.preds.as_deref()
        } else {
            None
        };
        match (&self.regrets[p], preds) {
            (Store::F32(rb), None) => {
                regret_match(unsafe { rb.slice(off, n) }, na, nh, sigma);
            }
            (Store::F32(rb), Some(preds)) => {
                let r = unsafe { rb.slice(off, n) };
                let pr = match &preds[p] {
                    Store::F32(pb) => unsafe { pb.slice(off, n) },
                    _ => unreachable!("prediction store mismatch"),
                };
                for i in 0..n {
                    sigma[i] = r[i].max(0.0) + pr[i];
                }
                regret_match_inplace(sigma, na, nh);
            }
            (Store::I16 { q, .. }, None) => {
                // Regret matching normalizes per hand, so the scale cancels:
                // match directly on the quantized values.
                regret_match_q(unsafe { q.slice(off, n) }, na, nh, sigma);
            }
            (Store::I16 { q, scale }, Some(preds)) => {
                let qr = unsafe { q.slice(off, n) };
                let kr = unsafe { scale.read_at(node_idx as usize) } / 32767.0;
                let (qp, kp) = match &preds[p] {
                    Store::I16 { q, scale } => (
                        unsafe { q.slice(off, n) },
                        unsafe { scale.read_at(node_idx as usize) } / 32767.0,
                    ),
                    _ => unreachable!("prediction store mismatch"),
                };
                for i in 0..n {
                    sigma[i] = qr[i].max(0) as f32 * kr + qp[i] as f32 * kp;
                }
                regret_match_inplace(sigma, na, nh);
            }
            _ => unreachable!("regret store mismatch"),
        }
    }

    /// Apply the regret/strategy (and PCFR+ prediction) update at an action
    /// node owned by traverser `p`. `out` holds the sigma-weighted node value.
    #[allow(clippy::too_many_arguments)]
    fn update_node(
        &self,
        node_idx: u32,
        node: &Node,
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
        let preds = if self.algo == Algorithm::PcfrPlus {
            self.preds.as_deref()
        } else {
            None
        };
        match self.storage {
            Storage::F32 => {
                let regrets = match &self.regrets[p] {
                    Store::F32(b) => unsafe { b.slice(off, n) },
                    _ => unreachable!(),
                };
                let strat = match &self.strat[p] {
                    Store::F32(b) => unsafe { b.slice(off, n) },
                    _ => unreachable!(),
                };
                for a in 0..na {
                    let base = a * nh;
                    for i in 0..nh {
                        let r = regrets[base + i];
                        let d = if r > 0.0 { disc.pos } else { disc.neg };
                        regrets[base + i] = r * d + (vals[base + i] - out[i]);
                        strat[base + i] =
                            strat[base + i] * disc.strat + reach_p[i] * sigma[base + i];
                    }
                }
                if let Some(preds) = preds {
                    let pr = match &preds[p] {
                        Store::F32(b) => unsafe { b.slice(off, n) },
                        _ => unreachable!(),
                    };
                    for a in 0..na {
                        let base = a * nh;
                        for i in 0..nh {
                            pr[base + i] = vals[base + i] - out[i];
                        }
                    }
                }
            }
            Storage::Compressed => {
                // Fused decode+update+max pass, then one quantize pass.
                let (rq, rscale) = match &self.regrets[p] {
                    Store::I16 { q, scale } => (unsafe { q.slice(off, n) }, scale),
                    _ => unreachable!(),
                };
                let (sq, sscale) = match &self.strat[p] {
                    Store::U16 { q, scale } => (unsafe { q.slice(off, n) }, scale),
                    _ => unreachable!(),
                };
                let kr = unsafe { rscale.read_at(node_idx as usize) } / 32767.0;
                // Fold the strategy discount into the decode constant.
                let kss = unsafe { sscale.read_at(node_idx as usize) } / 65535.0 * disc.strat;
                let mut rbuf = Buf::for_overwrite(n);
                let mut sbuf = Buf::for_overwrite(n);
                let mut rmax = 0f32;
                let mut smax = 0f32;
                for a in 0..na {
                    let base = a * nh;
                    for i in 0..nh {
                        let qv = rq[base + i];
                        let d = if qv > 0 { disc.pos } else { disc.neg };
                        let nr = qv as f32 * kr * d + (vals[base + i] - out[i]);
                        rbuf[base + i] = nr;
                        rmax = rmax.max(nr.abs());
                    }
                    for i in 0..nh {
                        let s = sq[base + i] as f32 * kss + reach_p[i] * sigma[base + i];
                        sbuf[base + i] = s;
                        smax = smax.max(s);
                    }
                }
                unsafe {
                    rscale.write_at(node_idx as usize, crate::store::quantize_i16(&rbuf, rmax, rq));
                    sscale.write_at(node_idx as usize, crate::store::quantize_u16(&sbuf, smax, sq));
                }
                if let Some(preds) = preds {
                    let mut pmax = 0f32;
                    for a in 0..na {
                        let base = a * nh;
                        for i in 0..nh {
                            let delta = vals[base + i] - out[i];
                            rbuf[base + i] = delta;
                            pmax = pmax.max(delta.abs());
                        }
                    }
                    let (pq, pscale) = match &preds[p] {
                        Store::I16 { q, scale } => (unsafe { q.slice(off, n) }, scale),
                        _ => unreachable!(),
                    };
                    unsafe {
                        pscale.write_at(
                            node_idx as usize,
                            crate::store::quantize_i16(&rbuf, pmax, pq),
                        );
                    }
                }
            }
        }
    }

    /// Vector-form CFR traversal for traverser `p`.
    /// `out` must be zeroed on entry; receives counterfactual values for p's hands.
    #[allow(clippy::too_many_arguments)]
    fn cfr(
        &self,
        node_idx: u32,
        p: usize,
        reach_p: &[f32],
        reach_o: &[f32],
        dealt: Dealt,
        disc: &Discounts,
        out: &mut [f32],
    ) {
        // Zero-reach pruning (exact): if no opponent hand can reach this node,
        // every counterfactual value below is identically zero — skip the
        // subtree. Regrets there only miss their discount step, which is the
        // standard partial-pruning trade and does not affect convergence.
        if reach_o.iter().all(|&r| r <= 0.0) {
            return;
        }
        let node = self.node(node_idx);
        let spot = &*self.spot;
        match node.kind {
            KIND_TERM_FOLD => {
                let amount = if node.player as usize == p {
                    node.t_lose
                } else {
                    node.t_win
                } as f32;
                fold_cfv(
                    &spot.hands[p],
                    &spot.hands[1 - p],
                    reach_o,
                    &spot.same_combo[p],
                    amount,
                    out,
                );
            }
            KIND_TERM_SHOWDOWN => {
                let eval = spot.river.get(&dealt);
                showdown_cfv(
                    eval,
                    p,
                    &spot.hands[p],
                    &spot.hands[1 - p],
                    reach_o,
                    &spot.same_combo[p],
                    node.t_win as f32,
                    node.t_lose as f32,
                    node.t_tie as f32,
                    out,
                );
            }
            KIND_CHANCE => {
                self.chance_node(node, p, reach_p, reach_o, dealt, out, |s, c, rp, ro, d, o| {
                    s.cfr(c, p, rp, ro, d, disc, o)
                });
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                if node.player as usize == p {
                    let nh = spot.hands[p].len();
                    let locked = self.locks.contains_key(&node_idx);
                    let mut sigma = Buf::for_overwrite(na * nh);
                    self.current_strategy(node_idx, node, &mut sigma);
                    let mut vals = Buf::zeroed(na * nh);
                    let mut reach_buf = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            reach_buf[i] = reach_p[i] * sig[i];
                        }
                        self.cfr(
                            self.child_of(node, a),
                            p,
                            &reach_buf,
                            reach_o,
                            dealt,
                            disc,
                            &mut vals[a * nh..(a + 1) * nh],
                        );
                    }
                    for a in 0..na {
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        let val = &vals[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            out[i] += sig[i] * val[i];
                        }
                    }
                    if !locked {
                        self.update_node(node_idx, node, p, &sigma, &vals, out, reach_p, disc);
                    }
                } else {
                    let o = 1 - p;
                    let nh_o = spot.hands[o].len();
                    let mut sigma = Buf::for_overwrite(na * nh_o);
                    self.current_strategy(node_idx, node, &mut sigma);
                    let nh = spot.hands[p].len();
                    let mut reach_buf = Buf::for_overwrite(nh_o);
                    let mut child_out = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh_o..(a + 1) * nh_o];
                        for j in 0..nh_o {
                            reach_buf[j] = reach_o[j] * sig[j];
                        }
                        child_out.fill(0.0);
                        self.cfr(
                            self.child_of(node, a),
                            p,
                            reach_p,
                            &reach_buf,
                            dealt,
                            disc,
                            &mut child_out,
                        );
                        for i in 0..nh {
                            out[i] += child_out[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Shared chance-node logic for all traversal kinds. `recurse` is called
    /// per valid card with fresh reach vectors and a zeroed output buffer.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn chance_node<F>(
        &self,
        node: &Node,
        p: usize,
        reach_p: &[f32],
        reach_o: &[f32],
        dealt: Dealt,
        out: &mut [f32],
        recurse: F,
    ) where
        F: Fn(&Self, u32, &[f32], &[f32], Dealt, &mut [f32]) + Sync,
    {
        let spot = &*self.spot;
        let nh = spot.hands[p].len();
        let nh_o = spot.hands[1 - p].len();
        let divisor = (46 - node.street as i32) as f32; // turn: 45, river: 44

        let mut cards_arr = [0u8; 52];
        let mut ncards = 0usize;
        for c in 0..52u8 {
            if spot.tree.children[node.children_start as usize + c as usize] != SENTINEL
                && !dealt.contains(c)
            {
                cards_arr[ncards] = c;
                ncards += 1;
            }
        }
        let cards = &cards_arr[..ncards];

        // Suit isomorphism: group cards into orbits under the suit symmetries
        // that fix the board and dealt cards; traverse one representative per
        // orbit and synthesize the others via hand-index permutation
        // (cfv_c[h] == cfv_rep[sigma(h)] exactly, because orbit branches share
        // their strategy by construction).
        let mut rep_of = [255u8; 52];
        let mut perm_of = [0usize; 52];
        if self.use_isomorphism && spot.suit_perms.len() > 1 {
            let valid = spot.perms_fixing(&dealt);
            for &c in cards {
                let mut rep = c;
                let mut k_rep = 0usize;
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
            for &c in cards {
                rep_of[c as usize] = c;
            }
        }
        let mut reps_arr = [0u8; 52];
        let mut nreps = 0usize;
        for &c in cards {
            if rep_of[c as usize] == c {
                reps_arr[nreps] = c;
                nreps += 1;
            }
        }
        let reps = &reps_arr[..nreps];

        // Parallelize when children start betting rounds (not bare runouts).
        let parallel = cards
            .first()
            .map(|&c| {
                let child =
                    self.spot.tree.children[node.children_start as usize + c as usize];
                self.node(child).kind == KIND_ACTION
            })
            .unwrap_or(false);

        let run_child = |c: u8| -> (u8, Buf) {
            let child = self.spot.tree.children[node.children_start as usize + c as usize];
            let cm = 1u64 << c;
            let mut rp = Buf::for_overwrite(nh);
            for (i, h) in spot.hands[p].iter().enumerate() {
                rp[i] = if h.mask & cm != 0 { 0.0 } else { reach_p[i] };
            }
            let mut ro = Buf::for_overwrite(nh_o);
            for (j, h) in spot.hands[1 - p].iter().enumerate() {
                ro[j] = if h.mask & cm != 0 { 0.0 } else { reach_o[j] };
            }
            let mut child_out = Buf::zeroed(nh);
            recurse(self, child, &rp, &ro, dealt.push(c), &mut child_out);
            (c, child_out)
        };

        let results: Vec<(u8, Buf)> = if parallel {
            reps.par_iter().map(|&c| run_child(c)).collect()
        } else {
            reps.iter().map(|&c| run_child(c)).collect()
        };

        let mut by_card: [Option<&[f32]>; 52] = [None; 52];
        for (c, v) in &results {
            by_card[*c as usize] = Some(&v[..]);
        }
        for &c in cards {
            let rep = rep_of[c as usize];
            let child_out = by_card[rep as usize].expect("orbit rep traversed");
            let cm = 1u64 << c;
            if c == rep {
                for (i, h) in spot.hands[p].iter().enumerate() {
                    if h.mask & cm == 0 {
                        out[i] += child_out[i];
                    }
                }
            } else {
                let tbl = &spot.hand_perm[p][perm_of[c as usize]];
                for (i, h) in spot.hands[p].iter().enumerate() {
                    if h.mask & cm == 0 {
                        out[i] += child_out[tbl[i] as usize];
                    }
                }
            }
        }
        let inv = 1.0 / divisor;
        for x in out.iter_mut() {
            *x *= inv;
        }
    }

    /// Average strategy (normalized cumulative strategy) for a node, written
    /// into `sigma` (na*nh). Locked nodes return the locked strategy.
    pub fn average_strategy_into(&self, node_idx: u32, node: &Node, sigma: &mut [f32]) {
        if let Some(lock) = self.locks.get(&node_idx) {
            sigma.copy_from_slice(lock);
            return;
        }
        let p = node.player as usize;
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        match &self.strat[p] {
            Store::F32(b) => {
                let strat = unsafe { b.slice(node.data_offset, na * nh) };
                for i in 0..nh {
                    let mut sum = 0f64;
                    for a in 0..na {
                        sum += strat[a * nh + i].max(0.0) as f64;
                    }
                    if sum > 1e-12 {
                        for a in 0..na {
                            sigma[a * nh + i] = (strat[a * nh + i].max(0.0) as f64 / sum) as f32;
                        }
                    } else {
                        let u = 1.0 / na as f32;
                        for a in 0..na {
                            sigma[a * nh + i] = u;
                        }
                    }
                }
            }
            // Normalization cancels the scale: average directly on quants.
            Store::U16 { q, .. } => {
                let qs = unsafe { q.slice(node.data_offset, na * nh) };
                for i in 0..nh {
                    let mut sum = 0u32;
                    for a in 0..na {
                        sum += qs[a * nh + i] as u32;
                    }
                    if sum > 0 {
                        let inv = 1.0 / sum as f32;
                        for a in 0..na {
                            sigma[a * nh + i] = qs[a * nh + i] as f32 * inv;
                        }
                    } else {
                        let u = 1.0 / na as f32;
                        for a in 0..na {
                            sigma[a * nh + i] = u;
                        }
                    }
                }
            }
            _ => unreachable!("strategy store mismatch"),
        }
    }

    /// Average strategy as a fresh Vec (see `average_strategy_into`).
    pub fn average_strategy(&self, node_idx: u32, node: &Node) -> Vec<f32> {
        let p = node.player as usize;
        let nh = self.spot.hands[p].len();
        let na = node.num_children as usize;
        let mut sigma = vec![0f32; na * nh];
        self.average_strategy_into(node_idx, node, &mut sigma);
        sigma
    }
}

impl Solver {
    /// Mark sibling chance branches as stale (e.g. after the GPU wrote fresh
    /// data into the representative branches only).
    pub fn mark_sym_dirty(&mut self) {
        self.sym_dirty = true;
    }

    /// Copy solved data from representative chance branches into their
    /// isomorphic siblings (suit-permuted), so queries and saves see a fully
    /// populated tree. Cheap no-op when nothing changed or no symmetry exists.
    pub fn ensure_symmetric(&mut self) {
        if !self.sym_dirty || !self.use_isomorphism || self.spot.suit_perms.len() < 2 {
            self.sym_dirty = false;
            return;
        }
        self.symmetrize_node(0, Dealt::default());
        self.sym_dirty = false;
    }

    fn symmetrize_node(&mut self, node_idx: u32, dealt: Dealt) {
        let spot = self.spot.clone();
        let node = &spot.tree.nodes[node_idx as usize];
        match node.kind {
            KIND_ACTION => {
                for a in 0..node.num_children as usize {
                    let child = spot.tree.children[node.children_start as usize + a];
                    self.symmetrize_node(child, dealt);
                }
            }
            KIND_CHANCE => {
                let valid = spot.perms_fixing(&dealt);
                let cards: Vec<u8> = (0..52u8)
                    .filter(|&c| {
                        spot.tree.children[node.children_start as usize + c as usize] != SENTINEL
                            && !dealt.contains(c)
                    })
                    .collect();
                let mut orbit: Vec<(u8, u8, usize)> = Vec::new(); // (card, rep, perm)
                for &c in &cards {
                    let mut rep = c;
                    let mut k_rep = 0usize;
                    for &k in &valid {
                        let pc = crate::cards::permute_card(c, &spot.suit_perms[k]);
                        if pc < rep {
                            rep = pc;
                            k_rep = k;
                        }
                    }
                    orbit.push((c, rep, k_rep));
                }
                // first finish the representatives' own subtrees...
                for &(c, rep, _) in &orbit {
                    if c == rep {
                        let child = spot.tree.children[node.children_start as usize + c as usize];
                        self.symmetrize_node(child, dealt.push(c));
                    }
                }
                // ...then transport them onto the other orbit members
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

    /// Copy all solver data below `src` onto the structurally identical
    /// branch below `dst`, permuting hands (and cards) by suit_perms[k].
    /// PCFR+ predictions are not copied: CFR only ever traverses orbit
    /// representatives, so sibling predictions are never read.
    fn copy_branch(&mut self, src_idx: u32, dst_idx: u32, k: usize) {
        let spot = self.spot.clone();
        let src = &spot.tree.nodes[src_idx as usize];
        let dst = &spot.tree.nodes[dst_idx as usize];
        debug_assert_eq!(src.kind, dst.kind);
        match src.kind {
            KIND_ACTION => {
                let p = src.player as usize;
                let nh = spot.hands[p].len();
                let na = src.num_children as usize;
                let n = na * nh;
                let tbl = &spot.hand_perm[p][k];
                let lock = self.locks.get(&src_idx).cloned();
                {
                    let mut src_r = Buf::zeroed(n);
                    let mut src_s = Buf::zeroed(n);
                    unsafe {
                        self.regrets[p].read_f32(src_idx, src.data_offset, n, &mut src_r);
                        self.strat[p].read_f32(src_idx, src.data_offset, n, &mut src_s);
                    }
                    let mut dst_r = Buf::zeroed(n);
                    let mut dst_s = Buf::zeroed(n);
                    for a in 0..na {
                        for i in 0..nh {
                            let j = tbl[i] as usize;
                            dst_r[a * nh + i] = src_r[a * nh + j];
                            dst_s[a * nh + i] = match &lock {
                                // locked source: materialize the locked sigma so
                                // average_strategy() on the copy matches it
                                Some(l) => l[a * nh + j],
                                None => src_s[a * nh + j],
                            };
                        }
                    }
                    unsafe {
                        self.regrets[p].write_f32(dst_idx, dst.data_offset, n, &dst_r);
                        self.strat[p].write_f32(dst_idx, dst.data_offset, n, &dst_s);
                    }
                }
                for a in 0..na {
                    let sc = spot.tree.children[src.children_start as usize + a];
                    let dc = spot.tree.children[dst.children_start as usize + a];
                    self.copy_branch(sc, dc, k);
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
                    self.copy_branch(sc, dc, k);
                }
            }
            _ => {}
        }
    }
}

/// Regret matching: sigma[a][i] = max(r,0)/sum, uniform when all non-positive.
pub fn regret_match(regrets: &[f32], na: usize, nh: usize, sigma: &mut [f32]) {
    debug_assert_eq!(regrets.len(), na * nh);
    debug_assert_eq!(sigma.len(), na * nh);
    for i in 0..nh {
        let mut sum = 0f32;
        for a in 0..na {
            sum += regrets[a * nh + i].max(0.0);
        }
        if sum > 1e-12 {
            let inv = 1.0 / sum;
            for a in 0..na {
                sigma[a * nh + i] = regrets[a * nh + i].max(0.0) * inv;
            }
        } else {
            let u = 1.0 / na as f32;
            for a in 0..na {
                sigma[a * nh + i] = u;
            }
        }
    }
}

/// Regret matching directly on quantized regrets (the per-node scale cancels
/// in the normalization, so it never needs to be applied).
pub fn regret_match_q(q: &[i16], na: usize, nh: usize, sigma: &mut [f32]) {
    debug_assert_eq!(q.len(), na * nh);
    debug_assert_eq!(sigma.len(), na * nh);
    for i in 0..nh {
        let mut sum = 0i32;
        for a in 0..na {
            sum += q[a * nh + i].max(0) as i32;
        }
        if sum > 0 {
            let inv = 1.0 / sum as f32;
            for a in 0..na {
                sigma[a * nh + i] = q[a * nh + i].max(0) as f32 * inv;
            }
        } else {
            let u = 1.0 / na as f32;
            for a in 0..na {
                sigma[a * nh + i] = u;
            }
        }
    }
}

/// Regret matching where `sigma` already holds the (possibly predicted)
/// regret values; normalized in place.
pub fn regret_match_inplace(sigma: &mut [f32], na: usize, nh: usize) {
    debug_assert_eq!(sigma.len(), na * nh);
    for i in 0..nh {
        let mut sum = 0f32;
        for a in 0..na {
            sum += sigma[a * nh + i].max(0.0);
        }
        if sum > 1e-12 {
            let inv = 1.0 / sum;
            for a in 0..na {
                sigma[a * nh + i] = sigma[a * nh + i].max(0.0) * inv;
            }
        } else {
            let u = 1.0 / na as f32;
            for a in 0..na {
                sigma[a * nh + i] = u;
            }
        }
    }
}
