//! Pairwise all-in tables over a weighted flop panel.
//!
//! For combos c and o (indexed by `combo_index`), `mass[c][o]` is the panel
//! weight of the flops compatible with both hands (zero when c and o share a
//! card) and `eq[c][o]` the same sum weighted by c's full-runout equity
//! (win + tie/2 over every turn and river). Preflop folds, all-ins and
//! check-downs of hands outside a continuation all price from these, so
//! they share the continuations' chance model exactly.

use crate::cards::{combo_from_index, combo_index, parse_cards, Card, NUM_COMBOS};
use crate::evaluator::evaluate7;
use rayon::prelude::*;

pub struct PairTables {
    pub mass: Vec<f32>,
    pub eq: Vec<f32>,
}

/// Turn and river pairs left after a flop and two private hands.
const RUNOUTS_PER_PAIR: f32 = 990.0;

impl PairTables {
    /// `flops`: board strings with weights summing to 1.
    pub fn build(flops: &[(String, f64)]) -> Result<PairTables, String> {
        let boards: Vec<(Vec<Card>, f64)> = flops
            .iter()
            .map(|(b, w)| parse_cards(b).map(|c| (c, *w)))
            .collect::<Result<_, _>>()?;
        if boards.iter().any(|(b, _)| b.len() != 3) {
            return Err("every panel board must be a flop".into());
        }
        let n = NUM_COMBOS;
        let combos: Vec<(Card, Card)> = (0..n).map(combo_from_index).collect();
        let masks: Vec<u64> = combos.iter().map(|&(a, b)| (1u64 << a) | (1u64 << b)).collect();
        let (mass, eq) = boards
            .par_iter()
            .map(|(board, w)| {
                let board_mask = board.iter().fold(0u64, |m, &c| m | (1u64 << c));
                // 2*wins + ties for c against o, summed over runouts.
                let mut score = vec![0u16; n * n];
                let mut strength = vec![0u32; n];
                let live: Vec<Card> = (0..52u8).filter(|c| board_mask & (1u64 << c) == 0).collect();
                for (i, &t) in live.iter().enumerate() {
                    for &r in &live[i + 1..] {
                        let dead = board_mask | (1u64 << t) | (1u64 << r);
                        let valid: Vec<usize> = (0..n).filter(|&c| masks[c] & dead == 0).collect();
                        for &c in &valid {
                            let (a, b) = combos[c];
                            strength[c] = evaluate7(&[board[0], board[1], board[2], t, r, a, b]);
                        }
                        for (k, &c) in valid.iter().enumerate() {
                            let (sc, mc) = (strength[c], masks[c]);
                            for &o in &valid[k + 1..] {
                                if mc & masks[o] != 0 {
                                    continue;
                                }
                                let so = strength[o];
                                let (x, y) = if sc > so { (2, 0) } else if sc < so { (0, 2) } else { (1, 1) };
                                score[c * n + o] += x;
                                score[o * n + c] += y;
                            }
                        }
                    }
                }
                let mut mass = vec![0f32; n * n];
                let mut eq = vec![0f32; n * n];
                for c in 0..n {
                    if masks[c] & board_mask != 0 {
                        continue;
                    }
                    for o in 0..n {
                        if masks[o] & (board_mask | masks[c]) != 0 {
                            continue;
                        }
                        mass[c * n + o] = *w as f32;
                        eq[c * n + o] = *w as f32 * score[c * n + o] as f32 / (2.0 * RUNOUTS_PER_PAIR);
                    }
                }
                (mass, eq)
            })
            .reduce(
                || (vec![0f32; n * n], vec![0f32; n * n]),
                |(mut m1, mut e1), (m2, e2)| {
                    m1.iter_mut().zip(&m2).for_each(|(a, b)| *a += b);
                    e1.iter_mut().zip(&e2).for_each(|(a, b)| *a += b);
                    (m1, e1)
                },
            );
        Ok(PairTables { mass, eq })
    }

    /// `out[c] = sum_o table[c][o] * reach[o]`.
    pub fn apply(table: &[f32], reach: &[f64]) -> Vec<f64> {
        let n = NUM_COMBOS;
        (0..n)
            .into_par_iter()
            .map(|c| {
                let row = &table[c * n..(c + 1) * n];
                row.iter().zip(reach).map(|(&m, &r)| m as f64 * r).sum()
            })
            .collect()
    }
}

/// Combo index of a hand given as two cards in any order.
pub fn combo_of(a: Card, b: Card) -> usize {
    combo_index(a, b)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn single_flop_tables_are_complementary_and_count_compatibility() {
        let t = PairTables::build(&[("Kh7d2c".into(), 1.0)]).unwrap();
        let n = NUM_COMBOS;
        let aa = combo_of(parse_cards("As").unwrap()[0], parse_cards("Ad").unwrap()[0]);
        let kk = combo_of(parse_cards("Ks").unwrap()[0], parse_cards("Kd").unwrap()[0]);
        let blocked = combo_of(parse_cards("Kh").unwrap()[0], parse_cards("Ac").unwrap()[0]);
        assert_eq!(t.mass[aa * n + kk], 1.0);
        assert_eq!(t.mass[aa * n + blocked], 0.0);
        // A set of kings is a big favourite over aces; equities are complementary.
        assert!(t.eq[kk * n + aa] > 0.85);
        assert!((t.eq[kk * n + aa] + t.eq[aa * n + kk] - 1.0).abs() < 1e-6);
        for c in (0..n).step_by(37) {
            for o in (0..n).step_by(41) {
                let s = t.eq[c * n + o] + t.eq[o * n + c];
                assert!((s - t.mass[c * n + o]).abs() < 1e-6);
            }
        }
    }
}
