# Root-action values under the retained complete policies

All 65,536 previously evaluated deals passed replay and independent readback. This is an exploratory diagnostic of the restricted 200bb BB-versus-BTN-2bb-open spot, with 0.5bb dead money and 5% rake capped at 2bb.

These results vary only the first BB action; later play remains fixed. They are not a full best response or a demonstration of accurate ranges. The eight original registered payoff comparisons remain inconclusive.

All 169 classes and eight crossed profiles are included. Evaluation counts range from 160 to 656 deals per class. Counts measure evaluation coverage, not the unavailable per-hand training support.

## Sample-selected root changes

The following diagnostic chooses the highest observed BB value separately for each class on this same sample. The resulting gains are upward-selected and have not been independently validated; they must not be called exploitability or measured improvement. Units are bb per entry to this restricted spot, not bb/100.

| Complete profile | Original BB value | Sample-selected root gain |
| --- | ---: | ---: |
| first:oldBB-oldBTN | -0.4468 | 0.3502 |
| first:oldBB-newBTN | -0.4288 | 0.4329 |
| first:newBB-oldBTN | -0.3920 | 0.2254 |
| first:newBB-newBTN | -0.3283 | 0.3863 |
| replication:oldBB-oldBTN | -0.4607 | 0.3039 |
| replication:oldBB-newBTN | -0.4642 | 0.3697 |
| replication:newBB-oldBTN | -0.3848 | 0.2440 |
| replication:newBB-newBTN | -0.4352 | 0.3355 |

## Why the candidate runs disagree

The candidate root ranges differ in their dominant action for 74 classes; entry-weighted total variation is 38.63%. For those classes, compare the two dominant actions under each run's own complete policies:

| Signs of the observed value difference | Classes | Incoming mass |
| --- | ---: | ---: |
| Both runs value the replication's action higher | 22 | 11.41% |
| Both runs value the first run's action higher | 23 | 14.71% |
| Each run values the other action higher | 3 | 1.55% |
| Each run values its own dominant action higher | 26 | 17.99% |

These categories use point-estimate signs, without a significance claim. Both opponent behavior and the BB's later behavior differ between runs, so this comparison cannot isolate which continuation causes a difference. All paired differences and descriptive standard errors are retained in the JSON report.

## Illustrative hands

These examples were chosen from earlier range concerns. The full table includes all hands, including unfavorable cases. Values below follow fold / call / raise / jam; probabilities show the already evaluated average policy.

| Hand | Deals | First policy (%) | First BB values | Replication policy (%) | Replication BB values |
| --- | ---: | --- | --- | --- | --- |
| AA | 246 | 0.0 / 0.0 / 99.6 / 0.3 | -1.00 / 1.68 / 29.13 / 25.55 | 0.0 / 0.0 / 99.6 / 0.4 | -1.00 / 1.89 / 23.73 / 28.53 |
| KK | 315 | 0.0 / 0.0 / 99.3 / 0.6 | -1.00 / -0.06 / 16.20 / 11.94 | 0.0 / 0.0 / 52.1 / 47.9 | -1.00 / 0.05 / 11.07 / 13.71 |
| QQ | 307 | 0.0 / 0.0 / 18.7 / 81.3 | -1.00 / -1.50 / 4.41 / 7.63 | 0.0 / 0.0 / 21.0 / 79.0 | -1.00 / -1.16 / 7.77 / 9.00 |
| JJ | 288 | 0.0 / 0.0 / 69.2 / 30.8 | -1.00 / -1.59 / 1.61 / 2.28 | 0.0 / 0.0 / 99.5 / 0.4 | -1.00 / -1.34 / 4.44 / 3.96 |
| TT | 290 | 0.0 / 0.0 / 21.5 / 78.4 | -1.00 / -2.09 / -0.62 / 1.00 | 0.0 / 0.0 / 99.6 / 0.4 | -1.00 / -2.17 / 1.48 / 2.29 |
| 99 | 305 | 0.0 / 0.0 / 99.3 / 0.6 | -1.00 / -2.98 / 1.48 / -4.21 | 0.0 / 0.0 / 99.6 / 0.3 | -1.00 / -2.68 / 0.99 / -3.58 |
| 88 | 295 | 0.0 / 84.5 / 10.9 / 4.5 | -1.00 / 1.90 / -0.29 / -3.48 | 0.0 / 0.0 / 96.4 / 3.6 | -1.00 / -2.38 / 3.01 / -4.36 |
| AQs | 165 | 0.0 / 37.9 / 61.4 / 0.8 | -1.00 / 4.35 / -1.07 / -4.18 | 0.0 / 0.0 / 99.5 / 0.5 | -1.00 / -1.57 / -1.10 / -4.13 |
| AJs | 179 | 0.0 / 27.6 / 71.9 / 0.5 | -1.00 / 2.55 / 1.19 / -7.29 | 0.0 / 61.8 / 37.8 / 0.4 | -1.00 / 1.39 / 0.15 / -6.90 |
| ATs | 192 | 0.0 / 5.0 / 94.4 / 0.5 | -1.00 / 0.90 / 0.56 / -8.77 | 0.0 / 90.3 / 9.3 / 0.4 | -1.00 / 0.84 / -2.99 / -8.75 |
| KQs | 195 | 0.0 / 98.9 / 0.6 / 0.5 | -1.00 / 2.46 / 2.66 / -9.91 | 0.0 / 99.3 / 0.5 / 0.2 | -1.00 / 1.74 / -4.34 / -10.05 |
| KQo | 577 | 0.0 / 77.5 / 22.3 / 0.2 | -1.00 / 0.63 / 0.85 / -6.72 | 0.0 / 51.5 / 48.3 / 0.2 | -1.00 / 0.43 / 1.69 / -7.28 |
| 98s | 204 | 2.8 / 97.1 / 0.0 / 0.0 | -1.00 / -0.01 / -3.68 / -8.94 | 43.9 / 35.0 / 21.1 / 0.0 | -1.00 / 0.20 / 1.03 / -9.51 |
| 76s | 202 | 47.0 / 41.8 / 11.2 / 0.0 | -1.00 / -0.96 / 0.43 / -12.64 | 6.6 / 93.4 / 0.0 / 0.0 | -1.00 / -0.44 / -3.40 / -13.97 |

## Evidence and limits

- [All hand classes and paired differences](board-root-action-all-classes-v1.json).
- [Flat all-hand table](board-root-action-all-classes-v1.csv).
- [Independent readback](board-root-action-replay-readback-v1-result.json).
- No new deals, new training, production deployment or fresh accuracy qualification.
- Preflop all-ins use the existing conditional equity calculation; ordinary postflop outcomes use sampled boards.
- The verifier shares the original poker evaluator. It independently checks retained inputs and arithmetic, not poker-engine correctness.
- Next-step selection requires reviewing this full result; any proposed gain needs fresh, specified validation.
