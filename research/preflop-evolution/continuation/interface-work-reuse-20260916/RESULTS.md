# N04: exact work removal, negligible measured gain

All three interleaved repeats preserved every saved regret and accumulated
strategy value exactly (69,335,461 entries in each of two arenas per run).
The independent oracle and ordinary CPU/GPU regressions had already passed.

| Path | Median seconds per iteration |
|---|---:|
| Ordinary Balanced | 1.112223 |
| Unoptimized conditional predictor | 1.421600 |
| Filtered, identical conditional predictor | 1.416516 |

The measured speedup is 1.003589x, about 0.36%. The filtered predictor still
costs 27.36% more per iteration than Balanced, missing the <=10% overhead
target. Each run used 50 warm-up and 100 timed iterations. This is fixed-work
speed, not convergence speed. The old predictor also remains accuracy-rejected.

[Complete timings](timing.json). No deployment or production-file changes.
