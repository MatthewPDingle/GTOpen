# Literal pre-pass GPU frozen control

`literal-control.patch` restores **only** these two files to the byte content from1b8fc3f:

- crates/solver/src/preflop/gpu.rs
- crates/solver/src/preflop/kernels.cu

No forced-policy accounting correction, optimized kernels, compatibility planner, instrumentation, CPU source, Cargo manifest, or frozen harness changes are included. Full original files are supplied. `source-manifest.json` records their literal Git blob/SHA256 identities and the base identities of unchanged CPU/harness files. The patch is based on9333943, the current corrected-compatible restoration. Source-only git apply --check passed there. If later candidate commits are applied first, run `generate.py NEW_BASE_REVISION` to regenerate this proposal against that committed source; the generator writes only its proposal directory.

This is intentionally a research control, not a production fix. It reinstates the original budget under-accounting to establish literal numerical behavior. Keep the accurately accounted candidate for production.

## Expected modeled-six reference choices

| Budget MB | Literal1b8fc3f | Existing corrected-accounting protocol |
|---:|---|---|
|19000|B24 / HU cache off|B23 / HU cache on|
|21000|B27 / HU cache on|B27 / HU cache off|
|23000|B31 / HU cache off|B30 / HU cache on|

Do not call the corrected protocol literal-deployed parity. Preserve its binaries, results and rules. Literal source prints its selected CDF batch but predates the optimized JSON layout diagnostic. HU mode is established by original source arithmetic; direct field observation requires a separately identified diagnostic/test build. Do not silently add logging and continue claiming byte-exact original GPU source.

## Concrete validation sequence for the parent

1. Finish/leave the current frozen queue intact. Archive the candidate source identity, then apply this control only when no benchmark compilation is in flight. Verify git diff names exactly the two preflop GPU files; confirm CPU and frozen example hashes against the manifest. Build the same release GPU examples with the existing toolchain/features. Archive literal control binaries with explicit source identity before restoring the candidate. No postflop/app/server action is needed.
2. Run the literal original GPU tests that still exist in its module: `reach_mass_preserves_original_addition_tree`, `compact_reach_has_unique_writers_and_fits_smaller_budget`, `captured_learning_matches_eager_and_preserves_stop`, `cached_evaluation_matches_full_sweeps_exactly`, and `coupled_terminal_matches_cpu_across_particle_batches`. Use the installed original module filter (for example cargo test -p solver --release --features gpu preflop::gpu::tests -- --test-threads=1). New optimized-only tests are intentionally absent from the literal source.
3. Run the frozen `preflop_budget_control INPUT.gtop 6 BUDGET_MB` independently at19000,21000,23000 using the same frozen native modeled input, equity cache and REALIZATION_FIT as its paired candidate. Retain the existing guard/resource policy. Its fixed output is `target/research-budget-control-roundtrip-BUDGET_MB.gtop`; archive that completed file under a distinct literal identity before a paired run can overwrite it. Do not overwrite original evidence or use unlike iteration counts after a guard fires.
4. Run the accurately accounted deployed-compatible candidate at those same budgets/inputs, preserving full outputs and expected B/cache table. Compare each pair with frozen `preflop_compare_saved ORIGINAL.gtop CANDIDATE.gtop EXISTING_EQ_CACHE`. Require raw arena and all-node effective-policy identity for a literal compatibility claim, including the previously divergent deep low-reach nodes. Check exact profile/lock/config/calibration provenance; identical root gaps or small weighted error is insufficient.
5. Repeat bounded all-solver and modeled/frozen/point-lock controls already in the frozen suite. The literal source intentionally fails the *new* forced-memory rejection behavior, so that safety test belongs on the optimized candidate, not a retroactive pass requirement for the defective control.
6. Add a separate literal convergence pair with unchanged `preflop_convergence_control INPUT.gtop BUDGET_MB ITERLIMIT TARGET_GAP_BB CHECKEVERY OUTPUT.gtop`; use the same already-frozen target/cadence/limit and REALIZATION_FIT. Output must be a new file inside target/research-convergence. Do not replace the completed corrected-accounting comparison or alter its stopping rules.

Literal23GB may be slow or fail because its reported need excludes414.3MB of forced storage; it is not permission to raise the budget, lower the target, reduce particles, or ignore a guard. Record incomplete controls as such. A modified diagnostic B31/cache-off control can supplement arithmetic investigation, but must be identified separately from a literal1b8fc3f run.

No builds, GPU executions, worktree edits, server actions, or benchmark/protocol changes were made while preparing this proposal.
