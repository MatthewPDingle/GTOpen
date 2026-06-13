//! Best-response and average-strategy traversals: exploitability measurement
//! and EV evaluation under the current average strategy profile.

use crate::cfr::Solver;
use crate::game::{fold_cfv, showdown_cfv, sweep_buckets, Dealt};
use crate::scratch::Buf;
use crate::tree::{KIND_ACTION, KIND_CHANCE, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN, SENTINEL};

impl Solver {
    /// Counterfactual values for player `p` when `p` plays a best response
    /// and the opponent plays the average strategy.
    pub fn traverse_br(&self, node_idx: u32, p: usize, reach_o: &[f32], dealt: Dealt) -> Vec<f32> {
        let mut out = vec![0f32; self.spot.hands[p].len()];
        self.br_into(node_idx, p, reach_o, dealt, &mut out);
        out
    }

    /// Best-response traversal writing into `out` (must be zeroed on entry).
    fn br_into(&self, node_idx: u32, p: usize, reach_o: &[f32], dealt: Dealt, out: &mut [f32]) {
        // zero-reach pruning (exact): see cfr()
        if reach_o.iter().all(|&r| r <= 0.0) {
            return;
        }
        let node = &self.spot.tree.nodes[node_idx as usize];
        let spot = &*self.spot;
        let nh = spot.hands[p].len();
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
                showdown_cfv(
                    spot.river.get(&dealt),
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
                let reach_p_dummy = Buf::filled(nh, 1.0);
                self.chance_node(
                    node,
                    p,
                    &reach_p_dummy,
                    reach_o,
                    dealt,
                    out,
                    |s, c, _rp, ro, d, o| s.br_into(c, p, ro, d, o),
                );
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                if node.player as usize == p {
                    let mut vals = Buf::for_overwrite(nh);
                    if let Some(lock) = self.locks.get(&node_idx) {
                        // Locked nodes are constraints: the best responder
                        // cannot deviate there.
                        for a in 0..na {
                            let child = spot.tree.children[node.children_start as usize + a];
                            vals.fill(0.0);
                            self.br_into(child, p, reach_o, dealt, &mut vals);
                            let sig = &lock[a * nh..(a + 1) * nh];
                            for i in 0..nh {
                                out[i] += sig[i] * vals[i];
                            }
                        }
                    } else {
                        for a in 0..na {
                            let child = spot.tree.children[node.children_start as usize + a];
                            vals.fill(0.0);
                            self.br_into(child, p, reach_o, dealt, &mut vals);
                            if a == 0 {
                                out.copy_from_slice(&vals);
                            } else {
                                for i in 0..nh {
                                    if vals[i] > out[i] {
                                        out[i] = vals[i];
                                    }
                                }
                            }
                        }
                    }
                } else {
                    let o_pl = 1 - p;
                    let nh_o = spot.hands[o_pl].len();
                    let mut sigma = Buf::for_overwrite(na * nh_o);
                    self.average_strategy_into(node_idx, node, &mut sigma);
                    let mut reach_buf = Buf::for_overwrite(nh_o);
                    let mut vals = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh_o..(a + 1) * nh_o];
                        for j in 0..nh_o {
                            reach_buf[j] = reach_o[j] * sig[j];
                        }
                        let child = spot.tree.children[node.children_start as usize + a];
                        vals.fill(0.0);
                        self.br_into(child, p, &reach_buf, dealt, &mut vals);
                        for i in 0..nh {
                            out[i] += vals[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Counterfactual values for player `p` when BOTH players play the
    /// average strategy.
    pub fn traverse_avg(&self, node_idx: u32, p: usize, reach_o: &[f32], dealt: Dealt) -> Vec<f32> {
        let mut out = vec![0f32; self.spot.hands[p].len()];
        self.avg_into(node_idx, p, reach_o, dealt, &mut out);
        out
    }

    /// Average-strategy traversal writing into `out` (must be zeroed on entry).
    fn avg_into(&self, node_idx: u32, p: usize, reach_o: &[f32], dealt: Dealt, out: &mut [f32]) {
        // zero-reach pruning (exact): see cfr()
        if reach_o.iter().all(|&r| r <= 0.0) {
            return;
        }
        let node = &self.spot.tree.nodes[node_idx as usize];
        let spot = &*self.spot;
        let nh = spot.hands[p].len();
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
                showdown_cfv(
                    spot.river.get(&dealt),
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
                let reach_p_dummy = Buf::filled(nh, 1.0);
                self.chance_node(
                    node,
                    p,
                    &reach_p_dummy,
                    reach_o,
                    dealt,
                    out,
                    |s, c, _rp, ro, d, o| s.avg_into(c, p, ro, d, o),
                );
            }
            KIND_ACTION => {
                let na = node.num_children as usize;
                if node.player as usize == p {
                    let mut sigma = Buf::for_overwrite(na * nh);
                    self.average_strategy_into(node_idx, node, &mut sigma);
                    let mut vals = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let child = spot.tree.children[node.children_start as usize + a];
                        vals.fill(0.0);
                        self.avg_into(child, p, reach_o, dealt, &mut vals);
                        let sig = &sigma[a * nh..(a + 1) * nh];
                        for i in 0..nh {
                            out[i] += sig[i] * vals[i];
                        }
                    }
                } else {
                    let o_pl = 1 - p;
                    let nh_o = spot.hands[o_pl].len();
                    let mut sigma = Buf::for_overwrite(na * nh_o);
                    self.average_strategy_into(node_idx, node, &mut sigma);
                    let mut reach_buf = Buf::for_overwrite(nh_o);
                    let mut vals = Buf::for_overwrite(nh);
                    for a in 0..na {
                        let sig = &sigma[a * nh_o..(a + 1) * nh_o];
                        for j in 0..nh_o {
                            reach_buf[j] = reach_o[j] * sig[j];
                        }
                        let child = spot.tree.children[node.children_start as usize + a];
                        vals.fill(0.0);
                        self.avg_into(child, p, &reach_buf, dealt, &mut vals);
                        for i in 0..nh {
                            out[i] += vals[i];
                        }
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    /// Sum over compatible (i, j) pairs of w_p[i] * w_o[j]: the normalization
    /// constant for converting reach-weighted values to per-hand averages.
    pub fn pair_weight_sum(&self) -> f64 {
        let spot = &*self.spot;
        let hands0 = &spot.hands[0];
        let hands1 = &spot.hands[1];
        let mut t = 0f64;
        let mut s = [0f64; 52];
        for h in hands1.iter() {
            let r = h.weight as f64;
            t += r;
            s[h.c1 as usize] += r;
            s[h.c2 as usize] += r;
        }
        let mut total = 0f64;
        for (i, h) in hands0.iter().enumerate() {
            let same = spot.same_combo[0][i];
            let same_r = if same != SENTINEL {
                hands1[same as usize].weight as f64
            } else {
                0.0
            };
            let valid = t - s[h.c1 as usize] - s[h.c2 as usize] + same_r;
            total += h.weight as f64 * valid;
        }
        total
    }

    /// Exploitability of the current average strategy profile, in chips
    /// (average of both players' best-response gains).
    pub fn exploitability(&self) -> f64 {
        let spot = &*self.spot;
        let denom = self.pair_weight_sum();
        if denom <= 0.0 {
            return f64::NAN;
        }
        let mut br = [0f64; 2];
        for p in 0..2 {
            let cfv = self.traverse_br(0, p, &spot.weights[1 - p], Dealt::default());
            br[p] = spot.weights[p]
                .iter()
                .zip(cfv.iter())
                .map(|(&w, &v)| w as f64 * v as f64)
                .sum::<f64>()
                / denom;
        }
        if spot.tree.config.rake_pct > 0.0 {
            // With rake the game is not zero-sum: compare against actual EVs.
            let mut v = [0f64; 2];
            for p in 0..2 {
                let cfv = self.traverse_avg(0, p, &spot.weights[1 - p], Dealt::default());
                v[p] = spot.weights[p]
                    .iter()
                    .zip(cfv.iter())
                    .map(|(&w, &val)| w as f64 * val as f64)
                    .sum::<f64>()
                    / denom;
            }
            ((br[0] - v[0]) + (br[1] - v[1])) / 2.0
        } else {
            (br[0] + br[1]) / 2.0
        }
    }

    /// Equity (win + tie/2 share against the opponent's reach distribution)
    /// for each of player p's hands, enumerating remaining board runouts.
    /// Returns NaN for hands with no compatible opponent holdings/runouts.
    pub fn equity(&self, p: usize, reach_o: &[f32], dealt: Dealt) -> Vec<f32> {
        let spot = &*self.spot;
        let nh = spot.hands[p].len();
        let mut win = vec![0f64; nh];
        let mut tie = vec![0f64; nh];
        let mut valid = vec![0f64; nh];
        let board_len = spot.board.len() + dealt.len as usize;
        match board_len {
            5 => {
                sweep_buckets(
                    spot.river.get(&dealt),
                    p,
                    &spot.hands[p],
                    &spot.hands[1 - p],
                    reach_o,
                    &spot.same_combo[p],
                    &mut win,
                    &mut tie,
                    &mut valid,
                );
            }
            4 => {
                for c in 0..52u8 {
                    if spot.board_mask & (1 << c) != 0 || dealt.contains(c) {
                        continue;
                    }
                    let mut ro = reach_o.to_vec();
                    let cm = 1u64 << c;
                    for (j, h) in spot.hands[1 - p].iter().enumerate() {
                        if h.mask & cm != 0 {
                            ro[j] = 0.0;
                        }
                    }
                    sweep_buckets(
                        spot.river.get(&dealt.push(c)),
                        p,
                        &spot.hands[p],
                        &spot.hands[1 - p],
                        &ro,
                        &spot.same_combo[p],
                        &mut win,
                        &mut tie,
                        &mut valid,
                    );
                }
            }
            _ => {
                for t in 0..52u8 {
                    if spot.board_mask & (1 << t) != 0 {
                        continue;
                    }
                    let tm = 1u64 << t;
                    let mut ro_t = reach_o.to_vec();
                    for (j, h) in spot.hands[1 - p].iter().enumerate() {
                        if h.mask & tm != 0 {
                            ro_t[j] = 0.0;
                        }
                    }
                    for r in (t + 1)..52 {
                        if spot.board_mask & (1 << r) != 0 {
                            continue;
                        }
                        let rm = 1u64 << r;
                        let mut ro = ro_t.clone();
                        for (j, h) in spot.hands[1 - p].iter().enumerate() {
                            if h.mask & rm != 0 {
                                ro[j] = 0.0;
                            }
                        }
                        sweep_buckets(
                            spot.river.get(&Dealt::default().push(t).push(r)),
                            p,
                            &spot.hands[p],
                            &spot.hands[1 - p],
                            &ro,
                            &spot.same_combo[p],
                            &mut win,
                            &mut tie,
                            &mut valid,
                        );
                    }
                }
            }
        }
        (0..nh)
            .map(|i| {
                if valid[i] > 1e-12 {
                    ((win[i] + 0.5 * tie[i]) / valid[i]) as f32
                } else {
                    f32::NAN
                }
            })
            .collect()
    }
}
