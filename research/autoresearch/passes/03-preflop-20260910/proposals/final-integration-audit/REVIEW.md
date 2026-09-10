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

## Accepted-source addendum — 4878044924f2e170692a897de4179690357cf669

This addendum supersedes the earlier source-selection, action-ownership exclusion, and grouped-terminal-specific sections above. It is a final source-only audit of the pinned accepted commit against production baseline 1b8fc3f; no compilation, tests, benchmarks, live-app access or implementation edits were performed by this reviewer.

**No source-level integration blocker found.** Curate exactly the five files listed above from the accepted commit, as one set. Their Git blob IDs and SHA-256 hashes of exact Git bytes are recorded in `accepted-source-manifest.json`. All five isolated worktree files matched those accepted bytes after line-ending normalization at review time. Main was at 49437f68876e938186632394da84d296a40a5511; its preflop production paths were clean and unchanged from 1b8fc3f. Recheck this before applying because the main branch may advance.

### Actual retained implementation

- `gpu.rs` and `kernels.cu` are byte-identical to their accepted 5f4f42c versions. They retain active-slot gating, prepared counterfactual probability, per-traverser compact CDF storage, optional normalized reaches, exact direct/minimal low-memory fallback, accurately accounted forced policies, and literal deployed batch/cache preference with explicitly labeled corrected-budget fallback/capacity extension.
- There are no O2/O3/O4 specialized terminal entrypoints, grouped dispatch fields/helpers, reordered terminal worklists, or diagnostic batch-cap override in these production files. The rejected shared-normalized CDF candidate is absent: normalized CDF still reads the persistent normalized array directly with four independent warps and 170-entry CDF stride. Earlier probe register results and grouped-specific deployment gates are not evidence for the accepted implementation and need not be reported as retained gains.
- `mod.rs` DOES retain the narrow tree-building action-ownership optimization, in addition to paired CPU checkpoints. Legal actions are moved into the node after trimming Vec capacity; next-state creation borrows one node action only until the owned next state is produced, before recursive construction can reallocate nodes. Enumeration, child order, state transitions and native format are unchanged in source. Preserve the separate frozen build/load identity and resource measurements when documenting this retained change; the research harness is evidence rather than a runtime dependency.
- `multiway.rs` retains the minimum mathematically exact Gauss rule by opponent count, all 1,024 particles and f64 arithmetic. CPU rounding may differ from the original five-point implementation; do not claim universal CPU bitwise identity. The old five-point oracle and dense/sparse/tie-heavy 0..8-opponent tests remain included.
- `checkpoint_tests.rs` is required by `mod.rs` under cfg(test). It includes independent old-traversal root comparison, constrained/unconstrained BR, frozen/locked/profile/hero cases, separate requested/pruned outputs, reach restoration, cancellation, and ignored allocation-frontier stress. The reference traversal remains intact. The production preflop worker still checks its stop flag before publishing checkpoint values or convergence; no server change is necessary for this integration.

### Scope and integration advice

The complete research commit also contains Cargo example declarations and eleven research/probe examples. Do not copy the entire branch or all changed files into production by accident. The rejected opponent kernel still exists as a standalone research probe example; this does not mean it is part of the accepted runtime. If research examples are intentionally retained, copy matching manifest feature gates and identify the probes as research artifacts. The curated five-file implementation requires no dependency/Cargo.lock, server, web, launcher, save-schema, report-library or postflop source changes.

Phase timing hooks remain cfg(test). Three production opt-in diagnostics (PREFLOP_MW_SLOT_STATS, PREFLOP_MW_KEY_STATS and PREFLOP_GPU_LAYOUT_STATS) remain inactive unless explicitly set; ordinary launches should leave them unset. Do not perform cosmetic kernel/planner cleanup after the final frozen gates without acknowledging a changed source identity.

`git diff --check` on the pinned five-file preflop change passed during this source review. No test-pass counts are newly asserted here: use the parent's final logs/executable hashes belonging to this accepted revision and the actual integrated build. Retain the existing minimum-memory real GPU checks, graph/zero-reach/partial-batch controls, native full-arena comparisons, and public CPU/server suite coverage described above. Preserve literal-versus-corrected baseline labels and all timeout/nonconvergence limitations. The earlier session-preservation section is advisory history, not current live state; any deployment must independently snapshot and verify the latest user's stopped/running sessions.
