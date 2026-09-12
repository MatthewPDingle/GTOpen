# Root-only repair rejected on both inputs

Six fixed mixtures toward the root's GPU best response were evaluated on each
compact-refined eight-player input. All later policy/history blocks stayed
exact, parent age stayed 1,050, and saved-file roundtrips were exact.

| Mixture | Sampled global gap (bb) | Sampled local passes | Native global gap (bb) | Native local passes |
|---|---:|---:|---:|---:|
| 0 | 0.02953004 | 26/27 | 0.00877509 | 26/27 |
| 1/16 | 1.03177539 | 9/27 | 1.05594160 | 12/27 |
| 1/8 | 3.42472991 | 4/27 | 3.50778448 | 12/27 |
| 1/4 | 8.27099169 | 3/27 | 8.52438532 | 12/27 |
| 1/2 | 18.06414067 | 3/27 | 18.57837421 | 12/27 |
| 1 | 37.77484708 | 3/27 | 38.83046796 | 3/27 |

The registered minimum-global-gap rule selects mixture zero on both. The
normalized root history recheck differs from its baseline by less than
1.3e-8 bb; both independent saved-file audits retain 26/27. Neither qualifies.
Process times were 75.375 and 73.266 seconds, plus about 4.7 seconds per final
correctness audit. These are diagnostic times, not accepted convergence gains.

The root actor's EV follows the predicted linear one-step improvement. For
example, sampled pure best response raises its EV from 0.07051871 to
0.09632075 bb, matching the diagnostic gain of 0.02580205 bb. Its own gap falls
from 0.02594030 to 0.00013825 bb, but the other seven seats' gaps rise to roughly
5.26-5.53 bb each. The failure is therefore not a failure to improve that
actor's root response. Changing its ranges exposes poor responses elsewhere.

`check_root_repair.py` independently reconstructs the mixture/tie rules,
checks the root EV prediction, recomputes every local tail gate, verifies
selection by unrestricted global gap, and compares final saved-file policy/Q
values. It correctly exits 1 for failed qualification. The small root-edit
test also passed preservation, invalid-input/fixed-policy rejection, and full
CPU/GPU value equivalence. CPU was used only as a correctness reference.

This rejects independent root repair with fixed continuations, alongside the
earlier rejected ancestor/branch alternation. Further work must address how
rare branches learn and remain consistent during global learning; the current
evidence does not justify deployment, weaker gates, or a longer repair loop.
