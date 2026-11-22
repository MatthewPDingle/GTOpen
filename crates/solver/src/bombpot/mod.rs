//! Bomb pots for 2 to 9 players, solved by sampled self-play.
//!
//! Everyone antes, nobody bets before the flop, and play starts on the flop
//! with every player holding any two cards. One board or two; with two, each
//! board awards half the pot.
//!
//! * `tree`: the betting tree (same rules as the exact solvers).
//! * `abstraction`: dealing, and the grouping of similar hands on later streets.
//! * `solver`: the self-play itself, playouts, and a one-seat challenger.
//! * `exact`: exact scoring of a two-player strategy, to check the rest.

pub mod abstraction;
pub mod exact;
pub mod solver;
pub mod tree;
#[cfg(test)]
mod tests;

pub use abstraction::AbsConfig;
pub use solver::{BpConfig, BpSolver};
pub use tree::BpTreeConfig;
