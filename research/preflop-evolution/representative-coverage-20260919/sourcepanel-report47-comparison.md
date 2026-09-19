# Matched training-panel reconstruction

The entering policies, private-card distribution and board panel are preserved. Both postflop strategies are rebuilt. A changed combined-game gap demonstrates reconstruction sensitivity; it does not alone distinguish equilibrium selection, averaging effects or implementation error. Raked general-sum game; no zero-sum safety guarantee is claimed.

Boards: 47; both runs use 2,000 iterations.

| Measurement | Original connected solve | Rebuilt postflop responses |
|---|---:|---:|
| Full deviation gain (bb) | 0.007423827 | 0.009961127 |
| OOP EV (bb) | -3.164821798 | -3.164967090 |
| IP EV (bb) | 6.310921951 | 6.311032373 |

Rebuilt postflop residual: 0.000148978 bb.
Entering checks: normalizer relative error 1.29e-15; maximum frequency error 1.22e-15; maximum hand-mass error 8.33e-17.

This is a same-training-panel diagnostic, not independent validation or a new acceptance rule.
