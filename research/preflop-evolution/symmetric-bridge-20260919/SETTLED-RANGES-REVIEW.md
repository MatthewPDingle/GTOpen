# Fixed ranges resolve the in-distribution disagreement in these six cases

All six registered stationary-tail cases passed at iteration 2,000. The first 100 steps reproduced the earlier root drift exactly. The differing-range probe agrees within the previously measured same-policy evaluation difference: the old check used compact/full evaluators, while this diagnostic deliberately uses full/full. An initial review script mistakenly demanded 1e-8 agreement across those evaluators; its assertion was corrected using that existing measured bound. Native diagnostic gates and outputs were unchanged.

| Initial schedule / board | Combined deviation, compact / explicit (bb) | Largest current-range hand value difference / opposing mass | Earlier different-range probe difference / opposing mass |
|---|---:|---:|---:|
| Abrupt / KsQs2d | 0.004433 / 0.004428 | 0.0007751 | 0.0293217 |
| Abrupt / KsQs2s | 0.000946 / 0.000896 | 0.0004654 | 0.0187936 |
| Abrupt / KsQh2d | 0.001997 / 0.001997 | 0 | 0 |
| Smooth / KsQs2d | 0.000910 / 0.000917 | 0.0010874 | 0.0773309 |
| Smooth / KsQs2s | 0.000901 / 0.000924 | 0.0007859 | 0.1017687 |
| Smooth / KsQh2d | 0.001085 / 0.001085 | 0 | 0 |

Aggregate EV differences were at most 0.0000343 bb. Root probabilities differed by at most 0.0000321. Each strategy's own deviation was computed against its current fixed ranges, with physical private-hand compatibility explicitly included. The JSON reports centered utility EVs; those are not unadjusted pot-share displays from Browse.

These results narrow the concern: the tested implementations can reach close, low-deviation outcomes for the fixed distributions despite taking slightly different paths while learning. They do not show that every intermediate response matches when reaches change. The earlier seed-777 probe is a different opponent distribution; its difference persists, and sometimes grows, even while the current-distribution deviations shrink. A low deviation against one range is not a guarantee against another.

Together with the local replay check and the confirmed zero-opponent CPU/GPU averaging difference, this argues against treating every old failure as the same bug. It still does not prove rounding is the sole cause or clear the compact bridge for arbitrary evolving preflop continuations. Keep the original failed gates visible. The proposed host-only storage prototype takes a separate route: restore the explicit reference's state exactly and retain its full traversal.

Execution took 73.5 seconds under the guard. Evidence: `settled-ranges-review.json`, protocol, source/build/runtime hashes and log; sibling `representative-coverage-20260919/settled-ranges-diagnostic*`. No production deployment.
