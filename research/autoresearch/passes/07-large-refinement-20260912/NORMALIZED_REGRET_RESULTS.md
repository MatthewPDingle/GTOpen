# Normalized-regret GPU optimizer rejected in the six-player screen

| Seed | Control iterations | Control seconds | Control final gap (bb) | Candidate iterations | Candidate seconds | Candidate final gap (bb) |
|---|---:|---:|---:|---:|---:|---:|
| 42 | 275 | 3.1260 | 0.00411035 | 1,000 | 10.6207 | 0.00982554 |
| 314159 | 325 | 3.5900 | 0.00395184 | 1,000 | 10.0654 | 0.01628628 |

Controls reached two consecutive full-1,024 checks at <=0.005 bb. Neither
candidate reached that gate within the registered limit; both also exceeded
twice their same-seed control's time. The runner correctly skipped the large
experiment. No large-game improvement, conditional qualification, or deployment
is claimed. Timings above are the benchmark's total times; process records also
include interpreter/process teardown overhead.

`normalized-regret-tests-v1` failed to compile because the helper method was
private to its child module. Restricting visibility to `pub(super)` fixed that
without changing arithmetic. `normalized-regret-tests-v2` passed two tests:

- Regret increments match a host calculation of native increments divided by
  opponent reach mass; upward values and strategy sums remain unchanged.
  The fixture includes a point lock, a frozen seat, and zero-mass branches.
- Captured and eager GPU learning match exactly across three iterations;
  standard final CPU/GPU values agree within the registered 0.005-bb tolerance.

`check_regret_normalization.py` independently checks all full-check particle
counts, summed gaps, consecutive-pass flags, options, roundtrips, and the
screen decision. Its exit 1 denotes the intended experiment rejection. The
optimizer remains available only behind `preflop-research` for reproducibility;
the server has no entry point enabling it. CPU work was correctness only.

The existing postflop and preflop GPU equivalence suites also passed with the
research feature compiled and the new option disabled: 6 postflop and 13
preflop tests (`research-gpu-regressions-v2`, 63.656 seconds process time).

Changing regret weights is not an accepted way to preserve conditional
quality. Next investigate a bounded-memory, unbiased variance reduction
estimator rather than extending this failed optimizer or increasing its cap.
