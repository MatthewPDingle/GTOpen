# Preflop CUDA performance — 2026-09-07

See the [GPU follow-up research](../research/autoresearch/gpu-pass.md) for the
latest continuation; the historical measurements below are preserved.

This records the first optimization pass. The subsequent three-hour
[autoresearch results](../research/autoresearch/report.md) use this improved
implementation as their baseline and document the additional gains.

Measured on the local RTX 3090, native Windows release build. The changes
reduce redundant computation and improve GPU memory access; tree shape,
equity values, precision, discounting, iteration order and convergence
targets are unchanged.

## Changes

1. Store the GPU equity table opponent-major. Neighboring threads evaluate
   neighboring hero classes, so they now read adjacent floats. Each dot
   product still multiplies and accumulates the same values in the same order.
2. Skip the terminal reduction of the traverser's own reach mass, which
   counterfactual values never read.
3. Reuse average-strategy reach and sigma across all seats during a
   convergence check. Reuse each seat's terminal values between best-response
   and average-EV aggregation. These passes do not modify learning state.
   An N-seat check now does one down sweep instead of 2N, N terminal passes
   instead of 2N, and the same 2N up sweeps.

## Measurements

The baseline is commit `1f6c630`, with the same benchmark harness added.
Each case warms up for five iterations, then times three blocks of 20
iterations, convergence measurement and full CPU synchronization separately.
The table reports the median of each set of three timings. Initialization,
tree construction and equity-cache loading are excluded. Solves reach 65
iterations in both runs. There was no active server solve or report.

| Game | Nodes | Iteration before / after | Convergence check before / after | CPU sync before / after |
|---|---:|---:|---:|---:|
| 2 seats, calibrated, 100bb | 40 | 0.213 / 0.189 ms | 0.414 / 0.268 ms | 0.029 / 0.028 ms |
| 6 seats, static, 100bb | 166,090 | 40.448 / 33.558 ms | 131.328 / 34.790 ms | 62.980 / 60.605 ms |
| 8 seats, calibrated, 150bb | 434,350 | 197.557 / 155.655 ms | 586.482 / 142.709 ms | 158.758 / 161.531 ms |

On the two larger games, iterations take 17–21% less time and convergence
checks are 3.8–4.1 times faster. Using these component medians, a block of
20 iterations plus a check and CPU sync falls from 1003 to 767 ms (6 seats)
and 4696 to 3417 ms (8 seats): approximately 24% and 27% less time. These are
estimates for that checkpoint cadence, not a universal end-to-end speedup.
Transfers, initialization, small trees, other GPUs and frozen-seat games
have different proportions of work.

## Accuracy checks

All three cases produced identical before/after arena fingerprints and
identical printed per-seat EVs and best-response gaps. The fingerprints
cover every f32 bit in both the regret and cumulative-strategy arenas:

| Seats | Before and after fingerprint |
|---|---|
| 2 | `6d4781fae03e3474` |
| 6 | `b70284af63586e3f` |
| 8 | `e01dd7a18632644d` |

`cached_evaluation_matches_full_sweeps_exactly` compares every gap and EV
bit against the original independent full-sweep calculation, including
repeated checks, two- and three-seat trees, raw/static/calibrated realization,
point locks, profiles and frozen seats in hero mode. It also verifies that
evaluation leaves both learning arenas and the iteration count unchanged.
The existing six postflop GPU tests and five preflop CPU/GPU equivalence
tests pass, including calibrated realization, profiles, locks, hero mode
and push/fold anchors. The full CPU suite passes all 123 tests, and
`cargo check --release -p server --features gpu` succeeds.

## Reproduction

From the repository root in PowerShell:

```powershell
$env:PATH = "$PWD\.cuda-nvrtc\nvidia\cuda_nvrtc\bin;" + $env:PATH
$env:RAYON_NUM_THREADS = '16'
cargo test --release -p solver --features gpu --test preflop_perf -- --ignored --nocapture
cargo test --release -p solver --features gpu --lib --test gpu --test preflop_gpu -- --test-threads=1
cargo test --release -p solver
cargo check --release -p server --features gpu
```

The benchmark uses the existing deterministic equity cache and requires
the calibrated fit. Baseline and modified runs must use identical caches,
hardware and benchmark settings. Normal launches via `GTOpen.cmd` rebuild
the server with these changes; an already-running server retains its old
executable until restarted.
