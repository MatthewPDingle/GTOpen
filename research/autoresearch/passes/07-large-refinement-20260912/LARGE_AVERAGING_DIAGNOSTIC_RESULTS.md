# Averaging alone does not qualify the large game

The forced-age diagnostic completed 3,000 iterations and passed its independent
saved-state checks. Its 264,950,257 regret entries are bit-for-bit identical to
the original gamma15 run. The average histories differ, as intended. The
separate read-only diagnostics also match every current policy and current
prefix/hand reach at all 27 registered paths.

| Final measurement | Gamma 15 | Gamma 2 (DCFR averaging) |
| --- | ---: | ---: |
| Global full-reference gap, bb | 0.464059 | 0.469437 |
| Conditional passes | 11 / 27 | 12 / 27 |
| Failed paths with zero current opponent mass | 9 | 9 |
| Complete example runtime | 1,684.14 s | 1,691.51 s |

No checkpoint pair qualified. All 60 gamma-2 checkpoints were independently
verified, including every per-hand gate. The independent final saved-game
audit exactly reproduces the recorded per-hand values and probabilities.
The two complete runtimes are diagnostic costs, not an equal-quality speedup.

Nine failing paths have zero current opponent reach in both saves even though
their average-policy state can still be inspected. Averaging alone therefore
does not restore the missing learning at those paths. Six of the gamma-2
failures have positive current reach, so missing reach is not a complete
explanation of the remaining error either.

Next, numerically validate the separately drafted accumulated-opponent learning
experiment in `AVERAGE_OPPONENT_PLAN.md`, then register a matched small-game
convergence screen if its calculations pass. Do not deploy either current
large result, weaken the quality gate, or infer that the next method converges
from its numerical tests. Port 56708 remains untouched.

Evidence: `raw/large-averaging-dcfr-v1-verified.json`, its compressed per-check
archive/envelope, separate audit and bitwise comparison, and
`raw/large-averaging-reach-verified.json` with both underlying diagnostics and
guarded process records.
