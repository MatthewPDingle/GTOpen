# Large corrected normalization: accuracy failure

The first registered seed (42) completed all 3,000 iterations, but did not
meet combined quality. Do not advance to seed 314159 or deploy this candidate.
The previously qualified small-game speedups have not transferred to this
1,567,754-node, eight-learning-seat game.

| Measurement | Result |
| --- | ---: |
| Complete example runtime, including save validation | 1,684.14 s (28.07 min) |
| Learning iterations | 1,159.74 s |
| Final native full-reference global gap | 0.464059 bb |
| Final conditional checks passed | 11 / 27 |
| Lowest global gap | 0.096897 bb at iteration 200; 6 / 27 local |
| Most conditional checks passed | 12 / 27 |

The unchanged gate requires a global gap at most 0.005 bb and all 27
conditional checks at two consecutive checkpoints. No checkpoint qualified.
All 60 checkpoints were independently recomputed from their recorded global
values and per-hand action values/probabilities. The independent saved-game
audit exactly reproduced the final per-hand records. Save/reload histories
were exact. The process and input hashes are retained beside the compressed
result and SHA-256 envelope in `raw/large-normalized-pair-seed42-v1*`.

This is a measured failure, not an equal-quality speed comparison: the earlier
large full-particle control also failed accuracy. Small-game qualification
remains separately documented in `NORMALIZED_PAIR_TAIL_RESULTS.md`.

Next is the separately registered `LARGE_AVERAGING_DIAGNOSTIC_PLAN.md`:
change only average-strategy weighting and require identical learned regret
histories. This distinguishes an averaging effect from a learning effect.
It does not assume averaging will repair zero-current-reach branches.
Port 56708 and the production app remain unchanged.
