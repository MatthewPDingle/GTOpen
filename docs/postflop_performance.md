# Postflop and report performance — 2026-09-07

Measured on the local RTX 3090 and Ryzen 5950X, native Windows release
build, with 16 Rayon threads and no active server solve or report.

## Changes

- Precompute each river hand's lower/upper boundaries in the opponent's
  sorted strength list. Showdown kernels used to binary-search those same
  fixed lists for every terminal and iteration. Blocker comparisons can
  also use the exact precomputed boundaries. Floating-point accumulation
  order is unchanged. The kernel needs less shared memory because it no
  longer copies the opponent's strengths into every block.
- Compute average-strategy reaches once per exploitability check. When
  rake requires both best-response and average-EV passes, reuse terminal
  values between the two passes for each player. Action/chance aggregation
  is still recomputed, and all terminal values are refreshed when changing
  players. Download the root CFVs directly without an extra staging kernel.
- Allow profile-locked report adaptation to use CUDA. Previously
  `report_solve` selected the CPU whenever its starting iteration was
  nonzero. The GPU now uploads the existing arenas and locks and uses the
  same additional-iteration budget and checkpoint cadence as the CPU path.
  CUDA failures retain the existing CPU fallback.

The game tree, bet menu, equity model, floating-point precision and target
accuracy are unchanged. These changes affect postflop CUDA solves and
profile-locked batch reports; CPU CFR traversal is unchanged.

## Measurements

The postflop benchmark uses `bench_spot.json` with three boards. The two
flop trees have 1,346,813 nodes and roughly 7.6 GB of GPU staging and arenas;
the river case has 33 nodes. Each case warms up for five iterations, then
times three batches of 20 iterations and a convergence check. Values below
are medians; initialization, tree construction and downloads are excluded.
GPU iteration timing includes synchronization so it measures completed work.

| Case | Iteration before / after | Exploitability check before / after |
|---|---:|---:|
| Rainbow flop, no rake | 63.930 / 58.186 ms | 52.597 / 40.839 ms |
| Two-tone flop, 5% rake | 38.079 / 34.441 ms | 66.240 / 31.325 ms |
| River, 5% rake | 0.363 / 0.346 ms | 1.245 / 0.627 ms |

Large-tree iterations took about 9–10% less time. Checks took about 22%
less time without rake and 53% less time with rake. A diagnostic kernel
profile attributes the iteration gain primarily to showdown evaluation.
Initialization may cost more because of the extra boundary tables; the
largest gains apply to repeated solving/checking, not one-iteration jobs.

A second timing run confirmed the large-tree results (64.295 to 58.064 ms
and 38.214 to 34.152 ms per iteration). Short GPU learning trajectories
varied between runs, so complete solves were also compared against an
isolated checkout of the original implementation. Both versions used a
0.3% exploitability target and checked every 20 iterations:

| Case | Iterations before / after | Solve time before / after | Final exploitability before / after (% pot) |
|---|---:|---:|---:|
| Rainbow flop, no rake | 200 / 200 | 13.447 / 11.991 s | 0.27247 / 0.28262 |
| Two-tone flop, 5% rake | 200 / 200 | 8.344 / 7.259 s | 0.25834 / 0.24340 |
| River, 5% rake | 60 / 60 | 0.025 / 0.024 s | 0.269897 / 0.269897 |

The large flop solves reached the same requested accuracy in approximately
11–13% less time, including accuracy checks. These solve timings exclude
tree/device initialization and final CPU downloads.

The report benchmark builds the rainbow flop in compressed CPU storage,
solves 40 baseline iterations on CUDA, locks IP to a postflop profile, and
times 40 additional report iterations. This includes GPU initialization and
the final CPU synchronization for the new path:

| Adaptation backend | Time | Final iteration | Exploitability (% pot) |
|---|---:|---:|---:|
| Previous CPU path | 19.316 s | 80 | 8.79638 |
| CUDA continuation | 5.248 s | 80 | 8.75885 |

That adaptation phase was about 3.7 times faster (73% less time). This is
not a whole-report speedup: baseline solving, profile construction and
report summary generation are separate costs. These deliberately short
runs compare equal iteration budgets; neither has converged to a typical
0.3% target. The CUDA result has slightly lower exploitability here.

## Accuracy and regression checks

- Exact integer comparisons verify the precomputed boundaries against
  every opponent strength, including ties, an all-tied board, asymmetric
  ranges, flop/turn/river roots and suit-isomorphism modes.
- Reused exploitability passes are compared with independent full passes
  on the same device state, before and after locking, with and without
  rake. Tolerance is 0.001% of pot; the existing fold kernel uses unordered
  atomic reductions, so independent GPU runs are not bitwise deterministic.
  Evaluations must leave every regret/strategy value and the iteration
  count unchanged.
- The report continuation test covers nonzero starting iterations,
  additional iteration limits, checkpoint-based early stopping, stop
  requests, lock preservation, f32/compressed storage, and CPU readback
  of GPU exploitability.
- The existing six postflop and five preflop GPU correctness tests pass,
  as do the new tests and the previous preflop exact-equivalence regression.
  The full workspace CPU suite also passes all 123 solver tests.

CPU and GPU learning trajectories can differ slightly due to floating-point
reduction and quantization order. These changes add no approximation;
the existing convergence tests remain the accuracy criterion.

## Reproduction

From the repository root in PowerShell:

```powershell
$env:PATH = "$PWD\.cuda-nvrtc\nvidia\cuda_nvrtc\bin;" + $env:PATH
$env:RAYON_NUM_THREADS = '16'
cargo test --release -p solver --features gpu --test postflop_perf -- --ignored --nocapture
# Optional: time complete solves to the same 0.3% target instead of 65 iterations.
$env:POSTFLOP_PERF_CONVERGENCE = '1'
cargo test --release -p solver --features gpu --test postflop_perf -- --ignored --nocapture
Remove-Item Env:POSTFLOP_PERF_CONVERGENCE
cargo test --release -p server --features gpu report_adaptation_benchmark -- --ignored --nocapture
cargo test --release -p solver --features gpu --lib --test gpu --test preflop_gpu -- --test-threads=1
cargo test --release -p server --features gpu -- --test-threads=1
cargo test --release --workspace
```

The postflop baseline uses the previous kernels/evaluation implementation
from `1f6c630` with the same benchmark harness. The report comparison holds
the new postflop GPU implementation constant and compares the old CPU-only
adaptation selection with CUDA continuation. Benchmarks use `SOLVER_GPU`
unset or enabled. A running server keeps its old executable until rebuilt
and restarted; `GTOpen.cmd` performs the normal rebuild on launch.
