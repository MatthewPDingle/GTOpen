# Native saved-state numerical comparator (proposal)

Files: `preflop_compare_saved.rs` and `comparator.patch` (adds the automatically discovered Cargo example at `crates/solver/examples/preflop_compare_saved.rs`). `git apply --check --ignore-space-change comparator.patch` passes. No build, comparison run, GPU work, active source edit, or input modification performed here.

## Purpose and use

Compare original and optimized modeled saved states when a memory-accounting change selects CDF batch 30 versus 32 at the same 23 GB budget. Different particle accumulation grouping can cause floating-point differences; a root hash alone cannot describe their extent. This utility reports the differences without accepting them, hiding them, or inventing a numerical tolerance.

After applying/building in the isolated checkout:

```
cargo test -p solver --example preflop_compare_saved
cargo run --release -p solver --example preflop_compare_saved -- ORIGINAL.gtop CANDIDATE.gtop cache/preflop_eq169.bin
```

Redirect stdout to a new report JSON. Use stderr for errors. Do not redirect onto either input. Run each benchmark to its native save first, then compare stable closed files. No solves, iterations, terminal evaluations or model regeneration are invoked by the comparator. Native constructors rebuild tree structure and initialize their normal shared deck/cache objects; these are not accuracy or performance trials.

## Comparability and coverage

- Requires the same native magic and full JSON header, including config, iteration, payoff model, seat models/frozen flags, point locks, hero/pre-hero state and backup metadata. Point locks are sorted by node first, since HashMap serialization order is immaterial. An absent V1 payoff label receives the native legacy default; V2 must explicitly identify its payoff model. Unknown differences cause a comparability error rather than a misleading numeric summary.
- Validates every native arena length and file extent, including optional hero backup arenas; rejects truncated or unexpected trailing bytes.
- Streams every regret and strategy-sum value from both files. Reports finite/nonfinite and negative counts (negative regrets are valid), numeric/bit equality, absolute max/mean/RMS, signed mean, symmetric relative max, ordered-f32 ULP max and absolute-difference histogram.
- Loads both states through `PreflopSolver::load_game` and visits every action node, checking child/arena layout. Compares both the raw arena-normalized strategy and effective `average_strategy`, which applies native point locks and model/adaptive policies.
- Root-only comparison is insufficient: node/hand/action entries are all compared. Largest effective differences include node, path indices, actor, hand label, action label, arena index, both strategy masses and both current reaching masses.

## Tiny/unreached distinctions

Two independent classifications are reported, and neither represents a sample-count confidence interval:

1. **Accumulated strategy mass:** exact zero; positive mass at/below the existing native `1e-12` uniform-fallback boundary; then descriptive decades above it. A zero raw arena at a modeled/locked node can still yield a valid nonuniform effective policy. The utility therefore reports raw-normalized and effective policies separately.
2. **Current factorized reaching mass:** propagated through both entire trees using the same f32 actor reach multiplications and opponent mass sums as the solver. Exact zero is distinct from tiny positive decades. These values include f32 underflow and the solver's factorized/card-removal approximation, so they are not proof of mathematical impossibility or exact joint poker probabilities.

For both classifications, original-to-candidate bin transitions are preserved. The report also includes unweighted per-class total variation, and decision-reach-weighted total variation using each state as the weighting reference. Summing decision opportunities over all nodes is not exploitability; do not present that number as an EV loss.

All bins are descriptive scales. The `1e-12` boundary is copied from existing `average_strategy`; every other boundary is only a labeled reporting decade. No acceptance threshold is assigned or loosened. Nonfinite values are counted separately and excluded from finite-error denominators; their presence must not be mistaken for a good mean error. Uniform fallback flags on top rows describe raw sums, not whether a forced policy is active.

## Memory and input preservation

The raw arena pass uses bounded chunks; it does not make `arena_snapshot` copies. The effective-policy pass holds two native solvers, plus depth-first path buffers and bounded aggregates. On the user's roughly 2.12 GB arena state, expect at least 4.24 GB for two arena sets plus both trees, optional hero backups and normal shared caches. Compared with loading two states and snapshotting both arenas, this avoids an additional approximately 4.24 GB of copies.

All saves are opened read-only. The existing equity cache is checked for exact format length and finite values before native `load_or_build` is used, ensuring that normal stable-input loading takes its read path. The tool never calls save_game, writes arenas, builds a replacement equity table or changes solver settings. Inputs must remain stable during the run; header equality and numerical output do not serve as a concurrent-file consistency protocol.

Full-policy comparison uses the comparator binary's current native policy routing for both saved states. Keep its source/model artifacts pinned, as with the benchmark. The saved arrays/headers remain original and unchanged.

## Required checks before interpreting a batch-30/32 report

1. Three included example unit tests cover native normalization fallback/tiny denominator amplification, signed zero/nonfinite/ULP accounting, and streaming/header lock-order canonicalization with unchanged test files.
2. Compare one real modeled save against itself. Require all raw and effective differences zero, exact coverage counts, no unexplained nonfinite values, and unchanged input hashes. This is a comparator correctness check, not a solver tolerance.
3. Compare the original and candidate same-iteration saves. Record the descriptive output alongside the actual batches, source commits, input/native-save hashes and benchmark manifests. Comparability errors must be resolved, never bypassed silently.
4. Interpret differences using the already-agreed fixed-state terminal parity and same-target time-to-accuracy gates. Even a small all-node strategy difference is not independently proof of retained solver correctness; conversely a large difference in an unreached/tiny-mass normalized row requires context rather than an automatically loosened cutoff.

No numerical acceptance recommendation is encoded in this proposal.
