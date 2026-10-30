# Board-root comparison: interpretation and next decision

The completed experiment shows a useful reduction in run-to-run range disagreement,
but does not yet establish stronger or sufficiently reliable preflop play. Keep
this method as a research candidate; do not promote it to the production model.

## What the full result supports

Both candidates completed 78 updates. All 65,536 registered evaluation deals and
all 2,048 batches passed readback across both checkpoint attempts. The comparison
and verification used the original registered sample and stopping rule.

Entry-weighted disagreement between the two runs fell from
49.65% to 38.63%:
11.02 percentage points, or about
22.2% less disagreement.
This describes these two runs. It is not an accuracy percentage, EV loss,
confidence interval over training seeds, or a general convergence guarantee.

The registered eight payoff intervals establish 0 gains and 0
losses; 8 remain inconclusive. Seven point estimates are
positive and one negative. They share evaluation deals and opponents, so their
signs must not be treated as eight independent replications or a new success test.
The full intervals, including the unfavorable comparison, remain in
[BOARD-FINAL-FINDINGS.md](BOARD-FINAL-FINDINGS.md).

## Descriptive hand-level review

These family summaries were added after seeing the completed results. They are
diagnostics, not new confirmatory tests. All 169 classes remain available in the
bound [complete table](board-final-all-hand-classes.json); families and hands
are correlated through shared training and boards.

| Family | Control disagreement | Candidate disagreement | Change |
| --- | ---: | ---: | ---: |
| pairs | 37.66% | 24.58% | -13.09 pp |
| suited | 53.85% | 37.18% | -16.67 pp |
| offsuit | 49.25% | 40.28% | -8.96 pp |

Disagreement decreased for 107/169 classes, representing
61.3% of incoming hand mass. It did not improve
everywhere: 62 classes worsened, and
55 still differ by more than 50 percentage
points of total variation between candidate runs.

For concrete examples of the remaining disagreement, TT jams
78.44% versus 0.40%, while 88 calls 84.52% versus
0.01%. These were selected as diagnostic examples after reviewing the
full table, not as separate statistical evidence. Root action-value evidence is
needed to distinguish costly errors from nearly tied actions; appearance alone
cannot settle that question.

## Runtime and verification

Recorded candidate update time was about 58 minutes per arm, similar to the
historical controls. Additional board work overlapped other work. This was not a
controlled speed comparison, and overlapping stage times must not be summed.

The successful resumed scientific evaluation invocation took
120.62 minutes. The earlier failed wrapper
attempt took 36.78 minutes and is not included in that number.
The recovery queue also includes waiting and admission overhead; its elapsed time
overlaps the successful invocation and must not be added to it. Full evaluation
readback took 13.87 minutes; complete training readback had
taken 241.89 minutes. These are research workflow
timings, not production solver latency.

Visual review of the generated plot confirmed all eight labeled comparisons,
readable axes and units, and complete error bars crossing zero. The 337 report
input hashes and four generated artifact hashes were checked. The readback shares
the poker engine and policy representation; this does not independently certify
the poker rules or equilibrium.

## Next research step

First examine the already saved root policies and regrets through all 78 updates
for both candidates, against the existing control trajectories. Report every
class and every transition, with fixed first/middle/last 26-generation windows.
Reproduce the evaluated average exactly and exclude unplayed generation 78 from
it. Generation 78 may appear only as an explicitly labeled movement diagnostic.
This requires no new training deals and does not extend the completed experiment.

The purpose is to distinguish ranges still changing substantially from ranges
that settled early into different answers. Then design a fresh fixed-policy
action-value diagnostic for the complete averaged policies, covering all 169
classes and separating exact preflop terms from postflop continuation estimates.
Do not substitute generation 77 for the evaluated average, smooth charts by hand,
or extend this finished payoff sample because an interval is close to zero.

Only after that evidence should we choose more boards, longer training, or a
change to continuation learning. A separate replication will be needed before
claiming a reliable gain across random seeds. Other positions, stack depths,
bet menus, multiway play, and matched GTO Wizard comparisons remain outstanding.
Production has not been changed.
