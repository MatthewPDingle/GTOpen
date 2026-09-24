# Root-retention replication: ranges are still unstable

The second fixed-budget run completed all 78 updates and passed the independent
training and endpoint audits. It does **not** reproduce a dependable improvement
in preflop ranges. Aggregate action percentages are fairly similar between runs,
but the hands assigned to those actions change substantially. Do not deploy or
select either seed as the better model.

This remains the single BB-versus-BTN 2 bb open, 200 bb, 5% rake capped at 2 bb
experiment with fixed incoming ranges and the registered limited tree. It does
not validate other positions, stacks, sizes or multiway games.

## Completion and restart provenance

The unexpected Windows reboot interrupted the original replication. Five fully
verified updates were imported into a separate store, their prefix was audited,
and the next update reproduced the original durable checkpoint byte for byte.
The resumed trial completed the originally planned 78 updates / 39,936 deals,
with unchanged seeds, algorithm and total runtime budget. The interrupted
original store is preserved and is not represented as a completed trial.

The full independent reader reconstructed all 39,936 BB roots, 893,839 BB and
126,943 BTN reservoir insertions, saved random streams, targets and policies.
Maximum root-state discrepancy was 3.64e-12 and maximum policy discrepancy was
1.44e-12. This verifies execution; it is not evidence of poker strength.

## Exact restricted endpoint results

Gains are bb per entry. Smaller is better, but these are restricted deviations,
not full exploitability. BB can move only its existing fold/jam probability;
call, non-all-in raise and subsequent play are fixed. BTN can change only its
response to the initial jam. The primary policy remains the linear-weighted
average of all played generations 0-77, excluding unplayed generation 78.

| Run | BB gain | BTN gain |
| --- | ---: | ---: |
| Older exact-initial pilot | 0.013793494 | 0.013539927 |
| First root-retention seed | 0.007994039 | 0.010040248 |
| Root-retention replication | 0.012498562 | 0.017961039 |

The replication is worse than the first seed on both endpoint measures. Compared
with the older pilot, BB is slightly better and BTN worse. Two seeds do not
isolate the causal effect of root retention, and we must not average away or
select around this unfavorable result.

All predeclared replication pairings:

| BB averaging / BTN averaging | BB gain | BTN gain |
| --- | ---: | ---: |
| equal/equal | 0.072837165 | 0.028396045 |
| equal/linear | 0.075856284 | 0.003832618 |
| linear/equal | 0.007836169 | 0.037276133 |
| linear/linear (primary) | 0.012498562 | 0.017961039 |

CPU/CUDA initial policies matched exactly. Independent outcome-wise scalar
reconstruction passed for all four pairings: maximum discrepancy 2.88e-16 bb,
cashflow-conservation discrepancy 1.42e-14 bb. The endpoint evaluator took
191.7 seconds, its independent reader 77.2 seconds.

## Overall percentages conceal hand-level instability

Percentages below use the exact incoming hand mass, including removal from the
opponent's fixed range.

| BB action | First seed | Replication | Change, percentage points |
| --- | ---: | ---: | ---: |
| Fold | 43.10% | 45.79% | +2.69 |
| Call | 41.12% | 38.61% | -2.51 |
| Raise | 15.33% | 14.81% | -0.52 |
| Jam | 0.45% | 0.78% | +0.33 |

The incoming-mass-weighted total variation is **46.32 percentage points**:
roughly 46% of action probability must move between actions, within each hand,
to turn the first chart into the second. This does not mean 46% of decisions
are proven wrong. It does mean the similar aggregate call/raise totals are
not evidence of a reproducible hand chart.

Examples (illustrative, not poker recommendations):

- AJs: 99.74% raise in the first run; 97.56% call in the replication.
- 85o: 99.91% call in the first run; 99.70% fold in the replication.
- T9s: 97.79% raise in the first run; 77.17% fold / 22.82% call in the replication.

The descriptive late-bank check does not support blaming early uniform play
alone. Cross-seed total variation is 43.56 points in generations 0-38, 48.23
in generations 39-77, and 49.38 in generations 65-77. These slices were inspected
after seeing the primary comparison and are diagnostics only. They are not
replacement candidate policies or predeclared quality tests.

## Why the next experiment should target noisy call/raise learning

Keeping all root observations prevents reservoir eviction, but does not create
additional information. Across the entire 39,936-deal trial, the first run has
95-421 samples per hand class and the replication 93-409; both medians are 171.
Suited classes frequently have little more than a hundred examples spread over
78 changing opponent policies and postflop continuations.

The existing observations show large call/raise payoff variation. For example,
AJs has 124 and 109 samples in the two trials; the sample standard deviation of
call-minus-raise payoff is 60.87 and 55.94 bb. Its corresponding means are -1.26
and +8.02 bb. These are descriptive training statistics, **not** confidence
intervals for a fixed opponent or proof of which action is best. Both players
and their continuation policies were changing during training.

The evidence is consistent with noisy action values producing unstable,
near-pure hand choices. It does not isolate sampling noise from downstream
model error, training dynamics or genuinely close action values. The existing
independent audits check the implemented calculations, not the adequacy of the
approximation to poker.

Next priority: a bounded, fixed-continuation diagnostic of call and raise values
across all classes, using balanced class coverage and paired estimates on common
deals. First measure estimator variance and repeatability, then test a variance
reduction or sampling change in a separately registered experiment. Preserve
the physical conditional card distribution and correct weights. Do not smooth
charts merely to make them look plausible, tune on inspected holdouts, claim
accuracy from all-in endpoints, or launch another large training sweep blindly.

A broader response evaluation of the replication remains **not run**. If needed,
it requires its own prospective seeds, numerical/resource admission and storage
gate. No claim about its full call/raise exploitability is made here.

## Storage and production

Previous lossless compression recovered 306.154 GB without deleting results.
The latest admission measured 754.788 GB of allocated research files across
S:/GTOpen-research, T:/GTOpen-research and this repository's research folder.
The global 800 GB ceiling includes a 2 GB reserve in new-job admission.

The resumed training store occupies 3.015 GB allocated (9.592 GB logical).
The endpoint store adds only 24,576 allocated bytes. The range comparison and
training diagnostics reuse existing evidence without new solves or model fits.
The previous wider study's 46.091 GB allocation allowance would not fit the
latest remaining headroom plus reserve, so that job must not simply be cloned
and launched under the current storage budget.

Production 56708 is unchanged by these evaluations. No model is promoted.

## Evidence

- Full training audit: `root-retained-replication-resume-v1-independent-review.json`
  (`62e29c894f7222897b19151c4786dd8eb0d1117189bcfbf887742e50b9cde9b9`).
- Endpoint registration: `root-retained-replication-exact-v1-registration.json`
  (`1ae6546761720a169db23b40cab8fc6e5c11a434909beca853acc9cdaac42a36`).
- Endpoint result: `root-retained-replication-exact-v1-result.json`
  (`7602b37dba4fdd3ecaf6901ea986440f04eb871a5a94b79339feaab5b6fbb5d4`).
- Independent endpoint reader: `root-retained-replication-exact-v1-independent-review.json`.
- Predeclared range comparison: `root-retained-seed-range-comparison-v1-result.json`
  (`8ccec24031d562aa51c90ce2e5b84e5ca21cf5e2491a0699b1fc8bfd460acb49`).
- Post-hoc sample diagnostics: `root-retained-seed-diagnostics-v1-result.json`
  (`0cdb7b5ddb24690a7a459a26aa5b5750c98cfff1ee1cd78ac1f468d40f7b02e4`).
