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


## E010 shared host staging — rejected

E010 reused the existing pinned host staging allocation for aligned, nonoverlapping compressed-word and scale buffers, removing both additional pinned allocations from E009. Checked capacity/alignment/overflow decline the optional path when needed; initialization remains inside the first readback. **92 solver unit tests passed**, including three new staging boundary/initialization/reuse tests and the existing exact-readback integration checks.

Three alternating pairs (B023/E010, E010R2/B024, B025/E010R3) matched complete compressed state, exploitability bits and stopping iterations. Their score was **11130.2839 → 10871.3492 ms (2.3264%)**, but the river median regressed **79.8807%**, with **3/3** paired regressions above 3%. E010 is rejected under the existing per-fixture guard. The comparison helper now records a repeatable failure as median regression above 3% plus a strict majority of pairs (minimum two); it still cannot accept any candidate. [Comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E010-three-pair-comparison/report.json), [92-test log](S:/GTOpen-research/postflop-gpu-20261016/runs/V010-unit/stdout.log).

The repeated river initialization overhead survived removal of extra pinned allocations. A separate D011 diagnostic will time descriptor construction, function loading, device allocations and existing transfer waits. No cause is confirmed yet. E004 remains the accepted implementation; E009/E010 source, binaries and raw results remain preserved. No new candidate has passed full F32 or broader saved-state/menu/resume qualification.


## D011 optional initialization profile

The [D011 diagnostic](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D011-init-summary/report.json) matched full compressed state, exploitability and stopping iterations on all three fixtures. The river's optional quantized setup took **0.1468 ms**, including **0.0600 ms** in its two function-load calls, while enclosing initialization took **167.7424 ms**. This does not support the suspected function lookup or direct optional setup as the cause of the repeated river regression. Rainbow/two-tone optional setup totals were 26.1699/15.7886 ms.

These are one-run diagnostic host spans with logging/timer disturbance, not qualifying speed results. The trace excludes work earlier in the constructor and its own final logging, and does not exclude indirect effects of the appended code on earlier module/context setup. The instrumentation was removed and the exact E010 source restored. D012 will separate the surrounding constructor stages before another implementation hypothesis is chosen.


## D012 constructor and D013 isolated-fixture diagnosis

[D012](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D012-constructor-summary/report.json) found the river excess in the CPU-side planning/budget wall span before context creation: **87.2595 ms**, versus **0.0350 ms** in a fresh D009 baseline diagnostic. Context, stream, module and optional setup spans did not explain the excess. This locates a wall-time stall, not its allocator, scheduling or computational cause. Both diagnostic binaries matched exact registered state; instrumentation was reversed with exact source-hash checks.

[D013](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D013-isolated-summary/report.json) ran three alternating pairs per isolated fixture using unchanged E004/E010 binaries. Two-tone complete-cycle medians were **4252.3019 -> 4347.9435 ms (2.2492% slower)**; its prior full-suite construction advantage disappeared (**79.6395 -> 87.9708 ms** isolated construction), while readback still improved. River medians were **195.8999 -> 209.6415 ms (7.0146% slower)**, a much smaller penalty than the full-suite 79.8807%. Both fixtures were slower in all three pairs. All 12 results retained exact configuration, complete-state fingerprints, exploitability bits and stopping iterations. An independent read-only audit verified preserved binary/manifest/log hashes.

Filtering changes execution history and puts first-use runtime NVRTC/PTX costs on the selected fixture. These diagnostic results do not replace the frozen primary score or prove an allocator cause. E010 remains rejected. Its source and all diagnostic patches/binaries remain preserved; the checkout GPU implementation was restored exactly to accepted E004. The registered complete cycle excludes destruction after fingerprinting: any future lifetime/drop-order experiment requires an additional entire-process measurement including destruction, to prevent moving work outside the score and calling it a saving.


## E011 design bound and D014/D015 CPU encoder probes

[E011](S:/GTOpen-research/postflop-gpu-20261016/runs/E011-zero-design/README.md) was preserved as an unimplemented design. Direct restoration of proven-zero compact inactive blocks is exact in principle, but even removing the entire affected two-tone CPU readback stage would fall below the registered 2% gate; rainbow uses the full arena. No source edits, build or measurement were performed for E011.

[D014](S:/GTOpen-research/postflop-gpu-20261016/runs/D014-host-max-proof/report.json) tested four independent maximum-reduction lanes against byte-preserved original encoders. All 20,480,834 encoded words, 22,696 scale bit patterns and 136,176 guards matched across 11,348 cases per type; input bits stayed unchanged and injected corruption failed before timing. However, 55 of 56 nine-pair CPU timing groups were slower. Assembly showed the original already vectorizes its maximum scan. The prototype is rejected without solver integration; all artifacts are retained.

[D015](S:/GTOpen-research/postflop-gpu-20261016/runs/D015-host-sse41-proof/report.json) instead calls the unchanged original encoder from a runtime-gated SSE4.1 function. It passed the same exact corpus and injected-failure guard. Compiled code replaced rintf library calls with rounding instructions. All 56 CPU timing groups improved; finite block times decreased 51-55%, with the runtime feature check included. These cached standalone timings do not establish any complete-solve improvement. E012 will test a private GPU readback wrapper; shared CPU CFR encoding remains unchanged. No kernel, workload, precision, stopping or evaluation changes are intended.

A separate [D016 contingency audit](S:/GTOpen-research/postflop-gpu-20261016/runs/D016-direct3-design/audit.md) corrected a coverage assumption: E005 already partitioned mixed levels for direct two-action processing, covering about 63% of flop action nodes. Its 5.84% predecessor census described homogeneous spans only. A direct three-action candidate is a distinct, untested lower-priority hypothesis, not a rerun of the rejected E005.


## E012 SSE4.1 Store wrapper — rejected

The private GPU host writer retained the original encoder and portable fallback, selecting the hardware path once per readback outside parallel node loops. It passed **84 solver unit tests**, including new exact-output/guard/fallback tests. Three alternating pairs (B026/E012, E012R2/B027, B028/E012R3) matched complete state, exploitability bits and stopping iterations. Score: **11306.9722 -> 11308.4885 ms (-0.0134%)**. No aggregate benefit was established; the river also failed the existing repeated-regression guard. [Comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E012-three-pair-comparison/report.json). No F32 or broader saved-state/menu/resume qualification followed the performance rejection.

[D017 compiled-library inspection](S:/GTOpen-research/postflop-gpu-20261016/runs/D017-E012-codegen/review.md) verified runtime selection and removal of rintf calls, but the integrated Store/raw-arena wrapper generated scalar roundss with no packed roundps. D015's standalone typed slice functions had vectorized quantization. All 109 tracked source/input hashes stayed unchanged during inspection, and frozen native binaries were not replaced. E013 is a bounded follow-up with separate non-inlined typed encoder function boundaries; the alias-information explanation remains an inference pending compiled-code evidence. E012 source, tests, binaries, patches and logs remain preserved; E004 remains the accepted implementation.

## E013 typed encoder boundaries — rejected

E013 added separate non-inlined SSE4.1 typed slice helpers around the unchanged encoders. It passed **84 solver unit tests** with four ignored. Three alternating pairs (B029/E013, E013R2/B030, B031/E013R3) matched all 18 complete-state/configuration records, exploitability bits and stopping iterations. The frozen complete-cycle score was **10990.0495 -> 11026.1506 ms (0.3285% slower)**, below the registered 2% gain gate. No fixture triggered the repeated-regression guard. [Primary comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E013-three-pair-comparison/report.json).

The [independent component audit](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E013-component-audit/summary.md) verified all six run/log/binary/manifest identities. The first pair's apparent 2.77% gain did not persist: 87.14% of its saving was in unchanged solve/checks and only 9.45% in readback. Summed readback medians fell **636.6522 -> 617.4982 ms**, a 19.154 ms component saving equivalent to only 0.1743% of the complete baseline score. Standalone D015 reused small buffers and excluded transfers, synchronization, parallel scheduling and scattered arena writes; existing measurements cannot attribute the difference to a specific cost or cause. Components do not replace the primary acceptance score.

No F32 or broader state/menu/resume qualification followed the failed performance screen. Candidate source, patches, binaries, manifests and logs remain preserved. The production source was restored exactly to accepted E004; [cleanup record](S:/GTOpen-research/postflop-gpu-20261016/runs/E013-cleanup-restored-E004.json).

## D017–D019 code-generation evidence correction

D017 and D018 emitted **library-stage assembly before final ThinLTO**. Their scalar rounding loops do not establish the instruction sequence in the measured final executables. Preserve those observations at their actual scope; the earlier scalar-code explanation for limited solver gains was not established.

[D019](S:/GTOpen-research/postflop-gpu-20261016/runs/D019-E013-final-codegen/review.md) emitted final executable assembly from unchanged E013 source: each typed encoder contains two packed `roundps` sites, one scalar `roundss` and no `rintf`, with the whole encoder body matching D015 after symbol/label normalization. This diagnostic executable has a different hash from the measured frozen E013 binary, and was not run. It confirms intended final-build vectorization from matching source, not a speedup or direct disassembly of the measured binary. All original artifacts and the [scope correction](S:/GTOpen-research/postflop-gpu-20261016/runs/D017-D018-evidence-boundary.md) remain preserved.

## D020 fresh action-kernel profiles

Three diagnostic runs using the accepted E004 binary matched the complete state, configuration, exploitability bits and stopping iterations against B029. The frozen harness's optional extra profiled iteration runs after scoring and fingerprinting, at iterations **201/201/61**. Every flop sample ranked **up_action > up_show > down_action > up_fold > up_chance > down_chance > copy_root**. Median up_action spans were 9.5945 ms rainbow and 6.0716 ms two-tone, followed by showdown at 7.1028/4.8732 ms. River ranking was unstable. [Summary](S:/GTOpen-research/postflop-gpu-20261016/comparisons/D020-profile-summary/report.json).

These are synchronized eager-launch host spans including launch construction and per-kernel waits, unlike normal CUDA graph replay. They omit inter-timer work, best-response evaluation and initialization/readback; copy_root can also drain the prior discount upload. They are neither device-time shares nor an apportionment of ordinary solve time. All profiled-run complete-cycle measurements are excluded from acceptance. An independent review verified all nine state records, raw-log hashes, profile stage records, names and launch counts.

The next bounded hypothesis is D016's direct-three-only action entry point, beginning with a compiler resource comparison. E005's unsuccessful direct-two result and added launch costs remain counterevidence. No new performance claim is made.

## D021 resource probe and E014 direct-three kernel — rejected

[D021](S:/GTOpen-research/postflop-gpu-20261016/runs/D021/README.md) found 40 registers and zero local bytes per thread for a direct `up_action_impl<3>` entry point, compared with 66 registers and 64 local bytes for the dispatcher. Theoretical occupancy at 128 threads was 12 versus 7 blocks per SM. Candidate dispatcher PTX and resources matched the baseline control. No kernel was launched in this diagnostic; the initial failed host link and successful thin-LTO retry are preserved. These counts justified a runtime hypothesis, not a speed claim.

E014 stable-partitioned only levels with at least 4,096 action nodes, using a three-action prefix and the existing dispatcher for the remainder. It retained node identities, offsets, child arithmetic/order, aggregate down/evaluation spans and 128 threads. New prefix counts are host metadata; both training-up launches remain in profile bucket 6. The runtime CUDA source is byte-identical to D021's candidate. **84 unit tests passed**, including two partition controls, with four ignored.

The compiler completed successfully, but the initial source-freeze check caught a concurrently added, uncompiled supplemental test. A separate [recovery audit](S:/GTOpen-research/postflop-gpu-20261016/runs/E014-build-freeze-recovery.json) verified every prebuild input unchanged, exactly the two explicit test targets, frozen executable/manifest hashes and unchanged archived source/patch. An independent reviewer also confirmed the supplemental file appears in neither compiled target's dependency file. It is excluded from qualification; the failed freeze assertion and recovery remain explicit evidence.

Three alternating pairs (B032/E014, E014R2/B033, B034/E014R3) matched all 18 complete-state/configuration records, exploitability bits and stopping iterations. The frozen score was **11361.8588 -> 11451.4847 ms (0.7888% slower)**. No fixture triggered the repeated-regression guard, but the aggregate failed the 2% gain gate. The unusually fast first reference and all subsequent samples were retained without changing the statistic. [Primary comparison](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E014-three-pair-comparison/report.json).

E014 is rejected. No F32 or broader state/menu/resume qualification followed the failed performance screen. The [D022 supplemental control](S:/GTOpen-research/postflop-gpu-20261016/runs/D022-direct3-control-design/README.md) was source-reviewed but never compiled or executed: existing frozen controls do not cover locked three-action nodes on qualifying large levels. Its source remains preserved outside the checkout. All four production files were restored exactly to E004, with [hash-checked cleanup](S:/GTOpen-research/postflop-gpu-20261016/runs/E014-cleanup-restored-E004.json).

## D023 paired reach-reuse hypothesis

[D023](S:/GTOpen-research/postflop-gpu-20261016/runs/D023-reach-reuse-design/audit.md) identifies duplicated work within an ordinary two-player iteration: the first down sweep computes both players' reaches, and player 0's subsequent up sweep does not change player 1's reach inputs. A narrowly scoped host-only candidate can pass `nh1=0` to the three down kernels in the immediately following player-1 sweep, retaining real hand counts for all upward work. Source inspection finds no zero-count division, barrier or unguarded player-1 data access in those down kernels.

This must be an explicit paired-iteration mode. First sweeps after evaluation, standalone continuation, paging, storage swaps and arbitrary player-1 entry points still require full propagation. The estimated 26.45% reduction in down-action hand visits is a structural count, not a timing forecast. E015 will test raw device-state equivalence and complete-cycle performance from accepted E004; no implementation or speed qualification follows from the design alone.

## D024 status payload maintenance

Between E014 and E015 cohorts, the runner's dashboard projection stopped duplicating nested `config` and `state_fingerprint` data inside experiment rows. Full run reports and logs remain unchanged and linked. The page uses row summary fields; exact comparison tools use raw reports. An independent dependency review found no consumer of the removed dashboard-only nested keys.

The [migration audit](S:/GTOpen-research/postflop-gpu-20261016/runs/D024-dashboard-payload/report.json) archived the complete before/after status, preserved all 120 rows and every other field/order, verified nonmutating/idempotent result copies and rehashed all E014 cohort reports/logs unchanged. Payload fell **4,640,621 -> 440,088 bytes**. This is a status-page maintenance result, not a solver speedup. Both subsequent E015 cohorts will use the same updated runner; frozen evaluator and workload remain unchanged.

## E015 paired reach reuse — accepted

E015 passes zero player-1 hands only to the three down kernels in the second sweep of an uninterrupted ordinary/profiled two-player iteration. The first sweep refreshes both players, player-0 upward work changes only player-0 learning state, and all upward kernels retain real hand counts. Standalone continuation, paging and workspace calls retain full propagation. CUDA source, arithmetic, precision, plans and evaluator are unchanged. The source is committed as `e868cfbb125002216f25046af2d88b22a697b2fd` and integrated into main as `bf0d15c42a587180981d616159af382dfd9dd45d`; main and research production source hashes match.

Three alternating pairs against E004 (B035/E015, E015R2/B036, B037/E015R3) produced **11262.8874 -> 10814.3093 ms (3.9828% lower complete-cycle time)**. All 18 complete non-timing result records matched, and no fixture failed the repeated-regression guard. A fresh original-baseline comparison (B038/E015C1, E015C2/B039, B040/E015C3) produced **10740.3699 -> 9707.2344 ms (9.6192% cumulative improvement)** with all 18 records exact. Cumulative fixture median gains were rainbow 9.4648%, two-tone 10.0665% and river 0.6671%. No sample was excluded. This cumulative result is directly measured; percentages were not added, and absolute timings must not be compared across the two cohorts.

Broader checks passed: **84 solver unit tests** (four ignored), **six GPU integration tests**, **160 exact saved-state/menu/resume snapshots**, and all three full-F32 state/configuration/exploitability/stopping comparisons. New tests compare raw device reach/regret/strategy bits against full-sweep references across DCFR/CFR+, F32/compressed storage, full/compact arenas, evaluation, locks, graph recapture and warm-image reconstruction. An independent original-kernel down pass confirms the unchanged reach invariant, including changed roots and poisoned reach buffers. Warm-image tests are not disk-resume tests; existing broader controls supply disk save/load coverage. Generic standalone player-1 refresh is tested; actual paging swaps are outside those new test cases.

The [qualification](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E015-qualification/report.json), [primary audit](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E015-independent-review/validation.json), [cumulative audit](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E015-independent-review/cumulative-validation.json) and [integration review](S:/GTOpen-research/postflop-gpu-20261016/comparisons/E015-integration-review/source-review.md) retain measured source/binary/log identities. All nine primary paired fixture solve spans improved. Their mean summed solve saving explains 98.33% of the mean summed complete-cycle saving, a descriptive component result distinct from the primary median statistic, without proving a unique cause.

Acceptance is scoped to fresh compressed native solves on this RTX 5090, the three fixed fixtures and warm-cache protocol. F32/resume performance, cold-start performance, arbitrary-tree gains and browser/API latency are not qualified. Fingerprinting and subsequent destruction remain outside the frozen score. The dashboard preserves E004 history and now shows the freshly measured 9.62% cumulative result. Automatic approval review previously rejected live binary replacement/restart with the generic reason "blocked by policy"; source integration and isolated server validation do not imply deployment.

The main-source server build was frozen separately as `binaries/E015-gto-server.exe` (SHA-256 `b893d0812ad5b87d7f1e12b9e31c1b4c882285ab17fe607550c7e4771e640ff9`), preserving the earlier E004 server binary. **Twenty server unit tests passed**, one ignored. The [isolated API smoke](S:/GTOpen-research/postflop-gpu-20261016/runs/E015-server-smoke/result.json) completed 100 GPU iterations, returned finite results and valid root/child strategies for both actors, and left live API snapshots unchanged. It verified ownership of test port 43736, stopped only its own child process and confirmed the port was released. These are server integration checks, not additional timing evidence or deployment.
