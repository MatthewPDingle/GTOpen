# Bounded grouped-terminal experiment

Proposal only against5f4f42c. `groups.patch` includes gpu.rs changes and the O2/O3/O4 probe entries; apply it directly to that base, not on top of probe.patch. Full files and generator are included. Source-only patch check passed. No active source changes, compilation or hardware execution. Do not apply/measure until the register probe shows a meaningful resource reduction.

## Scope

Stable-sort the existing prepared-path mw_terms vector into four groups: O2, O3, O4, O5–8. The first three select their corresponding specialized probe kernels; the last uses the existing generic preferred kernel. Preserve node order within each group. Seven fully specialized entries are deliberately avoided in this bounded first experiment. The minimal-metadata path neither sorts its terms nor uses grouped dispatch; it keeps its existing generic kernel and single launch.

Host spans contain four (start,count) pairs. The same GPU term allocation and probability allocation are reused. Preparation computes probability at the reordered index. Each grouped launch passes matching CudaView offsets for terms and probability, so no new kernel offset argument or device index map is needed. The allocation/lifetime remains owned by the existing CudaSlice; views introduce no device allocation. Their underlying addresses remain stable during graph replay.

Sample batches remain the outer loop; nonempty groups launch in ascending order inside each batch. Every terminal therefore sees the exact same sample/quadrature/accumulation sequence as before. ValuePlan assigns terminal values distinct slots, so changed inter-terminal launch order has no shared floating-point output. CDF work/source maps, normalization, literal/corrected reference selection, B, cache mode and VRAM array counts remain unchanged. Host stable sorting may allocate transient CPU scratch; it is not a GPU worklist. Extra compiled kernel code/context resources are not asserted to consume zero driver memory.

The phase profiler still records one coupled-terminal phase boundary for the entire group sequence, preserving existing phase-event capacity/count expectations. Empty groups do not launch. `use_mw_groups` is true by default; a test toggles it before any capture to compare generic dispatch on identical reordered terms. It is not a user-facing mode or runtime automatic policy.

## Tests

- Pure stable grouping coverage/order and invalid-index/live-count tests.
- Six-seat fixture with all four groups: verify unique terminal value slots, compare generic/grouped full regret and strategy arenas, gaps and EVs through three iterations and learning/evaluation graph replay, and require identical B/cache/CDF/normalization sizes.
- Fixed non-unit reach terminal parity across batch32 and partial batch7, live-opponent zero and ungated recovery. Cache refresh is explicit after manual reach replacement. Existing own-zero/folded-zero/normalization/minimal tests continue to exercise the grouped preferred path.
- Three existing tests that replace d_mw_terms with one target now also reset grouped spans. Their probability indices remain0 as before.

## Parent integration gates

1. O2/O3/O4 register probe first; reject/defer if resources do not materially improve or local-memory spills appear.
2. Compile focused tests, then all existing GPU correctness gates, especially zero-reach and minimal fallback.
3. Benchmark the same chosen launch geometry. This proposal preserves5f4f42c's192-thread terminal width in BOTH grouped and generic launch lines; if the independent geometry sweep chooses another width, deliberately apply it to both paths before comparing. Do not mix geometry changes into an attributed grouping speed result.
4. Inspect exact native arena hashes and gaps/EVs on all-solver/model fixtures at the same literal batch/cache. Then repeat frozen throughput/time-to-accuracy gates for any retained candidate. Four extra launch groups may outweigh register savings, especially tiny groups or B1.
5. Defer this experiment if it would consume the reserved long final validation window. A register decrease is a hypothesis, not sufficient evidence to retain a new dispatcher.
