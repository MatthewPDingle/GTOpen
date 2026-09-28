# Saved later-play fits: training loss diagnostic

This checks every saved fit from both board-root candidate runs, without fitting another model. Generation 0 used a uniform policy; fits 1–77 supplied played models, and fit 78 is an unplayed endpoint shown separately.

The quantity below is the reduction in grouped training-target squared error relative to always predicting zero. It is not held-out accuracy, a fraction of correct poker decisions, or an EV-loss estimate. Noise and changing training data prevent treating these windows as a controlled capacity experiment.

| Arm / player | Early played fits | Middle played fits | Late played fits | Late distinct observations |
| --- | ---: | ---: | ---: | ---: |
| 9266201-board-root / BB | 59.1% | 50.6% | 46.8% | 243,518 |
| 9266201-board-root / BTN | 76.5% | 58.5% | 49.8% | 114,022 |
| 9266301-board-root / BB | 61.1% | 50.6% | 47.5% | 244,092 |
| 9266301-board-root / BTN | 76.5% | 57.6% | 47.4% | 115,994 |

The windows are fits 1–25, 26–51, and 52–77, matching the played-policy history except for its unfitted initial uniform state. Each cell is the median over the stated fits. All individual records and the unplayed endpoint are retained in [the complete diagnostic](board-later-fit-diagnostic-v1.json).

The zero-prediction reference is reconstructed from the actual objective normalization: four times retained source weight, divided by weighted legal-action mass, minus within-observation variance. It is not assumed to equal one. Saved source hashes and all 156 generation-metric files were checked.

The saved metrics alone cannot separate limited optimization, network capacity, target noise and lack of generalization. A useful follow-up is a fixed-data, grouped-observation holdout comparison of additional fitting against the current fit budget. Lower training error alone would not qualify a range improvement. The root-action evaluation and paired later-policy comparisons should guide whether that experiment is warranted.
