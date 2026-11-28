//! Card removal (blockers) for the 169-class preflop model.
//!
//! The plain model treats every seat's hand class as independent of the
//! traverser's, so every class gets the same chance that the others fold.
//! With `card_removal` on, each opponent's range is conditioned on the
//! traverser's two cards before it is used: an opponent class `j` keeps only
//! the combos that share no card with one fixed combo of hero class `h`, and
//! the 1,225 two-card holdings left in a 50-card deck replace the 1,326 of a
//! full deck. Reaches already carry the class prior (`class_prob`), so
//!
//! `P(hero h, opponent j) = class_prob(h) * class_prob(j) * W[h][j]`, with
//! `W[h][j] = (1326/1225) * compatible(h, j) / combos(j)`,
//!
//! is the exact joint deal probability, and `W` is symmetric. Heads-up the
//! correction is exact at the class level (the equity table already averages
//! each class pair over compatible deals). With two or more opponents each
//! one is conditioned on the hero's cards only; blocking between opponents
//! is still ignored, as in the plain model.
//!
//! `conditioned_mass` computes `sum_j reach[j] * W[h][j]` for every `h` in
//! O(169) via inclusion-exclusion over the hero's two cards: by suit
//! symmetry an opponent's mass on combos holding one specific card depends
//! only on that card's rank.

use std::sync::OnceLock;

use super::{
    balanced_family,
    equity::{class_combos, class_parts, NUM_CLASSES},
    PreflopSolver, KIND_POT_SHARE,
};

/// 1326 two-card holdings in a full deck over the 1225 left after two cards
/// are dealt.
pub const DECK_SCALE: f64 = 1326.0 / 1225.0;

/// How many of class `j`'s combos hold one specific card of rank `rank`.
fn combos_with_card(j: usize, rank: u8) -> f64 {
    let (hi, lo, suited) = class_parts(j);
    if hi == lo {
        if hi == rank {
            3.0
        } else {
            0.0
        }
    } else if hi == rank || lo == rank {
        if suited {
            1.0
        } else {
            3.0
        }
    } else {
        0.0
    }
}

/// For every hero class `h`, the opponent's reach mass that is compatible
/// with one combo of `h`, rescaled to the 50-card deck: `sum_j reach[j] *
/// W[h][j]`. A full random range (`reach = class_prob`) gives exactly 1.
pub fn conditioned_mass(reach: &[f32], out: &mut [f64; NUM_CLASSES]) {
    let mut total = 0f64;
    let mut per_card = [0f64; 13];
    for (j, &r) in reach.iter().enumerate().take(NUM_CLASSES) {
        let r = r as f64;
        if r == 0.0 {
            continue;
        }
        total += r;
        let per_combo = r / class_combos(j) as f64;
        let (hi, lo, _) = class_parts(j);
        per_card[hi as usize] += per_combo * combos_with_card(j, hi);
        if lo != hi {
            per_card[lo as usize] += per_combo * combos_with_card(j, lo);
        }
    }
    for (h, o) in out.iter_mut().enumerate() {
        let (hi, lo, _) = class_parts(h);
        // Combos touching either hero card: those with card 1, plus those
        // with card 2, less the one combo holding both (hero's own combo).
        let own = reach[h] as f64 / class_combos(h) as f64;
        let compatible = total - per_card[hi as usize] - per_card[lo as usize] + own;
        *o = (DECK_SCALE * compatible).max(0.0);
    }
}

/// Number of class `j` combos sharing no card with one fixed combo of class
/// `h` (counted on real cards).
fn compatible_combos(h: usize, j: usize) -> f64 {
    let (hi, lo, suited) = class_parts(h);
    // A representative hero combo: suits 0 and (suited ? 0 : 1).
    let hero = [(hi, 0u8), (lo, if suited { 0 } else { 1 })];
    let (jhi, jlo, jsuited) = class_parts(j);
    let mut n = 0;
    for s1 in 0..4u8 {
        for s2 in 0..4u8 {
            let valid = if jhi == jlo {
                s1 < s2
            } else if jsuited {
                s1 == s2
            } else {
                s1 != s2
            };
            if !valid {
                continue;
            }
            let (a, b) = ((jhi, s1), (jlo, s2));
            if !hero.contains(&a) && !hero.contains(&b) {
                n += 1;
            }
        }
    }
    n as f64
}

/// The symmetric weight table `W[h * 169 + j]` (see the module docs).
pub fn weights() -> &'static [f32] {
    static W: OnceLock<Vec<f32>> = OnceLock::new();
    W.get_or_init(|| {
        let mut w = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            for j in 0..NUM_CLASSES {
                w[h * NUM_CLASSES + j] =
                    (DECK_SCALE * compatible_combos(h, j) / class_combos(j) as f64) as f32;
            }
        }
        w
    })
}

impl PreflopSolver {
    /// `chip_terminal_value` with card removal: each hero class's value
    /// times its own chance that the other seats hold their reaching hands.
    /// Heads-up showdowns also condition the opponent's range on the hero's
    /// cards (exact at the class level). Folds, a folded traverser, side pots
    /// and pots of three or more keep the plain per-class value given the
    /// opponents' ranges, reweighted per class.
    pub(super) fn removal_terminal_value(
        &self,
        node: usize,
        p: usize,
        reaches: &[Vec<f32>],
        out: &mut [f32],
    ) {
        let nd = &self.nodes[node];
        let mut prob = [1f64; NUM_CLASSES];
        let mut mass = [0f64; NUM_CLASSES];
        let mut plain = 1f64;
        for q in (0..self.n).filter(|&q| q != p) {
            conditioned_mass(&reaches[q], &mut mass);
            for h in 0..NUM_CLASSES {
                prob[h] *= mass[h];
            }
            plain *= reaches[q].iter().sum::<f32>() as f64;
        }
        if !(plain > 0.0) {
            out.iter_mut().for_each(|v| *v = 0.0);
            return;
        }
        let me = 1u32 << p;
        if nd.kind == KIND_POT_SHARE
            && nd.live & me != 0
            && nd.live.count_ones() == 2
            && nd.side_pots.is_empty()
        {
            let q = (0..self.n)
                .find(|&q| q != p && nd.live & (1 << q) != 0)
                .expect("a second live seat");
            self.removal_heads_up(node, p, &reaches[q], &prob, out);
            return;
        }
        self.plain_terminal_value(node, p, reaches, out);
        for h in 0..NUM_CLASSES {
            out[h] = (out[h] as f64 / plain * prob[h]) as f32;
        }
    }

    /// Heads-up showdown or flop leaf: the plain model's pricing with the
    /// opponent's range conditioned on each hero class's cards.
    fn removal_heads_up(
        &self,
        node: usize,
        p: usize,
        opp: &[f32],
        prob: &[f64; NUM_CLASSES],
        out: &mut [f32],
    ) {
        let nd = &self.nodes[node];
        let w = weights();
        let inv_p = nd.invested[p];
        let pot_eff = nd.pot - self.rake_of(nd.pot);
        if balanced_family(&self.cfg.realization) {
            let corr = self.leaf_correction(node, p);
            let r = nd.r[p];
            let blend = ((r - 1.0).abs() / 0.08).min(1.0) as f64;
            let tables = self.balanced_tables();
            let rel = &tables.rel[if r < 1.0 { 0 } else { 1 }];
            for h in 0..NUM_CLASSES {
                let row = &w[h * NUM_CLASSES..][..NUM_CLASSES];
                let (raw_row, rel_row) = (
                    &tables.raw[h * NUM_CLASSES..][..NUM_CLASSES],
                    &rel[h * NUM_CLASSES..][..NUM_CLASSES],
                );
                let (mut norm, mut raw, mut relative) = (0f64, 0f64, 0f64);
                for j in 0..NUM_CLASSES {
                    let d = opp[j] as f64 * row[j] as f64;
                    norm += d;
                    raw += d * raw_row[j] as f64;
                    relative += d * rel_row[j] as f64;
                }
                if !(norm > 0.0) {
                    out[h] = 0.0;
                    continue;
                }
                let share = (raw + blend * (relative - raw)) / norm;
                let learned = corr.map_or(0.0, |c| nd.pot * c[h] as f64);
                out[h] = (prob[h] * (pot_eff * share + learned - inv_p)) as f32;
            }
            return;
        }
        let mut min_left = f64::MAX;
        for i in (0..self.n).filter(|&i| nd.live & (1 << i) != 0) {
            min_left = min_left.min(self.cfg.left(i, nd.invested[i]));
        }
        let spr = (min_left / nd.pot).max(0.0);
        let rp = nd.r[p] as f64;
        for h in 0..NUM_CLASSES {
            let row = &w[h * NUM_CLASSES..][..NUM_CLASSES];
            let (mut norm, mut eq) = (0f64, 0f64);
            for j in 0..NUM_CLASSES {
                let d = opp[j] as f64 * row[j] as f64;
                norm += d;
                eq += d * self.eq.eq(h, j) as f64;
            }
            if !(norm > 0.0) {
                out[h] = 0.0;
                continue;
            }
            let eqp = eq / norm;
            // Calibrated R (legacy) as in plain_terminal_value: gross pot.
            let share = match (self.fit.as_ref(), spr > 1e-9) {
                (Some(fit), true) => nd.pot * eqp * fit.class_r(h, rp),
                _ => (pot_eff * eqp * rp).min(pot_eff),
            };
            out[h] = (prob[h] * (share - inv_p)) as f32;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::preflop::equity::{class_index, class_prob};

    /// Every two-card combo as (class, card, card), cards as rank*4+suit.
    fn all_combos() -> Vec<(usize, u8, u8)> {
        let mut v = Vec::new();
        for a in 0..52u8 {
            for b in (a + 1)..52 {
                let (ra, sa, rb, sb) = (a / 4, a % 4, b / 4, b % 4);
                v.push((class_index(ra, rb, sa == sb && ra != rb), a, b));
            }
        }
        v
    }

    #[test]
    fn conditioned_mass_matches_a_count_over_real_cards() {
        let combos = all_combos();
        assert_eq!(combos.len(), 1326);
        let reach: Vec<f32> = (0..NUM_CLASSES)
            .map(|j| class_prob(j) * (((j * 37 + 5) % 11) as f32 / 10.0))
            .collect();
        let mut fast = [0f64; NUM_CLASSES];
        conditioned_mass(&reach, &mut fast);
        let w = weights();
        for h in 0..NUM_CLASSES {
            // Brute force over every hero combo of class h (all must agree).
            for &(_, c1, c2) in combos.iter().filter(|c| c.0 == h) {
                let mut m = 0f64;
                for &(j, a, b) in &combos {
                    if a != c1 && a != c2 && b != c1 && b != c2 {
                        m += reach[j] as f64 / class_combos(j) as f64;
                    }
                }
                let brute = DECK_SCALE * m;
                assert!(
                    (brute - fast[h]).abs() < 1e-9,
                    "h={h}: {brute} vs {}",
                    fast[h]
                );
            }
            let table: f64 = (0..NUM_CLASSES)
                .map(|j| reach[j] as f64 * w[h * NUM_CLASSES + j] as f64)
                .sum();
            assert!(
                (table - fast[h]).abs() < 1e-6,
                "h={h}: table {table} vs {}",
                fast[h]
            );
        }
    }

    #[test]
    fn a_full_range_is_unchanged_and_weights_are_symmetric() {
        let reach: Vec<f32> = (0..NUM_CLASSES).map(class_prob).collect();
        let mut m = [0f64; NUM_CLASSES];
        conditioned_mass(&reach, &mut m);
        assert!(m.iter().all(|x| (x - 1.0).abs() < 1e-6), "{m:?}");
        let w = weights();
        for h in 0..NUM_CLASSES {
            for j in 0..NUM_CLASSES {
                let (a, b) = (w[h * NUM_CLASSES + j], w[j * NUM_CLASSES + h]);
                assert!((a - b).abs() < 1e-6, "W[{h}][{j}] {a} vs {b}");
            }
        }
        // Holding As5s leaves AA 3 of its 6 combos and AK 12 of its 16.
        let (aa, ako, aks) = (
            class_index(12, 12, false),
            class_index(12, 11, false),
            class_index(12, 11, true),
        );
        let a5s = class_index(12, 3, true);
        let ratio = |j: usize| w[a5s * NUM_CLASSES + j] as f64 / DECK_SCALE;
        assert!((ratio(aa) - 0.5).abs() < 1e-6);
        assert!(((ratio(ako) * 12.0 + ratio(aks) * 4.0) - 12.0).abs() < 1e-5);
    }
}
