# Decision checkpoint: useful preflop ranges

The goal is trustworthy hand choices across configurable preflop situations,
not merely more calls, prettier grids, or passing replay checks. The present
BB-versus-BTN 200 bb experiment is a test case for that goal. Its result cannot
establish full-table or cross-stack accuracy.

## Newly measured limitation in the evaluation

A CPU-only diagnosis of the completed combined 269-input candidate reconstructed
the registered response from all 8,192 response-training deals and reproduced
its reported gain on all 16,384 held-out deals. The running 302-input trial was
not read or changed by this analysis.

- The chosen response gains **2.047 bb** on the same hands used to choose it,
  but **-0.354 bb** on the held-out hands. The apparent difference is 2.401 bb.
  Training performance is optimistically biased by action selection; this is
  a descriptive diagnostic, not a confidence interval for overfitting.
- There are only **13 to 95 observations per hand class**, with median **37**,
  in the response-training set.
- Splitting that set into first and second halves leaves 89 classes with the
  original minimum of 16 observations in both halves. **45 of those 89 choose
  different actions**. Those disagreements cover 36.18% of the held-out hand
  mix; all eligible classes cover 75.77%. Splitting itself reduces support.

This diagnosis concerns the evaluation's fitted counter-strategy, not a direct
measurement of the self-play network's training error. It explains why a
negative fitted-response gain is weak reassurance. The true best response can
retain the original policy and cannot be worse than it.

Reproducible evidence: `sampled-combined-response-stability-v1-result.json` and
`tools/research/hu_response_stability_diagnosis_20260923.py`. All source batch
summaries were matched to the completed audit's recorded hashes; no new deals,
GPU training, model selection, range patches, or production changes were made.

## Next two substantive decisions

1. Finish the current visible-feature experiment exactly as registered. Report
   both players' tests, all intervals and all 169 hand classes. A detected
   profitable deviation is adverse evidence. No detected deviation with broad
   intervals is inconclusive. Cross-candidate action differences are descriptive
   because their opponents and continuations differ.
2. Improve measurement before another open-ended architecture search. Freeze a
   separate evaluation using the already controlled conditional all-in estimator
   and materially more response-training coverage. Preserve independent test
   hands and freeze the responder before viewing them. Use old completed results
   only for resource/precision planning, not as fresh confirmation. Explicitly
   measure response stability and coverage; integrating all-in board noise does
   not remove sampled non-all-in postflop noise. A larger test alone would not
   fix a badly estimated counter-strategy.

Before launching that second experiment, register the candidate(s), samples,
seeds, resource caps, alternatives and stopping rule. Estimate cost from actual
throughput and the existing precision study. If useful precision cannot fit a
reasonable run, change the estimator or test design instead of accumulating
more inconclusive architecture trials. Do not change the current trial's
estimator or budget after seeing its result.

## When to expand or change direction

Expand to another position/depth only after a specific improvement survives
independent value testing with a capable responder. Reduced disagreement is
useful supporting evidence, but not an accuracy certificate. Restricted tests
never certify a small full best-response gap.

If the current representation change and the sharper evaluation still cannot
establish useful progress, prioritize a small tractable poker reference game
with an independently computed best response. Use it to distinguish learning
failure from evaluation weakness before further full-budget self-play trials.
This is a diagnostic reference, not a replacement definition of the user's goal.

The separate native stack geometry checks support future implementation, but
they do not justify training a broad stack model yet. Likewise, Wizard is a
valuable matched-scenario reference; visual resemblance is not the optimization
target, and differences in trees or incoming ranges must remain explicit.

No deployment or preview replacement follows automatically from this document.
