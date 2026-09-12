# Four-seed small-game speed qualification passed

All four fresh 64-particle corrected runs met the unchanged combined accuracy
gate and beat the faster full-particle control by at least 1.25x. Measured
speedups were 2.54–4.40x on this 23,038-node six-seat fixture. This is the first
four-seed qualification for this combination; it is not large-game proof.

| Seed | Qualified iteration | Complete seconds | Speedup versus faster control |
| --- | --- | --- | --- |
| 42 | 1,300 | 17.954 | 2.87x |
| 271828 | 1,100 | 15.351 | 3.36x |
| 314159 | 825 | 11.711 | 4.40x |
| 1618033 | 1,475 | 20.274 | 2.54x |

Full controls qualified at iteration 950 in 51.573 and 51.567 seconds. The
conservative permitted runtime was 41.254 seconds per candidate. Each pass
requires native full-reference global gap <=0.005 bb and all six conditioned
action-quality paths passing on two consecutive 25-iteration checks. Timings
include setup, learning, checks and saved arena round-trip validation.

The earlier 1,000-iteration screen remains a failed two-seed screen. These
were separately registered fresh runs with a 3,000-iteration ceiling, the
same optimizer and the same accuracy/speed thresholds. Neither ceiling was
extended. The two repeated seeds reproduced every prior per-hand checkpoint,
global value and acceptance decision exactly. The two new seeds also passed.
Both full controls reproduced the prior full-control saved-game SHA-256.

`check_normalized_pair_tail.py` independently recomputed every checkpoint
gate, exact replay, separate saved per-hand audit and conservative timing
comparison. All six run/audit pairs completed normally. Code and evidence
are research-only; port 56708 and production defaults are unchanged.

The next requirement is the 1,567,754-node eight-seat case with all 27
conditional paths, where full-particle normalization previously failed.
The small-game result does not resolve its zero-current-reach or global
instability failures. Register a large corrected run separately and retain
those stricter checks before considering deployment.
