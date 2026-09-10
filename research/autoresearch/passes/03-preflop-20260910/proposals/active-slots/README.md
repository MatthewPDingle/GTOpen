# Active CDF slots proposal

This is an uncompiled, unbenchmarked proposal. Production sources and the user server were not changed.

Files:

- `active-slots.patch`: patch against the main checkout source snapshot identified by `baseline-sha256.json`.
- `gpu.rs` and `kernels.cu`: complete proposed source files, preserving UTF-8 and CRLF.
- `build_proposal.py`: reproducible proposal generator. It reads production sources, checks each replacement matches exactly once, and writes only this proposal directory.

Patch applicability was checked with `git apply --check --ignore-space-change`. Use that same whitespace flag when applying in an isolated checkout. Preserve any independently retained coupled-terminal launch change: this proposal leaves the existing `Self::cfg(self.mw_nterms)` launch untouched.

## Change

Before each traverser's particle-batch loop, clear one `u32` flag per CDF slot and launch one thread per multiway terminal. That thread computes the counterfactual probability using the original ascending seat loop, excluding only the traverser. Folded opponents still contribute to the probability. Positive-probability terminals atomically mark the live opponents' CDF slots. The CDF kernel skips unmarked slots. The terminal kernel reads its prepared probability instead of recomputing it for every particle batch.

The flags are reset for every call to `terminals`, including average-strategy gap evaluation. Both new launches have fixed dimensions and all state stays on the same stream, so the existing CUDA graph captures/replays remain applicable. No host synchronization or readback was added.

Extra allocation is `4 * (CDF slots + multiway terminals)` bytes. Constructor budget selection includes both arrays before choosing the particle batch size. The public estimate conservatively uses all node count for terminal storage, as it already did for the terminal index list.

## Correctness checks to run before retention

1. Existing `coupled_terminal_matches_cpu_across_particle_batches`: all 169 hands, 3/6/9 seats, batch sizes 32/7/1. Include eager and graph-replayed iterations plus gap evaluations.
2. Explicit zero-own-reach case: set one live traverser's reach block to all zero, keep every opponent mass positive, and verify that traverser's terminal values still match the ungated baseline. Checking only ordinary positive-reach cases would miss the most consequential pruning bug.
3. Explicit zero-opponent-reach case: keep traverser's reach positive, zero a live or folded opponent block, prefill `d_val` with nonzero sentinels, and verify the terminal's values are overwritten with zero on the first particle batch. Folded-opponent zero mass needs a 4+ seat terminal with at least three live players.
4. Stale-state sequence: positive opponent mass -> zero mass -> positive mass, with a different traverser between calls. Check results against CPU and ensure skipped CDF scratch is never consumed by a positive-probability terminal.
5. Underflow case: extremely small but positive opponent masses whose same ordered float product becomes zero. The implementation deliberately applies the old `prob <= 0` predicate rather than a new epsilon threshold.
6. Fully fixed/partly ruled policies: compare complete regret/strategy arenas, gap/EV results, and mode changes against the unmodified build. Measure the extra memory delta and a budget close to a particle-batch boundary.

## Performance interpretation

There is still one cheap block launch per statically listed CDF slot and terminal, but unneeded scans and repeated probability calculations disappear. Savings should be strongest when many branches have exactly zero counterfactual probability. Initially uniform trees may not benefit. The prepare kernel adds atomic writes for every live opponent of every positive terminal; contention on commonly shared slots is a reason to reject this version if measurements regress.

For attribution, compare the full proposal against a probability-only ablation (keep preparation/probability reuse but remove flag marking and CDF gating). Do not assume any gain is from pruning without measuring how many slots are actually skipped.

Large terminal grids currently use the adaptive `Self::cfg` 64-thread branch; only grids with fewer than 256 blocks use 256 threads. This proposal does not claim the baseline universally uses 256 threads.
