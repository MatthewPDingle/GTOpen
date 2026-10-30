# D045 sparse selected-kernel device-event diagnostic

Prepared only; no build, native test, GPU job or checkout activation was performed by the preparers. This reuses the fixed D035 sparse protocol and D033 R2 diagnostic against accepted E020. Original D033/D035 artifacts remain unchanged. The source archive is independently frozen under `source/`.

One rainbow compressed invocation warms both ordinary and instrumented states to140, then retains the three fixed20-iteration batches ending160/180/200, in native/instrumented, instrumented/native, native/instrumented order. Each graph retains all63 kernels and62 original edges and adds six events at19/20,29/30,34/35:69nodes and74edges. The selected launches are down_action19, up_show29 and up_action34. E020's actual up_show shared reservations are6300/5060 bytes; every selected launch has grid141120×1×1 and block128×1×1. All18 final-replay intervals are retained.

Full raw state is compared before exploitability at140/160/180/200, and all compressed q/scale words are compared afterward. All ten exploit anchors and the entire final state object, including root strategy bits, remain equal to original B038, historical E015C1 and accepted E020C1. The140 compressed comparison is source-enforced before graph setup rather than separately marked. Dual-arm device/host admission, bounded raw snapshots, explicit graph upload and checked cleanup are retained.

Every batch must have absolute instrumented/native device-envelope change≤10% for diagnostic usefulness. Failure is inconclusive, preserves all samples, and permits no extension. Passing does not bound individual interval bias. These are selected captured training launch intervals, not full native solve/family costs or speedup evidence. No family sums, full graph envelope, intergraph gap, candidate acceptance or deployment follows.

## Root execution

After independent source and script review, create `authorization.json` using `authorization.example.json`. Pin the frozen scripts manifest and each prerequisite report in `evidence_sha256`; the script-review pin is added after that review exists, avoiding a circular seal. Record its SHA256. Root applies only `source/candidate.patch` after verifying all162 accepted entries. This appends the test module declaration and adds one ignored helper, producing163 entries; production statements, CUDA and the frozen evaluator stay unchanged.

Run each command serially and observe terminal success before the next. Replace `AUTH_SHA256` with the exact root authorization hash:

```powershell
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D045-sparse-event-diagnostic\build.py' 'AUTH_SHA256'
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D045-sparse-event-diagnostic\run.py' 'AUTH_SHA256'
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D045-sparse-event-diagnostic\assess.py' 'AUTH_SHA256'
```

Build output is `runs/D045-build`, using a previously absent `build-d045-sparse-events` target and immutable `binaries/D045-solver.exe` plus manifest. The build is release, locked/offline, features gpu, lib tests only, no-run; it rejects compiler overrides, requires a fresh solver test artifact, verifies embedded complete E020 CUDA and the D045 marker, and retains source/dependency/log hashes. Its1800s timeout and10s best-effort heartbeat retain the existing GPU lock until owned-child cleanup.

Execution output is `runs/D045-execution`; the existing serialized runner owns the GPU lock, live-idle check,10s heartbeat, pre/post telemetry and raw `runs/D045R1` evidence. The sole ignored test filter is `gpu::graph_device_events::captured_graph_device_event_diagnostic`. Accepted E020 has84 passing plus4 ignored library tests; the added ignored test gives89 total, so this filter must report1 passed and88 filtered. The outer process has a fixed900s timeout and owned-child cleanup. No run/output may be overwritten.

Assessment creates `comparisons/D045-sparse-event-diagnostic` once, with parsed markers, all selected samples, outer perturbation, exactness evidence and report hashes. Native/build/provenance failures are invalid; excessive perturbation is inconclusive. Root's independent terminal audit follows. After evidence is preserved, root restores exact accepted `gpu/mod.rs` and removes only the newly introduced `gpu/graph_device_events.rs`, verifies all162 accepted identities, and records cleanup. Never restart or replace the live server.

The build/run lifecycle is narrowly adapted from D033, with the already-used D044 fresh-target, timeout, child-cleanup and source-pin safeguards. The assessor reuses D033's raw marker/anchor/topology checks and replaces dense aggregation with the six frozen sparse selectors. No numerical workload, reduction, alternative sampler or adaptive rescue is introduced.
