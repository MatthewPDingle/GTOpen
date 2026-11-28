//! Three-player play with every hand at once.
//!
//! As `range`, for three seats. A hand's value at the end of a line now
//! depends on the hands of two opponents, who cannot hold each other's
//! cards either. For hand h facing seats q and r it is a sum of "pair
//! masses": the likelihood of every pair (hq, hr), hq from a set X of q's
//! hands and hr from a set Y of r's, where h, hq and hr share no card. A
//! pair mass is exact by counting the shared cards out:
//!
//!   M = T'x T'y - sum over cards c not in h of S'x[c] S'y[c] + K'xy
//!
//! with T a set's total likelihood, S[c] its likelihood through card c,
//! primes meaning "hands that avoid h only", and K the likelihood of the
//! same two cards being in both sets (taken out twice by the sum). At a
//! showdown the sets are an opponent's weaker hands and its tied hands,
//! kept as running totals while the hands are swept in rising strength, so
//! a hand costs a few passes over the deck.
//!
//! Strategies come from a `range::Policy`, decisions go to a
//! `range::Recorder`, and cards to come are tried or drawn as in `range`.
//! No range inputs and no river solve on the spot.

use rayon::prelude::*;

use super::abstraction::{strengths, Abstraction, Rng, Runout};
use super::range::{all_zero, pick_draws, At, Chance, NodeView, Policy, Recorder};
use super::tree::*;
use crate::cards::{combo_from_index, combo_index, Card, NUM_COMBOS};

const NP: usize = 3;

/// Per seat and hand: the value summed over the other two seats' ranges.
/// A seat that was not asked for has empty vectors.
pub struct Vals3 {
    /// Every seat playing its strategy.
    pub avg: [Vec<f32>; NP],
    /// The seat playing a perfect reply to the other two (empty unless
    /// asked for): from the first street on, from the turn on only, and on
    /// the river only. Before the street a reply starts on, the seat plays
    /// its own strategy.
    pub best: [[Vec<f32>; NP]; 3],
}

/// One opponent's range by card: `m[a * 52 + b]` is the likelihood of the
/// hand (a, b), `s[c]` the likelihood of holding card c, `t` the total.
struct Dense {
    m: Vec<f64>,
    t: f64,
    s: [f64; 52],
}

/// Total and per-card likelihood of a set of hands.
#[derive(Clone)]
struct Sums {
    t: f64,
    s: [f64; 52],
}

impl Sums {
    fn new() -> Sums {
        Sums { t: 0.0, s: [0.0; 52] }
    }
    #[inline]
    fn add(&mut self, a: usize, b: usize, w: f64) {
        self.t += w;
        self.s[a] += w;
        self.s[b] += w;
    }
    fn add_all(&mut self, o: &Sums) {
        self.t += o.t;
        for c in 0..52 {
            self.s[c] += o.s[c];
        }
    }
}

/// One set of one opponent's hands as hand (a, b) sees it: the set's hands
/// through card a and through card b, its likelihood through every other
/// card among hands that avoid a and b, and the total of those hands.
struct Seen {
    xa: [f64; 52],
    xb: [f64; 52],
    e: [f64; 52],
    t: f64,
    pab: f64,
}

impl Seen {
    /// `keep(strength)` says which hands are in the set.
    #[inline]
    fn new(d: &Dense, sums: &Sums, a: usize, b: usize, strength: Option<&[u32]>, keep: impl Fn(u32) -> bool) -> Seen {
        let mut v = Seen { xa: [0.0; 52], xb: [0.0; 52], e: [0.0; 52], t: 0.0, pab: 0.0 };
        let (ra, rb) = (&d.m[a * 52..a * 52 + 52], &d.m[b * 52..b * 52 + 52]);
        match strength {
            Some(st) => {
                let (ka, kb) = (&st[a * 52..a * 52 + 52], &st[b * 52..b * 52 + 52]);
                for c in 0..52 {
                    v.xa[c] = if keep(ka[c]) { ra[c] } else { 0.0 };
                    v.xb[c] = if keep(kb[c]) { rb[c] } else { 0.0 };
                }
            }
            None => {
                v.xa.copy_from_slice(ra);
                v.xb.copy_from_slice(rb);
            }
        }
        for c in 0..52 {
            v.e[c] = sums.s[c] - v.xa[c] - v.xb[c];
        }
        v.e[a] = 0.0;
        v.e[b] = 0.0;
        v.pab = v.xa[b];
        v.t = sums.t - sums.s[a] - sums.s[b] + v.pab;
        v
    }
}

/// The pair mass of two sets as one hand sees them. `k` is the likelihood
/// of the same two cards being in both sets, over all hands.
#[inline]
fn mass(x: &Seen, y: &Seen, k: f64) -> f64 {
    let mut dot = 0.0f64;
    let mut z = 0.0f64;
    for c in 0..52 {
        dot += x.e[c] * y.e[c];
        z += x.xa[c] * y.xa[c] + x.xb[c] * y.xb[c];
    }
    x.t * y.t - dot + k - z + x.pab * y.pab
}

/// River showdown strengths on each board: by hand (0 for a hand that
/// cannot be held), the hands in rising order, and by card pair.
struct River {
    key: Vec<Vec<u32>>,
    order: Vec<Vec<u16>>,
    by_pair: Vec<Vec<u32>>,
}

struct Cx<'a> {
    policy: &'a dyn Policy,
    chance: Chance,
    want_best: bool,
    /// The seats whose values are worked out.
    want: [bool; NP],
    seed: u64,
}

pub struct Walker3<'a> {
    pub tree: &'a BpTree,
    pub abs: &'a Abstraction,
    c1: [u8; NUM_COMBOS],
    c2: [u8; NUM_COMBOS],
}

fn others(p: usize) -> (usize, usize) {
    ((p + 1) % NP, (p + 2) % NP)
}

impl<'a> Walker3<'a> {
    pub fn new(tree: &'a BpTree, abs: &'a Abstraction) -> Result<Walker3<'a>, String> {
        if tree.players() != NP {
            return Err("three-player whole-range play needs exactly three players".into());
        }
        let mut w = Walker3 { tree, abs, c1: [0; NUM_COMBOS], c2: [0; NUM_COMBOS] };
        for h in 0..NUM_COMBOS {
            let (a, b) = combo_from_index(h);
            w.c1[h] = a;
            w.c2[h] = b;
        }
        Ok(w)
    }

    #[inline]
    fn hits(&self, h: usize, mask: u64) -> bool {
        (1u64 << self.c1[h] | 1u64 << self.c2[h]) & mask != 0
    }

    /// Every hand that fits the starting boards, with weight 1.
    pub fn root_reach(&self) -> Vec<f32> {
        (0..NUM_COMBOS).map(|h| if self.hits(h, self.abs.dead) { 0.0 } else { 1.0 }).collect()
    }

    /// Number of ways to deal three hands at the root.
    pub fn root_triples(&self) -> f64 {
        let reach = self.root_reach();
        let mass = self.pair_mass(&reach, &reach);
        (0..NUM_COMBOS).map(|h| reach[h] as f64 * mass[h]).sum()
    }

    /// Pairs of opposing hands one hand can face at the root.
    pub fn root_norm(&self) -> f32 {
        let free = 52.0 - self.abs.dead.count_ones() as f32;
        (free - 2.0) * (free - 3.0) / 2.0 * (free - 4.0) * (free - 5.0) / 2.0
    }

    fn dense(&self, reach: &[f32]) -> Dense {
        let mut d = Dense { m: vec![0.0; 52 * 52], t: 0.0, s: [0.0; 52] };
        for h in 0..NUM_COMBOS {
            let w = reach[h] as f64;
            if w != 0.0 {
                let (a, b) = (self.c1[h] as usize, self.c2[h] as usize);
                d.m[a * 52 + b] = w;
                d.m[b * 52 + a] = w;
                d.t += w;
                d.s[a] += w;
                d.s[b] += w;
            }
        }
        d
    }

    /// For each hand, the summed likelihood of the pairs of hands, one from
    /// each range, that share no card with it or with each other.
    pub fn pair_mass(&self, reach_q: &[f32], reach_r: &[f32]) -> Vec<f64> {
        let (dq, dr) = (self.dense(reach_q), self.dense(reach_r));
        self.all_mass(&dq, &dr, same(reach_q, reach_r))
    }

    /// The pair mass of two whole ranges for every hand. Written out, the
    /// sum over cards in a pair mass is a handful of terms that do not
    /// depend on the hand, plus entries of the product of the two ranges'
    /// card tables: one product serves every hand.
    fn all_mass(&self, dq: &Dense, dr: &Dense, k: f64) -> Vec<f64> {
        let mut out = vec![0.0f64; NUM_COMBOS];
        if dq.t == 0.0 || dr.t == 0.0 {
            return out;
        }
        fn row(d: &Dense, i: usize) -> &[f64] {
            &d.m[i * 52..i * 52 + 52]
        }
        // g[i * 52 + j]: hands of q through card i against hands of r
        // through card j, summed over the card they share.
        let mut g = vec![0.0f64; 52 * 52];
        let mut vq = [0.0f64; 52];
        let mut vr = [0.0f64; 52];
        for i in 0..52 {
            if dq.s[i] != 0.0 {
                let ri = row(dq, i);
                vq[i] = (0..52).map(|c| ri[c] * dr.s[c]).sum();
                for j in 0..52 {
                    if dr.s[j] != 0.0 {
                        let rj = row(dr, j);
                        g[i * 52 + j] = (0..52).map(|c| ri[c] * rj[c]).sum();
                    }
                }
            }
            if dr.s[i] != 0.0 {
                let ri = row(dr, i);
                vr[i] = (0..52).map(|c| ri[c] * dq.s[c]).sum();
            }
        }
        let d: f64 = (0..52).map(|c| dq.s[c] * dr.s[c]).sum();
        for h in 0..NUM_COMBOS {
            let (a, b) = (self.c1[h] as usize, self.c2[h] as usize);
            let (pq, pr) = (dq.m[a * 52 + b], dr.m[a * 52 + b]);
            let tq = dq.t - dq.s[a] - dq.s[b] + pq;
            let tr = dr.t - dr.s[a] - dr.s[b] + pr;
            out[h] = tq * tr - d + vq[a] + vq[b] + vr[a] + vr[b]
                - 2.0 * g[a * 52 + a]
                - 2.0 * g[b * 52 + b]
                - g[a * 52 + b]
                - g[b * 52 + a]
                + (dq.s[a] - pq) * (dr.s[a] - pr)
                + (dq.s[b] - pq) * (dr.s[b] - pr)
                + k
                + pq * pr;
        }
        out
    }

    /// The same, one hand at a time (the plain formula).
    #[cfg(test)]
    pub fn pair_mass_plain(&self, reach_q: &[f32], reach_r: &[f32]) -> Vec<f64> {
        let (dq, dr) = (self.dense(reach_q), self.dense(reach_r));
        let k = same(reach_q, reach_r);
        let (sq, sr) = (Sums { t: dq.t, s: dq.s }, Sums { t: dr.t, s: dr.s });
        (0..NUM_COMBOS)
            .map(|h| {
                let (a, b) = (self.c1[h] as usize, self.c2[h] as usize);
                mass(&Seen::new(&dq, &sq, a, b, None, |_| true), &Seen::new(&dr, &sr, a, b, None, |_| true), k)
            })
            .collect()
    }

    fn river(&self, runout: &Runout) -> River {
        let nb = self.abs.num_boards();
        let fulls: Vec<[Card; 5]> = (0..nb).map(|b| self.abs.full_board(b, runout)).collect();
        let all = fulls.iter().flatten().fold(0u64, |m, &c| m | 1u64 << c);
        let mut r = River { key: Vec::new(), order: Vec::new(), by_pair: Vec::new() };
        for full in &fulls {
            let key = strengths(full, all);
            let mut order: Vec<u16> = (0..NUM_COMBOS as u16).filter(|&h| key[h as usize] != 0).collect();
            order.sort_unstable_by_key(|&h| key[h as usize]);
            let mut by_pair = vec![0u32; 52 * 52];
            for a in 0..52u8 {
                for b in 0..a {
                    let k = key[combo_index(a, b)];
                    by_pair[a as usize * 52 + b as usize] = k;
                    by_pair[b as usize * 52 + a as usize] = k;
                }
            }
            r.key.push(key);
            r.order.push(order);
            r.by_pair.push(by_pair);
        }
        r
    }

    /// What every hand of seat `p` earns at the end of a line, summed over
    /// the other two seats' ranges.
    fn terminal(&self, node_idx: u32, p: usize, reach: &[Vec<f32>; NP], dense: &[Option<Dense>; NP], river: Option<&River>) -> Vec<f32> {
        let node = &self.tree.nodes[node_idx as usize];
        let (q, r) = others(p);
        let (dq, dr) = (dense[q].as_ref().expect("range by card"), dense[r].as_ref().expect("range by card"));
        if dq.t == 0.0 || dr.t == 0.0 {
            return vec![0.0; NUM_COMBOS];
        }
        let k_all = same(&reach[q], &reach[r]);
        let base = self.all_mass(dq, dr, k_all);
        let put = self.tree.put(node_idx, p) as f64;
        let live = |s: usize| node.live >> s & 1 != 0;
        if node.kind == KIND_FOLD || !live(p) {
            let gain = if live(p) { node.pot_net as f64 - put } else { -put };
            return base.iter().map(|&m| (gain * m) as f32).collect();
        }
        let river = river.expect("river strengths");
        let nb = self.abs.num_boards();
        let win = node.pot_net as f64 / nb as f64;
        let mut out: Vec<f64> = base.iter().map(|&m| -put * m).collect();
        let all = [Sums { t: dq.t, s: dq.s }, Sums { t: dr.t, s: dr.s }];
        let ds = [dq, dr];
        let folded = [!live(q), !live(r)];
        let (rq, rr) = (&reach[q], &reach[r]);
        for b in 0..nb {
            let (key, order, by_pair) = (&river.key[b], &river.order[b], &river.by_pair[b]);
            let mut low = [Sums::new(), Sums::new()];
            let mut k_low = 0.0f64;
            let mut i = 0;
            while i < order.len() {
                let s = key[order[i] as usize];
                let mut tie = [Sums::new(), Sums::new()];
                let mut k_tie = 0.0f64;
                let mut j = i;
                while j < order.len() && key[order[j] as usize] == s {
                    let h = order[j] as usize;
                    let (a, c) = (self.c1[h] as usize, self.c2[h] as usize);
                    let (wq, wr) = (rq[h] as f64, rr[h] as f64);
                    tie[0].add(a, c, wq);
                    tie[1].add(a, c, wr);
                    k_tie += wq * wr;
                    j += 1;
                }
                for &h in &order[i..j] {
                    let h = h as usize;
                    let (a, c) = (self.c1[h] as usize, self.c2[h] as usize);
                    // Each opponent's sets: weaker and tied hands when it
                    // is still in, every hand when it has folded.
                    let seen: [[Option<Seen>; 2]; 2] = std::array::from_fn(|o| {
                        if folded[o] {
                            [Some(Seen::new(ds[o], &all[o], a, c, None, |_| true)), None]
                        } else {
                            [
                                (low[o].t != 0.0).then(|| Seen::new(ds[o], &low[o], a, c, Some(by_pair), |k| k != 0 && k < s)),
                                (tie[o].t != 0.0).then(|| Seen::new(ds[o], &tie[o], a, c, Some(by_pair), |k| k == s)),
                            ]
                        }
                    });
                    let mut share = 0.0f64;
                    for x in 0..2 {
                        let Some(sx) = &seen[0][x] else { continue };
                        for y in 0..2 {
                            let Some(sy) = &seen[1][y] else { continue };
                            // Tied opponents split the pot with the hand.
                            let ties = (!folded[0] && x == 1) as usize + (!folded[1] && y == 1) as usize;
                            let k = match (folded[0], folded[1]) {
                                (false, false) if x != y => 0.0,
                                (false, _) => [k_low, k_tie][x],
                                (true, _) => [k_low, k_tie][y],
                            };
                            share += mass(sx, sy, k) / (ties + 1) as f64;
                        }
                    }
                    out[h] += win * share;
                }
                low[0].add_all(&tie[0]);
                low[1].add_all(&tie[1]);
                k_low += k_tie;
                i = j;
            }
        }
        out.iter().map(|&v| v as f32).collect()
    }

    /// Walk the game from the root with every hand in every seat. `only`
    /// limits the work to one seat's values (what a recorder of that seat's
    /// decisions needs); `rng` is used only when cards are sampled.
    pub fn run(
        &self,
        policy: &dyn Policy,
        chance: Chance,
        want_best: bool,
        only: Option<usize>,
        rec: Option<&mut dyn Recorder>,
        rng: &mut Rng,
    ) -> Vals3 {
        let reach = [self.root_reach(), self.root_reach(), self.root_reach()];
        self.run_from(&reach, policy, chance, want_best, only, rec, rng)
    }

    /// As `run`, from any starting ranges.
    #[allow(clippy::too_many_arguments)]
    pub fn run_from(
        &self,
        reach: &[Vec<f32>; NP],
        policy: &dyn Policy,
        chance: Chance,
        want_best: bool,
        only: Option<usize>,
        mut rec: Option<&mut dyn Recorder>,
        rng: &mut Rng,
    ) -> Vals3 {
        let want = std::array::from_fn(|p| only.map_or(true, |s| s == p));
        let cx = Cx { policy, chance, want_best, want, seed: rng.next_u64() };
        let root = self.abs.root_street as usize;
        let runout: Runout = [[0; 2]; 2];
        let river = (root == 2).then(|| self.river(&runout));
        self.eval(&cx, &mut rec, rng, 0, root, reach, &runout, self.abs.dead, river.as_ref())
    }

    fn zeros(&self, cx: &Cx) -> Vals3 {
        let avg: [Vec<f32>; NP] = std::array::from_fn(|p| if cx.want[p] { vec![0.0f32; NUM_COMBOS] } else { Vec::new() });
        let best = self.best_like(cx, &avg);
        Vals3 { avg, best }
    }

    fn best_like(&self, cx: &Cx, avg: &[Vec<f32>; NP]) -> [[Vec<f32>; NP]; 3] {
        if cx.want_best {
            [avg.clone(), avg.clone(), avg.clone()]
        } else {
            Default::default()
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn eval(
        &self,
        cx: &Cx,
        rec: &mut Option<&mut dyn Recorder>,
        rng: &mut Rng,
        node_idx: u32,
        have: usize,
        reach: &[Vec<f32>; NP],
        runout: &Runout,
        used: u64,
        river: Option<&River>,
    ) -> Vals3 {
        let node = &self.tree.nodes[node_idx as usize];
        // A seat's values are zero once either opponent's range is empty.
        let empty: [bool; NP] = std::array::from_fn(|p| all_zero(&reach[p]));
        let alive = |p: usize| {
            let (q, r) = others(p);
            cx.want[p] && !empty[q] && !empty[r]
        };
        if !(0..NP).any(alive) {
            return self.zeros(cx);
        }
        let need = if node.kind == KIND_SHOWDOWN { 2 } else { node.street as usize };
        if node.kind != KIND_FOLD && have < need {
            return self.deal_street(cx, rec, rng, node_idx, have, reach, runout, used);
        }
        if node.kind != KIND_ACTION {
            let dense: [Option<Dense>; NP] =
                std::array::from_fn(|o| (0..NP).any(|p| p != o && alive(p)).then(|| self.dense(&reach[o])));
            let avg: [Vec<f32>; NP] = std::array::from_fn(|p| {
                if alive(p) {
                    self.terminal(node_idx, p, reach, &dense, river)
                } else if cx.want[p] {
                    vec![0.0f32; NUM_COMBOS]
                } else {
                    Vec::new()
                }
            });
            let best = self.best_like(cx, &avg);
            return Vals3 { avg, best };
        }
        let actor = node.player as usize;
        let na = node.num_children as usize;
        let street = node.street as usize;
        let mut sigma = vec![0.0f32; na * NUM_COMBOS];
        cx.policy.strategies(&At { node_idx, runout, used, range: None }, &mut sigma);
        let mut out = self.zeros(cx);
        if cx.want_best && cx.want[actor] {
            // A reply that starts on a later street plays the mix here.
            for (k, b) in out.best.iter_mut().enumerate() {
                if street >= k {
                    b[actor].fill(f32::NEG_INFINITY);
                }
            }
        }
        let recording = rec.is_some() && cx.want[actor];
        let mut action_vals: Vec<Vec<f32>> = Vec::new();
        let mut child_reach = reach.clone();
        for a in 0..na {
            let sa = &sigma[a * NUM_COMBOS..(a + 1) * NUM_COMBOS];
            let r: Vec<f32> = (0..NUM_COMBOS).map(|h| reach[actor][h] * sa[h]).collect();
            if all_zero(&r) && !recording && !(cx.want_best && cx.want[actor]) {
                // Never played: adds nothing to any seat's value.
                continue;
            }
            child_reach[actor] = r;
            let v = self.eval(cx, rec, rng, self.tree.child(node, a), have, &child_reach, runout, used, river);
            for p in 0..NP {
                if !cx.want[p] {
                    continue;
                }
                if p == actor {
                    for h in 0..NUM_COMBOS {
                        out.avg[p][h] += sa[h] * v.avg[p][h];
                    }
                } else {
                    for h in 0..NUM_COMBOS {
                        out.avg[p][h] += v.avg[p][h];
                    }
                }
                if cx.want_best {
                    for (k, b) in out.best.iter_mut().enumerate() {
                        let vb = &v.best[k][p];
                        if p != actor {
                            for h in 0..NUM_COMBOS {
                                b[p][h] += vb[h];
                            }
                        } else if street >= k {
                            for h in 0..NUM_COMBOS {
                                if vb[h] > b[p][h] {
                                    b[p][h] = vb[h];
                                }
                            }
                        } else {
                            for h in 0..NUM_COMBOS {
                                b[p][h] += sa[h] * vb[h];
                            }
                        }
                    }
                }
            }
            if recording {
                let mut v = v;
                action_vals.push(std::mem::take(&mut v.avg[actor]));
            }
        }
        if recording {
            if let Some(r) = rec.as_deref_mut() {
                let (q, o) = others(actor);
                let opp_mass: Vec<f32> = self.pair_mass(&reach[q], &reach[o]).iter().map(|&m| m as f32).collect();
                r.node(&NodeView {
                    node_idx,
                    runout,
                    used,
                    actor,
                    sigma: &sigma,
                    own_reach: &reach[actor],
                    opp_mass: &opp_mass,
                    action_vals: &action_vals,
                    node_val: &out.avg[actor],
                    range: None,
                });
            }
        }
        out
    }

    /// Deal the next street on every board and average over the cards.
    #[allow(clippy::too_many_arguments)]
    fn deal_street(
        &self,
        cx: &Cx,
        rec: &mut Option<&mut dyn Recorder>,
        rng: &mut Rng,
        node_idx: u32,
        have: usize,
        reach: &[Vec<f32>; NP],
        runout: &Runout,
        used: u64,
    ) -> Vals3 {
        let nb = self.abs.num_boards();
        let next = have + 1;
        // Cards left once the three hands are out of the deck.
        let left = (52 - used.count_ones()) as f64 - 6.0;
        let prob = if nb == 1 { 1.0 / left } else { 1.0 / (left * (left - 1.0)) };
        let (draws, total) = pick_draws(self.abs, cx.chance, cx.seed, have, runout, used);
        let scale = (prob * total as f64 / draws.len() as f64) as f32;
        let one = |draw: &[Card; 2], rec: &mut Option<&mut dyn Recorder>, rng: &mut Rng| -> Vals3 {
            let mut ro = *runout;
            let mut mask = 0u64;
            for b in 0..nb {
                ro[b][next - 1] = draw[b];
                mask |= 1u64 << draw[b];
            }
            let mut r = reach.clone();
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    for p in r.iter_mut() {
                        p[h] = 0.0;
                    }
                }
            }
            let river = (next == 2).then(|| self.river(&ro));
            let mut v = self.eval(cx, rec, rng, node_idx, next, &r, &ro, used | mask, river.as_ref());
            for h in 0..NUM_COMBOS {
                if self.hits(h, mask) {
                    for p in 0..NP {
                        if cx.want[p] {
                            v.avg[p][h] = 0.0;
                            if cx.want_best {
                                for b in v.best.iter_mut() {
                                    b[p][h] = 0.0;
                                }
                            }
                        }
                    }
                }
            }
            v
        };
        let add = |mut acc: Vals3, v: Vals3| {
            for p in 0..NP {
                if !cx.want[p] {
                    continue;
                }
                for h in 0..NUM_COMBOS {
                    acc.avg[p][h] += v.avg[p][h];
                }
                if cx.want_best {
                    for (a, b) in acc.best.iter_mut().zip(&v.best) {
                        for h in 0..NUM_COMBOS {
                            a[p][h] += b[p][h];
                        }
                    }
                }
            }
            acc
        };
        // The first cards dealt fan out over the threads, unless a recorder
        // is listening (it takes the decisions in order).
        let mut sum = if have == self.abs.root_street as usize && rec.is_none() {
            let seeds: Vec<u64> = draws.iter().map(|_| rng.next_u64()).collect();
            draws
                .par_iter()
                .zip(seeds.par_iter())
                .map(|(d, &seed)| one(d, &mut None, &mut Rng::new(seed)))
                .reduce(|| self.zeros(cx), add)
        } else {
            let mut acc = self.zeros(cx);
            for d in &draws {
                acc = add(acc, one(d, rec, rng));
            }
            acc
        };
        for p in 0..NP {
            sum.avg[p].iter_mut().for_each(|x| *x *= scale);
            for b in sum.best.iter_mut() {
                b[p].iter_mut().for_each(|x| *x *= scale);
            }
        }
        sum
    }
}

/// The likelihood of the same two cards being in both ranges.
fn same(reach_q: &[f32], reach_r: &[f32]) -> f64 {
    (0..NUM_COMBOS).map(|h| reach_q[h] as f64 * reach_r[h] as f64).sum()
}
