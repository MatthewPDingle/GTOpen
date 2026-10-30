# D055 source scout: schedule independent fold-card sums by length

Recommendation: one bounded, low-confidence integer-scheduling experiment is source-feasible. Keep accepted E020 as its explicit base. This scout contains no candidate code, compiler/native/GPU execution or performance claim. It is independent of E029's result and does not tune or rescue that change.

Accepted `gpu/kernels.cu:163-169` assigns cards0..51 directly to threads0..51 in `up_fold`. Each thread sums one card's original ascending opponent-hand list and writes a distinct `s[card]`. The proposal is one fixed stable order: descending list length, then ascending card ID for ties. Only task-to-card selection changes. Keep the `+0` initializer, every within-card hand lookup/addition, `s[card]` destination, original thread-index total partials (`:170-173`), total reduction (`:175-179`), all barriers, amount expression and final outputs (`:181-189`) unchanged. No warp/scan rewrite or floating reassociation is proposed.

The minimal representation appends52 card IDs after the existing53 entries of each `d_fold_card_off[p]`. The first53 offsets and all `fold_card_idx` contents stay byte-identical; the new mapping is read from offsets[53..105]. `mod.rs:289-300` already constructs these tables before upload. This preserves the launch ABI and two existing allocations while adding416 immutable device bytes total. Both existing up_fold call sites already select the opponent's card table. A future implementation must validate a complete52-card permutation, explicitly count105u32 in planned capacity (currently53 at `continuation_capacity.rs:37`), retain observed slice-length accounting, and add the extra416bytes once to exact admission and CPU-only public estimate. Mutable workspace, graph ownership, locks, reaches, arenas and save formats remain unchanged.

## Structural work proxy

`card-work-proxy.json` preserves all derived root hand lists,52 card lengths and the single proposed permutation. The frozen D037 range parser was reused only for pure range expansion; configs match immutable E020C1, and hand counts match D033 anchors. These are derived hand lists, not a native plan dump. Pair order does not affect the number of hands containing each card.

| Fixture / opponent player | Current warp maxima | Proposed warp maxima | Sum |
|---|---|---|---|
| Rainbow /0 |16,19|19,8|35 to27|
| Rainbow /1 |13,32|32,6|45 to38|
| Two-tone /0 |16,19|19,8|35 to27|
| Two-tone /1 |13,32|32,7|45 to39|
| River /0 |16,19|19,7|35 to26|
| River /1 |13,30|30,5|43 to35|
| Synthetic full-range turn |47,47|47,47|94 to94|

Warp maxima are a simple loop-divergence proxy, not native instructions, cycles, transactions, CTA latency or a complete-cycle bound. The longest single-card loop and the total number of scalar additions remain unchanged. NVIDIA's [CUDA12.9 Best Practices Guide, Control Flow](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-best-practices-guide/index.html#branching-and-divergence) explains why divergent paths within a warp can affect throughput; it does not establish that this permutation improves this kernel. Modern scheduling and predication still require inspection and measurement.

## Evidence, costs and limits

D033's dense-event trace reported a paired final-replay up_fold median3.457408ms, but its outer20-iteration device batches were perturbed by68.91-72.12%. This is only weak hotspot guidance. D045's lower-perturbation selected training launches did not measure up_fold. Neither diagnostic isolates these card loops or establishes2% complete-cycle headroom.

Reassignment keeps the same shared-reach loads but can change bank conflicts, per-warp latency hiding, compiler register use and overlap with other warps. It adds one mapping lookup per card task plus host sorting/upload bytes. Full-range work has no proxy improvement and is a useful adverse control; constructor-inclusive river timing still matters. No speed prediction is justified.

Scoped history found no same postflop card-task permutation in the current postflop ledger or searched autoresearch Markdown. E019 changed the fold reduction tail and failed the2% gate (0.7172% observed gain), so a smaller source cost does not ensure qualification. E020 is integer showdown-position caching; E021-29 change different staging, prefix, dispatcher, layout, normalization or zeroing mechanisms. None is composed here. This is a scoped search, not an exhaustive proof of historical novelty. The inspected mutable ledger bytes are preserved under `references/experiments.md`.

The scout also declines two weak directions: repeated fold-statistic reuse has no established useful duplicate reach-owner census, and root-seed removal overlaps E015/E016. Pair-graph fusion has no supporting headroom: D033's dense trace recorded0.000576ms inter-graph gaps, although that perturbed observation is not a native bound. No variant for either direction is proposed.

Next decision: if root selects this single hypothesis, reuse existing compiler inspection and complete actual-up_fold poisoned-output controls to check permutation identity, both players, zero/empty/full/asymmetric card lists, original sums/output bits and unchanged inputs. Then retain the fixed complete-cycle gate and existing broad/holdout requirements. Do not build another profiling framework, choose alternate sort orders after outcomes, or claim performance from this count table. None of that execution is authorized or performed by this scout.
