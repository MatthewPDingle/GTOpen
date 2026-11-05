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
use crate::icm::{icm_after_hand, malmuth_harville_groups, state_count, Group};
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
    /// More players at other tables, as counts of equal stacks (e.g. 144
    /// players of 25bb). Equal stacks price exactly and cheaply.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub field_groups: Vec<FieldGroup>,
    /// How often a pot that sees the flop with chips behind is played for
    /// them: it ends all-in with chance k / (k + SPR), SPR being the second
    /// largest stack behind over the pot. 0 keeps the plain pot lottery.
    #[serde(default = "default_stack_off")]
    pub stack_off: f64,
}

pub(crate) fn default_stack_off() -> f64 {
    1.0
}

/// `count` players with `stack` bb each, at other tables.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FieldGroup {
    pub stack: f64,
    pub count: usize,
}

impl IcmConfig {
    /// Every off-table player as groups of equal stacks, in first-seen order.
    pub fn groups(&self) -> Vec<Group> {
        let mut out: Vec<Group> = Vec::new();
        let all = self.field.iter().map(|&s| (s, 1)).chain(self.field_groups.iter().map(|g| (g.stack, g.count)));
        for (stack, count) in all {
            match out.iter_mut().find(|g| g.stack == stack) {
                Some(g) => g.count += count,
                None => out.push(Group { stack, count }),
            }
        }
        out.retain(|g| g.count > 0);
        out
    }

    /// Players still in the tournament: the table plus every field player.
    pub fn players(&self, table: usize) -> usize {
        table + self.groups().iter().map(|g| g.count).sum::<usize>()
    }

    pub(super) fn validate(&self, cfg: &PreflopConfig, n: usize) -> Result<(), String> {
        if self.payouts.is_empty() {
            return Err("ICM needs at least one payout".into());
        }
        if self.payouts.iter().any(|p| !p.is_finite() || *p < 0.0) {
            return Err("ICM payouts must be finite and not negative".into());
        }
        if self.field.iter().chain(self.field_groups.iter().map(|g| &g.stack)).any(|s| !s.is_finite() || *s <= 0.0) {
            return Err("ICM field stacks must be positive bb amounts".into());
        }
        let players = self.players(n);
        if self.payouts.iter().take(players).sum::<f64>() <= 0.0 {
            return Err("ICM payouts must pay something to the players still in".into());
        }
        if state_count(n, &self.groups(), self.payouts.len()).is_none() {
            return Err(format!(
                "this ICM field is too large to price exactly: give the players at other tables fewer distinct stacks ({} distinct now)",
                self.groups().len()
            ));
        }
        if !self.stack_off.is_finite() || self.stack_off < 0.0 {
            return Err("ICM stack_off must be 0 or more".into());
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
    /// Flop pots with chips behind: the all-in the hand can turn into.
    stack_off: Option<StackOff>,
}

/// The all-in a flop pot turns into with chance `weight`: every live seat
/// puts in up to the second largest stack behind. A seat that wins its
/// share of the flop pot wins every pot it is eligible for here with the
/// chance that keeps its chip EV unchanged, (b * pot + commit) / wins, so
/// the stack-off moves prize equity, never chips.
struct StackOff {
    weight: f64,
    pot: f64,
    pots: Vec<(f64, u32)>,
    outcomes: Vec<(Vec<u8>, Vec<f32>)>,
    /// Chips each seat adds, and the total of the pots it is eligible for.
    commit: Vec<f64>,
    wins: Vec<f64>,
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
    /// Off-table groups and each one's per-player equity before the hand.
    pub groups: Vec<Group>,
    pub group_equity: Vec<f64>,
    /// Symmetrized heads-up equity, `bal[j * 169 + h]` = class h vs class j.
    pub(crate) bal: Vec<f32>,
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
        let start: Vec<f64> = (0..n).map(|i| s.cfg.stack_of(i) + s.cfg.ante).collect();
        let groups = icm.groups();
        let players = icm.players(n);
        let prizes: f64 = icm.payouts.iter().take(players).sum();
        let chips = start.iter().sum::<f64>() + groups.iter().map(|g| g.stack * g.count as f64).sum::<f64>();
        let scale = chips / prizes;
        let (start_equity, group_equity) = malmuth_harville_groups(&start, &groups, &icm.payouts);

        let mut index = vec![u32::MAX; s.nodes.len()];
        let mut terms = Vec::new();
        // Final stacks of every outcome, deduplicated before pricing.
        let mut keys: HashMap<Vec<u64>, usize> = HashMap::new();
        let mut finals: Vec<Vec<f64>> = Vec::new();
        let mut refs: Vec<Vec<usize>> = Vec::new();
        // Price every way `pots` can fall after each seat has paid `paid`.
        let mut outcomes_of = |pots: &[(f64, u32)], paid: &[f64]| -> (Vec<Vec<u8>>, Vec<usize>) {
            let mut winners = Vec::new();
            enumerate(pots, 0, &mut Vec::new(), &mut winners);
            let mut ids = Vec::with_capacity(winners.len());
            for w in &winners {
                let mut fin = start.clone();
                for i in 0..n {
                    fin[i] -= paid[i];
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
                ids.push(*keys.entry(key).or_insert_with(|| {
                    finals.push(fin);
                    finals.len() - 1
                }));
            }
            (winners, ids)
        };
        let mut stack_off_refs: Vec<Option<Vec<usize>>> = Vec::new();
        for (node, nd) in s.nodes.iter().enumerate() {
            if nd.kind != KIND_FOLD_WIN && nd.kind != KIND_POT_SHARE {
                continue;
            }
            let pots = pots_of(nd);
            let (winners, term_refs) = outcomes_of(&pots, &nd.invested);
            let mut stack_off = None;
            let mut off_refs = None;
            if nd.kind == KIND_POT_SHARE && nd.side_pots.is_empty() && icm.stack_off > 0.0 {
                let live: Vec<usize> = (0..n).filter(|&q| nd.live & (1 << q) != 0).collect();
                let mut behind: Vec<f64> = live.iter().map(|&q| s.cfg.left(q, nd.invested[q]).max(0.0)).collect();
                behind.sort_by(|a, b| b.partial_cmp(a).unwrap());
                let cover = behind.get(1).copied().unwrap_or(0.0);
                if cover > 1e-9 && nd.pot > 0.0 {
                    let commit: Vec<f64> = (0..n)
                        .map(|q| if nd.live & (1 << q) != 0 { s.cfg.left(q, nd.invested[q]).max(0.0).min(cover) } else { 0.0 })
                        .collect();
                    let paid: Vec<f64> = (0..n).map(|q| nd.invested[q] + commit[q]).collect();
                    let a_pots = super::settle_pots(&s.cfg, &paid, nd.live)
                        .map(|(_, p)| p)
                        .filter(|p| !p.is_empty())
                        .unwrap_or_else(|| vec![(paid.iter().sum(), nd.live)]);
                    let wins = (0..n)
                        .map(|q| a_pots.iter().filter(|(_, m)| m & (1 << q) != 0).map(|(a, _)| a).sum())
                        .collect();
                    let (a_winners, a_ids) = outcomes_of(&a_pots, &paid);
                    stack_off = Some(StackOff {
                        weight: icm.stack_off / (icm.stack_off + cover / nd.pot),
                        pot: nd.pot,
                        pots: a_pots,
                        outcomes: a_winners.into_iter().map(|w| (w, Vec::new())).collect(),
                        commit,
                        wins,
                    });
                    off_refs = Some(a_ids);
                }
            }
            index[node] = terms.len() as u32;
            terms.push(Term { pots, outcomes: winners.into_iter().map(|w| (w, Vec::new())).collect(), stack_off });
            refs.push(term_refs);
            stack_off_refs.push(off_refs);
        }
        let equities: Vec<Vec<f64>> =
            finals.par_iter().map(|fin| icm_after_hand(&start, fin, &groups, &icm.payouts).0).collect();
        let price = |id: usize| -> Vec<f32> {
            (0..n).map(|i| ((equities[id][i] - start_equity[i]) * scale) as f32).collect()
        };
        for ((term, ids), off_ids) in terms.iter_mut().zip(refs).zip(stack_off_refs) {
            for (outcome, id) in term.outcomes.iter_mut().zip(ids) {
                outcome.1 = price(id);
            }
            if let (Some(a), Some(ids)) = (term.stack_off.as_mut(), off_ids) {
                for (outcome, id) in a.outcomes.iter_mut().zip(ids) {
                    outcome.1 = price(id);
                }
            }
        }
        let mut bal = vec![0f32; NUM_CLASSES * NUM_CLASSES];
        for j in 0..NUM_CLASSES {
            for h in 0..NUM_CLASSES {
                bal[j * NUM_CLASSES + h] = s.balanced_raw_equity(h, j);
            }
        }
        IcmTables { index, terms, scale, start_equity, groups, group_equity, bal }
    }

    /// The tables flattened for the GPU (see `gpu/icm.rs`): one entry per
    /// terminal in node order. `None` when a terminal has more than eight
    /// pots, which the packed winner words cannot hold.
    #[cfg_attr(not(feature = "gpu"), allow(dead_code))]
    pub(crate) fn flat(&self, s: &PreflopSolver) -> Option<IcmFlat> {
        let mut f = IcmFlat::default();
        f.pot_start.push(0);
        f.out_start.push(0);
        f.a_pot_start.push(0);
        f.a_out_start.push(0);
        let pack = |w: &[u8]| w.iter().enumerate().fold(0u32, |acc, (k, &x)| acc | (x as u32) << (4 * k));
        for (node, &ti) in self.index.iter().enumerate() {
            if ti == u32::MAX {
                continue;
            }
            let term = &self.terms[ti as usize];
            if term.pots.len() > 8 || term.stack_off.as_ref().is_some_and(|a| a.pots.len() > 8) {
                return None;
            }
            let nd = &s.nodes[node];
            f.nodes.push(node as u32);
            f.kinds.push(if nd.kind == KIND_FOLD_WIN { 0 } else if nd.side_pots.is_empty() { 1 } else { 2 });
            match &term.stack_off {
                Some(a) => {
                    f.weight.push(a.weight as f32);
                    f.pot.push(a.pot as f32);
                    f.commit.extend(a.commit.iter().map(|&x| x as f32));
                    f.wins.extend(a.wins.iter().map(|&x| x as f32));
                    f.a_masks.extend(a.pots.iter().map(|&(_, m)| m));
                    for (w, value) in &a.outcomes {
                        f.a_winners.push(pack(w));
                        f.a_values.extend_from_slice(value);
                    }
                }
                None => {
                    f.weight.push(0.0);
                    f.pot.push(0.0);
                    f.commit.extend(std::iter::repeat(0.0).take(s.n));
                    f.wins.extend(std::iter::repeat(1.0).take(s.n));
                }
            }
            f.a_pot_start.push(f.a_masks.len() as u32);
            f.a_out_start.push(f.a_winners.len() as u32);
            f.masks.extend(term.pots.iter().map(|&(_, m)| m));
            f.pot_start.push(f.masks.len() as u32);
            for (w, value) in &term.outcomes {
                f.winners.push(pack(w));
                f.values.extend_from_slice(value);
            }
            f.out_start.push(f.winners.len() as u32);
        }
        f.bal = self.bal.clone();
        Some(f)
    }

    #[cfg_attr(not(feature = "gpu"), allow(dead_code))]
    pub(crate) fn terminal_count(&self) -> usize {
        self.terms.len()
    }

    fn outcomes(&self) -> usize {
        self.terms.iter().map(|t| t.outcomes.len() + t.stack_off.as_ref().map_or(0, |a| a.outcomes.len())).sum()
    }
}

/// ICM terminals flattened for the GPU, one entry per terminal.
#[derive(Default)]
#[cfg_attr(not(feature = "gpu"), allow(dead_code))]
pub(crate) struct IcmFlat {
    pub nodes: Vec<u32>,
    /// 0 = fold win, 1 = one pot, 2 = side pots.
    pub kinds: Vec<i32>,
    /// Eligible-seat mask of each pot, terminal t's at `pot_start[t]..pot_start[t + 1]`.
    pub pot_start: Vec<u32>,
    pub masks: Vec<u32>,
    /// Outcomes of terminal t at `out_start[t]..out_start[t + 1]`: winner of
    /// pot k in bits 4k..4k+4, and each seat's prize change at `values[o * n + q]`.
    pub out_start: Vec<u32>,
    pub winners: Vec<u32>,
    pub values: Vec<f32>,
    pub bal: Vec<f32>,
    /// The stack-off all-in of each flop pot (empty ranges elsewhere): its
    /// chance, the flop pot, each seat's added chips and eligible pots
    /// (`[t * n + q]`), and its pots and outcomes laid out as above.
    pub weight: Vec<f32>,
    pub pot: Vec<f32>,
    pub commit: Vec<f32>,
    pub wins: Vec<f32>,
    pub a_pot_start: Vec<u32>,
    pub a_masks: Vec<u32>,
    pub a_out_start: Vec<u32>,
    pub a_winners: Vec<u32>,
    pub a_values: Vec<f32>,
}

/// What an ICM game's values mean, for API readers.
#[derive(Debug, Clone, Serialize)]
pub struct IcmSummary {
    /// Big blinds per unit of prize: EVs are prize-equity changes times this.
    pub bb_per_prize: f64,
    /// Each table seat's prize equity before the hand, in payout units.
    pub seat_equity: Vec<f64>,
    /// Players at other tables as (stack, count, per-player prize equity
    /// before the hand in payout units), equal stacks grouped.
    pub field: Vec<(f64, usize, f64)>,
    /// Terminal outcomes priced when the game was built.
    pub outcomes: usize,
}

impl PreflopSolver {
    /// Present when the game pays ICM prizes rather than chips.
    pub fn icm_summary(&self) -> Option<IcmSummary> {
        let t = self.icm.as_ref()?;
        Some(IcmSummary {
            bb_per_prize: t.scale,
            seat_equity: t.start_equity.clone(),
            field: t.groups.iter().zip(&t.group_equity).map(|(g, e)| (g.stack, g.count, *e)).collect(),
            outcomes: t.outcomes(),
        })
    }
}

impl PreflopSolver {
    /// Chance that a hand from range `a` beats one from range `b` (both
    /// normalized), ties split, from the symmetrized pairwise table.
    fn icm_pair_odds(tables: &IcmTables, a: &[f32], b: &[f32]) -> f64 {
        let mut total = 0f32;
        for j in 0..NUM_CLASSES {
            let db = b[j];
            if db == 0.0 {
                continue;
            }
            total += db * dot(&tables.bal[j * NUM_CLASSES..(j + 1) * NUM_CLASSES], a);
        }
        total as f64
    }

    /// Range-against-range chance of each seat in `set` holding the best
    /// hand among `set`: the product of its heads-up chances against each
    /// other seat, normalized to sum to one. `pairs[w * 9 + x]` caches the
    /// heads-up chances (negative until computed).
    fn icm_range_odds(&self, tables: &IcmTables, dists: &[Option<Vec<f32>>], set: u32, pairs: &mut [f64; 81]) -> Vec<f64> {
        let mut out = vec![0.0; self.n];
        let seats: Vec<usize> = (0..self.n).filter(|&q| set & (1 << q) != 0).collect();
        if let [only] = seats[..] {
            out[only] = 1.0;
            return out;
        }
        for &w in &seats {
            let mut v = 1f64;
            for &x in &seats {
                if x == w {
                    continue;
                }
                if pairs[w * 9 + x] < 0.0 {
                    let r = match (&dists[w], &dists[x]) {
                        (Some(a), Some(b)) => Self::icm_pair_odds(tables, a, b),
                        _ => 0.5,
                    };
                    pairs[w * 9 + x] = r;
                    pairs[x * 9 + w] = 1.0 - r;
                }
                v *= pairs[w * 9 + x];
            }
            out[w] = v;
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
        let j = pots.iter().take_while(|(_, mask)| mask & (1 << p) != 0).count();

        // V[t]: average prize change given the traverser first wins pot t
        // (t = j: wins nothing), over how the other pots fall.
        let mut odds: Vec<(u32, Vec<f64>)> = Vec::new();
        let mut pairs = [-1f64; 81];
        let mut odds_of = |set: u32| -> Vec<f64> {
            if let Some((_, v)) = odds.iter().find(|(s, _)| *s == set) {
                return v.clone();
            }
            let v = self.icm_range_odds(tables, &dists, set, &mut pairs);
            odds.push((set, v.clone()));
            v
        };
        let me = 1u32 << p;
        let v_t: Vec<f64> = (0..=j).map(|t| icm_v(pots, &term.outcomes, p, t, j, &mut odds_of)).collect();
        // A flop pot that may end all-in: blend in the all-in's values.
        let (mut base, mut c) = if j == 0 { (v_t[0], 0.0) } else { (v_t[1], v_t[0] - v_t[1]) };
        if let Some(a) = &term.stack_off {
            let ja = a.pots.iter().take_while(|(_, mask)| mask & me != 0).count();
            let w = a.weight;
            if ja == 0 {
                base = (1.0 - w) * base + w * icm_v(&a.pots, &a.outcomes, p, 0, 0, &mut odds_of);
            } else {
                let win = icm_v(&a.pots, &a.outcomes, p, 0, ja, &mut odds_of);
                let lose = icm_v(&a.pots, &a.outcomes, p, ja, ja, &mut odds_of);
                base = (1.0 - w) * base + w * (lose + a.commit[p] / a.wins[p] * (win - lose));
                c = (1.0 - w) * c + w * a.pot / a.wins[p] * (win - lose);
            }
        }

        if j == 0 {
            let v = (prob * base) as f32;
            out.iter_mut().for_each(|x| *x = v);
            return;
        }
        // The value is linear in b[t][h], the chance class h holds the best
        // hand among pot t's seats: V[j] + sum over t < j of b[t] (V[t] - V[t+1]).
        // The GPU prices it with the chip-EV kernels by swapping the pot
        // amounts for those coefficients, so the two must stay identical.
        if nd.side_pots.is_empty() {
            // One pot: b is the chip-EV share, which carries the game's
            // showdown or continuation model (the pot lottery at flop leaves).
            let mut chip = vec![0f32; NUM_CLASSES];
            self.chip_terminal_value(node, p, reaches, &mut chip);
            let inv = nd.invested[p];
            let c = c.max(0.0);
            for h in 0..NUM_CLASSES {
                out[h] = (prob * base + (chip[h] as f64 + prob * inv) * c / nd.pot) as f32;
            }
            return;
        }
        let mut value = vec![v_t[j]; NUM_CLASSES];
        for (t, &(_, mask)) in pots[..j].iter().enumerate() {
            let opponents: Vec<Vec<f32>> = (0..self.n)
                .filter(|&q| q != p && mask & (1 << q) != 0)
                .filter_map(|q| dists[q].clone())
                .collect();
            let b = self.showdown_shares(&opponents);
            let c = v_t[t] - v_t[t + 1];
            for h in 0..NUM_CLASSES {
                value[h] += b[h] * c;
            }
        }
        for h in 0..NUM_CLASSES {
            out[h] = (prob * value[h]) as f32;
        }
    }
}

/// The traverser's average prize change when it first wins pot `t` of
/// `pots` (t = j: wins nothing, j being how many pots it is eligible for),
/// over how the other pots fall by the other seats' range odds.
fn icm_v(
    pots: &[(f64, u32)],
    outcomes: &[(Vec<u8>, Vec<f32>)],
    p: usize,
    t: usize,
    j: usize,
    odds_of: &mut dyn FnMut(u32) -> Vec<f64>,
) -> f64 {
    let me = 1u32 << p;
    let (mut num, mut den) = (0f64, 0f64);
    for (w, value) in outcomes {
        let mut q = 1f64;
        for (k, &(_, mask)) in pots.iter().enumerate() {
            let wk = w[k] as usize;
            if k > 0 && mask & (1 << w[k - 1]) != 0 {
                if w[k] != w[k - 1] {
                    q = 0.0;
                    break;
                }
                continue;
            }
            let cand = if mask & me != 0 {
                if k == t {
                    if wk != p {
                        q = 0.0;
                        break;
                    }
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
            if q == 0.0 {
                break;
            }
        }
        if q > 0.0 {
            num += q * value[p] as f64;
            den += q;
        }
    }
    if den > 0.0 { num / den } else { 0.0 }
}

/// Dot product in eight independent lanes, so it vectorizes.
fn dot(a: &[f32], b: &[f32]) -> f32 {
    let mut acc = [0f32; 8];
    let (ca, cb) = (a.chunks_exact(8), b.chunks_exact(8));
    let tail: f32 = ca.remainder().iter().zip(cb.remainder()).map(|(x, y)| x * y).sum();
    for (x, y) in ca.zip(cb) {
        for i in 0..8 {
            acc[i] += x[i] * y[i];
        }
    }
    acc.iter().sum::<f32>() + tail
}

#[cfg(test)]
mod tests;
