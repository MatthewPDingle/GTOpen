//! Three-player postflop solving: tree, spot, exact terminal evaluation and
//! CFR. Independent of the heads-up engine so heads-up saves, kernels and
//! results are untouched.

pub mod eval;
pub mod game;
#[cfg(feature = "gpu")]
pub mod gpu;
pub mod query;
pub mod save;
pub mod solver;
pub mod tree;
#[cfg(test)]
mod tests;

pub use game::{MwSpot, MwSpotConfig};
pub use solver::{MwProgress, MwSolver};
pub use tree::{MwTreeConfig, NP};
