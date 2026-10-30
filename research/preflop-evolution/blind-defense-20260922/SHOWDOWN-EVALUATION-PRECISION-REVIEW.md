# What the pending comparison can establish

This review was made while the second matched training arm was running, before
any fresh evaluation deals were drawn. It does not change the fixed protocol,
sample count, seeds, model selection, stopping rule, or running training code.
The companion `showdown-evaluation-precision-review-v1.json` binds the reviewed
sources and records the calculation.

## Sampling and contrasts

The full-deck sampler draws compatible private hands from the registered entry
ranges, then samples five public cards without replacement within each deal.
It starts a new draw for every deal; it does not reject repeats across deals.
All eight policy profiles use the same physical deal, which permits paired
comparisons. The four player-replacement contrasts per seed keep the opponent
fixed. Correlation between those eight contrasts is allowed by the union bound.

The evaluation freezes the policies before sampling, uses ordinary game payoffs,
and makes one final inferential look after 65,536 deals. Training-target
corrections are not added to evaluation winnings. Resource interruption is an
incomplete experiment, not an alternative stopping rule for claiming a winner.

## Uncertainty resolution

The implementation matches the scaled one-sided bound in Theorem 4 of
[Maurer and Pontil (2009)](https://www.learningtheory.org/colt2009/papers/012.pdf),
applied to both tails of eight contrasts. Allocating 0.05/16 to each tail gives
the logarithmic factor log(640). Scaling to the registered difference support
[-400.5, 400.5] produces radius

`sqrt(2 * sample_variance * log(640) / 65536) + 7 * 801 * log(640) / (3 * 65535)`.

The second term alone is **0.184275 bb per entry**. Thus even an observed
zero-variance contrast cannot get a smaller untruncated radius under this
registered method. The following are illustrations, not measured variances or
power estimates:

| Sample standard deviation (bb per entry) | Interval radius (bb per entry) |
| ---: | ---: |
| 0 | 0.1843 |
| 5 | 0.2545 |
| 10 | 0.3247 |
| 20 | 0.4651 |
| 40 | 0.7460 |

These are units per entry into this restricted research game, not win rates
per hand dealt at a full table. Small real improvements may remain unresolved.
The independent reader recomputes means and sample variances from the archived
paired values with scalar sums; it does not call the evaluation accumulator.

## Decision after the fixed comparison

Report all eight means, standard errors, and simultaneous intervals. A positive
interval supports that particular player replacement against that fixed
opponent; a negative interval supports harm. An interval containing zero is
inconclusive. Do not select a favorable seed, continue sampling until a result
becomes significant, or replace the registered interval after viewing results.

Report the two-seed root-range consistency comparison separately. It describes
reproducibility, not accuracy. Even favorable payoff and consistency results do
not establish an equilibrium or agreement with GTO Wizard. Opponent coverage,
blind defenses, other positions, stack depths, and the quality of the postflop
continuation model remain part of the wider preflop research objective.

No source defect was identified in this review. Full-bank GPU/later-action
controls and fresh evaluation still have to run after all training arms and
their independent audits finish. No fresh outcomes were inspected here.
