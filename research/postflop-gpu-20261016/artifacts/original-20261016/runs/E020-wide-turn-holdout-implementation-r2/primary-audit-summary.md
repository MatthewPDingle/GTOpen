# E020 independent primary review

Verdict: PASS for the registered primary screen; provisional qualification only. The independently recomputed sum of three fixture medians is 10,486.8499 to 10,254.6581 ms, a 2.2141234% reduction. This exceeds the unchanged 2% threshold by 0.2141 percentage points. No fixture triggers the registered repeated >3% regression guard. There is no acceptance or deployment claim.

All 18 complete non-timing result objects and all 138 convergence records match across the six fixed runs. Comparison includes the full state_fingerprint object, every root strategy bit, exploitability bits, configuration, target flags, checks and stopping iterations. Every raw stage matches after removing only timing fields. The unit screen passed 84 tests with 4 ignored, with the same 88-test inventory as retained E015. This establishes the executed compressed-state screen; unsynchronized raw GPU floats and broader immutable-original F32/menu/resume/continuation controls remain separate requirements.

The exact declared order is V020-unit, B062, E020R1, E020R2, B063, B064, E020R3. Raw wrapper/native terminal records are successful and serialized; the successful Cargo build and both frozen artifacts precede every native test. All 162 source keys agree with accepted E015 except precisely kernels.cu and gpu/mod.rs; both candidate bytes match the authorized D037 archives and build copies. Binary, build-log, source-map, protocol, script, source/resource-review and report artifact hashes verify. The E020R1 patch alias is byte-identical to the build patch; no synthesized logical E020 measurement or exclusions are present. The audit passed 802 assertions and retained hashes for 125 source/evidence inputs.

Descriptive component medians (candidate minus baseline, ms):

| Fixture | Build | Init | Solve/checks | Readback | Full cycle |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rainbow | -1.7482 | -5.3816 | -87.1971 | +9.9919 | -85.6464 |
| Two-tone | -41.3274 | -43.6870 | -34.2824 | +2.5868 | -145.6097 |
| River | -0.0183 | -1.3517 | -1.1876 | -0.2173 | -0.9357 |

Rainbow and two-tone solve/check spans improve in all three pairs. Total paired solve/check deltas are -134.7159, -89.5699 and -123.5055 ms. Build/init variation also contributes, particularly two-tone, and cannot be attributed to the CUDA change from this cohort. Per-component medians do not add exactly to median full-cycle differences. Pairwise sums improve 1.3480%, 1.7616% and 2.2708%; these are descriptive and do not replace the registered sum-of-fixture-medians statistic. River is slower in two pairs (+2.0447% and +2.9146%) and faster in one (-2.4379%); none exceeds the >3% threshold. Its median improves 0.8425%. Whole-test/process diagnostics improve in all three pairs, but include hashing/teardown and are not the score.

The wide-turn protocol was sealed at 10:43:51.213895Z, independently reviewed at 10:45:05.585982Z, and attested with every planned run ID absent at 10:45:28Z. Invocation and V020-unit start follow at 10:45:29Z. All associated hashes verify. This preserves the prospective extra guard prompted by D037's wide-case theoretical occupancy drop; no holdout execution, occupancy measurement or numerical result is inferred from that protocol. The primary/resource audit entry condition passes. The holdout's actual evaluator, execution bindings and evidence still require their own reviews, and immutable-original broader controls plus a fresh-original cumulative cohort remain mandatory before adoption.

Scope: three serialized warm-driver-cache repetitions per binary, no cache reset, no statistical-significance claim, no all-workload guarantee. Runtime NVRTC/JIT and complete readback remain inside the primary boundary; Cargo, final fingerprinting/destruction, browser/API latency and disk saving remain outside. This review used only CPU-side reads, hashes and arithmetic and wrote additive evidence; no source/status edits, compilation or GPU work. The audit checklist was written after terminal notification; measurement policy was fixed by the earlier sealed protocol.
