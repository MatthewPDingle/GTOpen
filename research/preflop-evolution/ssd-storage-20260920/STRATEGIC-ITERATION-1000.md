# Weighted 112-board study: iteration 1,000

The first two registered segments completed successfully. The queue restored
the iteration-1,000 checkpoint and is training toward 1,500. The fixed endpoint
remains 2,000 iterations for each weighting scheme; neither the equal-weight
control nor the reserved-flop comparison has run yet.

| Iteration | Within-training-panel total gap (bb) |
| --- | ---: |
| 100 | 0.823835 |
| 500 | 0.057798 |
| 1,000 | 0.017229 |

The gap is falling but remains above the study's 0.01 bb criterion. This is
convergence evidence within the restricted training game, not evidence of
accuracy on unseen boards or agreement with a full preflop solution.

## Range movement

Using the same physical-hand entry distribution at every checkpoint, root
calling frequency moved from 8.733% at iteration 100 to 6.638% at 500 and
6.344% at 1,000. The prior-weighted root policy distance between 500 and 1,000
is 0.522%, compared with 5.959% between 100 and 500. This measures action
probability movement for the same hands; it is not an EV loss or accuracy score.
The detailed report is `strategic-weighted112-progress-1000-v1.md` and its JSON.

## Checks and retained evidence

Both completed results were independently rechecked with the existing numerical
validator: finite values, normalized policies, terminal probability, chip/rake
accounting, the qualified manifest, and expected memory-transfer accounting.
Result hashes match the segment reviews. The fresh-process evaluation at the
500 boundary exactly reproduces the preceding segment's final evaluation.
The segment reviews retain checkpoint file hashes and successful save checks.

The runs preserved at least 24.24 GB of free host RAM and 11.87 GB of free GPU
memory, above their registered limits. The SSD retains the checkpoints; training
uses RAM-backed state with no per-iteration SSD reads or writes. No active
runner, experimental setting, reserved result, or production application was
changed for this review.

The first attempt to recheck these results supplied the capacity document
instead of its `totals` object and stopped with a missing-key error. Correcting
the review invocation made both checks pass; no experiment artifact was changed.

The remaining scientific comparison is unchanged: finish both registered
training branches, freeze their policies, qualify the common evaluator, and
compare both with the older 47-board reference on the reserved 95 flops.
Keep convergence, coverage, and held-out accuracy conclusions separate.
