//! Tournament (ICM) payoffs for the Preflop Lab.
//!
//! With `PreflopConfig.icm` set, every terminal pays each seat the change in
//! its Malmuth–Harville prize equity instead of its chip delta. Values are
//! reported in big-blind equivalents: prize equity times total chips over
//! total prizes, so a winner-take-all payout reproduces chip EV exactly.
//!
//! The stacks after a hand depend only on who wins each pot, never on the
//! hole cards, so each terminal's possible outcomes and every seat's prize
//! change in each are computed once when the game is built. During the solve
//! a seat's value for hand class h is
//!
//! ```text
//! sum over t of P(h wins exactly the pots t..j) * V_t
//! ```
//!
//! where the seat is eligible for pots 1..j (main pot first) and `V_t` is
//! its average prize change over the ways the other pots can fall, given
//! that result. The seat's own result is exact under the game's showdown
//! model: it wins pots t..j exactly when it holds the best hand among the
//! seats eligible for pot t but not for pot t-1, and those chances are the
//! side-pot shares the chip-EV game already uses. Who else wins the pots
//! the seat loses is weighted by the other seats' range-against-range
//! chances, which do not depend on the seat's own hand: an approximation
//! that only matters with three or more live seats. Ties count as fractional
//! wins, as in the chip-EV game.
//!
//! Terminals that see a flop with chips behind are priced as a pot lottery:
//! the continuation model's share of the pot becomes the chance of winning
//! the whole pot, and otherwise the seat loses what it put in. This captures
//! the risk premium on the preflop pot but not on the chips still behind.

use super::equity::NUM_CLASSES;
use super::{PNode, PreflopConfig, PreflopSolver, KIND_FOLD_WIN, KIND_POT_SHARE};
use crate::icm::{icm_after_hand, malmuth_harville, MAX_EXACT_PLAYERS};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Tournament payout settings for an ICM game.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct IcmConfig {
    /// Prize for each finishing place among the players still in, first
    /// place first, in any currency (only ratios matter). Places past the
    /// number of players are ignored; missing places pay nothing.
    pub payouts: Vec<f64>,
    /// Stacks in bb of players at other tables, who take no part in the
    /// hand but share the remaining places.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub field: Vec<f64>,
}

impl IcmConfig {
    pub(super) fn validate(&self, cfg: &PreflopConfig, n: usize) -> Result<(), String> {
        if self.payouts.is_empty() {
            return Err("ICM needs at least one payout".into());
        }
        if self.payouts.iter().any(|p| !p.is_finite() || *p < 0.0) {
            return Err("ICM payouts must be finite and not negative".into());
        }
        let players = n + self.field.len();
        if players > MAX_EXACT_PLAYERS {
            return Err(format!(
                "ICM is exact for up to {MAX_EXACT_PLAYERS} players (table plus field); this game has {players}"
            ));
        }
        if self.payouts.iter().take(players).sum::<f64>() <= 0.0 {
            return Err("ICM payouts must pay something to the players still in".into());
        }
        if self.field.iter().any(|s| !s.is_finite() || *s <= 0.0) {
            return Err("ICM field stacks must be positive bb amounts".into());
        }
        if cfg.rake_pct != 0.0 {
            return Err("ICM games have no rake: set rake_pct to 0".into());
        }
        Ok(())
    }
}

/// One terminal's money: its pots and every way they can fall.
struct Term {
    /// (amount, eligible live-seat mask) per pot, main pot first.
    pots: Vec<(f64, u32)>,
    /// Winner seat per pot, and each seat's prize change in bb equivalents.
    outcomes: Vec<(Vec<u8>, Vec<f32>)>,
}

/// Precomputed prize changes for every terminal of an ICM game.
pub(crate) struct IcmTables {
    /// Node index -> term index (u32::MAX for action nodes).
    index: Vec<u32>,
    terms: Vec<Term>,
    /// Big blinds per unit of prize: total chips over total prizes.
    pub scale: f64,
    /// Each seat's prize equity before the hand, in payout units.
    pub start_equity: Vec<f64>,
}

fn pots_of(nd: &PNode) -> Vec<(f64, u32)> {
    match nd.kind {
        KIND_FOLD_WIN => vec![(nd.pot, 1u32 << nd.winner)],
        _ if nd.side_pots.is_empty() => vec![(nd.pot, nd.live)],
        _ => nd.side_pots.clone(),
    }
}

/// Every consistent assignment of a winner to each pot: the winner of a pot
/// also wins every later (smaller) pot it is eligible for.
fn enumerate(pots: &[(f64, u32)], k: usize, cur: &mut Vec<u8>, out: &mut Vec<Vec<u8>>) {
    if k == pots.len() {
        out.push(cur.clone());
        return;
    }
    let mask = pots[k].1;
    if let Some(&prev) = cur.last() {
        if mask & (1 << prev) != 0 {
            cur.push(prev);
            enumerate(pots, k + 1, cur, out);
            cur.pop();
            return;
        }
    }
    for w in 0..32u8 {
        if mask & (1 << w) != 0 {
            cur.push(w);
            enumerate(pots, k + 1, cur, out);
            cur.pop();
        }
    }
}

impl IcmTables {
    pub(super) fn build(s: &PreflopSolver, icm: &IcmConfig) -> IcmTables {
        let n = s.n;
        let start: Vec<f64> = (0..n)
            .map(|i| s.cfg.stack_of(i) + s.cfg.ante)
            .chain(icm.field.iter().copied())
            .collect();
        let players = start.len();
        let prizes: f64 = icm.payouts.iter().take(players).sum();
        let scale = start.iter().sum::<f64>() / prizes;
        let start_equity = malmuth_harville(&start, &icm.payouts);

        let mut index = vec![u32::MAX; s.nodes.len()];
        let mut terms = Vec::new();
        // Final stacks of every outcome, deduplicated before pricing.
        let mut keys: HashMap<Vec<u64>, usize> = HashMap::new();
        let mut finals: Vec<Vec<f64>> = Vec::new();
        let mut refs: Vec<Vec<usize>> = Vec::new();
        for (node, nd) in s.nodes.iter().enumerate() {
            if nd.kind != KIND_FOLD_WIN && nd.kind != KIND_POT_SHARE {
                continue;
            }
            let pots = pots_of(nd);
            let mut winners = Vec::new();
            enumerate(&pots, 0, &mut Vec::new(), &mut winners);
            let mut term_refs = Vec::with_capacity(winners.len());
            for w in &winners {
                let mut fin = start.clone();
                for i in 0..n {
                    fin[i] -= nd.invested[i];
                }
                for (k, &(amount, _)) in pots.iter().enumerate() {
                    fin[w[k] as usize] += amount;
                }
                for x in fin.iter_mut() {
                    if *x < 1e-9 {
                        *x = 0.0;
                    }
                }
                let key: Vec<u64> = fin.iter().map(|x| x.to_bits()).collect();
                let id = *keys.entry(key).or_insert_with(|| {
                    finals.push(fin);
                    finals.len() - 1
                });
                term_refs.push(id);
            }
            index[node] = terms.len() as u32;
            terms.push(Term { pots, outcomes: winners.into_iter().map(|w| (w, Vec::new())).collect() });
            refs.push(term_refs);
        }
        let equities: Vec<Vec<f64>> =
            finals.par_iter().map(|fin| icm_after_hand(&start, fin, &icm.payouts)).collect();
        for (term, ids) in terms.iter_mut().zip(refs) {
            for (outcome, id) in term.outcomes.iter_mut().zip(ids) {
                outcome.1 = (0..n)
                    .map(|i| ((equities[id][i] - start_equity[i]) * scale) as f32)
                    .collect();
            }
        }
        IcmTables { index, terms, scale, start_equity }
    }

    fn outcomes(&self) -> usize {
        self.terms.iter().map(|t| t.outcomes.len()).sum()
    }
}

/// What an ICM game's values mean, for API readers.
#[derive(Debug, Clone, Serialize)]
pub struct IcmSummary {
    /// Big blinds per unit of prize: EVs are prize-equity changes times this.
    pub bb_per_prize: f64,
    /// Each table seat's prize equity before the hand, in payout units.
    pub seat_equity: Vec<f64>,
    /// Each field player's prize equity before the hand, in payout units.
    pub field_equity: Vec<f64>,
    /// Terminal outcomes priced when the game was built.
    pub outcomes: usize,
}

impl PreflopSolver {
    /// Present when the game pays ICM prizes rather than chips.
    pub fn icm_summary(&self) -> Option<IcmSummary> {
        let t = self.icm.as_ref()?;
        Some(IcmSummary {
            bb_per_prize: t.scale,
            seat_equity: t.start_equity[..self.n].to_vec(),
            field_equity: t.start_equity[self.n..].to_vec(),
            outcomes: t.outcomes(),
        })
    }
}

impl PreflopSolver {
    /// Range-against-range chance of each seat in `set` holding the best
    /// hand among `set`, normalized to sum to one.
    fn icm_range_odds(&self, dists: &[Option<Vec<f32>>], set: u32) -> Vec<f64> {
        let mut out = vec![0.0; self.n];
        let seats: Vec<usize> = (0..self.n).filter(|&q| set & (1 << q) != 0).collect();
        if let [only] = seats[..] {
            out[only] = 1.0;
            return out;
        }
        for &w in &seats {
            let Some(dw) = &dists[w] else { continue };
            let others: Vec<Vec<f32>> =
                seats.iter().filter(|&&q| q != w).filter_map(|&q| dists[q].clone()).collect();
            let shares = self.showdown_shares(&others);
            out[w] = (0..NUM_CLASSES).map(|h| dw[h] as f64 * shares[h]).sum();
        }
        let total: f64 = out.iter().sum();
        if total > 0.0 {
            out.iter_mut().for_each(|x| *x /= total);
        } else {
            let k = seats.len() as f64;
            for &w in &seats {
                out[w] = 1.0 / k;
            }
        }
        out
    }

    /// Terminal value for traverser `p` in an ICM game, times `prob` (the
    /// product of the other seats' reach mass), as `terminal_value` returns.
    pub(super) fn icm_terminal_value(
        &self,
        tables: &IcmTables,
        node: usize,
        p: usize,
        reaches: &[Vec<f32>],
        prob: f64,
        out: &mut [f32],
    ) {
        let nd = &self.nodes[node];
        let term = &tables.terms[tables.index[node] as usize];
        if nd.kind == KIND_FOLD_WIN {
            let v = (prob * term.outcomes[0].1[p] as f64) as f32;
            out.iter_mut().for_each(|x| *x = v);
            return;
        }
        let dists: Vec<Option<Vec<f32>>> = (0..self.n)
            .map(|q| {
                if nd.live & (1 << q) == 0 {
                    return None;
                }
                let s: f32 = reaches[q].iter().sum();
                (s > 0.0).then(|| reaches[q].iter().map(|&x| x / s).collect())
            })
            .collect();
        let pots = &term.pots;
        let m = pots.len();
        let j = pots.iter().take_while(|(_, mask)| mask & (1 << p) != 0).count();

        // b[k][h]: chance class h holds the best hand among pot k's seats.
        let mut b: Vec<Vec<f64>> = Vec::with_capacity(j);
        if j > 0 && nd.side_pots.is_empty() {
            // One pot: invert the chip-EV share, which carries the game's
            // showdown or continuation model (the pot lottery at flop leaves).
            let mut chip = vec![0f32; NUM_CLASSES];
            self.chip_terminal_value(node, p, reaches, &mut chip);
            let inv = nd.invested[p];
            b.push(
                chip.iter()
                    .map(|&v| ((v as f64 / prob + inv) / nd.pot).clamp(0.0, 1.0))
                    .collect(),
            );
        } else {
            for &(_, mask) in &pots[..j] {
                let opponents: Vec<Vec<f32>> = (0..self.n)
                    .filter(|&q| q != p && mask & (1 << q) != 0)
                    .filter_map(|q| dists[q].clone())
                    .collect();
                b.push(self.showdown_shares(&opponents).to_vec());
            }
        }

        // V[t]: average prize change given the traverser first wins pot t
        // (t = j: wins nothing), over how the other pots fall.
        let mut odds: Vec<(u32, Vec<f64>)> = Vec::new();
        let mut odds_of = |set: u32| -> Vec<f64> {
            if let Some((_, v)) = odds.iter().find(|(s, _)| *s == set) {
                return v.clone();
            }
            let v = self.icm_range_odds(&dists, set);
            odds.push((set, v.clone()));
            v
        };
        let me = 1u32 << p;
        let mut v_t = vec![0f64; j + 1];
        for t in 0..=j {
            let (mut num, mut den) = (0f64, 0f64);
            for (w, value) in &term.outcomes {
                let mut q = 1f64;
                for k in 0..m {
                    let mask = pots[k].1;
                    let wk = w[k] as usize;
                    if k > 0 && mask & (1 << w[k - 1]) != 0 {
                        if w[k] != w[k - 1] {
                            q = 0.0;
                        }
                        if q == 0.0 { break; }
                        continue;
                    }
                    let cand = if mask & me != 0 {
                        if k == t {
                            if wk != p { q = 0.0; }
                            if q == 0.0 { break; }
                            continue;
                        }
                        if t == j {
                            mask & !me
                        } else if k < t {
                            mask & !pots[t].1 & !me
                        } else {
                            0 // the traverser already won a larger pot it is in
                        }
                    } else {
                        mask
                    };
                    if cand & (1 << wk) == 0 {
                        q = 0.0;
                        break;
                    }
                    if cand.count_ones() > 1 {
                        q *= odds_of(cand)[wk];
                    }
                    if q == 0.0 { break; }
                }
                if q > 0.0 {
                    num += q * value[p] as f64;
                    den += q;
                }
            }
            v_t[t] = if den > 0.0 { num / den } else { 0.0 };
        }

        if j == 0 {
            let v = (prob * v_t[0]) as f32;
            out.iter_mut().for_each(|x| *x = v);
            return;
        }
        for h in 0..NUM_CLASSES {
            let mut prev = 0f64;
            let mut value = 0f64;
            for t in 0..j {
                let bt = b[t][h].max(prev);
                value += (bt - prev) * v_t[t];
                prev = bt;
            }
            value += (1.0 - prev).max(0.0) * v_t[j];
            out[h] = (prob * value) as f32;
        }
    }
}

#[cfg(test)]
mod tests;
