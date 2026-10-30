D020 profiler audit and three-run design

Design only. No GPU execution, compilation, checkout change or live mutation was performed.

The registered evaluator has POSTFLOP_AUTORESEARCH_PROFILE=1 support in the frozen
E004 binary. It emits one AUTORESEARCH_STAGE diagnostic_profile after each scored
fixture, fingerprint and target assertion. Arrays profile_ms and launches follow:
copy_root, down_action, down_chance, up_fold, up_show, up_chance, up_action.
Values sum one additional iteration, both players and every relevant level.

What is actually timed
- Instant starts before launch-builder and argument submission. prof_acc waits for
  the stream after each launch, then adds elapsed host wall time and count.
- Normal iterations replay two CUDA graphs; iterate_profiled calls eager sweeps
  instead. Timings include CPU submission, synchronization/wakeup and GPU execution.
- The discount upload precedes the first timer but can complete during the first
  copy_root wait. The profiler starts after CPU fingerprinting, so GPU clock/cache
  state is not an immediate steady-state continuation.
- The sum omits work between timers and does not profile best-response/evaluation
  sweeps, CPU allocation, initialization or readback. It cannot apportion solve_ms.
- GPU state advances one iteration after the scored CPU fingerprint and is then
  discarded. A profile at 201 does not replace the recorded result at 200.

Interpretation limit: NO DEVICE-TIME-SHARE CLAIM. Repeated large-kernel rankings can
prioritize hypotheses; percentages are only of this synchronization-instrumented
host-time sample. Launch counts expose possible bias but do not calibrate it.
River and small kernels are particularly sensitive. Never use copy_root to subtract
one common per-launch overhead.

Prior evidence
The D000 raw log is preserved here, checksum verified against its diagnostic.json.
It contains older postflop_timings profiles. The known source uses F32 and profiles
iteration 66; it does not represent the new compressed terminal-state samples.
D000 had no original binary hash or process timestamp provenance. Its synchronized
sums were 29.1427 ms vs ordinary median 27.588 ms for rainbow (+5.64%), 17.1518 vs 16.270 ms
for two-tone (+5.42%), and 1.282 vs 0.260 ms for river (4.93x). This illustrates that
perturbation is fixture-dependent. The largest old flop bins were up_action,
up_show, then down_action. A scan of 99 runner stdout logs found no enabled optional
registered profile, so this is not repeated current evidence.

Plan
After E013 finishes, run exactly three serialized full compressed suites using the
frozen E004 executable and its build manifest. procedure.txt contains commands and
validation checks. audit.json records input identities, expected scored fingerprints,
format semantics and prior measurements. Source snapshots were extracted at the
build manifest commit and checked against its source hashes. Full-cycle timings
present in these diagnostic runs remain excluded from acceptance decisions.

No new profiling code or frozen evaluator edits are required. Preserve raw failures
and ambiguous ranks. D016 direct-three remains a contingency, not an implementation
instruction.
