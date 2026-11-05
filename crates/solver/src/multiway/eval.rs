//! Terminal counterfactual values for three players.
//!
//! For traverser hand h and opponents q, r every terminal needs
//!
//!   cfv(h) = sum over compatible (hq, hr) of pi_q(hq) pi_r(hr) u(h, hq, hr)
//!
//! where u depends only on how each opponent's hand compares with h (weaker,
//! tied, stronger) — see `payoff_table`. Writing each comparison class as a
//! difference of cumulative sets L (weaker), Q (weaker or tied) and A (all)
//! turns cfv(h) into a few "pair masses" M(X, Y)(h): the reach of compatible
//! opponent pairs with hq in X and hr in Y, both avoiding h's cards. Each mass
//! is exact via inclusion-exclusion over shared cards:
//!
//!   M = T'x T'y - sum_{c not in h} S'x[c] S'y[c] + K'xy
//!
//! with T the set's total reach, S[c] its reach through card c, primes
//! meaning "restricted to hands avoiding h" and K the reach of combos both
//! opponents hold. A river showdown sweeps hands in strength order so L/Q
//! sums are running totals; each hand then costs O(52).

use super::game::{MwRiverEval, MwSpot, NO_HAND};
use super::tree::{others, MwNode, NP};

/// Basis indices for the cumulative sets.
const L: usize = 0;
const Q: usize = 1;
const A: usize = 2;

/// Category (weaker / tied / stronger) indicator in the (L, Q, A) basis.
const B: [[f64; 3]; 3] = [[1.0, 0.0, 0.0], [-1.0, 1.0, 0.0], [0.0, -1.0, 1.0]];

/// Coefficients C[X][Y] with cfv(h) = sum C[X][Y] M(X, Y)(h).
pub fn basis_coeffs(pay: &[[f64; 3]; 3]) -> [[f64; 3]; 3] {
    let mut c = [[0.0; 3]; 3];
    for x in 0..3 {
        for y in 0..3 {
            let mut v = 0.0;
            for cq in 0..3 {
                for cr in 0..3 {
                    v += pay[cq][cr] * B[cq][x] * B[cr][y];
                }
            }
            c[x][y] = if v.abs() < 1e-12 { 0.0 } else { v };
        }
    }
    c
}

/// Running card sums for one opponent set.
#[derive(Clone)]
struct SetSums {
    t: f64,
    s: [f64; 52],
}

impl SetSums {
    fn new() -> Self {
        SetSums { t: 0.0, s: [0.0; 52] }
    }
    #[inline]
    fn add(&mut self, c1: u8, c2: u8, w: f64) {
        self.t += w;
        self.s[c1 as usize] += w;
        self.s[c2 as usize] += w;
    }
}

/// Counterfactual values for player `p` at a terminal. `dealt` lists the
/// cards dealt below the root board (needed for showdowns). `out` is fully
/// overwritten; hands that cannot reach this terminal get 0 or values the
/// caller masks.
pub fn terminal_cfv(
    spot: &MwSpot,
    node: &MwNode,
    dealt: &[u8],
    p: usize,
    reach: [&[f32]; NP],
    out: &mut [f32],
) {
    let pay = spot.payoff_table(node, p);
    let coef = basis_coeffs(&pay);
    let (q, r) = others(p);
    let only_all = (0..3).all(|x| (0..3).all(|y| (x == A && y == A) || coef[x][y] == 0.0));
    if only_all || node.kind != super::tree::KIND_TERM_SHOWDOWN {
        all_mass(spot, p, q, r, reach[q], reach[r], coef[A][A], out);
    } else {
        let eval = spot.river.get(dealt);
        showdown(spot, eval, p, q, r, reach[q], reach[r], &coef, out);
    }
    if let (Some(icm), super::tree::KIND_TERM_SHOWDOWN) = (&spot.icm, node.kind) {
        icm_order_terms(spot, icm.order(node, p), node, spot.river.get(dealt), p, q, r, reach, out);
    }
}

/// Adds the ICM corrections for the opponents' order (see `multiway::icm`).
#[allow(clippy::too_many_arguments)]
fn icm_order_terms(
    spot: &MwSpot,
    order: [f64; 4],
    node: &MwNode,
    eval: &MwRiverEval,
    p: usize,
    q: usize,
    r: usize,
    reach: [&[f32]; NP],
    out: &mut [f32],
) {
    let mut masses = vec![(0f64, 0f64); out.len()];
    let mut add = |bounds: &(dyn Fn(u32) -> (i64, i64) + Sync), dw: f64, dt: f64, masses: &mut Vec<(f64, f64)>| {
        if dw == 0.0 && dt == 0.0 {
            return;
        }
        order_masses(spot, eval, p, q, r, reach[q], reach[r], bounds, masses);
        for (o, &(w, t)) in out.iter_mut().zip(masses.iter()) {
            *o += (dw * w + dt * t) as f32;
        }
    };
    if node.live & (1 << p) == 0 {
        add(&|_| (NEG_INF, POS_INF), order[0], order[1], &mut masses);
    } else {
        add(&|s| (s as i64, POS_INF), order[0], order[1], &mut masses);
        add(&|s| (NEG_INF, s as i64), order[2], order[3], &mut masses);
    }
}

/// Dense 52x52 reach matrix of one opponent (P[a*52+b] = reach of combo ab)
/// plus its total and per-card sums.
fn dense(spot: &MwSpot, o: usize, reach: &[f32], only: Option<&[(u32, u16)]>) -> (Vec<f64>, SetSums) {
    let mut m = vec![0f64; 52 * 52];
    let mut sums = SetSums::new();
    let mut put = |j: usize| {
        let w = reach[j] as f64;
        if w != 0.0 {
            let h = &spot.hands[o][j];
            let (a, b) = (h.c1 as usize, h.c2 as usize);
            m[a * 52 + b] = w;
            m[b * 52 + a] = w;
            sums.add(h.c1, h.c2, w);
        }
    };
    match only {
        Some(list) => list.iter().for_each(|&(_, j)| put(j as usize)),
        None => (0..reach.len()).for_each(put),
    }
    (m, sums)
}

/// Same-combo reach product summed over combos both opponents hold.
fn same_combo_mass(spot: &MwSpot, q: usize, r: usize, reach_q: &[f32], reach_r: &[f32], list: impl Iterator<Item = usize>) -> f64 {
    let mut k = 0f64;
    for j in list {
        let jr = spot.combo_hand[r][spot.hand_combo[q][j] as usize];
        if jr != NO_HAND {
            k += reach_q[j] as f64 * reach_r[jr as usize] as f64;
        }
    }
    k
}

const PAR_CHUNK: usize = 32;

/// Reach mass of the opponents' compatible hand pairs for each of p's hands
/// (the normalizer that turns counterfactual values into per-hand EVs).
pub fn compatible_mass(spot: &MwSpot, p: usize, reach: [&[f32]; NP], out: &mut [f32]) {
    let (q, r) = others(p);
    all_mass(spot, p, q, r, reach[q], reach[r], 1.0, out);
}

/// Fold terminals and anything else whose payoff ignores hand strength:
/// cfv(h) = amount * M(A, A)(h).
#[allow(clippy::too_many_arguments)]
fn all_mass(
    spot: &MwSpot,
    p: usize,
    q: usize,
    r: usize,
    reach_q: &[f32],
    reach_r: &[f32],
    amount: f64,
    out: &mut [f32],
) {
    let (pq, sq) = dense(spot, q, reach_q, None);
    let (pr, sr) = dense(spot, r, reach_r, None);
    if sq.t == 0.0 || sr.t == 0.0 || amount == 0.0 {
        out.fill(0.0);
        return;
    }
    let k = same_combo_mass(spot, q, r, reach_q, reach_r, 0..reach_q.len());
    let hands = &spot.hands[p];
    let work = |i: usize, o: &mut f32| {
        let h = &hands[i];
        let (a, b) = (h.c1 as usize, h.c2 as usize);
        let (qa, qb) = (&pq[a * 52..a * 52 + 52], &pq[b * 52..b * 52 + 52]);
        let (ra, rb) = (&pr[a * 52..a * 52 + 52], &pr[b * 52..b * 52 + 52]);
        let tq = sq.t - sq.s[a] - sq.s[b] + qa[b];
        let tr = sr.t - sr.s[a] - sr.s[b] + ra[b];
        let mut dot = 0f64;
        let mut z = 0f64;
        for c in 0..52 {
            z += qa[c] * ra[c] + qb[c] * rb[c];
            dot += (sq.s[c] - qa[c] - qb[c]) * (sr.s[c] - ra[c] - rb[c]);
        }
        // c = a and c = b were included in the dot; take them back out.
        for c in [a, b] {
            dot -= (sq.s[c] - qa[c] - qb[c]) * (sr.s[c] - ra[c] - rb[c]);
        }
        *o = (amount * (tq * tr - dot + k - z + qa[b] * ra[b])) as f32;
    };
    run_hands(out, work);
}

fn run_hands(out: &mut [f32], work: impl Fn(usize, &mut f32) + Sync) {
    use rayon::prelude::*;
    if out.len() > 2 * PAR_CHUNK {
        out.par_chunks_mut(PAR_CHUNK).enumerate().for_each(|(ci, ch)| {
            for (k, o) in ch.iter_mut().enumerate() {
                work(ci * PAR_CHUNK + k, o);
            }
        });
    } else {
        for (i, o) in out.iter_mut().enumerate() {
            work(i, o);
        }
    }
}

/// Per strength group: the L (strictly weaker) and Q (weaker or tied) sums
/// of both opponents, and the matching same-combo masses.
struct Group {
    s: u32,
    low: [SetSums; 2],
    tied: [SetSums; 2],
    k_low: f64,
    k_tied: f64,
}

/// River showdown. Strength groups are swept once to snapshot the running
/// L/Q sums; hands are then evaluated in parallel against their group.
#[allow(clippy::too_many_arguments)]
fn showdown(
    spot: &MwSpot,
    eval: &MwRiverEval,
    p: usize,
    q: usize,
    r: usize,
    reach_q: &[f32],
    reach_r: &[f32],
    coef: &[[f64; 3]; 3],
    out: &mut [f32],
) {
    out.fill(0.0);
    let (sq, sr, spp) = (&eval.sorted[q], &eval.sorted[r], &eval.sorted[p]);
    let (pq, all_q) = dense(spot, q, reach_q, Some(sq));
    let (pr, all_r) = dense(spot, r, reach_r, Some(sr));
    if all_q.t == 0.0 || all_r.t == 0.0 {
        return;
    }
    let k_all = same_combo_mass(spot, q, r, reach_q, reach_r, sq.iter().map(|&(_, j)| j as usize));
    // Sweep: one Group per distinct strength among p's hands.
    let mut groups: Vec<Group> = Vec::new();
    let mut group_of = vec![u32::MAX; spot.hands[p].len()];
    let mut low = [SetSums::new(), SetSums::new()];
    let mut k_low = 0f64;
    let (mut iq, mut ir, mut ip) = (0usize, 0usize, 0usize);
    let add_q = |sums: &mut SetSums, k: &mut f64, j: usize| {
        let h = &spot.hands[q][j];
        let w = reach_q[j] as f64;
        sums.add(h.c1, h.c2, w);
        let jr = spot.combo_hand[r][spot.hand_combo[q][j] as usize];
        if jr != NO_HAND {
            *k += w * reach_r[jr as usize] as f64;
        }
    };
    let add_r = |sums: &mut SetSums, j: usize| {
        let h = &spot.hands[r][j];
        sums.add(h.c1, h.c2, reach_r[j] as f64);
    };
    while ip < spp.len() {
        let s = spp[ip].0;
        while iq < sq.len() && sq[iq].0 < s {
            add_q(&mut low[0], &mut k_low, sq[iq].1 as usize);
            iq += 1;
        }
        while ir < sr.len() && sr[ir].0 < s {
            add_r(&mut low[1], sr[ir].1 as usize);
            ir += 1;
        }
        let mut tied = low.clone();
        let mut k_tied = k_low;
        let mut jq = iq;
        while jq < sq.len() && sq[jq].0 == s {
            add_q(&mut tied[0], &mut k_tied, sq[jq].1 as usize);
            jq += 1;
        }
        let mut jr = ir;
        while jr < sr.len() && sr[jr].0 == s {
            add_r(&mut tied[1], sr[jr].1 as usize);
            jr += 1;
        }
        let g = groups.len() as u32;
        while ip < spp.len() && spp[ip].0 == s {
            group_of[spp[ip].1 as usize] = g;
            ip += 1;
        }
        groups.push(Group { s, low: low.clone(), tied, k_low, k_tied });
    }
    let need_q: [bool; 3] = std::array::from_fn(|x| (0..3).any(|y| coef[x][y] != 0.0));
    let need_r: [bool; 3] = std::array::from_fn(|y| (0..3).any(|x| coef[x][y] != 0.0));
    let hands = &spot.hands[p];
    let rp = &eval.rank_pair;
    let work = |i: usize, o: &mut f32| {
        let g = group_of[i];
        if g == u32::MAX {
            *o = 0.0;
            return;
        }
        let grp = &groups[g as usize];
        let s = grp.s;
        let h = &hands[i];
        let (a, b) = (h.c1 as usize, h.c2 as usize);
        let sets = [[&grp.low[0], &grp.tied[0], &all_q], [&grp.low[1], &grp.tied[1], &all_r]];
        let kk = [grp.k_low, grp.k_tied, k_all];
        // Membership-filtered rows: rows[o][kind][col][c], col 0 = card a.
        let mut rows = [[[[0f64; 52]; 2]; 3]; 2];
        for (o, pm) in [&pq, &pr].into_iter().enumerate() {
            for (col, x) in [a, b].into_iter().enumerate() {
                let src = &pm[x * 52..x * 52 + 52];
                let rk = &rp[x * 52..x * 52 + 52];
                for c in 0..52 {
                    let w = src[c];
                    rows[o][A][col][c] = w;
                    rows[o][L][col][c] = if rk[c] < s { w } else { 0.0 };
                    rows[o][Q][col][c] = if rk[c] <= s { w } else { 0.0 };
                }
            }
        }
        let mut v = 0f64;
        for x in 0..3 {
            if !need_q[x] {
                continue;
            }
            for y in 0..3 {
                let cxy = coef[x][y];
                if cxy == 0.0 || !need_r[y] {
                    continue;
                }
                let (sx, sy) = (sets[0][x], sets[1][y]);
                let (xa, xb) = (&rows[0][x][0], &rows[0][x][1]);
                let (ya, yb) = (&rows[1][y][0], &rows[1][y][1]);
                let (pxab, pyab) = (xa[b], ya[b]);
                let tx = sx.t - sx.s[a] - sx.s[b] + pxab;
                let ty = sy.t - sy.s[a] - sy.s[b] + pyab;
                let mut dot = 0f64;
                let mut z = 0f64;
                for c in 0..52 {
                    z += xa[c] * ya[c] + xb[c] * yb[c];
                    dot += (sx.s[c] - xa[c] - xb[c]) * (sy.s[c] - ya[c] - yb[c]);
                }
                for c in [a, b] {
                    dot -= (sx.s[c] - xa[c] - xb[c]) * (sy.s[c] - ya[c] - yb[c]);
                }
                v += cxy * (tx * ty - dot + kk[x.min(y)] - z + pxab * pyab);
            }
        }
        *o = v as f32;
    };
    run_hands(out, work);
}

/// O(n^3) reference used by tests.
pub fn terminal_cfv_brute(
    spot: &MwSpot,
    node: &MwNode,
    dealt: &[u8],
    p: usize,
    reach: [&[f32]; NP],
) -> Vec<f64> {
    let pay = spot.payoff_table(node, p);
    let (q, r) = others(p);
    let showdown = node.kind == super::tree::KIND_TERM_SHOWDOWN;
    let eval = if showdown { Some(spot.river.get(dealt)) } else { None };
    let mut dmask = 0u64;
    for &c in dealt {
        dmask |= 1u64 << c;
    }
    let rank = |o: usize, j: usize| -> u32 {
        let h = &spot.hands[o][j];
        eval.unwrap().rank[crate::cards::combo_index(h.c1, h.c2)]
    };
    let cat = |mine: u32, theirs: u32| if theirs < mine { 0 } else if theirs == mine { 1 } else { 2 };
    let cache = std::sync::Mutex::new(std::collections::HashMap::new());
    spot.hands[p]
        .iter()
        .enumerate()
        .map(|(i, h)| {
            if h.mask & dmask != 0 {
                return 0.0;
            }
            let mut v = 0f64;
            for (jq, hq) in spot.hands[q].iter().enumerate() {
                if hq.mask & (h.mask | dmask) != 0 {
                    continue;
                }
                for (jr, hr) in spot.hands[r].iter().enumerate() {
                    if hr.mask & (h.mask | hq.mask | dmask) != 0 {
                        continue;
                    }
                    let w = reach[q][jq] as f64 * reach[r][jr] as f64;
                    if w == 0.0 {
                        continue;
                    }
                    let u = match (&spot.icm, showdown) {
                        // Exact: every player's hand strength.
                        (Some(icm), true) => {
                            let mut st = [0i32; NP];
                            st[p] = rank(p, i) as i32;
                            st[q] = rank(q, jq) as i32;
                            st[r] = rank(r, jr) as i32;
                            icm.values(node, st, &mut cache.lock().unwrap())[p]
                        }
                        (_, true) => {
                            let s = rank(p, i);
                            pay[cat(s, rank(q, jq))][cat(s, rank(r, jr))]
                        }
                        _ => pay[0][0],
                    };
                    v += w * u;
                }
            }
            v
        })
        .collect()
}

// --- Ordered pair masses (ICM) -------------------------------------------

/// Running sums over one player's hands in strength order.
struct Cum {
    s: Vec<u32>,
    w: Vec<f64>,
    /// c[k] = sum of w[..k].
    c: Vec<f64>,
}

impl Cum {
    fn new(entries: impl Iterator<Item = (u32, f64)>) -> Cum {
        let (mut s, mut w, mut c) = (Vec::new(), Vec::new(), vec![0f64]);
        for (st, x) in entries {
            s.push(st);
            w.push(x);
            c.push(c[c.len() - 1] + x);
        }
        Cum { s, w, c }
    }
    /// Sum over strengths < t.
    #[inline]
    fn below(&self, t: i64) -> f64 {
        self.c[self.s.partition_point(|&x| (x as i64) < t)]
    }
    /// Sum over lo < strength < hi.
    #[inline]
    fn range(&self, lo: i64, hi: i64) -> f64 {
        if hi <= lo + 1 { 0.0 } else { self.below(hi) - self.below(lo + 1) }
    }
    #[inline]
    fn eq(&self, t: i64) -> f64 {
        self.below(t + 1) - self.below(t)
    }
    /// Sum over strengths >= t.
    #[inline]
    fn from(&self, t: i64) -> f64 {
        self.c[self.c.len() - 1] - self.below(t)
    }
}

/// One opponent's sums: all hands and, per card, the hands holding it.
struct OppCum {
    all: Cum,
    card: Vec<Cum>,
}

impl OppCum {
    fn new(spot: &MwSpot, o: usize, sorted: &[(u32, u16)], weight: impl Fn(usize) -> f64) -> OppCum {
        let mut per: Vec<Vec<(u32, f64)>> = vec![Vec::new(); 52];
        let mut all = Vec::with_capacity(sorted.len());
        for &(st, j) in sorted {
            let w = weight(j as usize);
            all.push((st, w));
            let h = &spot.hands[o][j as usize];
            per[h.c1 as usize].push((st, w));
            per[h.c2 as usize].push((st, w));
        }
        OppCum { all: Cum::new(all.into_iter()), card: per.into_iter().map(|v| Cum::new(v.into_iter())).collect() }
    }
}

pub const NEG_INF: i64 = -1;
pub const POS_INF: i64 = u32::MAX as i64 + 1;

/// Ordered pair masses for each of p's hands h: the reach of opponent hand
/// pairs (a for q, b for r), pairwise disjoint with h, whose strengths lie
/// strictly inside `bounds(h)` = (lo, hi), with a stronger than b (`.0`) and
/// tied with b (`.1`). Exact via inclusion-exclusion over the four cards of
/// b and h, the same way the 3x3 classes are.
#[allow(clippy::too_many_arguments)]
pub fn order_masses(
    spot: &MwSpot,
    eval: &MwRiverEval,
    p: usize,
    q: usize,
    r: usize,
    reach_q: &[f32],
    reach_r: &[f32],
    bounds: impl Fn(u32) -> (i64, i64) + Sync,
    out: &mut [(f64, f64)],
) {
    let (sq, sr) = (&eval.sorted[q], &eval.sorted[r]);
    let (pq, _) = dense(spot, q, reach_q, Some(sq));
    let (pr, _) = dense(spot, r, reach_r, Some(sr));
    let rk = &eval.rank_pair;
    let qc = OppCum::new(spot, q, sq, |j| reach_q[j] as f64);
    let rc = OppCum::new(spot, r, sr, |j| reach_r[j] as f64);
    // Per r hand b: reach times the q mass above b (u) and tied with b
    // (ut), both avoiding b's cards.
    let rank_of = |o: usize, j: usize| {
        let h = &spot.hands[o][j];
        rk[h.c1 as usize * 52 + h.c2 as usize]
    };
    let u_of = |j: usize| {
        let h = &spot.hands[r][j];
        let s = rank_of(r, j) as i64;
        let (b1, b2) = (h.c1 as usize, h.c2 as usize);
        reach_r[j] as f64
            * (qc.all.range(s, POS_INF) - qc.card[b1].range(s, POS_INF) - qc.card[b2].range(s, POS_INF))
    };
    let ut_of = |j: usize| {
        let h = &spot.hands[r][j];
        let s = rank_of(r, j) as i64;
        let (b1, b2) = (h.c1 as usize, h.c2 as usize);
        reach_r[j] as f64 * (qc.all.eq(s) - qc.card[b1].eq(s) - qc.card[b2].eq(s) + pq[b1 * 52 + b2])
    };
    let mut u = vec![0f64; reach_r.len()];
    let mut ut = vec![0f64; reach_r.len()];
    for &(_, j) in sr {
        u[j as usize] = u_of(j as usize);
        ut[j as usize] = ut_of(j as usize);
    }
    let uc = OppCum::new(spot, r, sr, |j| u[j]);
    let utc = OppCum::new(spot, r, sr, |j| ut[j]);
    let hands = &spot.hands[p];
    let work = |i: usize, o: &mut (f64, f64)| {
        let h = &hands[i];
        let (h1, h2) = (h.c1 as usize, h.c2 as usize);
        let sh = rk[h1 * 52 + h2] as i64;
        if sh == 0 {
            *o = (0.0, 0.0);
            return;
        }
        let (lo, hi) = bounds(sh as u32);
        let inside = |t: i64| lo < t && t < hi;
        let pr_h = pr[h1 * 52 + h2];
        let pq_h = pq[h1 * 52 + h2];
        // r mass avoiding h, strictly between lo and t / exactly at t.
        let rh_range = |t: i64| {
            rc.all.range(lo, t) - rc.card[h1].range(lo, t) - rc.card[h2].range(lo, t)
                + if lo < sh && sh < t { pr_h } else { 0.0 }
        };
        let rh_eq = |t: i64| {
            rc.all.eq(t) - rc.card[h1].eq(t) - rc.card[h2].eq(t) + if sh == t { pr_h } else { 0.0 }
        };
        // r's own copy of the combo h, if inside.
        let jr = spot.combo_hand[r][spot.pair_combo[h1 * 52 + h2] as usize];
        let (u_h, ut_h) = if jr != NO_HAND && inside(sh) { (u[jr as usize], ut[jr as usize]) } else { (0.0, 0.0) };
        // Singles and pairs of b's cards (u, ut).
        let mut w = uc.all.range(lo, hi) - uc.card[h1].range(lo, hi) - uc.card[h2].range(lo, hi) + u_h;
        let mut t = utc.all.range(lo, hi) - utc.card[h1].range(lo, hi) - utc.card[h2].range(lo, hi) + ut_h;
        // a strictly between b and hi, not just above b.
        if hi < POS_INF {
            w -= qc.all.from(hi) * rh_range(hi);
            for c in 0..52 {
                if c == h1 || c == h2 {
                    continue;
                }
                let qa = qc.card[c].from(hi);
                if qa == 0.0 {
                    continue;
                }
                let mut rb = rc.card[c].range(lo, hi);
                for hj in [h1, h2] {
                    if inside(rk[c * 52 + hj] as i64) {
                        rb -= pr[c * 52 + hj];
                    }
                }
                w += qa * rb;
            }
        }
        // a holds a card of h.
        for hj in [h1, h2] {
            let list = &qc.card[hj];
            for k in 0..list.s.len() {
                let sa = list.s[k] as i64;
                if !inside(sa) || list.w[k] == 0.0 {
                    continue;
                }
                w -= list.w[k] * rh_range(sa);
                t -= list.w[k] * rh_eq(sa);
            }
        }
        // a is h itself.
        if pq_h != 0.0 && inside(sh) {
            w += pq_h * rh_range(sh);
            t += pq_h * rh_eq(sh);
        }
        // a pairs a card x of b with a card of h.
        for hj in [h1, h2] {
            for x in 0..52 {
                if x == h1 || x == h2 {
                    continue;
                }
                let wa = pq[x * 52 + hj];
                if wa == 0.0 {
                    continue;
                }
                let ta = rk[x * 52 + hj] as i64;
                if !inside(ta) {
                    continue;
                }
                let mut rb = rc.card[x].range(lo, ta);
                let mut re = rc.card[x].eq(ta);
                for hk in [h1, h2] {
                    let tb = rk[x * 52 + hk] as i64;
                    if lo < tb && tb < ta {
                        rb -= pr[x * 52 + hk];
                    }
                    if tb == ta {
                        re -= pr[x * 52 + hk];
                    }
                }
                w += wa * rb;
                t += wa * re;
            }
        }
        *o = (w, t);
    };
    use rayon::prelude::*;
    out.par_iter_mut().enumerate().for_each(|(i, o)| work(i, o));
}
