# Static live-terminal worklists

Proposal only; no build, GPU execution or source-checkout modifications by the
proposal agent. Source hashes/revision are in `base.txt`. Apply `combined.patch`
or `implementation.patch` then `tests.patch`; do not apply both alternatives.

## Scope

Keep the existing global `d_mw_terms`, `d_mw_prob` and prepare kernels. Build a
flat immutable list of **indices into that global term array**, with one span
per traverser. Include a term exactly when that traverser is live; preserve
original term order within the span. All live zero-reach terminals are included.

The coupled terminal launch uses the selected span length rather than all
multiway terms. Its first operations map local block index to original term
index, then use that index for both `terms[index]` and `terminal_prob[index]`.
The latter is essential: using the local index for probability would silently
read another terminal's counterfactual reach.

No per-hand, particle, opponent, CDF, quadrature or accumulation loop changes.
No altered launch width (still 192), templates, base-address hoisting, floating
arithmetic, precision or sample count. The old folded-seat early return remains
as a guard and for the low-memory identity-index fallback. Ordinary terminal
launches remain unchanged and continue writing every folded traverser's value.

## Counts and memory

For `T` global multiway terminals, `N` seats, and terminal live masks `L[t]`:

- Old blocks per complete sweep and particle batch: `N*T`.
- New blocks: `sum(popcount(L[t]))`.
- New GPU bytes: `4*sum(popcount(L[t]))`; host spans are `N*8` bytes.
- Removed blocks: `sum(N-popcount(L[t]))`.

The eight-seat log has 805,640 **total** terminals, so new index bytes are
bounded above by 25,780,480 bytes (25.78 MB), and actual allocation is smaller:
fold-win and heads-up terminals are absent from `T`. This is a bound, not the
measured multiway count. Constructor output reports global T, actual per-seat
counts and allocated MB to obtain exact data during the parent's next run.
Every 3-live terminal removes five of its eight blocks per batch. A removed
block used to return almost immediately, so launch-count reduction is not a
proportional runtime prediction. Each remaining block gains one u32 work read.

Budgeting is optional-performance-only. First compute the previous CDF plan;
enable worklists only if their bytes leave its batch and normalization mode
unchanged. Retain any HU equity cache that fitted before adding the list.
Otherwise use an identity-index kernel path with a dummy one-u32 list. This
preserves minimum fit and prevents smaller batches or mode/cache differences
from confounding the experiment. Preferred-memory estimates include the list.

## Tests and validation

`terminal_work_budget_keeps_batch_and_normalization_mode` covers direct minimum,
normalized minimum, maximum preferred batch boundaries, and checked underflow.

`coupled_live_terminal_work_matches_identity_indexing` compares indexed versus
identity indexing with identical allocated caches. It verifies every span is
exactly the ordered live subset, then compares full regret/strategy/gap/EV bits
through three iterations and evaluation graph replay. It also isolates two
terminals where target original index 1 becomes work index 0. That catches an
incorrect local probability lookup. It tests zero own/live/folded opponent
reach, positive-zero-positive transitions, gated and ungated calls, folded
traverser ordinary values, non-unit reaches and poisoned buffers at batch32/7.
All169 target values are checked against CPU terminal evaluation.

Existing isolated-terminal tests mutate `d_mw_terms`; the test patch rebuilds
their worklist and spans as well, preserving their zero/stale/direct-boundary
coverage. Apply this test patch with the implementation, not later.

Suggested parent runs (on an idle GPU):

```powershell
cargo test --release -p solver --features gpu --lib terminal_work_budget -- --test-threads=1
cargo test --release -p solver --features gpu --lib coupled_live_terminal_work -- --test-threads=1 --nocapture
cargo test --release -p solver --features gpu --lib preflop::gpu::tests:: -- --test-threads=1
cargo test --release -p solver --features gpu --lib coupled_minimum_budget_direct_and_normalized_paths_match -- --ignored --test-threads=1 --nocapture
```

Then use the frozen eight-seat benchmark at its existing iteration count and
check exact arena hash/gaps/EV, identical batch/normalization/HU-cache choices,
and new list counts. Include 3/6/7-seat controls because fewer folded seats may
leave little benefit while adding an indirection. Repeat after an initial win.
Supplementary phase profiling can confirm the coupled-terminal phase changed
while CDF stayed stable, but retain/reject on production graph timings.
