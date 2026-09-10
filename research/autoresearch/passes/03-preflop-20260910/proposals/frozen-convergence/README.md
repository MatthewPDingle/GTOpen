# Frozen preflop convergence harness (proposal only)

`preflop_convergence_control.rs` is a separate example. No existing benchmark, production solver, or CUDA math changes. Not compiled or run by the proposing agent.

Exactly six explicit arguments:

```
preflop_convergence_control INPUT.gtop BUDGET_MB ITERLIMIT TARGET_GAP_BB CHECKEVERY OUTPUT.gtop
```

- INPUT must be a frozen native preflop save. This deliberately excludes a config-only JSON input: native saves retain ranges, profiles, hero mode, frozen seats, point locks, existing iteration/arenas, and coupled/legacy identity.
- BUDGET_MB is a positive decimal-MB constructor budget. Record `PREFLOP_GPU_LAYOUT_STATS=1` alongside the run to identify actual batch/cache allocation. Do not assume equal budget means equal batch.
- ITERLIMIT is positive **additional** iterations, as in the server request. No huge default is supplied. Start and final native iteration are recorded.
- TARGET_GAP_BB is a finite positive **sum of learning-seat gaps in bb**, not a percentage or per-seat average. Freeze it before either candidate runs. Do not tune it after seeing a trajectory.
- CHECKEVERY is explicit; use **10 for the planned paired comparison**. Both executables must receive the same value. The final iteration is checked even if not divisible by 10.
- OUTPUT must be a new `.gtop` under the pre-created, canonical `target/research-convergence` directory in the isolated worktree. Native save writes a fresh private staging directory; after reload verification, a same-volume hard link publishes without replacing an existing output. If this filesystem cannot hard-link, fail and retain the staged save; do not fall back to overwrite-style rename.

Freeze the same native input SHA256, equity cache SHA256, realization-fit artifact, executable/source hashes, target, interval, limit, model, and CUDA precision flags before the pair. The harness reports input/cache streaming FNV-1a fingerprints for change detection, not cryptographic provenance. Use the parent guard's SHA256 manifest for provenance. Freeze/calibrate the fit beforehand; this harness does not intentionally refit, edit profiles, or override model identity. Existing native loader behavior is retained.

## Server equivalence verified against local source

`crates/server/src/main.rs:1308` checks `done % check == 0 || done >= max`; lines 1335 onward call GPU `gaps_and_evs` then `sync_to_cpu`; lines 1379–1398 obtain `s.live_seats()`, sum the selected gaps in seat order as f64, and stop on `total < target_gap || done >= max`.

`crates/solver/src/preflop/mod.rs:1172` defines the learning mask. A frozen seat is excluded. A hero seat remains learning unless frozen. A profile with all buckets supplied and no adaptive response is fully ruled and excluded. Partial profiles and adaptive-response profiles remain learning. Normal GPU gap evaluation already uses the appropriate constrained best response for adaptive modeled seats. The harness calls those existing methods rather than duplicating policy logic.

There is no initial check or early exit based on a previous saved gap. A table with zero learning seats still reaches its first scheduled checkpoint, then a zero total satisfies the positive target, just as in the server. `no_learning_seats` makes that distinguishable from convergence of unrestricted players. Gaps are neither clamped nor averaged. At exact equality with target, continue. At limit without meeting target, output is explicitly `not_converged_iteration_limit`, `converged:false`; a valid bounded non-converged result exits successfully.

One deliberate failure-handling difference: CUDA failures abort the controlled run instead of silently falling back to CPU as the interactive server does. Nonfinite diagnostics also fail. A killed run is incomplete and has no final result; do not count it as converged. Only the final scheduled checkpoint is saved, so use the parent deadline guard and a deliberately chosen finite limit; this is not a resumable job scheduler.

## Measurements and verification

Each iteration emits its time and both additional/native iteration numbers. Each checkpoint emits every gap and EV, learning mask, summed gap, target result, separate gap-check and CPU-sync times, and cumulative iteration/check/sync times. `trajectory_ms` spans iteration/check work plus logging and orchestration, excluding save/reload. The final result repeats all stopping inputs and measured totals.

After the last checkpoint, fingerprint regret and strategy arenas, save, reload, and compare arena bits via the same FNV-1a fingerprint plus public config/model/iteration/hero/profile/frozen/learning metadata. Input and equity-cache fingerprints must remain unchanged before publication. This checks arena persistence, not every private native metadata field independently. Existing native-save tests cover private point-lock/hero-backup serialization.

Different batch sizes can produce tiny rounding differences and divergent long trajectories. Compare target attainment and all checkpoint numerical outputs; do not demand an identical final arena for different batches. A matched-batch control is the separate way to establish bitwise arithmetic equivalence. An identical starting save is necessary even if both model names match.

## Integration and bounded validation for the parent

Apply `add-convergence-harness.patch` in the isolated worktree, build this one example with the existing GPU feature/toolchain, and freeze the resulting executable hash. This proposal adds one host-only test of the gap filter/strict comparison (not yet run). Run a tiny native fixture with an explicit small limit before the expensive modeled pair. Verify a target-limit miss, strict equality helper, final off-cadence check, an existing-output refusal, save/reload fingerprints, and a modeled fixture's learning mask. Do not change thresholds/assertions to accommodate a failure.

Recommended paired protocol: one predeclared target and interval 10; finite limit selected from observed convergence and remaining deadline; separate fresh OUTPUT paths. Keep timing inclusive/exclusive categories identical. Report not-converged honestly rather than extrapolating a completion time from the early speedup.
