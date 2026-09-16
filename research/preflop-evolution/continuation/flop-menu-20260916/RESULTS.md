# Wider flop-menu validation (N21)

All 160 prespecified fresh references completed and were audited. The same frozen N15 predictor was compared in four fixed range contexts using 20 matched flops each, with either half-pot flop bets or 33/50/75% flop bets. Turn/river menus remain half pot, maximum one raise, no all-in, no rake. These are familiar range contexts on new flops, not untouched contexts or full-game validation.

| Context/menu | Candidate MAE (% pot) | Ordinary Balanced MAE (% pot) | Improvement |
|---|---:|---:|---:|
| original-bb-call-0-control | 6.1693 | 8.9916 | 31.39% |
| original-bb-call-0-expanded | 6.3130 | 9.1762 | 31.20% |
| original-bb-call-1-control | 5.6942 | 8.8002 | 35.29% |
| original-bb-call-1-expanded | 5.7723 | 8.9893 | 35.79% |
| candidate-bb-call-0-control | 5.4745 | 8.1505 | 32.83% |
| candidate-bb-call-0-expanded | 5.5570 | 8.3131 | 33.15% |
| candidate-bb-call-1-control | 5.2102 | 9.0019 | 42.12% |
| candidate-bb-call-1-expanded | 5.2307 | 9.1522 | 42.85% |

All eight pass the frozen >=15% improvement over ordinary Balanced and <=10% regression against the older predictor gates; all eight also improve over that older predictor. The paired 90% resampling intervals favor the candidate. Maximum CPU reference gap is 0.09979% pot; maximum GPU gap is 0.09987% pot. Maximum reference pot-accounting discrepancy is below 0.00000028 bb. Prediction conservation and physical stack bounds pass.

The average absolute reference-value change caused by the expanded flop menu is 0.3381 to 0.4062% pot across the four contexts. This limited menu change does not reverse the accuracy advantage. It does not resolve the end-to-end settling failure found in N19/N27, and it does not qualify the later N34 blend or newly generated ranges. No deployment.
