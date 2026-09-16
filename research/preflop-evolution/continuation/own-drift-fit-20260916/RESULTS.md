# Support-preserving own-mean regularization (N30)

All fixed settings failed the joint screen. All26 zero-strength control errors reproduced N15 within1e-9; two numerical checks passed and15 frozen dependency/input hashes remained unchanged. No candidate or GPU follow-up was produced.

| Strength | Mean error(%pot) | Mean error change vsN15 | Worst family change | Own-response change | Eligible |
|---|---:|---:|---:|---:|---|
| 0.0 | 6.2837 | +0.00% | +0.00% | +0.00% | False |
| 0.0001 | 6.2249 | -0.94% | +3.16% | -0.14% | False |
| 0.001 | 6.3906 | +1.70% | +6.59% | -7.30% | False |
| 0.01 | 6.3602 | +1.22% | +11.81% | -30.78% | False |

The mildest setting slightly improves mean error while preserving every family, but barely changes the targeted response. The strongest setting reduces targeted response by30.78%, but its worst-family error increases11.81%, beyond the fixed5% limit. No strengths or thresholds were added after inspection.

These are training-family selection results, not fresh prediction or strategy accuracy. The regularizer is a modeling hypothesis; smaller own-range response is not itself evidence of correct poker behavior or convergence. No inference-time speed claim is made.
