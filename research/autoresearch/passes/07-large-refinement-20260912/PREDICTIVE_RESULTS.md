# Predictive GPU update: numerically validated, convergence rejected

No candidate is admitted to a large solve or deployment. Port 56708 is unchanged.
The fixed six-branch small-fixture screen rejected predictive updates with both
full and sampled payoffs; the matched zero-prediction case also failed.

## Complete learning runs

Fresh 23,038-node, six-learning-player fixture; calibrated heads-up continuation
and canonical coupled-deck multiway model. Every 25 iterations, evaluate with
all 1,024 particles. Qualification requires global gap <= 0.005 bb and all six
fixed per-hand conditional branch gates on two consecutive checks. Cap: 3,000
iterations. These complete executable times include evaluation, not disconnect
or conversation silence. Process wall durations are recorded separately.

| Mode | Particles | Seed | Iterations | Seconds | Final global gap | Branches | Qualified |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Existing normalized-pair control | 64 | 42 | 1,300 | 19.016 | 0.003364 | 6/6 | Yes |
| Predictive | 1,024 | 42 | 3,000 | 243.558 | 0.026866 | 2/6 | No |
| Zero prediction | 1,024 | 42 | 3,000 | 252.326 | 0.004323 | 2/6 | No |
| Predictive with pair correction | 64 | 42 | 3,000 | 57.265 | 0.025947 | 2/6 | No |
| Predictive with pair correction | 64 | 314159 | 3,000 | 54.595 | 0.027805 | 3/6 | No |
| Existing normalized-pair control | 64 | 314159 | 825 | 12.420 | 0.003672 | 6/6 | Yes |

Both existing controls exactly replay their earlier saved histories and complete
quality trajectories. Independent saved-game audits match the terminal check
for every case. Candidate times cannot be presented as equal-quality speedups.
In this matched full-particle comparison, prediction worsens the global gap
and does not improve branch coverage. Extending the budget is not admitted.

## Numerical and storage evidence

- Three predictive tests pass: exact compressed terminal-history round trips;
  independent full-node host prediction/update recursion; captured/eager replay,
  read-only evaluation and admission rejection. Cases include raw/calibrated
  continuation, full/sampled particles, fixed seats, point locks and zero reach.
- The full default release solver suite passes (136.891 seconds including
  compilation). Previous RM+ compatibility tests pass. Native GPU equivalence passes all six
  postflop and thirteen preflop tests.
- Exact 1,567,754-node geometry requires 2,912,588,772 additional bytes, below
  the 4 GiB cap; large GPU allocation has not been tested. Small compression
  reconstruction is bit-exact.

Predictive and zero-prediction modes retain each player's most recently selected
policy and use quadratic averaging. The zero mode isolates prediction under
the same policy timing. It is not a replay of the earlier native RM+ baseline,
which used linear averaging and recomputed policies from updated regrets.
Native evaluation remains independent of predictive history and policy buffers.
The feature is research-only, fresh-state only, and has no server entrypoint.

The complete plans are PREDICTIVE_NUMERICAL_PLAN.md and PREDICTIVE_SCREEN_PLAN.md.
check_predictive_storage.py and check_predictive_screen.py verify the arithmetic,
input hashes, quality decisions, control replay and saved audits. Raw logs,
compressed results and independent audits are retained under raw/predictive-*.

The next design direction is NEXT_CONDITIONAL_REPAIR.md. Global algorithm changes
have not repaired rare branches; the next experiment must preserve the original
globally accurate policy while testing smaller non-root policy corrections.
All existing global and conditional thresholds remain unchanged.
