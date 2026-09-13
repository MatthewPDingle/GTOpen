# Fixed behavioral constraints: diagnostic protocol

Register before any convergence run. This is a mechanism diagnostic, not a
deployment or speed qualification. No epsilon transition is implemented.

## Prerequisites and implementation

`NEXT_BEHAVIORAL_REFINEMENT.md` defines the virtual-action transformation.
An independent host recursion must verify all 169 hands, repeat traverser
actions, forced/frozen behavior, transformed regrets, own-reach averages and
the constrained best response. Native epsilon-zero and eager/captured learning
must agree exactly, and canonical evaluation must be read-only and native.
Run default release and native GPU equivalence suites before learning runs.

## Fixed cases

Use the existing fresh six-player 23,038-node fixture and unchanged six paths
from `exploration-diagnostic-paths.json`. Pin the equity cache and realization
fit. Use canonical 1,024 particles for learning and evaluation, seed 42, gamma15
averaging with horizon 1000. No pair correction, normalization, exploration,
CV, RM+, predictive history, learning masks or special roots.

Run serially, in order: epsilon 0, 0.01, 0.05. Each run executes exactly 1,000
iterations with diagnostics every 50, maximum 180 seconds per process.
The same executable implements all cases; epsilon zero takes native kernels.
No early stopping or additional seed based on an attractive intermediate value.

Every diagnostic records:

- Unrestricted full-particle per-seat gaps, EVs and total learning gap.
- A separate constrained full-particle gap, with learning deviations limited
  to the fixed behavioral simplex. Frozen and forced nodes retain their policy.
- Independent conditional per-hand quality on all six paths, using actual
  arriving ranges and the unchanged local tail gate.
- Learning and total elapsed time. Final roundtrip and saved-file audit.

A constrained gap is never substituted for the unrestricted global gap. These
fixed positive-epsilon runs cannot establish an unrestricted transition or a
production speedup even if their final checks happen to pass.

## Decision after the diagnostic

Investigate an epsilon-zero transition only if a positive-epsilon candidate
passes more conditional branches at iteration 1000 than the matched zero case
and its constrained total gap is <= 0.005 bb. Both conditions must hold in the
independently verified final check. This is admission for further numerical
design, not large learning or deployment. If neither candidate meets them,
stop this fixed-stage design without extending the budget or sweeping epsilon.

Keep port 56708 read-only. The existing guard cancels only its own process if
user work becomes busy or status is unavailable. One hardware workload at a
time. Retain failed logs, exact inputs, source hashes and all fixed checkpoints.
