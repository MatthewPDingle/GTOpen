# Posterior64 river target findings

2026-09-28. Candidate K=64 passed the retained-data control and the real native
two-stage comparison. No model was fitted and no production build changed.
The whole objective remains robust preflop policy quality; this is preparation
for a matched training test, not evidence of improved ranges yet.

## What changed

Normalize the opponent distribution across **all 990 compatible hands**, using
the original entry weights and the current policy's actual action-history
likelihood. This first stage needs historical decision queries only. Then draw
64 hands with replacement from that exact distribution and compute complete
future river action trees for those draws. Repeated hands retain multiplicity.
All hero action values share the same draws and current-policy centering.
No hidden card enters a visible policy input, and source-deal weights are not
applied a second time. Zero opponent support rejects explicitly.

For a fixed visible state and current policy, this sample mean has the same
expectation as exhaustive opponent averaging. Its conditional covariance is
single-opponent covariance / 64. It remains noisy, and neither this identity
nor correct target generation proves faster learning or better preflop play.

## Retained-data control

Plan: RIVER-POSTERIOR64-PLAN.md. Result:
river-posterior64-control-v2-result.json. All eight prior TRAIN cases and their
67 targets were retained, with the same last-played generation-77 policies.

The v1 runner stopped **before registration and computation** because a manifest
path used slash separators instead of native Windows separators. V1 source is
preserved. V2 changes that lookup and records the correction; no policy, case,
K, seed, tolerance or acceptance gate changed.

- Exact posterior agreement in every case. Subset-inferred probabilities
  matched the complete reference within 4.45e-16, with identical support.
- Maximum selected-value discrepancy was 2.85e-14 bb. All complete legal
  actions and history dependencies stayed in the selected calculation.
- Prepared rows: 173,955 exhaustive versus 106,131 projected two-stage rows,
  including duplicated preparation: **38.989% fewer**. The preregistered
  25% reduction gate passed. This alone was not a native timing result.
- 2,048 independent repetitions per target agreed with analytic mean checks.
  Summed empirical squared target error was 3651.10 versus predicted 3689.17
  (ratio 0.98968). These sums are unweighted reused fixtures, heavily affected
  by large pots; do not interpret them as population-wide poker performance.
- Seven invalid-input controls rejected, and deliberate unequal repetition
  detected the error that would result from treating unique hands equally.
- Runtime 25.06 s; CPU only, under the 8 MB evidence allowance.

## Actual native comparison

Plan: RIVER-POSTERIOR64-NATIVE-PLAN.md. Result:
river-posterior64-native-control-v1-result.json. New standalone research
exporter: hu_river_two_stage_v1. Existing executables/sources were preserved.

Fresh native exhaustive and native two-stage calculations were paired for all
eight cases with alternating order. Each path includes request creation,
native export, JSON parsing, query preparation, CPU inference and values;
the candidate also includes posterior construction and both native invocations.
Independent equivalence checks and evidence hashing were outside those times.

| Path | Aggregate elapsed time |
|---|---:|
| Full 990-hand shared export and evaluation | 29.272 s |
| Exact posterior plus 64 selected hands | 11.578 s |

That is **2.5282x throughput**, or **60.446% less elapsed time**. Every paired
case improved, from 1.281x to 2.853x. This is one comparison per reused case,
not a broadly repeated hardware benchmark, not a production speedup and not
the training speed relative to the original single-opponent trainer.

Candidate stages: history export/parsing 3.367 s, history preparation/inference
5.741 s, posterior/draw selection 0.362 s, selected export/parsing 1.332 s,
selected preparation/inference 0.603 s, sampled values 0.172 s. Native stages
prepared 95,705 history rows plus 10,781 selected rows. The small difference
from the subset projection comes from native selected exports retaining all
selected-pair history queries. That duplicated work is included in timing.

Every historical query, complete history pair path, selected native tree,
legal action, geometry, payoff and outcome matched the exhaustive reference
after index remapping. Maximum policy error was 3.34e-16; every sampled regret
matched the preceding control exactly. Fourteen malformed transport/value
controls rejected, and a deliberate uneven multiplicity control passed.
Runtime including qualification: 60.77 s; raw evidence approximately 186.64 MB,
within the 384 MB cap. GPU remained occupied by another workload and unused.

## Next acceptance step

Retain the candidate and move into the **real weighted training ingestion**.
The existing trainer already averages future actions; it must retain those
flop/turn rows and all exact preflop/board-root overrides. Only approved river
rows change. Verify unchanged visit order, keys, source weights and reservoir
sampling RNG through real insertion, not just a replacement-map comparison.

Use a valid complete class-stratified source generation and a bounded slice for
that integration check; the existing pilot deals have no newly fabricated
source weights. Keep K=64 and the two played policies fixed. Reject a wrong
policy, query/trace binding, record identity, illegal padding or duplicate row
before mutating real reservoirs. Explicitly retain unsupported-state handling.

Then preregister a small matched training experiment from the same starting
state, with fresh full-policy evaluation. The candidate still performs more
work than a single-opponent target, so judge quality per elapsed time. Account
for board-root work, fitting, checkpoint publication and evidence IO in the
complete training measurement. Do not multiply independent microbenchmarks.

Before any larger admission, bound storage: control-sized full JSON exports
must not accumulate unboundedly per training generation. Prefer a versioned
in-memory/streaming native transport with replayable inputs and bounded retained
evidence, then re-inventory the 800 GB global budget. Preserve historical
archives, previous results and all executed/registered sources.
