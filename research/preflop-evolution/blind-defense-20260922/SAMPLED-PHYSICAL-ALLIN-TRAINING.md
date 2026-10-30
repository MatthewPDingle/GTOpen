# Conditional-all-in candidate: training and evaluation complete

All 78 registered updates completed, covering 39,936 fresh physical deals. The
worker reported 4,853.0 seconds (80.9 minutes). This finishes training, not the
strategic qualification of the resulting ranges.

| Training item | Final value |
|---|---:|
| Complete updates | 78 |
| Deals per update | 512 |
| Complete physical deals | 39,936 |
| BB advantage visits seen | 912,726 |
| BB retained examples | 262,144 |
| BTN advantage visits seen / retained | 110,944 / 110,944 |
| Played models in the candidate | 0 through 77 |
| Final newly fitted, unused model | 78; excluded from the candidate |

The final checkpoint digest is
`1399fcadc1ff016081bc95a668eccd576212865ecde7e019ea8f4aabbf59fd83`.
Training kept the original dense recipe and changed only the preflop all-in
terminal estimator to exact private-pair equity. Postflop outcomes remained
sampled and model inputs remained unchanged.

The full independent replay **passed** in 159.5 seconds. It verified 263
registered inputs, replayed all 39,936 deals and 79,872 native-checked updater
traversals, and reproduced both final reservoir arrays and random states
exactly. All subbatches used the same frozen generation within each update.
The complete played bank and unused generation 78 were verified. Neural fitting
and inference were not rerun by this audit. The earlier four-update prefix
control was not used as a substitute for this terminal review.

The original evaluation stopped at its first CPU/CUDA numerical-control batch,
before response selection or held-out draws. The separately versioned
[precision repair](ALLIN-NUMERICAL-REPAIR.md) passed all 256 control deals and
its artifact readback. Both predeclared BB/BTN tests and final audits have now
completed. See [completed findings](SAMPLED-PHYSICAL-ALLIN-FINDINGS.md): shoving
fell substantially, calling remained almost unchanged, and the candidate is
not qualified for deployment. The separate conditional evaluation estimator
was not substituted into this trial.

No training loss, chart or partial checkpoint is a strength qualification.
Production and the range preview are unchanged. Evidence uses the
`sampled-physical-allin-pilot-v1` and `sampled-physical-allin-study-v3` prefixes.
