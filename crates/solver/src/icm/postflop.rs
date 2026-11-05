//! Tournament (ICM) payoffs for postflop solves.
//!
//! With `TreeConfig.icm` set, every terminal pays each player the change in
//! its Malmuth–Harville prize equity instead of its chip delta, in big-blind
//! equivalents (prize change times total chips over total prizes), measured
//! from the root with the pot split evenly. Winner-take-all payouts are
//! linear in chips and reproduce chip EV exactly. ICM makes the game
//! general-sum, so each player gets its own payoff per terminal.

use super::{icm_after_hand, malmuth_harville_groups, state_count, Group};
use crate::preflop::FieldGroup;
use crate::tree::{Tree, KIND_TERM_FOLD, KIND_TERM_SHOWDOWN};
use serde::{Deserialize, Serialize};

/// Tournament payouts for a postflop spot.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PostflopIcm {
    /// Prize for each finishing place among the players still in, first
    /// place first (only ratios matter).
    pub payouts: Vec<f64>,
    /// Chips each player has behind at the root, in bb, in seat order (OOP
    /// first). Each must cover the effective stack; the deeper player's
    /// extra chips are never at risk but count for ICM. Default: the
    /// effective stack for everyone.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub behind: Option<Vec<f64>>,
    /// Stacks of every other player still in the tournament (folded players
    /// at this table and players at other tables), in bb.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub others: Vec<f64>,
    /// More players elsewhere, as counts of equal stacks.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub field_groups: Vec<FieldGroup>,
}

impl PostflopIcm {
    /// Players outside the hand, grouped by stack. Single players are kept
    /// as groups of one, which the grouped DP prices exactly.
    pub fn groups(&self) -> Vec<Group> {
        let mut out: Vec<Group> = Vec::new();
        let all = self.others.iter().map(|&s| (s, 1)).chain(self.field_groups.iter().map(|g| (g.stack, g.count)));
        for (stack, count) in all {
            match out.iter_mut().find(|g| g.stack == stack) {
                Some(g) => g.count += count,
                None => out.push(Group { stack, count }),
            }
        }
        out.retain(|g| g.count > 0);
        out
    }

    /// Each hand player's chips behind at the root.
    pub fn behind_for(&self, players: usize, effective: f64) -> Vec<f64> {
        self.behind.clone().unwrap_or_else(|| vec![effective; players])
    }

    pub fn validate(&self, players: usize, effective: f64, rake_pct: f64) -> Result<(), String> {
        if self.payouts.is_empty() || self.payouts.iter().any(|p| !p.is_finite() || *p < 0.0) {
            return Err("ICM payouts must be a list of finite, non-negative prizes".into());
        }
        let behind = self.behind_for(players, effective);
        if behind.len() != players {
            return Err(format!("ICM behind needs one stack per player ({players})"));
        }
        if behind.iter().any(|b| !b.is_finite() || *b < effective - 1e-9) {
            return Err("ICM behind stacks must each cover the effective stack".into());
        }
        let groups = self.groups();
        if groups.iter().any(|g| !g.stack.is_finite() || g.stack <= 0.0) {
            return Err("ICM stacks of other players must be positive".into());
        }
        let total = players + groups.iter().map(|g| g.count).sum::<usize>();
        if self.payouts.iter().take(total).sum::<f64>() <= 0.0 {
            return Err("ICM payouts must pay something to the players still in".into());
        }
        if state_count(players, &groups, self.payouts.len()).is_none() {
            return Err("this ICM field is too large to price exactly: give the other players fewer distinct stacks".into());
        }
        if rake_pct != 0.0 {
            return Err("ICM spots have no rake: set rake to 0".into());
        }
        Ok(())
    }
}

/// Prices final stacks for the players in a hand.
pub struct IcmPricer {
    reference: Vec<f64>,
    groups: Vec<Group>,
    payouts: Vec<f64>,
    start_equity: Vec<f64>,
    /// Big blinds per unit of prize.
    pub scale: f64,
}

impl IcmPricer {
    /// `reference`: each hand player's stack with the root pot split evenly.
    pub fn new(icm: &PostflopIcm, reference: Vec<f64>) -> Self {
        let groups = icm.groups();
        let players = reference.len() + groups.iter().map(|g| g.count).sum::<usize>();
        let prizes: f64 = icm.payouts.iter().take(players).sum();
        let chips = reference.iter().sum::<f64>() + groups.iter().map(|g| g.stack * g.count as f64).sum::<f64>();
        let (start_equity, _) = malmuth_harville_groups(&reference, &groups, &icm.payouts);
        IcmPricer { reference, groups, payouts: icm.payouts.clone(), start_equity, scale: chips / prizes }
    }

    /// Each hand player's prize change, in bb equivalents, for final stacks.
    pub fn value(&self, after: &[f64]) -> Vec<f64> {
        let fin: Vec<f64> = after.iter().map(|&x| if x < 1e-9 { 0.0 } else { x }).collect();
        let (eq, _) = icm_after_hand(&self.reference, &fin, &self.groups, &self.payouts);
        eq.iter().zip(&self.start_equity).map(|(a, b)| (a - b) * self.scale).collect()
    }

    pub fn start_equity(&self) -> &[f64] {
        &self.start_equity
    }
}

/// Heads-up per-player payoffs: `win[p][n]`, `lose[p][n]`, `tie[p][n]` replace
/// a terminal's `t_win`, `t_lose`, `t_tie` for player p. At fold terminals
/// `lose` is p's value when p folded and `win` when the opponent did.
pub struct HuIcmPayoffs {
    pub win: [Vec<f32>; 2],
    pub lose: [Vec<f32>; 2],
    pub tie: [Vec<f32>; 2],
    pub scale: f64,
    pub start_equity: Vec<f64>,
}

impl HuIcmPayoffs {
    pub fn build(tree: &Tree, icm: &PostflopIcm) -> Self {
        let cfg = &tree.config;
        let half = cfg.starting_pot / 2.0;
        let behind = icm.behind_for(2, cfg.effective_stack);
        let reference: Vec<f64> = behind.iter().map(|b| b + half).collect();
        let pricer = IcmPricer::new(icm, reference.clone());
        let n = tree.nodes.len();
        let mut win = [vec![0f32; n], vec![0f32; n]];
        let mut lose = [vec![0f32; n], vec![0f32; n]];
        let tie = [vec![0f32; n], vec![0f32; n]];
        let mut cache: std::collections::HashMap<[u64; 2], [f32; 2]> = std::collections::HashMap::new();
        let mut price = |s: [f64; 2]| -> [f32; 2] {
            *cache.entry([s[0].to_bits(), s[1].to_bits()]).or_insert_with(|| {
                let v = pricer.value(&s);
                [v[0] as f32, v[1] as f32]
            })
        };
        for (ni, node) in tree.nodes.iter().enumerate() {
            let put = node.put;
            // Player w takes the pot: each loses its own put, w gains both.
            let won_by = |w: usize| -> [f64; 2] {
                let mut s = [reference[0] - put[0], reference[1] - put[1]];
                s[w] += put[0] + put[1];
                s
            };
            match node.kind {
                KIND_TERM_FOLD => {
                    let f = node.player as usize;
                    let v = price(won_by(1 - f));
                    lose[f][ni] = v[f];
                    win[1 - f][ni] = v[1 - f];
                }
                KIND_TERM_SHOWDOWN => {
                    for p in 0..2 {
                        win[p][ni] = price(won_by(p))[p];
                        lose[p][ni] = price(won_by(1 - p))[p];
                    }
                    // Equal puts: a split returns both to the reference.
                }
                _ => {}
            }
        }
        HuIcmPayoffs { win, lose, tie, scale: pricer.scale, start_equity: pricer.start_equity().to_vec() }
    }
}

#[cfg(test)]
mod tests;
