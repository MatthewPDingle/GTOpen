# Postflop GPU experiment ledger — 16 October 2026

Evidence snapshot: published status at **2026-10-16 05:04:46 UTC**. This ledger covers E001–E008 and the D009 diagnostic; later activity belongs in a subsequent update. [Protocol](program.md) · [Live dashboard](http://127.0.0.1:43735/research/postflop-gpu-20261016/) · [Published status](X:/Dev/GTOpen/web/research/postflop-gpu-20261016/status.json).

## Measurement and decision rules

All performance screens use the fixed rainbow, two-tone and river fixtures on the RTX 5090, compressed CPU storage and f32 GPU arithmetic. The primary repeated score is the **sum of per-fixture median complete-cycle wall times**, with three measurements per binary. Initial screens use one serialized three-fixture sum. Positive gain below means less elapsed time; negative gain means more. Each row compares its own baseline cohort; gains and absolute times across cohorts must not be compounded or compared as a trend.

The cycle includes tree construction, CPU allocation, GPU initialization, runtime NVRTC compilation/CUDA JIT, fixed-quality solving and complete readback. Repeated cohorts use a warm driver cache; runtime compilation is still inside the clock. Cargo compilation, correctness hashing, browser/API latency and disk saving are excluded. The fixed target is 0.3% of starting pot, checked every 20 iterations, with a 400-iteration ceiling. Qualification requires a reproducible aggregate reduction of at least 2%, no repeatable material fixture regression over 3%, and broader correctness checks. These small samples do not establish statistical significance.

## Candidates

Times are milliseconds. “Exact compressed screen” means matching complete-state fingerprints, exploitability bits and stopping iterations on all three registered fixtures; it is not full correctness qualification. All rejected candidates below passed that screen only. F32 and broader suites were not used to qualify them after the performance screen failed.

| ID | Hypothesis | Baseline → candidate | Observed gain | Decision and evidence |
| --- | --- | ---: | ---: | --- |
| E001 | 64-thread action/chance kernels | 11902.3264 → 12125.5239 | −1.8752% | Rejected initial screen; no promising gain. [Report](S:/GTOpen-research/postflop-gpu-20261016/runs/E001/comparison-B001.json) |
| E002 | 256-thread action/chance kernels | 11724.6973 → 12578.2880 | −7.2803% | Rejected initial screen; no promising aggregate gain. [Report](S:/GTOpen-research/postflop-gpu-20261016/runs/E002/comparison-B002.json) |
| E003 | Declare action regret/strategy buffers non-overlapping | 10757.0015 → 10690.4739 | +0.6185% | Rejected after three pairs; below 2% gate. [Report](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E003-warm-comparison/report.json) |
| **E004** | Initialize proven-zero compressed arenas directly on GPU | **11773.5454 → 11139.7477** | **+5.3832%** | **Accepted and validated** after three pairs and broader checks. [Qualification](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E004-qualification/report.json) |
| E005 | Direct two-action kernel for large action levels | 11042.9072 → 11052.9290 | −0.0908% | Rejected initial screen; no promising aggregate gain. [Report](S:/GTOpen-research/postflop-gpu-20261016/runs/E005/comparison-B010.json) |
| E006 | `up_action` launch bounds `(128,8)` | 11143.9813 → 11041.0797 | +0.9234% | Rejected after three pairs; below 2% gate. [Report](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E006-three-pair-comparison/report.json) |
| E007 | `up_action` launch bounds `(128,9)` | 10188.8390 → 10057.1178 | +1.2928% | Rejected after three pairs; below 2% gate. [Report](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E007-three-pair-comparison/report.json) |
| E008 | Carry the showdown prefix in a register, preserving addition order | 11291.3518 → 11099.8155 | +1.6963% | Rejected after three pairs; below 2% gate. [Report](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E008-three-pair-comparison/report.json) |

The initial-screen rejections are practical screening decisions, not statistically proven regressions. The sub-2% results remain observations in the record, not accepted speedups or proven zero effects.

## Accepted scope and deployment

E004's gain comes from **initialization of fresh compressed native solves**. It does not establish faster iterations, resumed-solve performance, F32 performance, or browser end-to-end latency. Validation included exact compressed and F32 complete-state comparisons, **160 saved-state/menu/resume snapshots per binary** (24 state, 24 menu, 112 resume), **82 solver unit tests** and **6 GPU integration tests**. See the [control comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E004-controls-comparison/report.json), [F32 comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E004-f32-comparison/report.json), [unit log](S:/GTOpen-research/postflop-gpu-20261016/runs/V004-unit/stdout.log) and [GPU integration log](S:/GTOpen-research/postflop-gpu-20261016/runs/V004-gpu/stdout.log).

Research commit: `5e021499c67c840f8c88e4378e5889918bbe27c6`. Main integration commit: `f3741e87dc76f1622164c78bf4df7b9455066d89`. **Accepted does not mean deployed:** automatic approval review rejected replacing/restarting the live server with the generic reason **“blocked by policy”**, without further detail. At this snapshot, main source and the tested binary are ready, but the live executable remains the original version. The qualification report's earlier `deployment: pending` is historical; the published deployment status is `blocked`.

## Run cohorts and retained evidence

Raw evidence root: [S:\GTOpen-research\postflop-gpu-20261016](S:/GTOpen-research/postflop-gpu-20261016). For every runner-managed ID, retain `runs/<ID>/report.json` and `stdout.log`; reports identify frozen workload/harness hashes, environment, binary hashes and build manifests. Candidate patches `runs/E001.patch` through `runs/E008.patch`, preserved binaries/manifests under `binaries/`, comparison reports and raw logs remain evidence even after implementation edits are reverted.

| Candidate | Baseline IDs | Candidate IDs used in score |
| --- | --- | --- |
| E001 | B001 | E001 |
| E002 | B002 | E002 |
| E003 | B004, B005, B006R | E003R2, E003R3, E003R4 |
| E004 | B007, B008, B009 | E004, E004R2, E004R3 |
| E005 | B010 | E005 |
| E006 | B011, B012, B013 | E006, E006R2, E006R3 |
| E007 | B014, B015, B016 | E007, E007R2, E007R3 |
| E008 | B017, B018, B019 | E008, E008R2, E008R3 |

- Preserve initial/cold B003 and E003, excluded from E003's warm cohort, and the initial flat `runs/B000-initial-baseline.log`; do not substitute them for the repeated score.
- [B006](S:/GTOpen-research/postflop-gpu-20261016/runs/B006/report.json) is invalid: Windows denied atomic replacement of `status.json`; B006R supplies the replacement measurement.
- [V000-resume-baseline](S:/GTOpen-research/postflop-gpu-20261016/runs/V000-resume-baseline/report.json) is invalid: its test filter executed no tests. The corrected `V000-resume-baseline-r` is retained separately.
- Diagnostic profiles, register-resource sweeps and lifecycle instrumentation are preserved under `runs/`; component timings and theoretical occupancy are not qualifying complete-cycle gains.

## D009 and next investigation

[D009 lifecycle summary](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D009-lifecycle-summary/report.json) passed the exact compressed state screen on all three fixtures. Across the two flop fixtures, host spans total **445.4546 ms for CPU encode/scatter/restore** and **188.9854 ms for device-to-host copy calls plus existing completion waits**. These are diagnostic measurements with timer/logging overhead, not isolated device timings or a qualifying performance cohort; no accepted gain follows from them. Raw [report](S:/GTOpen-research/postflop-gpu-20261016/runs/D009/report.json), [stdout](S:/GTOpen-research/postflop-gpu-20261016/runs/D009/stdout.log) and [instrumentation patch](S:/GTOpen-research/postflop-gpu-20261016/runs/D009.patch) are retained.

E004 is restored as the retained implementation; no new candidate is active at this checkpoint. The next investigation is GPU-side result quantization that preserves CPU `round_ties_even`, saturating-cast and nonfinite behavior. It has no performance or correctness claim yet.

## D010 standalone numeric proof

The subsequent [D010 proof](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D010-proof-summary/report.json) passed on the RTX 5090. Actual Rust `encode_i16`/`encode_u16` outputs matched the experimental CUDA kernel for 2,212 cases and 1,964,131 values per type: 3,928,262 encoded values, 4,424 scale bit patterns and 26,544 output guard words. All 1,977,403 packed input float bit patterns remained unchanged. Curated cases cover ties and adjacent floats, signed zeros, NaNs, infinities, subnormal scales, reciprocal overflow, empty blocks and long tails; randomized inputs use a fixed seed.

This is finite standalone numerical evidence, not solver integration or a speedup. The experimental kernel and ignored test are preserved under `crates/solver/tests/`; the CPU encoder is the independent oracle. [Integration design](S:/GTOpen-research/postflop-gpu-20261016/runs/D010-quantization-design/README.md) describes descriptors, scratch resources, budget fallback and unchanged inactive restoration. Integrated state checks and complete-cycle qualification remain required.


## E009 integrated GPU quantization — rejected

The integrated candidate passed **89 solver unit tests**, including **21 same-device-image comparisons** with the existing CPU readback writer (16 full syncs and 5 strategy-only syncs). Tests covered full/compact compressed storage, initial zeros, warm state, inactive restoration, materialization, locks, continuation, tight-budget fallback and F32 fallback. All four live device float arrays remained unchanged. A synthetic host test checks quantized-data gaps and nonowned scales; the game fixtures assert nonowned-scale coverage but do not guarantee q gaps. Forced CUDA allocation failure was not injected. [Unit evidence](S:/GTOpen-research/postflop-gpu-20261016/runs/V009-unit/stdout.log).

Three alternating pairs (B020/E009, E009R2/B021, B022/E009R3) matched full compressed fingerprints, exploitability bits and stopping iterations. The sum of fixture medians was **11150.6615 → 10995.9118 ms**, an observed **1.3878%** improvement, below the registered 2% gate. The river median regressed **110.8524 → 203.4038 ms**; initialization increased **91.3395 → 183.9442 ms**. The candidate is rejected, despite lower flop readback time. [Comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E009-three-pair-comparison/report.json).

The patch, new source files, binaries, manifests and logs remain under `runs/E009.patch`, `runs/E009-source/` and `binaries/E009-*`. No broader saved-state/menu/resume or full F32 benchmark qualification was performed after the performance screen failed. E004 remains the accepted implementation. E010 investigates reuse of the existing host staging allocation for compressed words and scales, eliminating redundant pinned allocations while retaining checked capacity/alignment and the original fallback path; it has no speed claim yet.
