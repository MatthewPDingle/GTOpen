# Balanced board coverage did not improve this comparison

The main GPU comparison completed, but the independent CPU verification
failed its fixed classification tolerance. Treat the numbers below as
retained GPU results, not a fully independently qualified improvement.
Nothing is promoted, deployed, retrained or retried. The original failed
verification and its thresholds remain unchanged.

## Main result

Both training sets used 1,024 boards, the same eight fixed training runs,
and shared validation. The primary comparison is structured versus random
training boards with 387 inputs. Stress boards and the 362-input diagnostic
remain separate. All models were selected before final-test labels existed.

| Seed | Random loss / stack | Structured loss / stack | Change in error | Required result |
| --- | ---: | ---: | ---: | --- |
| 9297101 | 0.09975% | 0.10026% | +0.51% | Fail |
| 9297102 | 0.11056% | 0.15367% | +38.99% | Fail |

Lower loss is better. The required reduction was at least 20% in BOTH seeds,
plus mean loss at most 0.001 starting stacks at EACH of 60bb and 150bb.
Structured training did not clear either combined gate. The slight increase
in the first seed and substantial increase in the second do not support
adopting this board-balancing recipe. This is a finite two-seed comparison,
not proof that every structured sampling approach is ineffective.

| Seed | Stack | Random mean, bb | Structured mean, bb | Required maximum, bb | Structured p99, bb | Structured maximum, bb |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 9297101 | 60 | 0.06150 | 0.06702 | 0.060 | 2.2289 | 21.7750 |
| 9297101 | 150 | 0.14549 | 0.13322 | 0.150 | 3.4008 | 64.2750 |
| 9297102 | 60 | 0.06890 | 0.09596 | 0.060 | 2.7871 | 29.5083 |
| 9297102 | 150 | 0.15943 | 0.22109 | 0.150 | 5.7584 | 76.3674 |

Loss here is per evaluated terminal river decision, not bb/100 or whole-game
exploitability. The opponent is uniform over legal hands. These diagnostic
weights are not an all-street policy and do not establish preflop accuracy.

## Why independent verification failed

The first preserved failure is seed 9297101, random training, 362 inputs,
random test boards, 40bb. Two board-level majority-action error rates
differed by one classified decision each:

| Board index | Eligible decisions | GPU errors | CPU errors | Rate difference | Fixed limit |
| --- | ---: | ---: | ---: | ---: | ---: |
| 51 | 75652 | 994 | 995 | 0.00001322 | 0.00001 |
| 101 | 75670 | 908 | 907 | 0.00001322 | 0.00001 |

The context-wide mean loss differed by 8.4318286e-08bb.
All other recorded metric checks in this failing context stayed within their
fixed tolerances, including board-level cash means and tails. Nevertheless,
the full verification did not pass and remaining comparisons were not all
completed. Do not label the entire study independently verified.
The count difference is proven; the exact affected holdings/raw scores were
not retained in this failure and their numerical cause remains unconfirmed.
No thresholds are relaxed after observing the outcome.

## Diagnostic arms and stress test

| Seed | Training | Inputs | Test | Selected update | Validation loss/stack | Held-out-depth loss/stack |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| 9297101 | random | 362 | stress | 8192 | 0.13559% | 0.67353% |
| 9297101 | structured | 362 | stress | 8192 | 0.13285% | 0.40788% |
| 9297101 | random | 387 | stress | 8192 | 0.08709% | 0.91472% |
| 9297101 | structured | 387 | stress | 8192 | 0.08686% | 0.15233% |
| 9297101 | random | 362 | test | 8192 | 0.13559% | 0.13714% |
| 9297101 | structured | 362 | test | 8192 | 0.13285% | 0.13095% |
| 9297101 | random | 387 | test | 8192 | 0.08709% | 0.09975% |
| 9297101 | structured | 387 | test | 8192 | 0.08686% | 0.10026% |
| 9297102 | random | 362 | stress | 8192 | 0.14702% | 0.71525% |
| 9297102 | structured | 362 | stress | 4096 | 0.21957% | 0.41171% |
| 9297102 | random | 387 | stress | 8192 | 0.15167% | 1.28437% |
| 9297102 | structured | 387 | stress | 8192 | 0.12835% | 0.24890% |
| 9297102 | random | 362 | test | 8192 | 0.14702% | 0.18741% |
| 9297102 | structured | 362 | test | 4096 | 0.21957% | 0.20355% |
| 9297102 | random | 387 | test | 8192 | 0.15167% | 0.11056% |
| 9297102 | structured | 387 | test | 8192 | 0.12835% | 0.15367% |

The companion JSON preserves every hand/actor/price contribution and every
board-cell count/mean, including empty cells and adverse results. It never
combines deliberately rare stress boards into the natural-frequency test.
Fresh boards and seeds differ from prior studies, so cross-study reductions
must not be claimed as a matched effect of adding more random boards.

## Next recommendation

Keep natural-frequency random board sampling as the research baseline.
Do not spend another long run extending this balanced recipe unchanged.
First propose a small, separately registered numerical diagnostic on frozen
weights that records the exact decisions and probabilities near the 50%
classification boundary. It should explain this verification failure without
relabeling the failed attempt as a success. No such diagnostic is launched here.
Then choose the next accuracy study using the retained error breakdown, with
fresh evaluation boards and unchanged separation from any tuning data.
Action-conditioned opponent ranges and multiple decisions remain essential
before these results can improve practical preflop ranges.

## Resources and disposition

Main work took 1953.2s; failed CPU verification ended after 235.0s.
Peak CUDA allocation/reservation was 2.065/2.139GB.
Both processes exited and the research lock was released. All failures and
scientific artifacts remain intact. Production 56708 is unchanged.
No GitHub push, deployment or claim of broad preflop-goal completion.
