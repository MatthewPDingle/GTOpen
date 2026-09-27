# Reuse prior precision work and existing terminal arithmetic

This note refines the proposed feasibility work. No additional training or
production change has been launched.

## Do not repeat the already completed precision studies

The [earlier fixed-root diagnostic](ROOT-ACTION-NOISE-FINDINGS.md) already used
256 observations per class under one frozen policy. Its incoming-mass-weighted
RMS descriptive standard errors were 0.917 bb for call minus fold and 1.269 bb
for call minus raise. Its two 128-observation halves chose different actions in
62 classes, covering 35.82% of entry mass.

The later [frozen-continuation study](FROZEN-ROOT-PRECISION-FINDINGS.md) reused
65,536 physical deals for four complete policy pairs, with 165–646 observations
per class. Its raise-minus-call RMS standard errors remained about 0.994–1.058
bb. These are historical exploratory measurements for their frozen policies,
not estimates for the current stratified arms or simultaneous confidence bounds.

Thus a new generic diagnostic merely showing that more observations are needed
would add little. A proposed estimator must instead be compared with the current
native estimator under the **same** fixed policy and distribution, measuring
precision per elapsed time. Reuse admitted transport, chance-law and native
accounting controls; do not rerun a long study just to reproduce these facts.

## A less expensive alternative to dense pair values at every node

The production postflop CUDA implementation already contains relevant terminal
arithmetic in `crates/solver/src/gpu/kernels.cu`:

- `up_fold` uses total opponent reach minus the two card-overlap sums, adding
  back the duplicate identical-hand term.
- `up_show` sorts opponent hands by strength, uses cumulative reach to separate
  weaker/equal/stronger hands, and corrects each category for shared cards.

This suggests reusing the mathematical construction in an isolated research
adapter rather than storing a dense private-pair value at every decision.
On a fixed public runout, a player's behavioral probabilities depend only on
its own holding and the visible public history. Given this context's product
entry weights and physical compatibility constraint, public-path reach can be
represented by one holding-weight vector per player. Terminal expectations
can then be reduced against the opponent vector with blocker corrections.

This is an implementation inference from the inspected code, not a completed
adapter or a guarantee of lower runtime. The existing kernels use float32;
the current research reference evaluates probabilities in float64. Reusing
the structure does not authorize silently changing precision or claiming
the production kernel directly implements this research estimator.

## Smallest useful implementation check

First compare sorted-rank/card-removal terminal reductions with explicit dense
pair summation on fixed real boards, both players, varied nonnegative reach
weights, zero reaches, ties and identical-hand exclusions. Preserve exact known
fold and initial-jam values. Next validate public-path propagation and all
branch/root values against the admitted native fixed-policy evaluator.

Only then time a streamed end-to-end fixed-board adapter, including feature
construction and learned-policy inference. The [capacity measurement](BOARD-FIRST-CAPACITY-FINDINGS.md)
counted roughly 353,000–376,000 raw policy observations per tested board, so
terminal arithmetic alone may not be the bottleneck. Peak GPU allocation and
time per conditional root estimate must be measured before another training
trial is justified. The current registered comparison retains priority.
