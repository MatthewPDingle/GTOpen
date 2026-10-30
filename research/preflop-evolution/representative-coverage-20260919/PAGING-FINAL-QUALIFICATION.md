# Full-arena transfer optimization: qualified for this research workload

Completed 20 September 2026 at 07:58 Adelaide. The isolated candidate passed the 160-switch bitwise state/value test, all five saved checkpoints, convergence and independent physical-card/chip accounting checks. Every saved scientific field matched exactly; only elapsed time and the registered transfer-byte counter changed. Frozen source and executable hashes were rechecked after execution.

| Measurement | Fresh baseline | Candidate |
|---|---:|---:|
| 2,000-iteration solver elapsed time | 1,112.750 s | 1,050.935 s |
| Iterations 500 to 2,000 | 823.580 s | 754.110 s |
| Relative transferred arena bytes | 100% | 83.3333% |

The complete run took **5.56% less time** (1.059× speed), with 16.67% fewer transferred bytes. The later interval took 8.44% less time. The earlier historical baseline took 1,199.075 seconds; using only that older number would exaggerate the measured benefit. Retain both comparisons.

This was one sequential pair, candidate first. No other research GPU solve ran concurrently. CPU population diagnostics overlapped the early candidate phase and finished before checkpoint 500; light host activity also occurred. “Uncontended” in the generated paired JSON means GPU-uncontended, not a completely idle host. There are no randomized repeated timings or uncertainty bounds, and the later interval is a diagnostic rather than a replacement for the complete run.

Sampled free host memory stayed above 98.94 GB and free GPU memory above 20.84 GB. The optimization omits uploading the other player's untouched average-strategy array. It does not reduce host strategy storage, qualify the separate suit-compressed bridge, or speed up the current resident Preflop Lab implementation. Nothing was deployed or restarted on port 56708.

Candidate source remains isolated on `codex/paging-own-average-research` at `42d76079`; it has not been merged into the production or primary research solver. Saved evidence now accompanies that branch. The primary checkout retains exact and paired reviews, fresh-baseline evidence, and `paging-final-qualification.json`, which records archive hashes and timing context. Compressed results reproduce the original JSON bytes exactly.

Evidence: `paging-candidate-{qualification-freeze,qualification-status,exact-review,paired-review}.json`; `paging-final-qualification.json`; `ownavg-fresh-baseline-*`; candidate checkout `ownavg-switch-test*` and `ownavg-two*`. `tools/research/finalize_paging_zero_reach_20260920.py` independently rechecked the registered results and archived them without rerunning the benchmark.
