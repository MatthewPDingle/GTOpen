# Conditional sampling diagnostic, before another variance-reduction candidate

Status: registered diagnostic design; not implemented or run. The large
full-particle qualification run has priority and remains unchanged. Run no
second GPU workload alongside it.

The small combined-quality screen found that full-particle normalization
passes all six selected paths while its 64-particle counterparts do not.
The final sampled failures include blind responses after an open and a call.
Existing pair-control and stratification screens measured terminal payoffs,
not the regret differences at these actual conditional decision nodes.

Use immutable final games from these three completed small runs:

- `particle-quality-s64-seed42-norm1-v1` (iteration 1,000)
- `particle-quality-s64-seed314159-norm1-v1` (iteration 1,000)
- `particle-quality-s1024-seed42-norm1-v1` (iteration 950)

Use all six paths in `exploration-diagnostic-paths.json`, all legal actions,
and all 169 hands. At each saved state, freeze the **current** regret-matched
policy for learning seats and retain actual frozen/forced policies. Report
current-policy prefix masses, not average-policy masses. Verify this snapshot
against CPU current-policy diagnostics. This is a diagnostic of a fixed
state; different stop ages must not be presented as a controlled comparison
of learning trajectories.

Compute full canonical 1,024-particle action values, then enumerate all 1,024
cyclic offsets of the existing 64-particle sampler. Capture child values before
parent-depth scratch reuse, as in the frontier diagnostic. Do not learn or
discount between offsets. Calculate regret differences Q(a) - sum(sigma*Q)
in host f64 and divide by the same fixed opponent-prefix-mass denominator
(floor 1e-12) used by normalized regret. Preserve both raw and normalized
units. Zero-reach paths are reported separately, not silently normalized into
valid conditioned states.

For each hand/action, record sample mean, bias, variance and mean-square error
against the full result; also calculate covariance across actions and the
probability of reversing the full-result best-action ordering when its margin
exceeds 0.1 bb. Report relevant-hand results using current conditional hand
mass >=0.0025, plus complete unfiltered records. Do not sum overlapping-node
statistics into a purported whole-game BR gap.

Correctness gates before interpretation:

- The frozen current-policy snapshot agrees with source policy/constraints.
- Full action values agree with an independent fixed-policy CPU reference
  within the established GPU correctness tolerance.
- Enumeration mean agrees with the full result within floating-point
  tolerance; any discrepancy is investigated as estimator or evaluator bias.
- Full-particle sampling reproduces the full reference.
- Original device histories and saved files remain exact; no learning, age
  advance, or production session modification occurs.

This diagnostic does not itself qualify a faster solver. Its purpose is to
choose whether a subsequent candidate should reduce action-difference noise,
increase samples selectively, or address another demonstrated failure.
Register that candidate and its equal-quality speed gate separately. Continue
to use run07 hashes, caps, one-workload guard, and read-only live status checks.
