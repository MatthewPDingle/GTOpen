# Equity-pricing comparison: completed findings

The candidate did not achieve an independently qualified pass of the registered primary comparison.

Independent CPU verification: passed.
The table uses retained GPU measurements. Independent CPU reconstruction agrees within the fixed tolerances.

| Seed | Baseline loss / stack | Candidate loss / stack | Error reduction | Recorded primary gate |
| --- | ---: | ---: | ---: | --- |
| 9297601 | 0.09416% | 0.09083% | +3.54% | Fail |
| 9297602 | 0.12185% | 0.07080% | +41.89% | Pass |

The fixed requirement was at least 20% lower mean normalized loss in BOTH
seeds, plus mean loss no greater than 0.001 starting stacks at EACH of 60bb
and 150bb. These depths were excluded from fitting and model selection.

| Seed | Stack | Baseline mean, bb | Candidate mean, bb | Allowed mean, bb | Baseline p99, bb | Candidate p99, bb | Baseline worst, bb | Candidate worst, bb |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9297601 | 60 | 0.06298 | 0.05743 | 0.060 | 1.8306 | 2.1553 | 24.8114 | 40.5803 |
| 9297601 | 150 | 0.12502 | 0.12890 | 0.150 | 3.5030 | 4.2250 | 47.8742 | 92.8705 |
| 9297602 | 60 | 0.07104 | 0.04298 | 0.060 | 2.5576 | 1.3672 | 26.2833 | 14.0985 |
| 9297602 | 150 | 0.18793 | 0.10494 | 0.150 | 5.4311 | 3.0371 | 64.1561 | 39.8886 |

Adverse outcomes must stay visible alongside the aggregate improvements:

- Seed 9297601 at 60bb: candidate worsened p99, worst observed loss.
- Seed 9297601 at 150bb: candidate worsened mean, p99, worst observed loss.

Loss is foregone value per evaluated terminal river decision, not bb/100
or whole-game exploitability. Rows share boards and public situations; the
large decision count is not a count of independent samples.

## Model selection and separate stress results

| Seed | Approach | Evaluation boards | Selected update | Validation loss / stack | Held-out-depth loss / stack |
| --- | --- | --- | ---: | ---: | ---: |
| 9297601 | direct_value | stress | 8192 | 0.07799% | 0.95190% |
| 9297601 | equity_priced | stress | 4096 | 0.10588% | 1.26771% |
| 9297601 | direct_value | test | 8192 | 0.07799% | 0.09416% |
| 9297601 | equity_priced | test | 4096 | 0.10588% | 0.09083% |
| 9297602 | direct_value | stress | 8192 | 0.09573% | 0.41516% |
| 9297602 | equity_priced | stress | 8192 | 0.06141% | 1.18277% |
| 9297602 | direct_value | test | 8192 | 0.09573% | 0.12185% |
| 9297602 | equity_priced | test | 8192 | 0.06141% | 0.07080% |

Both approaches received the same batch objects and training budget. All four
selected model identities were frozen before the new final-test/stress labels
were generated. Ordinary and deliberately rare stress boards stay separate.
The candidate has fewer learned parameters and different known structure;
this is not an equal-capacity comparison or an isolated feature ablation.

## What this does and does not establish

This reference fixes the opponent to a uniform distribution of legal hands.
It tests learning visible-card equity and known terminal calling economics.
It does not test actual opponent ranges selected by previous betting, future
betting decisions, multiway continuation, or end-to-end preflop ranges.

Earlier evidence already rejected substituting uniform-opponent equity for
betting-conditioned equity in larger pots. A positive result here would
justify a range-conditioned follow-up, not a production replacement.

The companion JSON retains hand/actor/price contributions, board-cell means
and every numerical discrepancy, including adverse outcomes. No historical
failure is retried or relabeled, and no numerical tolerance is relaxed.

## Resources

Main work: 1008.0s. CPU verification: 1588.0s.
Peak reserved CUDA memory: 2.154 GB.
No production change or GitHub push. The broader preflop goal remains incomplete.
