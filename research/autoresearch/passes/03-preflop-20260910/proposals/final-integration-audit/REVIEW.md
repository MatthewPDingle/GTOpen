# Curated final integration review

Source-only review: no build, test, app access, or deployment performed. Reference retained source5f4f42c; grouped-terminal2ab5ea1 remains an experiment until its gates pass. Recheck final revision rather than copying moving worktree files.

## Production files

The main-to-research net implementation is confined to these five files:

- crates/solver/src/preflop/gpu.rs: planner/accounting, compact/normalized/active paths, prepared/minimal compatibility paths and embedded tests.
- crates/solver/src/preflop/kernels.cu: matching CUDA implementation; always integrate together with gpu.rs.
- crates/solver/src/preflop/mod.rs: paired CPU checkpoint evaluator and test-module declaration.
- crates/solver/src/preflop/multiway.rs: minimum exact CPU quadrature and reference tests.
- crates/solver/src/preflop/checkpoint_tests.rs: required new module referenced by mod.rs under cfg(test).

No server, web, schema, native-save format, dependency, or launcher implementation change is required. The build-action-ownership proposal is NOT in the retained net mod.rs diff and must not be described as shipped. Inclusive CDF/unroll proposals are also not retained code.

Research Cargo.toml additions only gate six GPU-only examples. Omit that manifest diff when excluding research examples. If preserving frozen harnesses in main, import their exact sources together with matching required-features declarations; otherwise default cargo test will attempt GPU-only examples without the feature. Preserve them in the research branch/proposal evidence instead of accidentally shipping allocation/register probes as required runtime code. No Cargo.lock change is needed.

Copy the selected five-file set from one pinned accepted commit into a reviewable integration diff; compare main against the frozen pre-integration HEAD first to preserve unrelated user changes. Do not cherry-pick the entire experimental branch with rejected/reverted controls. Retain test-only phase hooks under cfg(test). The three opt-in diagnostic environment blocks (PREFLOP_MW_SLOT_STATS, PREFLOP_MW_KEY_STATS, PREFLOP_GPU_LAYOUT_STATS) exist outside cfg(test); they are inactive normally. Leave them unset for ordinary app launch and benchmarks. Removing them is optional cleanup but changes final source and should precede final validation.

## Grouped-terminal specific gate

2ab5ea1 sorts the existing term list stably into O2/O3/O4/O5+ groups and slices the term and prepared-probability arrays together. Minimal mode bypasses grouping. Three new entrypoints are loaded even for legacy/minimal constructors, so final module allocation and real minimum-fit tests must run on that binary. Earlier5f4f42c boundary evidence does not cover the extra compiled entrypoints. Require unique terminal output slots, full term coverage, group/probability alignment, graph replay, gated zero reach, odd/final batches, every opponent count, and literal modeled/frozen native comparisons. A toggle test compares generic/grouped with the same already-sorted list; independent original whole-arena controls are still necessary to verify the reorder itself.

## Final validation commands (not executed here)

Run from the repository or the appropriate Cargo package cwd, with NVRTC on PATH and frozen cache/fit inputs. Serialize hardware jobs through the existing guard; never overlap live user solves. Archive commands, final commit, executable hashes, logs, exits and fixture hashes.

```powershell
cargo test --release -p solver
cargo test --release -p solver --features gpu --lib --test preflop_gpu --test gpu --test cuda_resources --test save_compat --test save_locks --test postflop_resume_state -- --test-threads=1
cargo test --release -p solver --features gpu --lib coupled_minimum_budget_direct_and_normalized_paths_match -- --ignored --nocapture --test-threads=1
cargo test --release -p solver --features gpu --lib coupled_minimal_metadata_retains_former_union_budget_fit -- --ignored --nocapture --test-threads=1
cargo test --release -p server --features gpu -- --test-threads=1
cargo build --release -p server --features gpu --target-dir target/desktop-runtime
```

When guards require built test executables, use cargo --no-run and then run_guarded.py with each exact executable/filter; preserve Cargo package cwd for fixture-dependent tests. The all-lib GPU run must include actual forced-policy allocation/refusal, deployed-reference planner, all-O terminal, graph/cancellation, and paired checkpoint tests, not only preflop::gpu::tests (other test modules sit outside that prefix). Existing benchmark paired exactness and CPU numerical tolerances remain separate; no blanket bitwise CPU-equity claim.

Repeat final accepted-source frozen all-solver3/6/7/8 controls, modeled literal19/21GB and frozen-coupled full-native comparisons. Native roundtrip should verify config, profiles, locks/frozen/hero, model, iteration, both complete arenas and effective policies. Literal23GB original timed out before iteration1, so that whole-game parity/speed ratio remains unestablished. At minimum preserve successful literal19/21 and frozen coverage. Do not rerun23GB just to seek a favorable timing.

## Session-preserving deployment checklist

1. Re-read live status immediately before maintenance. Parent currently reports port56708, stopped preflop status73 with authoritative native save74, and postflop210 on Kd6s5c. These are parent-supplied preservation targets, not live readings from this audit. If anything changed, snapshot latest state instead of overwriting it with old research inputs.
2. Save both idle sessions to unique native backups, pin hashes, record visible paths/config/board/ranges/model/profiles/locks/hero/frozen and actual native iteration. Do not decrement native74 to match stale displayed73. Never restore the research iteration174 or modeled convergence fixtures into the user's game.
3. Build the final accepted runtime while the old process remains available. Test a separately bound isolated server with copies of both backups; verify preflop native74 and postflop210/Kd6s5c and complete persisted state. Do not start a solve merely to smoke-test restoration.
4. Re-verify the process owning56708 and its executable before a permitted restart. Preserve the previous executable and backups for rollback. If stop/replacement is blocked, use an allowed alternate-port installation and state that clearly; do not claim the old process was updated.
5. The current launcher reuses any ready server BEFORE rebuilding, and defaults to3737. Thus double-clicking alone does not replace a running56708 binary. Build explicitly first and preserve the actual shortcut's port/working directory. Use hidden background launch and verify PID/executable hash/version after start; do not infer deployment from a successful build.
6. Restore both native backups, verify state above, inspect read-only Preflop/Browse/Reports behavior, and leave both solves stopped. Report native74 versus prior display73 candidly if visible. No library/report/scenario migration is needed for this change.

## Documentation/evidence gaps to close

Refresh the earlier validation-coverage snapshot: literal19/21GB and frozen-coupled full-native exactness are now recorded in literal-compatibility-comparisons.json and saved-literal logs; minimal boundary and preflopGPU13 also passed on the earlier deployed-compatible revision. Preserve literal/corrected labels in final charts and reports. Original eight100 additional iterations missed target; a separately frozen extended pair may add evidence but cannot erase that miss. Mark B32 policy mismatch,23GB timeout, rejected geometry trials, and untested proposals explicitly. Update findings/run/results/main README performance scope and any speed/memory UI prose that cites old numbers; leave model precision/sample/menu claims unchanged. Final suite counts must belong to integrated source, not historical174 tests.

This is an integration plan, not a deployment claim.
