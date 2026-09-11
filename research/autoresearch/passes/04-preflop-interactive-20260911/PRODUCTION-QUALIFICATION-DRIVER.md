# Curated production qualification driver (not executed by its author)

`qualify_production.py` is pinned to source commit `53ce9dec08de9fa2f93f246d7f5efcccc8c22c68` in `target/autoresearch/preflop-interactive-production-20260911`. Default invocation only prints a plan. It must be launched by root after the current hardware queue ends, with the normal working MSVC/Rust build environment available on PATH.

```
python research/autoresearch/passes/04-preflop-interactive-20260911/qualify_production.py --execute --phase all --id production-53ce9de-a
```

Alternatively run `--phase build`, review the created `build-manifest.json`, then run:

```
python research/autoresearch/passes/04-preflop-interactive-20260911/qualify_production.py --execute --phase tests --manifest T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911/target/qualification/production-53ce9de-a/build-manifest.json
```

Both phases share the same maximum900-second window from build start, capped by2026-09-11T03:03:27Z. Separating phases does not reset that deadline. Per Cargo build cap is420seconds; each test executable cap240seconds; doctests180seconds, all additionally bounded by the shared deadline. A completed partial phase and every failure preserve logs/artifacts/results. Use a new ID after a failed run; do not overwrite evidence.

The GPU server is built first using the existing research lab Cargo target cache. Its compiler-artifact executable is frozen and immediately copied into the production worktree's `target/qualification/gto-server.exe` before any CPU build can replace the shared target's server. An existing staged executable must match exactly or the driver refuses; it never silently overwrites a different runtime. Each subsequent test artifact is copied under the unique qualification directory with a SHA256-qualified name before other builds continue. Cargo JSONL logs retain compiler-artifact provenance and diagnostics; manifests record source commit, command, original/frozen executable, SHA256, crate/source target, features, test profile, cache/fit hashes, fixed environment and individual timings. This is staging for private qualification, not deployment.

Build schedule: GPU server; GPU solver library plus `gpu`/`preflop_gpu` integration test executables; GPU server tests; all non-GPU solver library/bin/integration test executables; non-GPU server tests; non-GPU server runtime compile. Explicit target selectors avoid rebuilding or replacing the research example EXEs in the shared Cargo target.

Default test schedule: the new detached exactness GPU library test; all6 `gpu` and14 `preflop_gpu` integration tests; GPU server publication/lifecycle tests; every non-GPU solver library/bin/integration executable; CPU server tests; solver doctests. Each test binary runs serially with `--test-threads=1` in its actual production crate directory. The unrelated full GPU library H/I suite is not rerun. Example compilation is deliberately excluded while full non-GPU test targets and doctests are included.

Ownership: each hidden child starts suspended, is attached to its own Windows kill-on-close Job Object, and is resumed only after assignment succeeds. Its Cargo/rustc/test descendants remain in that owned job. Every0.5seconds the driver checks the real port56708 preflop, postflop and report status using read-only GETs; activity, failed guard, time limit or interruption closes only the owned job. No process-name or port-wide termination, live POST, server restart, user save or deployment occurs. The production qualification lock prevents simultaneous invocations of this driver; root must still serialize it with other research runners.

Source author performed only AST syntax parsing, without invoking the plan, builds, tests or ownership APIs. Root should treat actual driver startup/Job Object support as unverified until first execution; setup failures stop before child code is resumed. No evidence of successful compilation/tests should be inferred from this source preparation.
