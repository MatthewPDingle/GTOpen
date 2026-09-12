# Corrected normalized learning: one fast pass, candidate not qualified

The 64-particle corrected candidate passed combined quality on seed 314159
in 11.822 seconds, versus 51.585 seconds for its matched full-particle control:
4.363x faster at the same gate on that run. Seed 42 did not pass by the
registered 1,000-iteration limit. Therefore the candidate fails the required
two-seed screen. No large-game or deployment qualification follows.

| Pair correction | Samples | Seed | Iteration | Seconds | Global gap (bb) | Conditional paths | Combined pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Off | 1,024 | 42 | 950 | 51.645 | 0.002839 | 6 / 6 | Yes |
| On | 64 | 42 | 1,000 | 14.011 | 0.009490 | 6 / 6 | No |
| On | 256 | 314159 | 1,000 | 27.927 | 0.007470 | 3 / 6 | No |
| Off | 1,024 | 314159 | 950 | 51.585 | 0.002839 | 6 / 6 | Yes |
| On | 64 | 314159 | 825 | 11.822 | 0.003672 | 6 / 6 | Yes |
| On | 256 | 42 | 1,000 | 28.549 | 0.004819 | 3 / 6 | No |

Seconds include setup, learning, repeated quality checks and save/reload
validation. A separate executable then verified the saved per-hand audit.
Both full controls reproduce the prior full-control save's SHA-256 exactly.
Their different seeds are timing repeats, not independent full-particle
learning trajectories. Every checkpoint's full global gap, conditional gate,
stop streak and terminal saved audit was independently recomputed by
`check_normalized_pair.py`. All six guarded processes and audits completed
normally without a cap extension or restart.

Three normalized-update Rust tests passed, including the explicit new
combination: corrected regret increments use the actual counterfactual mass,
one-sweep values and strategy sums retain their existing behavior, captured
and eager histories agree exactly, and final full-reference evaluation agrees
with CPU validation. Existing ordinary entry points still refuse unsupported
mixed modes. This code is behind `preflop-research` and is not deployed.
All eight existing pair-control compatibility/estimator tests also passed.

The fixed-state variance reduction was real, and one timed solve converted it
into a substantial equal-quality gain. The failure of the second seed and
both 256-particle runs shows that lower estimator variance alone is not a
reliable convergence guarantee. Retain this result as a failed two-seed
qualification; do not label the whole candidate 4.36x faster.

Next work should distinguish a longer but still faster convergence tail from
loss of conditional learning on zero-current-reach branches. Any follow-up
must be a separately registered fresh experiment with an explicit wall-time
criterion and additional seed coverage; preserve the failed original screen
and its unchanged 1,000-iteration cap. Large-game convergence remains an
independent requirement.

Evidence: `raw/normalized-pair-quality-verified.json`, per-case result archives
and envelopes, all guarded exit records, saved audits and
`NORMALIZED_PAIR_QUALITY_PLAN.md`.
