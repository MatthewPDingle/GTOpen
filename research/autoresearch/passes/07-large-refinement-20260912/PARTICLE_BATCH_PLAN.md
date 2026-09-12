# Next GPU variance experiment: equally weighted stratified particle batches

Motivation: pair correction passed expectation checks but added work and failed
both learning screens. Its 8-player variance reduction was insufficient to
halve sampling. Test a different sampling arrangement with the same 64 samples
and unchanged terminal arithmetic, before adding more terminal computation.

This plan is not implemented or qualified yet. Port 56708 remains excluded.

## Fixed construction, independent of learning runs

Partition the existing 1,024 canonical particles into 64 strata of 16 particles.
Represent each particle by its 169 mid-rank features `(lower + upper) / 338`.
Recursively split at the median along the feature with greatest variance until
64 equal leaves exist. Resolve feature ties by class index and particle ties
by canonical index. No opponent ranges, solve results, convergence seeds or
player-history data enter the partition.

Deterministically shuffle each 16-particle leaf with construction seed 90211,
using unbiased bounded-integer draws. Form batch j from the jth particle in
each leaf, producing 16 disjoint 64-particle batches. Freeze the resulting
permutation and its checksum before numerical/learning evaluation. Do not try
several construction seeds and retain whichever passes the tests.

Each learning iteration chooses one batch uniformly; use the existing seeded
random stream. Every canonical particle has exactly probability 1/16 of being
included, and each receives weight 1/64. Therefore a fixed policy's mean
estimate equals the canonical 1,024-particle mean. This is a claim about the
canonical approximation, not physical poker or conditional unbiasedness of a
converging solver's final strategy.

Use the same table allocations and CDF/terminal kernels as native sampling.
Copy the selected batch first into order/lower/upper together. All selected
indices must refer to the same original particle. Full checks restore all
canonical particles in canonical order. No added per-terminal matrix projection
or payoff correction; no pair CV, normalized regret, branch masks or custom
root ranges in the first experiment. Partition construction time counts in the
reported end-to-end runtime.

## Registered gates before implementation/execution

1. Prove the partition is a permutation: 64 strata x 16 elements, 16 batches x
   64, every index 0..1023 exactly once, deterministic checksum. Verify paired
   table indices, zero reach, fixed constraints and capture/eager execution.
2. Reuse the twelve 3/4/6/8-player fixed-range fixtures. Evaluate all 16 batches,
   compare with the canonical full mean and native 64 at all 1,024 cyclic
   offsets. Require every hand's mean error <=0.0002 bb. Report all per-hand
   variances, including regressions. Require overall pooled candidate/native
   variance <=0.9 and no fixture above 1.25 before learning trials. Also report
   the eight-player subset separately so a small-player improvement cannot be
   mistaken for large-player evidence.
3. Same-binary six-player native controls vs batch candidates, seeds 42 and
   314159, gamma15/64, limit 1,000, full checks every 25, target 0.005 bb twice,
   cap 600 seconds each. Both must converge and each total time must be no
   slower than its control. Archive failures; don't change gates after results.
4. Only after passing, initial eight-player trial: existing user-session
   fixture, seed 42, gamma15/64, limit 1,500, checks every 50, target twice,
   cap 1,200 seconds. Save/reload exactly; independently evaluate all 27 paths
   with the existing conditioned-action gates. All global and conditional
   requirements still apply. Further seeds, constraints and matched large
   controls are required before deployment, even if this first screen passes.

The premise is that neighboring rank profiles produce similar multiway shares,
so selecting one from every stratum may reduce noise. That premise is unproven:
nonlinear range interactions or fixed cross-stratum pairings may defeat it.
Reject the arrangement if its numerical or learning evidence fails the gates.
