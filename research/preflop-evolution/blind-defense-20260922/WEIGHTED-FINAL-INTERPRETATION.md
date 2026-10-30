# Covering every starting hand did not solve the range-consistency problem

The completed test gives us **no established improvement in playing strength**
from stratified training at this budget. It successfully fixes missing hand
classes during training, but the two resulting runs still disagree heavily
about which hands should take which actions.

## What the evidence says

Both candidates finished 78 training updates. A separate test used all 65,536
registered deals, and the independent audit passed across 2,048 batches and
29,772,319 recorded policy observations. The largest discrepancy in the audited
statistical calculations was 1.42e-12. The audit shares the poker engine and
does not independently repeat neural inference.

- Every hand class now receives training samples in every update. The earlier
  method missed about 19 of the 169 classes per update on average.
- Despite that coverage improvement, weighted disagreement between the two
  runs increased from **46.94% to 49.65%**. Their most frequent action differs
  for **96 of 169 classes**, compared with 95 for the earlier method.
- All eight payoff comparisons remain inconclusive under the predeclared
  simultaneous 95% intervals. Estimated changes span about -0.121 to +0.084 bb
  per entry into this spot. Every interval includes both a gain and a loss.

The disagreement measure describes how much action probability changes between
these runs. It is not the percentage of incorrectly played hands or an EV-loss
estimate. Two runs also cannot establish a general increase in variability.
Different policies can sometimes have similar value; that possibility is not
resolved by these results.

An inconclusive payoff result is not proof that the methods are equivalent.
The uncertainty remains substantial, especially with large-pot outcomes. We
will retain the original sample count and intervals rather than extend this
test after seeing its results.

## Decision

Do not promote this candidate as a more accurate preflop model. Wider aggregate
calling frequencies, or a chart that looks closer to another solver, would not
override the missing evidence of reliable hand selection and playing strength.
Neither experimental baseline nor candidate is thereby certified as accurate.

The findings establish that **coverage alone is insufficient**. They do not
isolate whether remaining disagreement comes mostly from noisy action values,
approximate postflop predictions, limited training, or differences between
similarly valued strategies.

## Next experiment

Continue the already specified board-root experiment. It changes the estimate
used for BB's initial decision: evaluate many compatible private hands on each
sampled public board, rather than relying only on a few sampled private hands.
That addresses a different source of variation from simply ensuring that every
starting-hand class appears.

The two stratified runs remain the preselected controls for this experiment;
they are controls for isolating the change, not declared winners. The plan was
written before the current payoff results were available. Its four-board budget,
78 updates per arm, seeds, physical sampling and optimizer work remain fixed.
The additional board calculations cost compute, so elapsed time must also be
reported. Improvement is a hypothesis to test, not a promised result.

First qualify actual GPU training and recovery, then audit the two-generation
prefix and check measured storage before continuing to the full study. A new
evaluation with its registered fresh seed follows completed, audited training.

This remains a restricted **200bb BB-versus-BTN** experiment with a 2bb open,
0.5bb dead money and 5% rake capped at 2bb. It does not establish accuracy for
other positions, stacks, sizing menus, multiway play, or agreement with GTO Wizard.
Production has not been changed.

See the [complete comparison](WEIGHTED-FINAL-FINDINGS.md),
[all 169 hand classes](weighted-final-all-hand-classes.json),
[all eight payoff intervals](weighted-final-gains.png), and the
[prospective next-study plan](BOARD-ROOT-MATCHED-STUDY-PLAN.md).
