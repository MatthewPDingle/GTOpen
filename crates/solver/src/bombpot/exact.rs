//! Exact scoring of a two- or three-player bomb pot strategy.
//!
//! Walks the whole game with every hand at once (no sampling, no hand
//! grouping on the scoring side) and returns what each seat earns under the
//! strategies, and what each seat could earn with a perfect reply to the
//! others. The gap between the two is how far the strategies are from
//! unbeatable, in chips per hand. With three players "unbeatable" means
//! that no seat gains by changing its own play alone; two seats working
//! together are not looked at.

use super::abstraction::{Abstraction, Rng};
use super::range::{Chance, Policy, TablePolicy, Walker};
use super::range3::Walker3;
use super::solver::BpSolver;
use super::tree::BpTree;
use crate::cards::NUM_COMBOS;

pub struct ExactValues {
    /// Each seat's result when every seat plays the strategy.
    pub value: Vec<f64>,
    /// Each seat's result with a perfect reply to the others' strategy.
    pub best: Vec<f64>,
    /// The same when the reply may start only on the turn, or only on the
    /// river (index 0 is `best`): shows which street gives the most away.
    pub best_from: [Vec<f64>; 3],
}

impl ExactValues {
    /// Average of the seats' possible gains, in chips per hand.
    pub fn exploitability(&self) -> f64 {
        self.gain_from()[0]
    }

    /// The same for replies that start on the flop, the turn or the river.
    pub fn gain_from(&self) -> [f64; 3] {
        let n = self.value.len() as f64;
        std::array::from_fn(|k| self.best_from[k].iter().zip(&self.value).map(|(b, v)| b - v).sum::<f64>() / n)
    }

    /// What each seat could gain by changing its own play.
    pub fn gain(&self) -> Vec<f64> {
        self.best.iter().zip(&self.value).map(|(b, v)| b - v).collect()
    }
}

/// Score any strategy on one game. With `Chance::All` the result is exact;
/// with sampled cards it is an estimate (and reads a little high, because
/// the reply is fitted to the cards that were drawn).
pub fn score(tree: &BpTree, abs: &Abstraction, policy: &dyn Policy, chance: Chance, seed: u64) -> Result<ExactValues, String> {
    score_solved(tree, abs, policy, chance, seed, 0)
}

/// As `score`. With `river_iters` above 0 the strategy scored is the
/// policy's on the flop and turn and, on the river, the solution of each
/// river spot for the ranges the policy arrives with (see
/// `Walker::river_iters`; two players only).
pub fn score_solved(
    tree: &BpTree,
    abs: &Abstraction,
    policy: &dyn Policy,
    chance: Chance,
    seed: u64,
    river_iters: u32,
) -> Result<ExactValues, String> {
    if tree.players() == 3 {
        if river_iters > 0 {
            return Err("with three players the river is not solved on the spot".into());
        }
        let w = Walker3::new(tree, abs)?;
        let v = w.run(policy, chance, true, None, None, &mut Rng::new(seed));
        let reach = w.root_reach();
        let deals = w.root_triples();
        let total = |x: &[f32]| (0..NUM_COMBOS).map(|h| reach[h] as f64 * x[h] as f64).sum::<f64>() / deals;
        let best_from: [Vec<f64>; 3] = std::array::from_fn(|k| (0..3).map(|p| total(&v.best[k][p])).collect());
        return Ok(ExactValues { value: (0..3).map(|p| total(&v.avg[p])).collect(), best: best_from[0].clone(), best_from });
    }
    let mut w = Walker::new(tree, abs)?;
    w.river_iters = river_iters;
    let v = w.run(policy, None, chance, true, None, &mut Rng::new(seed));
    let reach = w.root_reach();
    let pairs = w.root_pairs();
    let total = |x: &[f32]| (0..NUM_COMBOS).map(|h| reach[h] as f64 * x[h] as f64).sum::<f64>() / pairs;
    let best_from: [Vec<f64>; 3] = std::array::from_fn(|k| (0..2).map(|p| total(&v.best[k][p])).collect());
    Ok(ExactValues { value: (0..2).map(|p| total(&v.avg[p])).collect(), best: best_from[0].clone(), best_from })
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
