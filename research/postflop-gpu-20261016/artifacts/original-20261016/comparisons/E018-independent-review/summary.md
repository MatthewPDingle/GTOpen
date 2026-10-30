# E018 independent terminal review

**Audit PASS; rejection confirmed.** Sum of per-fixture medians is 9739.3074 -> 9800.7838 ms (-0.631219% observed gain), below the unchanged 2% gate. No fixture triggers the repeatable >3% regression guard.

| Fixture | E015 median ms | E018 median ms | Observed gain | Paired regressions >3% |
|---|---:|---:|---:|---:|
| rainbow | 5720.0181 | 5771.6172 | -0.902079% | 0/3 |
| two-tone | 3918.0579 | 3926.9452 | -0.226829% | 0/3 |
| river | 101.2314 | 102.2214 | -0.977957% | 0/3 |

All 18 raw complete non-timing result objects match across the six runs, including every state fingerprint, root value/exploitability field, stop, configuration and workload setting. Only the six established timing fields were removed. Raw markers also equal their report copies. Frozen evaluator/workload hashes, native binaries, manifests, build logs and patches verify. Exactly the five reviewed production files differ from E015; all 162 build-source entries match runtime provenance for the three candidates and two validation runs.

Both builds completed before validation/timing. V018-unit: **86 passed, 4 ignored, zero failed**; all seven focused mapping/estimate/lifecycle/evaluation/tight-budget tests were located in stdout. The two printed invalid-slot panics are deliberate caught negative cases followed by ok. V018-capacity: **one passed**, covering the turn and river, uploaded mapping equality, planned/observed payload and exactly-once byte accounting.

Observed order matches the prospective protocol: V018-unit, V018-capacity, B056, E018R1, E018R2, B057, B058, E018R3. Adjacent timing runs have gaps of zero or one second at report timestamp precision. Pairs remain B056/R1, B057/R2, B058/R3. All six have the same registered environment and GPU/driver identity.

The first invocation was refused while the feature build held gpu-run.lock. The runner acquires this lock before creating a run directory or calling the native launch path; the operator record reports all planned IDs absent and zero native launches/samples. Its evidence origin is root tool output; a separate raw stderr transcript was not saved. The unchanged script was rerun after the build completed. No measured sample was replaced or excluded.

The comparison used measured E018R1 while E018 remains the logical dashboard row. Build, r2 design and E018R1 alias patches are byte-identical. Preserved assessment invocation/stdout/stderr verify successful publication; stderr is empty and no dry-run correction is recorded. The warm-cache label does not subtract runtime NVRTC/JIT or establish controlled cache temperature/cold-start behavior.

Descriptive paired-total means, candidate minus baseline: build_ms -10.1967 ms, init_ms -9.7945 ms, solve_ms +53.3347 ms, readback_ms -4.4627 ms, full_cycle_ms +28.8929 ms. These are not the primary median statistic and do not identify a causal bottleneck.

**Scope limit:** failed primary performance stops qualification. No broader immutable-original F32, saved-state/menu/resume or continuation paging/storage controls were run for E018. Existing unit comparisons sharing the candidate up kernel are useful lifecycle checks but cannot independently validate that changed kernel. This review confirms the measured rejection and scoped exactness; it makes no general compatibility, accepted-gain or deployment claim.

This reviewer performed no build, GPU execution, source edit or dashboard update. Preserved binaries and source archives remain authoritative after checkout restoration.
