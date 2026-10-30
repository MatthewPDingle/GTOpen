# D028 independent diagnostic review

Protocol and provenance pass: all nine prespecified runs retained, serialized in the original/E015/E016 Latin order; every arm occupies each block position once. All 27 complete non-timing records are exact and match the earlier frozen cohort. Executable, manifest, raw-log and source hashes verify. E015/E016 differ only in gpu/mod.rs among their recorded source files.

This diagnostic does not isolate the earlier river discrepancy uniquely to E016 or to retained E015. It did not reproduce a repeatable river regression pattern. The failed E016 cumulative cohort stays failed; no candidate acceptance follows.

| Arm | Rainbow median ms | Two-tone median ms | River median ms | River init median [range] ms | River solve median ms |
|---|---:|---:|---:|---:|---:|
| original | 6923.6330 | 4701.7968 | 119.1263 | 97.9332 [90.2645, 104.7114] | 18.3594 |
| E015 | 6386.7291 | 4352.4935 | 116.6824 | 97.8461 [94.2254, 106.0796] | 18.2610 |
| E016 | 5887.8822 | 4110.6693 | 120.6387 | 101.7570 [93.6697, 103.3785] | 17.6565 |

| River contrast | Median regression | Block-paired regressions | Repeats >3% |
|---|---:|---|---:|
| E015 versus original | -2.0515% | +2.7216%, +6.5947%, -4.6577% | 1/3 |
| E016 versus original | +1.2696% | -0.8379%, +10.2090%, -5.6843% | 1/3 |
| E016 versus E015 | +3.3907% | -3.4651%, +3.3907%, -1.0768% | 1/3 |

All three initialization ranges overlap. The E016 river median init exceeds original by 3.8238ms and E015 by 3.9109ms; its median solve is lower by 0.7029ms and 0.6045ms. These separate medians do not add to the full-cycle median. Graph capture occurs in solve, so this does not directly implicate graph capture as an initialization cost.

Both optimized arms improve both flop medians, and E016 improves every block-paired flop solve span relative to E015. All three arm contrasts also favor the optimized comparator in the retained whole-test/process envelopes. Those broader clocks include correctness hashing, destruction and/or runner work; they do not excuse a per-fixture guard failure.

The schedule balances block position, but three deterministic repetitions do not establish significance or remove history/cache/scheduling effects. Boundary telemetry shows the same device/driver and 2542MHz SM; 45–51°C samples are not per-river tracing. No cause is assigned.

Next narrow step: a predeclared, balanced original/E015/E016 river-only diagnostic using these same preserved binaries and the existing fixture filter. This tests whether the observed behavior persists without the earlier large fixtures. Disclose that river becomes the first fixture, changing NVRTC/cache history; it cannot by itself isolate the constructor substage or overturn the failed full-suite cohort. If needed, use a separate D012-style constructor-substage diagnostic without changing the frozen evaluator.

No builds, GPU runs, or production edits were performed for this review. Existing primary, broader and cumulative artifacts remain sealed.
