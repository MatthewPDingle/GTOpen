# D016: direct-three-action contingency design

Source-only audit. No candidate implementation, build, GPU execution, or speed measurement was performed. The current next path remains D015; this is a contingency. Source identities are preserved in `manifest.json`.

## Correction to E005 coverage

E005 already regrouped mixed action levels, not only homogeneous levels. `S:/GTOpen-research/postflop-gpu-20261016/runs/E005.patch:113-160` defines a 4096-node level threshold and stable-partitions each qualifying level into NA2 and remainder. The 5.84% rainbow figure in D001 describes homogeneous spans **without** regrouping; it is not E005 coverage.

Recalculation from the retained D001 per-level histograms, using E005's exact threshold:

| Fixture | All action nodes | E005 eligible NA2 nodes | Additional eligible NA3 nodes | NA2+NA3 node coverage | NA2+NA3 child-visit coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rainbow | 523,533 | 330,752 (63.1769%) | 154,056 (29.4262%) | 92.6031% | 96.5766% |
| Two-tone | 318,562 | 201,142 (63.1406%) | 93,749 (29.4288%) | 92.5694% | 96.5409% |
| River | 12 | 0 | 0 | 0% | 0% |

The eligible NA3 child-visit fractions are 39.7221% and 39.7229%. Per-iteration up-hand visit fractions equal node fractions because both traverser sweeps use the same node list. These are scheduled-work counts, not latency estimates.

E005 added 12 training-up launches per iteration to each flop fixture. NA2/NA3/remainder would add 22, or 10 more than E005. A NA3/remainder-only design would add 12. River does not meet the threshold.

D005 reported direct2 at 39 registers/0 local bytes versus the original dispatcher at 66 registers/64 local bytes per thread. Nonetheless E005's complete-cycle screen was 11042.9072 to 11052.9290 ms (0.0908% slower), with exact states, exploitability bits and stops on all three fixtures. This was one run per binary, not a statistically established regression. Its solve components improved only 0.71% rainbow and 0.44% two-tone. Evidence: `runs/D005/stdout.log`, `runs/E005/comparison-B010.json`. This lowers the priority of more entry-point specialization.

## Novel bounded candidate

The smallest distinct candidate is **direct3 only**, stable-partitioning levels >=4096 into NA3 then remainder, retaining 128 threads and the original dispatcher for everything else. Use one new `up_action_3` wrapper that calls the unchanged `up_action_impl<3>` with identical arguments and compiler flags. No arithmetic, discount, child order, or evaluation changes.

Current `crates/solver/src/gpu/kernels.cu:406-429` already dispatches to inline specializations for NA2/3/4. Novelty is a separate entry point and its resource allocation, not introducing compile-time NA3 arithmetic. A search of research Markdown found no retained direct3 experiment. E005 already covers the stable partition and direct2 architecture; E006/E007 separately tested whole-dispatcher launch bounds and failed the 2% gate. An NA2+NA3 design would partially repeat E005 rather than test an entirely new approach.

Before an evaluator run, a compiler-only diagnostic should compare direct3 registers, local-memory allocation, and occupancy against the retained dispatcher under identical options. Lower resources are necessary hypothesis evidence, not sufficient performance evidence; D005 demonstrated that distinction. No resource value for direct3 has been measured here.

D000's synchronization-instrumented up-action bucket was 9.4272 ms rainbow and 5.8627 ms two-tone per sampled iteration. The entire bucket is the broad diagnostic ceiling; the NA3-only share is unknown. Multiplying census fractions into those times would be an assumption, not a measured upper bound. Primary complete-cycle timing must include added plan partition work, entry-point compilation/loading, and graph/launch costs.

## Exactness and integration conditions

Source paths below are relative to `X:/Dev/GTOpen-gpu-research-20261016`.

- Reorder only independent nodes within one level. Action children are assigned level+1 (`plan.rs:154-165`); CFV output slots are distinct at the same level (`plan.rs:218-240`, invariant at `533-540`). Never move work across levels, where parity scratch slots are reused.
- Preserve node IDs, per-node offsets, children arrays and each node's ascending child loop. Arena offsets are assigned by tree-node enumeration (`plan.rs:368-392`), independent of action-list order. The unchanged action math is `kernels.cu:328-403`; its locked, traverser and opponent branches must remain intact.
- Keep aggregate action spans unchanged for down/evaluation (`mod.rs:563,725,781`); replace only training-up dispatch (`945-976`). Keep both sublaunches on the same stream, skip empty spans, and retain profile bucket 6 across both. Verify membership, stable order, full/disjoint coverage, threshold boundaries, all-3/no-3 levels, and arbitrary-menu remainder.
- Load the new function in the constructor (`mod.rs:309`) before graph capture (`400-423`). Resumed nonzero iteration state may capture immediately, so ordinary iteration-1 warmup cannot be the sole protection. Spans remain immutable during graph lifetime.
- Reuse the existing action-node device buffer. Add only host span metadata to plan/solver and retained-host capacity accounting (`continuation_capacity.rs:74`); do not count it as uploaded CUDA metadata. Paging/storage swaps keep their existing mutable buffers; per-solver immutable span metadata must not be swapped.
- Reordering CTAs can alter locality and runtime scheduling, and separate entry points can alter compiler code generation. Neither is a source-level sum-order change, but exact fingerprints, exploitability bits, stops, locks/resume and compact/isomorphic lifecycle checks remain required. The original down/evaluation kernels also see the reordered list, so their timing can change despite unchanged arithmetic.

Recommendation: retain direct3 as low-priority contingency, do not rerun E005 under the mistaken homogeneous-only premise, and prefer the current D015 path first.
