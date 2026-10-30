# Matched training-panel reconstruction

The entering policies, private-card distribution and board panel are preserved. Both postflop strategies are rebuilt. A changed combined-game gap demonstrates reconstruction sensitivity; it does not alone distinguish equilibrium selection, averaging effects or implementation error. Raked general-sum game; no zero-sum safety guarantee is claimed.

Boards: 10; both runs use 2,000 iterations.

| Measurement | Original connected solve | Rebuilt postflop responses |
|---|---:|---:|
| Full deviation gain (bb) | 0.004091560 | 0.005662568 |
| OOP EV (bb) | -3.199849720 | -3.199870713 |
| IP EV (bb) | 5.979339695 | 5.979645700 |

Rebuilt postflop residual: 0.001049447 bb.
Entering checks: normalizer relative error 1.08e-15; maximum frequency error 3.33e-16; maximum hand-mass error 8.33e-17.

This is a same-training-panel diagnostic, not independent validation or a new acceptance rule.
