//! Exact scoring of a two-player bomb pot strategy.
//!
//! Walks the whole game with every hand at once (no sampling, no hand
//! grouping on the scoring side) and returns what each seat earns under the
//! strategies, and what each seat could earn with a perfect reply to the
//! other. The gap between the two is how far the strategies are from
//! unbeatable, in chips per hand. Two players only: with more, an exact reply
//! needs every combination of opponents' hands.

use super::abstraction::{Abstraction, Rng};
use super::range::{Chance, Policy, TablePolicy, Walker};
use super::solver::BpSolver;
use super::tree::BpTree;
use crate::cards::NUM_COMBOS;

pub struct ExactValues {
    /// Each seat's result when both play the strategy.
    pub value: [f64; 2],
    /// Each seat's result with a perfect reply to the other's strategy.
    pub best: [f64; 2],
}

impl ExactValues {
    /// Average of the two seats' possible gains, in chips per hand.
    pub fn exploitability(&self) -> f64 {
        ((self.best[0] - self.value[0]) + (self.best[1] - self.value[1])) / 2.0
    }
}

/// Score any two-player strategy on one game. With `Chance::All` the result
/// is exact; with sampled cards it is an estimate (and reads a little high,
/// because the reply is fitted to the cards that were drawn).
pub fn score(tree: &BpTree, abs: &Abstraction, policy: &dyn Policy, chance: Chance, seed: u64) -> Result<ExactValues, String> {
    let w = Walker::new(tree, abs)?;
    let v = w.run(policy, chance, true, None, &mut Rng::new(seed));
    let reach = w.root_reach();
    let pairs = w.root_pairs();
    let mut out = ExactValues { value: [0.0; 2], best: [0.0; 2] };
    for p in 0..2 {
        out.value[p] = (0..NUM_COMBOS).map(|h| reach[h] as f64 * v.avg[p][h] as f64).sum::<f64>() / pairs;
        out.best[p] = (0..NUM_COMBOS).map(|h| reach[h] as f64 * v.best[p][h] as f64).sum::<f64>() / pairs;
    }
    Ok(out)
}

/// Exact scoring of the average strategy in a solver's tables.
pub struct Exact2<'a> {
    s: &'a BpSolver,
}

impl<'a> Exact2<'a> {
    pub fn new(s: &'a BpSolver) -> Result<Exact2<'a>, String> {
        if s.players() != 2 {
            return Err("exact scoring needs exactly two players".into());
        }
        Ok(Exact2 { s })
    }

    pub fn values(&self) -> ExactValues {
        score(&self.s.tree, &self.s.abs, &TablePolicy(self.s), Chance::All, 0).expect("two players")
    }
}
