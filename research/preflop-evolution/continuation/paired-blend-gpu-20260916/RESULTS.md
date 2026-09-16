# N35: fixed 25% blend fails the practical screen

All correctness and sparse-safety checks passed, but neither arm passed the registered final settling screen. The blend also exceeded the desired 10% learning-time overhead. It does not advance to N36 fresh-flop validation.

| Arm | Final gap (bb) | Max action change | Max weighted hand TV | Learning seconds |
|---|---:|---:|---:|---:|
| control | 0.005839043 | 0.001210 | 0.001980 | 521.483 |
| blend | 0.015135316 | 0.017249 | 0.020142 | 576.826 |

Blend/control learning time: **1.106127** (10.61% longer). Gap target remains 0.005 bb; action and weighted hand-change limits remain 0.01. The paired-accounting control differs from ordinary production Balanced and itself finishes just above the gap target; do not claim that this particular control converged.

Independent audit rechecked all 46 frozen inputs, four snapshots, selected strategies, node changes, per-seat gaps and chip conservation. The linearity oracle contains 10,309 hand/action values and differs from its expected mixture by at most 1.669e-6 bb, below the fixed 2e-6 tolerance. Sparse two-, three- and eight-player safety checks passed.

The ordered 500-step warm-start comparison is exploratory timing, not a repeated benchmark or a cold-start time-to-target claim. N38 is a separately registered bounded extension because the blend gap fell from 0.03254 to 0.01514 bb; that follow-up cannot rewrite this failed fixed-budget screen. No production deployment.
