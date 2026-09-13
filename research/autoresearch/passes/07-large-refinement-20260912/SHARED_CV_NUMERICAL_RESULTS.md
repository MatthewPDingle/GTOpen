# Shared-reference CV: numerical and memory gates passed

This is a research implementation, with no live server entrypoint. Large-game
GPU allocation and faster convergence are not established by these gates.

## Exact storage inventory

The original 1,567,754-node eight-player save has 602,914 multiway terminals
and 2,362,251 live-learning terminal/traverser entries. Shared storage is:

| Allocation | Bytes |
| --- | ---: |
| One reference reach snapshot | 1,059,806,436 |
| One reference mass snapshot | 6,271,044 |
| Packed full reference payoffs | 1,596,881,676 |
| Current sampled terminal scratch | 407,569,864 |
| Per-terminal/traverser offsets | 19,293,248 |
| Total extra | 3,089,822,268 |

This fits the 4,294,967,296-byte cap. The old representation required
12,196,748,616 bytes: sharing/packing saves 9,106,926,348 bytes (74.67%).
Two exact-tree inventories agree; check_shared_cv_storage.py independently
recomputes both representations and verifies immutable input hashes. This is
geometry accounting, not a successful large GPU allocation measurement.

## Numerical evidence

On a 526-node four-player fixture with a frozen seat and point lock, both raw
and calibrated HU continuation are covered:

- CPU geometry equals actual small GPU allocations. Every cached live
  terminal/hand value matches the full reference bit-for-bit; frozen/folded
  entries use the invalid-offset sentinel. Invalid kinds, masks, indices and
  overflow are rejected; a zero memory allowance rejects before CV allocation.
- With 1,024 particles the correction cancels exactly: complete regret and
  average arenas match disabled native learning bit-for-bit over five alternating
  iterations, and full GPU checks agree exactly.
- Eager and captured shared-reference updates match all learned arenas and
  reference buffers bit-for-bit across six iterations and three refresh epochs.
  Canonical evaluation leaves those buffers unchanged. Captured commands continue
  to use the correct buffers after reference refresh and table rotation.
- The stale-reference test changes a previously zero-reach branch into a
  positive, hand-dependent distribution. Across all sixteen disjoint 64-particle
  cohorts, 39,208 live terminal/hand values per fixture match the canonical full
  payoff in expectation. Maximum normalized mean error is 1.558e-7, below 2e-4.
  Corrections include both signs, ranging from -0.24535 to +0.21108; they are not
  clipped or a degenerate all-zero correction.
- Reconfiguration, root replacement, learning masks, frontier reads and old-CV
  admission are rejected once the shared state is installed. Cancellation before
  the first sweep leaves state and iteration unchanged.
- Old-CV compatibility passes. Native GPU equivalence passes six postflop and
  thirteen preflop tests. The complete default release solver suite passes.

The initial v1 compile missed a test import; that failed log is retained. V2
passed the initial cases. V3 strengthened the stale test to require nonzero
signed corrections after a hand-dependent policy change. V4 added reverse
admission checks and invalid-kind validation. No numerical tolerance was relaxed.
Final numerical tests: 92.063 seconds including compilation (1.53-second test
body); old-CV compatibility 1.016 seconds; native equivalence 67.421 seconds;
default release suite 131.797 seconds. Final build: 61.391 seconds.

SHARED_CV_SCREEN_PLAN.md separately registers the convergence/cost comparison.
The shared snapshot is taken before an epoch's first alternating sweep, so its
sampled trajectory is not expected to replay the older per-traverser snapshots.
The estimator preserves native counterfactual units and canonical evaluation;
its usefulness still depends on measured variance, convergence and total cost.
