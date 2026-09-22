# River frontier: direct full-panel decomposition is not the next implementation

The independent frontier census passed on all 336 continuations. It preserves
each distinct betting history and ordered public-card prefix, rather than
merging subgames that currently have similar ranges. Its river interior bytes
and action counts reconcile exactly with the previous canonical census.

| Quantity | Result |
|---|---:|
| Canonical river subgames | 11,507,596 |
| Earlier-street regret/strategy state | 6.246 GB |
| River interior regret/strategy state | 1,087.676 GB |
| One f64 boundary value per hand, both players | 160.032 GB |
| Two f64 vectors per player plus 64-byte record headers | 320.801 GB |
| Earlier state plus the larger boundary allowance | 327.047 GB |
| Including existing retained CPU metadata | 359.532 GB |
| Largest individual river regret/strategy state | 99,680 bytes |

The smaller boundary figure counts values only; it is not a qualified resolving
format. The larger figure allows a numerator and denominator per hand and a
record header. Neither includes atomic checkpoint copies, indexing overhead,
GPU working buffers, allocator overhead or process reserves. The available
RAM and SSD do not make the larger design automatically admissible. A compact
correct boundary representation would have to be specified and tested.

## Runtime constraint

At 2,000 outer iterations, one complete solve of every river subgame per outer
iteration requires **23.0 billion subgame solves**. The following is arithmetic,
not a measured GPU benchmark:

| Amortized time per complete river solve | Total for those subgames alone |
|---|---:|
| 1 microsecond | 6.39 hours |
| 10 microseconds | 63.93 hours |
| 100 microseconds | 639.31 hours |
| 1 millisecond | 6,393.11 hours |

Finishing this component in four hours would require about 0.626 microseconds
per complete mutual river solve, averaged across the batch. This excludes
earlier-street updates, transfers, reconstruction and evaluation; an alternating
trunk update can require another solve. These are complete subgame solutions,
not single CFR sweeps. The fact that each subgame is small does not establish
that billions of sufficiently accurate solutions are affordable.

## Rake and correctness

The census independently checks every visited river terminal's win/loss/tie
cashflow against configured matched-pot rake. It found 7,801,760 local subgames
with constant total terminal rake and 3,705,836 with action-dependent total rake.
The full raked game remains general-sum. Locally constant-sum pieces do not turn
the whole game into the zero-sum setting assumed by the CFR-D guarantee.

## Decision

Do not implement a naive full-panel, every-iteration river re-solve loop.
Decomposition combined with sampling or a substantially cheaper boundary oracle
could remain a later research option, but would require both a new correctness
contract and measured runtime. Neither is established here.

First test the remaining cheaper storage uncertainty: **late-state compression
on the actual wide-support geometry**. The earlier 1.665x result came from the
narrow original context. A separately registered resident-GPU probe will keep
the same full support and action menu, reproduce the existing iteration-four
checkpoint, then collect states at 100, 500 and 2,000 iterations under the
existing deterministic changing-reach schedule. Exact compression of those
states measures storage only; it is not connected preflop training or a claim
that the repeated changing-range problem has converged.

Evidence: `river-frontier-registration.json`, `river-frontier-review.json`,
the full panel/probe results and logs. The CPU panel finished in 27.05 seconds
with no CUDA allocation and at least 102.72 GB free RAM. All 115 frozen input
hashes were verified. Production 56708 remains unchanged.
