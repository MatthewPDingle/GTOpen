# Visible-feature candidate: completed sampled evaluation

The additional visible poker features changed the strategy substantially, but the completed sampled tests do **not establish an accuracy improvement**. Both candidates remain research-only. All 78 training updates and both-player evaluation audits passed; those passes establish execution and reconstruction, not equilibrium accuracy.

## Fixed test context

BB facing a BTN open to 2 bb, 200 bb effective stacks, pot 3.5 bb, 5% rake capped at 2 bb, fixed incoming ranges and a limited betting menu. This is a heads-up continuation extracted from a seven-seat context. Earlier folded cards remain omitted. These results do not establish performance across positions, stacks, larger menus or the earlier UTG/LJ Wizard comparison.

Each candidate used 78 played generations and 39,936 training deals. The unused next generation is excluded. Each evaluation used 8,192 responder-training deals and 16,384 separate test deals. The new candidate needed 186.764 minutes of cumulative training-controller execution, including a separately declared completion extension; it failed the original three-hour wall-time cap. Offline audits and reboot downtime are additional.

## Complete-prior root frequencies

These use the independently checked compatible-card prior, not rounded UI percentages or an unweighted average of 169 classes.

| Candidate | Fold | Call | Raise to 6 bb | Shove to 200 bb |
|---|---:|---:|---:|---:|
| combined_269 | 48.54% | 31.42% | 15.86% | 4.17% |
| visible_302 | 40.90% | 36.60% | 18.79% | 3.71% |

The new candidate folds 7.64 percentage points less and calls 5.18 points more. Its entry-weighted per-class total-variation distance from the previous policy is 38.49%. More calling and greater visual variety are not accuracy measures. Opponent and continuation policies also changed, so these are not values against a common opponent.

## All registered deviation tests

Values are gains relative to the corresponding baseline, in bb per original spot entry. Positive means the alternative did better. Each family reserves 2.5% error across its alternatives. These are restricted deviations, not a full best-response upper bound. Negative fitted-response estimates can arise from an imperfect responder and sampling error; they do not imply negative exploitability.

| Player / alternative | Previous mean [lower, upper] | New mean [lower, upper] |
|---|---:|---:|
| BB / trained-response | -0.354 [-1.802, +1.093] | -0.363 [-1.762, +1.036] |
| BB / always-fold | -0.639 [-2.033, +0.755] | -0.387 [-1.765, +0.991] |
| BB / always-call | -1.239 [-2.538, +0.060] | -0.755 [-2.022, +0.511] |
| BB / always-raise | -5.277 [-6.748, -3.805] | -4.924 [-6.376, -3.471] |
| BB / always-jam | -15.663 [-18.610, -12.717] | -16.140 [-19.152, -13.128] |
| BTN / trained-response | -0.180 [-1.171, +0.811] | -0.050 [-1.027, +0.926] |
| BTN / always-fold | +0.004 [-1.005, +1.013] | -0.017 [-1.000, +0.965] |
| BTN / always-call | -1.634 [-2.903, -0.366] | -1.021 [-2.264, +0.221] |

No tested alternative has a positive lower bound for the new candidate. However, the learned BB response interval still allows about +1.04 bb per entry, and the BTN response interval allows about +0.93 bb. These broad intervals are inconclusive. The earlier completed response-stability diagnosis also showed that sparse response-training samples can produce a weak counter-strategy; absence of detected gains is therefore limited reassurance.

Conditional BTN calling after a BB shove was 25.88% for the previous candidate and 26.26% for the new one on their separate sampled streams. This is conditional on reaching the shove and is not the fraction of all dealt hands. Sampled BB shove reach was 4.25% versus 3.73%.

## Next decision

Finish the complete private-pair equity cache, independently audit it, then run the fixed exhaustive BTN response check and BB fold/shove reallocation check for both candidates. Those endpoints can expose concrete errors without a fitted responder or chance sampling, while remaining narrow tests of the fixed context. Their results will determine whether to change training or first strengthen the remaining call/raise evaluation. No production promotion follows from these sampled results.

The comparison initially stopped on the legacy empty-session activity check; v2 changes only that guard and output identity. The separately prepared equity controller then failed before enumeration when writing an existing status file. Its original attempt and stale-lock provenance are preserved; v2 repairs atomic status updates and lock cleanup. No model or payoff code changed in either repair.

## Complete 169-class policy readback

Order within each cell is fold / call / raise / shove, in percent. These are descriptive policies, not per-hand statistical accuracy claims. No hand is selected for a corrective range patch.

| Hand | Previous F / C / R / J | New F / C / R / J |
|---|---:|---:|
| 22 | 32.6 / 41.7 / 3.1 / 22.5 | 22.9 / 40.9 / 26.4 / 9.8 |
| 32o | 36.4 / 62.8 / 0.4 / 0.3 | 88.7 / 0.9 / 10.0 / 0.3 |
| 42o | 80.2 / 19.1 / 0.3 / 0.3 | 10.6 / 88.8 / 0.3 / 0.3 |
| 52o | 94.0 / 5.2 / 0.5 / 0.3 | 46.4 / 24.3 / 29.0 / 0.3 |
| 62o | 96.3 / 2.2 / 1.1 / 0.3 | 44.6 / 54.1 / 1.0 / 0.3 |
| 72o | 80.2 / 19.0 / 0.3 / 0.5 | 56.3 / 42.9 / 0.3 / 0.5 |
| 82o | 96.0 / 3.4 / 0.3 / 0.3 | 94.0 / 5.0 / 0.7 / 0.3 |
| 92o | 43.7 / 47.0 / 9.0 / 0.3 | 18.9 / 80.1 / 0.7 / 0.3 |
| T2o | 43.4 / 45.6 / 10.8 / 0.3 | 18.6 / 51.9 / 29.2 / 0.3 |
| J2o | 4.8 / 90.9 / 4.0 / 0.3 | 34.3 / 15.5 / 49.9 / 0.3 |
| Q2o | 45.4 / 53.9 / 0.3 / 0.3 | 73.3 / 26.1 / 0.3 / 0.3 |
| K2o | 83.7 / 6.0 / 9.1 / 1.2 | 85.6 / 0.8 / 12.3 / 1.2 |
| A2o | 52.7 / 42.5 / 3.5 / 1.3 | 2.9 / 94.4 / 1.3 / 1.4 |
| 32s | 24.2 / 75.2 / 0.3 / 0.3 | 86.7 / 6.4 / 6.6 / 0.3 |
| 33 | 43.0 / 26.8 / 17.3 / 12.9 | 2.9 / 14.7 / 82.2 / 0.3 |
| 43o | 76.6 / 13.2 / 9.9 / 0.3 | 33.5 / 59.9 / 6.3 / 0.3 |
| 53o | 98.6 / 0.8 / 0.3 / 0.3 | 58.5 / 15.3 / 25.9 / 0.3 |
| 63o | 69.4 / 29.6 / 0.7 / 0.3 | 49.1 / 44.8 / 5.7 / 0.3 |
| 73o | 58.2 / 30.3 / 11.2 / 0.3 | 66.0 / 32.2 / 1.5 / 0.3 |
| 83o | 11.9 / 57.7 / 30.1 / 0.3 | 35.4 / 63.5 / 0.8 / 0.3 |
| 93o | 55.0 / 42.3 / 2.4 / 0.3 | 54.9 / 43.7 / 1.0 / 0.3 |
| T3o | 72.8 / 25.3 / 0.8 / 1.1 | 70.5 / 27.2 / 1.2 / 1.1 |
| J3o | 83.9 / 14.9 / 0.9 / 0.3 | 65.9 / 32.9 / 0.9 / 0.3 |
| Q3o | 16.1 / 79.3 / 4.2 / 0.3 | 90.6 / 8.8 / 0.3 / 0.3 |
| K3o | 67.3 / 30.4 / 1.0 / 1.3 | 39.6 / 57.8 / 1.4 / 1.3 |
| A3o | 71.6 / 26.0 / 2.1 / 0.3 | 49.9 / 48.6 / 1.1 / 0.3 |
| 42s | 59.1 / 18.2 / 20.1 / 2.6 | 78.9 / 16.2 / 2.2 / 2.6 |
| 43s | 74.6 / 17.7 / 7.4 / 0.3 | 54.8 / 44.6 / 0.3 / 0.3 |
| 44 | 46.0 / 39.3 / 12.9 / 1.8 | 24.9 / 63.8 / 9.5 / 1.8 |
| 54o | 29.3 / 65.7 / 4.7 / 0.3 | 23.2 / 59.6 / 16.9 / 0.3 |
| 64o | 62.7 / 27.2 / 8.9 / 1.3 | 62.7 / 30.8 / 5.2 / 1.3 |
| 74o | 98.4 / 0.9 / 0.3 / 0.3 | 27.7 / 71.6 / 0.3 / 0.3 |
| 84o | 97.1 / 1.0 / 1.5 / 0.3 | 73.2 / 25.3 / 1.2 / 0.3 |
| 94o | 47.2 / 33.4 / 19.1 / 0.3 | 97.0 / 0.7 / 2.0 / 0.3 |
| T4o | 51.8 / 47.5 / 0.3 / 0.3 | 70.2 / 29.1 / 0.3 / 0.3 |
| J4o | 36.2 / 62.4 / 1.1 / 0.3 | 11.0 / 48.4 / 40.3 / 0.3 |
| Q4o | 26.8 / 72.3 / 0.5 / 0.3 | 89.0 / 10.1 / 0.5 / 0.3 |
| K4o | 42.8 / 54.5 / 1.1 / 1.5 | 66.7 / 31.2 / 0.5 / 1.6 |
| A4o | 13.6 / 58.9 / 27.2 / 0.3 | 21.9 / 77.4 / 0.3 / 0.3 |
| 52s | 89.5 / 9.9 / 0.3 / 0.3 | 60.5 / 11.2 / 28.0 / 0.3 |
| 53s | 33.8 / 19.7 / 45.9 / 0.6 | 48.0 / 22.5 / 28.3 / 1.2 |
| 54s | 56.7 / 2.5 / 30.4 / 10.4 | 72.2 / 25.8 / 1.7 / 0.3 |
| 55 | 13.6 / 17.8 / 64.0 / 4.6 | 28.1 / 63.6 / 3.1 / 5.2 |
| 65o | 46.4 / 12.4 / 40.8 / 0.3 | 38.7 / 55.1 / 5.9 / 0.3 |
| 75o | 96.9 / 2.2 / 0.6 / 0.3 | 79.7 / 19.7 / 0.3 / 0.3 |
| 85o | 28.7 / 70.6 / 0.4 / 0.3 | 33.5 / 49.1 / 17.1 / 0.3 |
| 95o | 59.4 / 39.8 / 0.5 / 0.3 | 46.8 / 1.9 / 51.0 / 0.3 |
| T5o | 95.1 / 0.9 / 3.7 / 0.3 | 96.5 / 2.8 / 0.3 / 0.3 |
| J5o | 47.4 / 50.3 / 1.9 / 0.3 | 37.1 / 58.6 / 4.0 / 0.3 |
| Q5o | 1.2 / 62.0 / 36.5 / 0.3 | 76.7 / 11.4 / 11.6 / 0.3 |
| K5o | 51.5 / 21.8 / 26.4 / 0.3 | 69.9 / 26.7 / 3.0 / 0.3 |
| A5o | 47.9 / 29.9 / 19.1 / 3.1 | 23.4 / 65.3 / 8.9 / 2.3 |
| 62s | 94.3 / 0.8 / 3.8 / 1.1 | 74.7 / 21.9 / 2.3 / 1.1 |
| 63s | 75.6 / 17.0 / 7.1 / 0.3 | 39.1 / 59.7 / 0.9 / 0.3 |
| 64s | 51.3 / 48.0 / 0.3 / 0.3 | 61.7 / 37.7 / 0.3 / 0.3 |
| 65s | 3.3 / 5.1 / 90.4 / 1.1 | 27.1 / 58.8 / 13.0 / 1.1 |
| 66 | 0.7 / 24.4 / 35.5 / 39.5 | 0.4 / 1.4 / 72.0 / 26.1 |
| 76o | 52.0 / 46.5 / 0.3 / 1.2 | 43.1 / 55.4 / 0.3 / 1.2 |
| 86o | 52.1 / 47.3 / 0.3 / 0.3 | 31.4 / 37.8 / 30.5 / 0.3 |
| 96o | 13.4 / 82.9 / 3.3 / 0.3 | 7.8 / 18.9 / 73.0 / 0.3 |
| T6o | 51.2 / 27.6 / 20.9 / 0.3 | 30.6 / 68.7 / 0.3 / 0.3 |
| J6o | 64.1 / 31.2 / 4.4 / 0.3 | 73.1 / 25.0 / 1.5 / 0.3 |
| Q6o | 21.3 / 57.5 / 20.8 / 0.3 | 71.5 / 25.2 / 3.0 / 0.3 |
| K6o | 54.3 / 44.3 / 1.1 / 0.3 | 79.8 / 14.1 / 5.8 / 0.3 |
| A6o | 51.5 / 19.8 / 20.6 / 8.1 | 12.7 / 59.9 / 20.9 / 6.6 |
| 72s | 86.4 / 11.3 / 2.0 / 0.3 | 22.0 / 77.1 / 0.5 / 0.3 |
| 73s | 39.9 / 58.0 / 1.7 / 0.3 | 0.9 / 98.2 / 0.5 / 0.3 |
| 74s | 89.6 / 9.7 / 0.3 / 0.3 | 60.0 / 20.0 / 19.6 / 0.3 |
| 75s | 56.8 / 15.2 / 27.6 / 0.4 | 35.9 / 30.4 / 33.3 / 0.4 |
| 76s | 60.9 / 0.7 / 38.0 / 0.3 | 66.8 / 14.0 / 18.9 / 0.3 |
| 77 | 1.2 / 0.7 / 94.9 / 3.2 | 23.5 / 55.0 / 10.9 / 10.6 |
| 87o | 42.2 / 19.1 / 38.4 / 0.3 | 28.6 / 42.6 / 28.5 / 0.3 |
| 97o | 91.6 / 7.7 / 0.3 / 0.3 | 22.8 / 45.6 / 31.3 / 0.3 |
| T7o | 71.8 / 6.6 / 21.4 / 0.3 | 71.6 / 16.4 / 11.7 / 0.3 |
| J7o | 42.6 / 16.3 / 40.7 / 0.3 | 1.2 / 27.5 / 71.0 / 0.3 |
| Q7o | 95.1 / 1.2 / 3.3 / 0.3 | 64.2 / 29.8 / 5.7 / 0.3 |
| K7o | 69.9 / 27.8 / 1.1 / 1.1 | 13.2 / 71.7 / 14.5 / 0.6 |
| A7o | 1.1 / 94.0 / 1.8 / 3.1 | 7.7 / 36.2 / 51.9 / 4.3 |
| 82s | 31.4 / 43.2 / 25.1 / 0.3 | 77.5 / 21.0 / 1.2 / 0.3 |
| 83s | 53.0 / 11.1 / 35.6 / 0.3 | 8.8 / 88.8 / 2.1 / 0.3 |
| 84s | 74.0 / 18.8 / 6.8 / 0.3 | 43.4 / 48.1 / 8.2 / 0.3 |
| 85s | 38.1 / 54.6 / 6.8 / 0.5 | 24.5 / 73.8 / 1.4 / 0.3 |
| 86s | 15.9 / 6.0 / 77.8 / 0.3 | 51.8 / 18.0 / 30.0 / 0.3 |
| 87s | 68.9 / 12.4 / 18.0 / 0.7 | 57.8 / 37.6 / 3.8 / 0.7 |
| 88 | 0.6 / 78.5 / 20.1 / 0.9 | 6.9 / 17.0 / 36.3 / 39.8 |
| 98o | 50.4 / 19.2 / 30.1 / 0.3 | 2.6 / 78.8 / 18.2 / 0.3 |
| T8o | 50.9 / 1.8 / 47.1 / 0.3 | 24.8 / 74.5 / 0.3 / 0.3 |
| J8o | 98.1 / 0.9 / 0.7 / 0.3 | 23.3 / 76.0 / 0.3 / 0.3 |
| Q8o | 78.9 / 14.6 / 4.8 / 1.8 | 17.1 / 80.8 / 0.3 / 1.8 |
| K8o | 93.0 / 4.1 / 2.6 / 0.3 | 96.7 / 2.3 / 0.7 / 0.3 |
| A8o | 3.5 / 30.6 / 55.4 / 10.5 | 73.4 / 11.1 / 2.9 / 12.6 |
| 92s | 25.8 / 71.5 / 2.4 / 0.3 | 3.5 / 0.9 / 95.2 / 0.3 |
| 93s | 88.4 / 11.0 / 0.3 / 0.3 | 68.1 / 11.0 / 20.5 / 0.3 |
| 94s | 67.0 / 20.7 / 12.0 / 0.3 | 36.6 / 44.1 / 19.0 / 0.3 |
| 95s | 12.8 / 84.1 / 2.9 / 0.3 | 7.5 / 5.6 / 86.6 / 0.3 |
| 96s | 14.7 / 67.4 / 17.6 / 0.3 | 64.6 / 19.4 / 15.8 / 0.3 |
| 97s | 45.5 / 43.2 / 11.0 / 0.3 | 27.7 / 62.6 / 9.3 / 0.3 |
| 98s | 46.8 / 51.5 / 0.3 / 1.4 | 62.1 / 32.8 / 3.6 / 1.4 |
| 99 | 0.3 / 0.3 / 70.0 / 29.3 | 2.1 / 4.8 / 13.7 / 79.5 |
| T9o | 64.2 / 23.5 / 11.9 / 0.3 | 8.4 / 90.1 / 1.2 / 0.3 |
| J9o | 48.3 / 17.2 / 34.2 / 0.3 | 9.9 / 44.4 / 45.4 / 0.3 |
| Q9o | 10.0 / 88.4 / 1.3 / 0.3 | 38.7 / 29.7 / 31.3 / 0.3 |
| K9o | 91.2 / 1.3 / 7.0 / 0.6 | 41.3 / 54.6 / 3.7 / 0.3 |
| A9o | 33.3 / 26.0 / 31.5 / 9.3 | 11.5 / 29.6 / 58.5 / 0.3 |
| T2s | 88.0 / 11.3 / 0.3 / 0.3 | 14.6 / 84.7 / 0.3 / 0.3 |
| T3s | 81.9 / 16.6 / 1.2 / 0.3 | 90.3 / 8.8 / 0.5 / 0.3 |
| T4s | 77.1 / 17.0 / 5.6 / 0.3 | 60.5 / 36.0 / 3.2 / 0.3 |
| T5s | 9.1 / 34.7 / 55.8 / 0.3 | 27.5 / 57.3 / 14.9 / 0.3 |
| T6s | 33.4 / 45.2 / 21.1 / 0.3 | 44.7 / 29.0 / 26.0 / 0.3 |
| T7s | 95.1 / 4.2 / 0.3 / 0.3 | 97.6 / 1.8 / 0.3 / 0.3 |
| T8s | 40.5 / 58.0 / 0.3 / 1.2 | 54.9 / 21.7 / 15.2 / 8.1 |
| T9s | 27.0 / 37.5 / 35.2 / 0.3 | 0.9 / 95.7 / 3.1 / 0.3 |
| TT | 0.3 / 0.9 / 6.7 / 92.0 | 0.3 / 0.3 / 0.3 / 99.0 |
| JTo | 82.3 / 7.2 / 10.2 / 0.3 | 43.0 / 17.8 / 38.9 / 0.3 |
| QTo | 69.9 / 24.2 / 4.1 / 1.9 | 6.5 / 38.8 / 52.8 / 1.9 |
| KTo | 7.5 / 32.9 / 58.7 / 0.9 | 51.4 / 42.6 / 5.1 / 0.9 |
| ATo | 31.8 / 57.0 / 5.2 / 6.0 | 0.3 / 96.3 / 3.1 / 0.3 |
| J2s | 72.7 / 21.9 / 5.0 / 0.4 | 48.1 / 25.6 / 25.5 / 0.7 |
| J3s | 34.3 / 51.3 / 14.1 / 0.3 | 40.9 / 57.7 / 1.1 / 0.3 |
| J4s | 66.9 / 19.7 / 13.1 / 0.3 | 50.3 / 12.9 / 36.5 / 0.3 |
| J5s | 87.0 / 11.2 / 1.5 / 0.3 | 1.9 / 26.1 / 71.7 / 0.3 |
| J6s | 71.2 / 24.0 / 3.3 / 1.4 | 50.0 / 30.0 / 19.1 / 0.9 |
| J7s | 24.4 / 74.6 / 0.7 / 0.3 | 78.9 / 19.7 / 1.0 / 0.3 |
| J8s | 5.4 / 0.3 / 93.9 / 0.3 | 6.0 / 91.1 / 2.6 / 0.3 |
| J9s | 12.1 / 86.0 / 1.6 / 0.3 | 35.3 / 40.5 / 23.9 / 0.4 |
| JTs | 14.1 / 75.8 / 5.5 / 4.6 | 76.9 / 14.0 / 6.4 / 2.7 |
| JJ | 0.7 / 12.1 / 78.9 / 8.3 | 0.5 / 7.8 / 91.4 / 0.3 |
| QJo | 31.0 / 58.7 / 8.7 / 1.6 | 2.6 / 21.4 / 74.3 / 1.7 |
| KJo | 41.1 / 55.5 / 1.7 / 1.7 | 28.3 / 15.4 / 55.9 / 0.4 |
| AJo | 1.5 / 68.0 / 24.0 / 6.5 | 12.8 / 8.0 / 63.4 / 15.9 |
| Q2s | 78.3 / 4.2 / 17.1 / 0.3 | 55.3 / 41.9 / 2.5 / 0.3 |
| Q3s | 40.0 / 40.7 / 19.0 / 0.3 | 32.0 / 41.4 / 26.3 / 0.3 |
| Q4s | 62.4 / 29.1 / 6.5 / 2.0 | 49.6 / 47.2 / 1.3 / 1.9 |
| Q5s | 82.9 / 6.3 / 9.6 / 1.2 | 38.4 / 51.2 / 9.5 / 0.9 |
| Q6s | 12.3 / 44.7 / 42.7 / 0.3 | 39.9 / 43.8 / 15.6 / 0.7 |
| Q7s | 18.9 / 1.7 / 79.1 / 0.3 | 1.9 / 13.0 / 84.8 / 0.3 |
| Q8s | 71.6 / 21.9 / 5.5 / 1.0 | 79.9 / 18.8 / 0.3 / 1.0 |
| Q9s | 56.8 / 3.7 / 13.4 / 26.2 | 23.4 / 23.0 / 3.9 / 49.6 |
| QTs | 2.0 / 95.1 / 1.0 / 1.9 | 3.1 / 49.4 / 44.0 / 3.5 |
| QJs | 33.7 / 47.4 / 5.4 / 13.5 | 15.0 / 57.0 / 23.6 / 4.4 |
| QQ | 0.3 / 0.3 / 58.6 / 40.8 | 0.3 / 0.5 / 46.9 / 52.3 |
| KQo | 28.0 / 0.5 / 63.0 / 8.5 | 57.2 / 29.2 / 0.7 / 12.8 |
| AQo | 1.7 / 0.3 / 46.3 / 51.7 | 0.3 / 0.4 / 63.0 / 36.2 |
| K2s | 19.9 / 32.5 / 47.2 / 0.4 | 57.1 / 37.6 / 5.0 / 0.3 |
| K3s | 26.2 / 29.3 / 40.4 / 4.1 | 26.0 / 66.3 / 3.9 / 3.8 |
| K4s | 38.3 / 10.2 / 49.8 / 1.7 | 24.3 / 37.6 / 36.5 / 1.6 |
| K5s | 66.9 / 4.7 / 21.7 / 6.7 | 80.5 / 1.7 / 17.5 / 0.3 |
| K6s | 82.0 / 5.9 / 11.6 / 0.5 | 37.1 / 60.2 / 1.5 / 1.1 |
| K7s | 85.4 / 14.0 / 0.3 / 0.3 | 84.2 / 15.2 / 0.3 / 0.3 |
| K8s | 2.6 / 76.2 / 20.9 / 0.3 | 49.2 / 34.6 / 15.9 / 0.4 |
| K9s | 10.6 / 9.4 / 69.8 / 10.1 | 8.9 / 15.5 / 71.7 / 3.9 |
| KTs | 12.6 / 48.3 / 37.4 / 1.7 | 52.5 / 30.2 / 12.5 / 4.8 |
| KJs | 25.9 / 39.0 / 29.5 / 5.6 | 73.1 / 13.4 / 2.8 / 10.7 |
| KQs | 30.7 / 24.6 / 20.8 / 23.9 | 13.2 / 21.3 / 49.4 / 16.0 |
| KK | 0.3 / 0.3 / 74.2 / 25.1 | 0.3 / 0.3 / 88.9 / 10.5 |
| AKo | 1.0 / 15.0 / 25.4 / 58.7 | 0.3 / 2.6 / 68.7 / 28.4 |
| A2s | 28.6 / 62.8 / 7.7 / 0.9 | 37.5 / 1.9 / 59.5 / 1.1 |
| A3s | 53.3 / 24.8 / 20.2 / 1.7 | 59.5 / 33.8 / 6.0 / 0.8 |
| A4s | 9.5 / 89.3 / 0.9 / 0.3 | 79.8 / 17.9 / 0.5 / 1.8 |
| A5s | 63.1 / 22.4 / 0.6 / 13.9 | 53.4 / 44.9 / 1.4 / 0.3 |
| A6s | 2.0 / 48.8 / 48.2 / 1.0 | 57.9 / 10.4 / 28.1 / 3.6 |
| A7s | 2.9 / 90.3 / 6.5 / 0.3 | 8.2 / 76.2 / 14.7 / 0.9 |
| A8s | 4.9 / 40.8 / 43.2 / 11.1 | 0.4 / 3.7 / 91.5 / 4.4 |
| A9s | 34.3 / 3.5 / 48.2 / 14.0 | 8.7 / 66.7 / 17.1 / 7.5 |
| ATs | 4.7 / 45.2 / 1.9 / 48.2 | 0.3 / 0.3 / 92.9 / 6.5 |
| AJs | 1.1 / 35.8 / 38.6 / 24.6 | 0.3 / 1.7 / 69.6 / 28.4 |
| AQs | 25.0 / 1.0 / 1.9 / 72.0 | 3.8 / 14.0 / 47.9 / 34.3 |
| AKs | 2.0 / 0.3 / 30.3 / 67.4 | 2.0 / 0.3 / 26.1 / 71.5 |
| AA | 0.7 / 0.6 / 83.9 / 14.8 | 0.3 / 0.3 / 95.2 / 4.2 |

## Evidence

Comparison: `sampled-visible-hybrid-completion-comparison-v2-result.json`; SHA-256 `8a4c862cb2e510c44d2680a4e104b2de47ac1cfde4bf8a8dbfb8372f97ec6008`.

Training: `sampled-visible-hybrid-completion-pilot-v1-independent-review.json`. BB: `sampled-visible-hybrid-completion-evaluation-v1-{result,independent-review}.json`. BTN: `sampled-visible-hybrid-completion-btn-evaluation-v1-{result,independent-review}.json`. The comparison records original-candidate evidence and all input hashes.
