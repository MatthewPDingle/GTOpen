# Decision after the matched river continuation

The completed comparison does not justify adopting the river treatment as a
better preflop model. Keep it as a research candidate. Its direction is promising,
but the size and reliability of the benefit remain uncertain, and its additional
training cost matters.

All 120 new training updates and 16,384 fresh evaluation deals completed. The
separate readback passed across 512 batches and 7,443,270 observations, with a
maximum scalar-statistic discrepancy of 1.47e-14. This establishes consistency of
the recorded experiment, not poker accuracy. The review uses the same qualified
native engine, rather than an independent poker implementation.

## What the results support

- All eight fixed replacement contrasts have positive point estimates, from
  +0.0052 to +0.0440 bb per entry. These are not bb/100 across all dealt hands.
- None of the eight primary bounded intervals excludes zero. The study cannot
  establish a reliable improvement at its registered primary threshold.
- The exploratory normal approximation excludes zero only for the two BTN
  comparisons in seed B. Those share a training seed and evaluation deals; they
  are not two independent confirmations. The other six exploratory intervals
  include zero.
- Rare deals remain influential: the ten largest squared deviations account for
  approximately 15.5% to 27.1% of the variance sums. Do not present normal
  intervals as guaranteed coverage or disregard the primary result.
- The treatment changed actual preflop decisions. At played model 109 the BB
  entry-weighted action differences were 6.56% and 10.04% for seeds A and B.
  Differences are evidence that learning propagated, not proof it improved play.
  The evaluated strategy averages all played models 0-109, not just model 109.
- Candidate training-pipeline time was 3.077 times baseline for seed A and 2.812
  times baseline for seed B. These sums exclude outer restore/readback, cleanup,
  copying, admission, evaluation and independent review. This was an equal-update
  comparison, not an equal-compute comparison.

## Next work and decision gates

1. Complete the already prepared fitted-network and complete-update equivalence
   controls for faster feature and query preparation. Keep the scientific run and
   all original sources/evidence unchanged. Passing a component control alone
   does not authorize claiming an end-to-end speedup.
2. If exact complete-update equality passes, use the separately versioned runtime
   in a prospectively specified cost comparison. Compare baseline and treatment
   with similar training budgets, fixed seeds and a new fixed evaluation sample;
   record actual cost rather than assume the earlier timing ratio transfers.
3. Improve evaluation precision before committing to another large training run.
   Investigate paired/conditional evaluation that preserves the same estimand and
   validate it independently. Do not narrow the existing confidence intervals
   after observing their results, clip rare outcomes, or repeat tests until one
   passes.
4. Broaden stack, rake, sizing, position and multiway contexts only after a useful
   cost/quality tradeoff is demonstrated. This one 200bb heads-up BB-versus-BTN
   context does not validate flexible preflop ranges or history-backed profiles.

No production promotion, deployment, or new GitHub push follows from this result.
The broad preflop research goal remains active.

## Evidence

- [Verified findings](RIVER-MATCHED-CONTINUATION-FINDINGS.md)
- [Registered study plan](RIVER-MATCHED-CONTINUATION-PLAN.md)
- [Independent review](river-matched-continuation-v1-independent-review-v1.json)
  SHA256: 8676d3ae76e0c3d026fecc468b3052278dd8ff06a6816463a16049bc3bede5fb
- [Study result](river-matched-continuation-v1-result.json)
  SHA256: e0a81a258b3189047c3cfee9581a0ef6496eacdddc686b2c4f15c32dea1eaf95
