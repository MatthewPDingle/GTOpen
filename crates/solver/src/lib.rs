//! GTO postflop solver core: game tree construction, discounted CFR,
//! exploitability measurement and strategy inspection.

/// Hot paths use pooled scratch buffers (see `scratch`), but tree building
/// and queries still allocate from many threads; mimalloc removes the
/// resulting allocator contention.
#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

pub mod best_response;
pub mod cards;
pub mod cfr;
pub mod evaluator;
pub mod game;
#[cfg(feature = "gpu")]
pub mod gpu;
pub mod query;
pub mod range;
pub mod save;
pub mod scratch;
pub mod store;
pub mod tree;

pub use cards::*;
pub use cfr::{Algorithm, Progress, RunOptions, Solver};
pub use game::{Spot, SpotConfig};
pub use query::{NodeView, PathStep};
pub use range::Range;
pub use store::Storage;
pub use tree::{parse_sizes, BetSize, StreetSizing, TreeConfig};
