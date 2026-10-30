# Fresh-deal evaluation path for BB's first decision

The complete evaluation path now works with a saved physical-policy bank:
sample compatible private cards and a full runout, average only played models
using each player's own action reach, integrate all later betting actions,
train a class-based first-decision responder, and evaluate it on a separate
stream of fresh deals. This prepares the next accuracy check for the queued
physical BB/BTN pilot. It is not yet a result for that pilot.

## What the check can establish

The baseline is the frozen bank average. The evaluator changes only BB's first
action; both players' subsequent behavior stays fixed. It compares the baseline
with a responder trained separately for each of the 169 hand classes, and with
four predeclared simple deviations: always fold, call, raise or jam. All five
comparisons share each test deal, reducing unrelated deal noise.

The responder is written and hashed before the test stream is instantiated.
Only BB's own hand class selects its action. Classes with too few training
observations preserve the entire baseline strategy. Test outcomes never choose
the response, support threshold, checkpoint or stopping point. Losing deviations
remain negative; they are not clipped or replaced by the best test action.

Intervals use complete independent deals, conservative chip bounds derived
from stack and dead money, and a 5% family error budget across the five
comparisons at one declared final sample count. Bounds do not come from sample
extrema. These are intervals for particular tested deviations, **not upper
bounds on best-response gain**. A small result could mean the policy is good,
the responder is weak, the sample is inadequate, or several of these at once.

## Completed end-to-end control

Evidence prefix: `sampled-physical-root-evaluation-control-v1`.

- Source bank: generations 0 and 1 from the earlier tiny CPU controller check;
  unused generation 2 excluded. These are deliberately unqualified models.
- 32 newly sampled training deals, then 32 newly sampled test deals; different
  frozen seeds, eight deals per batch, minimum two training deals per class.
- All 30 source/input hashes verified. Eight batches retain native outputs,
  averaged-policy transports, root mixtures and paired payoff differences.
- Maximum baseline/root-action mixture error: **7.11e-15**. Independent forward
  chip accounting differed from recursive evaluation by at most **1.21e-13**.
- All 160 paired values and all five sample means/variances reconstructed
  independently from saved payoff summaries. Saved class choices and counts
  matched an independent training aggregation.
- All 32 test deals fell in classes below the training support threshold, so
  the trained responder used baseline fallback everywhere. Its zero difference
  is therefore **not an accuracy result**. The five comparisons still exercised
  the native payoff and interval path; the earlier synthetic root-deviation
  control separately checks non-fallback choices and negative test outcomes.
- Total control time: **8.30 seconds**, CPU inference with two threads, no GPU.

Large disposable transports remain at
`S:/GTOpen-research/sampled-physical-root-evaluation-control-v1/`; the registration,
review, aggregate result and responder are retained beside this document. Their
hashes bind the saved checkpoint and per-batch evidence.

## Applying it to the actual pilot

First inspect the pilot's terminal outcome and select a valid completed
checkpoint using a declared rule, not test performance. Freeze that checkpoint,
the complete bank, context/action menu, independent training/test seeds, sample
counts, class-support threshold and resource budget before any new draw. Use
enough responder-training deals to cover the broader BB support; the tiny
control above plainly does not do that. Report fallback coverage alongside the
payoffs and uncertainty, and preserve an incomplete result if the budget expires.

The test retains the complete saved BB/BTN incoming ranges and all continuation
branches. Those incoming ranges remain fixed, the betting menu remains limited,
and earlier folded cards are omitted. This does not learn other opening spots,
qualify arbitrary preflop trees, or directly compare against Wizard.

Implementation: `sampled_physical_root_evaluation_v1.py`; completed control:
`hu_sampled_physical_root_evaluation_control_20260922.py`. No production solver,
player model, or range preview has changed.
