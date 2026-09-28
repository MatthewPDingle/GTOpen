# Fixed-policy river pilot and CPU preparation findings

Completed 2026-09-28. All three jobs are terminal and passed. No training,
production deployment, or improvement to preflop ranges is claimed here.

## Exact conditional values under played policies

`river-current-policy-pilot-v1` used generation 77 (last played) from each of
the two audited board-root arms. Each policy included its preflop, exact BTN,
and board-root overrides. The same policy supplied earlier action likelihoods
and future river decisions. These are reused training fixtures, not new tests
of generalization or a behavioral average of earlier models.

- Twelve native situations, two fixed model pairs: 23/24 evaluations supported.
  The unsupported case was p1-jam-raise under arm 9266201-board-root. It was
  retained explicitly rather than filled with invented probabilities.
- Eighteen supported evaluations had zero own-path reach but positive
  counterfactual opponent support; these remain valid update targets.
- CPU/GPU probabilities agreed within 1.94e-13; complete action values within
  1.17e-12 bb. All 108 independent distribution controls passed. Coverage includes
  both actors, checking, calling, folding, betting, raising and all-in actions.
- In 19 nonzero-variance evaluations, the median share of sampled regret
  variance from the opponent's private hand was 99.956%. Summing variances
  across fixtures gives 97.51%; this latter figure is dominated by large pots.
  Neither measure estimates gameplay-weighted or population-wide variance.
- Exact conditional full-action vectors have zero conditional target variance
  by construction. This does not establish unbiased integrated sampling,
  faster wall-time convergence, or more accurate complete preflop policies.

The pilot retained about 11.67 MB. Total wall time was 189.08 seconds, of which
approximately 140 seconds preceded registration (including the global storage
inventory); the post-registration section took about 48.82 seconds. The total
is not an inference benchmark. Peak CUDA allocated memory was 55.33 MB.

Across 72 repetitions, median CPU preparation was 306.6 ms, GPU inference
7.13 ms, and full value calculation 35.26 ms. The four newly exported jam cases
averaged 120.5 ms each for native export. The other eight native export timings
were retained from an earlier run and are separately labeled in the result.
Cached Python sampling took about 10.4 microseconds per sample, excluding
query construction, feature preparation, inference, and posterior draws. That
restricted timing cannot be compared with the complete exact pipeline.

## Measured preparation bottleneck and equivalent optimization

`river-current-policy-prepare-profile-v1` attributed 44%-51% of profiled
preparation time to repeated scalar visible-hand summaries. Profiler overhead
means these times should not be substituted for unprofiled timings.

New, separate vectorized helpers batch those same calculations. In
`visible-summaries-vector-control-v1`:

- All 40,528 direct examples produced identical float32 bytes, including all
  nine made-hand categories, wheels, two trips, three pairs, board-only hands,
  all suit permutations of crafted examples and reversed group ordering.
- All 57,025 query rows across the 12 frozen batches produced byte-identical
  complete features and preparation arrays, including table overrides and
  own histories. Empty inputs matched and nine malformed inputs were rejected.
- Direct summary calculation was 10.69x faster. Complete preparation was
  **1.837x faster**, measured in reference/vector/vector/reference order for
  every case: 10.264 seconds versus 5.588 seconds over 24 calls per version.
  Paired medians were 436.8 ms versus 237.8 ms; use this paired experiment for
  the speed claim, not timings from different runs.

This change is qualified for reuse in new research integration code. It has
not been inserted into a production solve or an already-registered trainer.
Identical prepared inputs preserve the policy, rather than changing its poker
assumptions. The control was CPU-only and took 31.05 seconds.

## Next gate

Implement a separate native research walker that preserves all sampled visits
and random draws while substituting a complete exact river action vector.
Verify common regret centering, ancestor returns, source-deal importance
weights, zero-own-reach behavior, and unsupported situations. Then measure
integrated cost/variance before bounded training and fresh full-policy tests.
Do not reintroduce the poorly performing gated-baseline variant or mistake a
local prediction improvement for full-game convergence.

Evidence: the three matching `*-registration.json` / `*-result.json` pairs in
this directory; native exports and probability arrays are under
`river-current-policy-pilot-v1/`. Executed sources remain immutable. The latest
global inventory admitted this work at 717.79 GB of the 800 GB allocated cap.
