# GPU action-value diagnostic

Read-only inspections of 173 registered early, ancestor, sibling, and selected
decisions in four 1,567,754-node saved games. All used the canonical 1,024-particle
coupled-deck model and an unrestricted full eight-seat global check.

| Input | Global gap (bb) | Root one-step deviation gain (bb) | Process seconds |
|---|---:|---:|---:|
| Original sampled | 0.0039928184 | 0.0000523556 | 18.172 |
| Compact refined sampled | 0.0295300368 | 0.0258020465 | 18.094 |
| Joint retained sampled | 0.1684210684 | 0.0100084501 | 18.156 |
| Joint retained native | 0.0706766863 | 0.0180311808 | 18.078 |

These are diagnostic runtimes, not learning/convergence speedups. Node gains
overlap and must not be summed as a full best-response decomposition.

The compact sampled policy's root alone has a 0.0258-bb profitable one-step
deviation, against a 0.0295-bb global gap. The first joint history experiment
therefore targeted a real upstream inconsistency, but its update scheme did
not resolve the whole game. After retained joint updates, multiple upstream
decisions have gains around 0.001-0.003 bb. In the sampled retained result,
unrefined neighboring paths `[1,0,0,2]` and `[1,0,0,0,3]` have gains of
0.00207823 and 0.00187984 bb respectively. This supports investigating how
upstream changes interact with fixed neighboring continuations. It does not
establish that any proposed exploration or expanded-update scheme will pass.

## Validation and failed instrumentation attempt

`frontier-tests-v1` failed its unreachable-branch assertion. The new diagnostic
read child action values after the complete upward traversal, but GPU action
scratch slots are reused between nonadjacent depths. This was a diagnostic
bug, not evidence of a production solver defect.

The corrected research-only traversal captures child values immediately before
each parent depth is evaluated. `frontier-tests-v2` passed: raw action values
match an independent CPU reference within 0.0002 bb on a small four-player
fixture, including a point lock, a frozen seat, and an unreachable branch.
The downloaded regret and average-strategy arenas remain exactly unchanged.
The CPU was used only for correctness, not performance measurement.

`frontier-build-v1` and all four guarded diagnostic processes succeeded.
`summarize_frontier.py` validates completed records, unique paths, finite gains,
and eight finite nonnegative global gaps. Full outputs and source/input hashes
are in `raw/frontier-*`. Global gaps exactly reproduce the respective prior
saved-game checks. No learning, live-server mutation, or deployment occurred.
