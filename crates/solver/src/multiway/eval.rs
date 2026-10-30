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
use super::tree::{others, payoff_table, MwNode, NP};

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
    let cfg = &spot.tree.config;
    let pay = payoff_table(node, p, cfg.rake_pct, cfg.rake_cap);
    let coef = basis_coeffs(&pay);
    let (q, r) = others(p);
    let only_all = (0..3).all(|x| (0..3).all(|y| (x == A && y == A) || coef[x][y] == 0.0));
    if only_all || node.kind != super::tree::KIND_TERM_SHOWDOWN {
        all_mass(spot, p, q, r, reach[q], reach[r], coef[A][A], out);
    } else {
        let eval = spot.river.get(dealt);
        showdown(spot, eval, p, q, r, reach[q], reach[r], &coef, out);
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
    let cfg = &spot.tree.config;
    let pay = payoff_table(node, p, cfg.rake_pct, cfg.rake_cap);
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
                    let u = if showdown {
                        let s = rank(p, i);
                        pay[cat(s, rank(q, jq))][cat(s, rank(r, jr))]
                    } else {
                        pay[0][0]
                    };
                    v += w * u;
                }
            }
            v
        })
        .collect()
}
