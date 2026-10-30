# D033: captured-graph device-event diagnostic (prospective, source only)

Recommend a temporary ignored lib-test module that clones the actual accepted E015 CUDA graphs and inserts timing events between their existing kernel nodes. This avoids D029's synchronization after each eager launch and does not need an external profiler or elevation. It measures **event-perturbed device intervals**, not uninstrumented kernel execution shares or a performance qualification score. No harness has been implemented, built or executed for this design.

## Approved base and temporary scope

The inspected checkout is restored E015: `gpu/mod.rs` SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`. E016, E017 and E018 are excluded. The source manifest records the current production, evaluator, fixture and dependency hashes; sealed binaries and prior evidence remain untouched.

After root authorization, the entire source change should be an appended `#[cfg(test)] mod graph_event_diagnostic;` declaration in `crates/solver/src/gpu/mod.rs` and a new `crates/solver/src/gpu/graph_event_diagnostic.rs`. A descendant module can access private solver graph/buffer fields without changing production methods. Archive full base/candidate files, patch, build command, hashes and binary first; strip the exact appended declaration to prove byte-identical E015 recovery. Restore both paths after the diagnostic. The evaluator and control tests are never modified. A GPU-only release lib test is sufficient; no new features or Cargo dependencies are intended.

## Implementable API path

The project uses cudarc 0.19.7 with dynamic loading and `cuda-12060`. Its `CudaGraph::cu_graph()` and `cu_graph_exec()` expose borrowed handles; they must never be destroyed by diagnostic code. Clone via `cuGraphClone`, map originals with `cuGraphNodeFindInClone`, enumerate with `cuGraphGetNodes`/`cuGraphGetEdges`, inspect node types and `cuGraphKernelNodeGetParams`, and use `cuFuncGetName` for stable kernel labels. Raw bindings exist in the installed dependency. Cudarc's graph wrapper fields are private, so keep diagnostic graph/exec owners separate; do not manufacture a wrapper or replace the solver's graphs.

Create events with `new_event(Some(CU_EVENT_DEFAULT))`; `new_event(None)` disables timing. The ordinary safe `CudaEvent::record` is suitable for outer stream brackets, not for explicit captured nodes. For inner boundaries use `cuGraphAddEventRecordNode`; instantiate with the same `AUTO_FREE_ON_LAUNCH` flag used by E015 and upload with `cuGraphUpload`. Bind the owning context before raw calls. A future implementation must check every return code and report unsupported symbols/operations as invalid diagnostics.

Official CUDA event documentation specifies timing-enabled events, replay record overwrite semantics and approximately 0.5 microsecond elapsed-time resolution. Events can include intervening scheduled work. `cuEventRecordWithFlags(..., CU_EVENT_RECORD_EXTERNAL)` is a valid alternative during capture but is not needed for the clone route. [CUDA 12.6.3 events](https://docs.nvidia.com/cuda/archive/12.6.3/cuda-driver-api/group__CUDA__EVENT.html)

## Preserve graph identity and order

At iteration 140, synchronize and inspect each of the two original graphs. Require one nonempty, kernel-only, single-stream dependency chain: one root, one leaf, all nodes visited once, no branches/child graphs/memcpy/host/event/allocation nodes or nondefault edge dependencies. Reject unexpected topology; do not impose a serial order on a different graph. `cuGraphGetNodes` enumeration order is not execution order.

Clone each original graph. For N kernel nodes K0..K(N-1), allocate N+1 distinct timing events E0..EN. Add E0 -> K0; for 0<i<N add K(i-1) -> Ei -> Ki; add K(N-1) -> EN. Retain all original edges. These shared boundaries enforce the same original kernel ordering and prevent racing post/pre events. A mere side-branch event after a kernel is insufficient because the successor could otherwise run concurrently with the event.

Verify every original-to-clone node mapping, original edge, node type, function handle/name, grid, block and dynamic shared-memory value. Preserve the original kernel parameter payload by cloning; never call a kernel-parameter setter, reconstruct argument arrays, or dereference unknown parameter-storage sizes. Save a stable ordered descriptor (graph index/node ordinal/kernel name/launch dimensions) and original/projected topology in raw output. Pointer addresses may also be logged as run-local evidence but are not cross-run identities. The clone adds exactly N+1 event nodes and 2N boundary edges; original N-1 edges remain. No kernel body, argument, launch dimension, traversal order or math changes.

CUDA documents graph cloning/event nodes and warns that graph APIs, including inspection/clone, require external serialization. [CUDA 12.6.3 graphs](https://docs.nvidia.com/cuda/archive/12.6.3/cuda-driver-api/group__CUDA__GRAPH.html)

## Fixed prospective workload and schedule

Use only the registered rainbow compressed fixture (`Ks7h2d`, original `bench_spot.json`, rake0/cap3), default DCFR and suit isomorphism. Both arms use separate host stores and device buffers; sharing immutable Spot data is acceptable. Both receive identical discounts, weights, locks and exploitability checks at every multiple of20 from20 through200. Do not use `iterate_profiled`.

1. Advance both arms normally with `GpuSolver::iterate()` through140. Check all every20 exploit bits against the sealed native anchor. At140 compare the complete initialized raw learning/reach state, full CPU q/scales and exploit bits between arms.
2. Build the instrumented clones without replaying them. Upload native and cloned execs and synchronize outside all sample brackets. This prepares first-launch resources without an uncounted learning iteration.
3. Run three batches of20 paired iterations, ending160,180,200. Fixed arm order is native/instrumented, instrumented/native, native/instrumented. Never overlap arms. Each native batch uses ordinary `iterate()`; each instrumented iteration performs only the original iteration increment, `Discounts::for_iteration` and identical three-float upload followed by clone0 then clone1. Extract these host statements verbatim from the accepted source and mechanically verify their identity. Keep solver-owned ordinary graphs live and unchanged.
4. Put explicit timing-enabled stream events around each complete20-iteration batch, finish the batch, record its end and synchronize. Extract every inner event interval before the instrumented handles are replayed again. Repeated records overwrite prior timestamps: node intervals describe **only iteration160,180 or200**, never all20 iterations or their mean. No per-node or per-pair host wait is added. Store outer device interval and host wall duration separately.
5. Outside brackets, compare raw state before evaluation, call ordinary exploitability on both arms, verify saved native exploit bits, sync full stores and compare q/scales. Keep all three samples and report any unstable timing. Do not trim, rerun or select faster samples.
6. At200 reproduce the frozen evaluator's exact state-fingerprint helper (byte-extracted unchanged, import-only adaptation if required). Both arms must match the full `state_fingerprint` object, all four per-arena hashes, root strategy bits, iteration and exploit bits in `anchor-rainbow.json`. This object is equal in accepted E015C1 and original B038. Final fingerprint `65fb2853a11f3acc`, exploit bits `4595130701932466176`; no learned-state reset or approximate comparison.

## Admission, exactness and lifetime obligations

Before constructing two resident GPU solvers, calculate and disclose a conservative combined live device requirement using accepted plan/full-allocation estimates plus both graph/event sets and an explicit reserve; query available device bytes and reject insufficient capacity. Never silently switch to a smaller fixture, storage/layout or sequential restored-state design. Before large host allocation, likewise account for two CPU arenas (2 x1,386,321,040 bytes), immutable tree/plan copies, both pinned staging buffers and comparison scratch; report the formula and headroom. Confirm actual allocated lengths/layouts of both arms agree before measurement. Avoid claiming exact VRAM figures from a historical estimate.

Compare every raw f32 bit of both players' regrets, strategy sums and reaches, plus iteration and discounts. Use bounded views of at most1,048,576 floats per arm, at most8 MiB transient comparison storage, and compare words directly; streaming hashes are evidence, not a substitute for equality. Report checked lengths and first mismatches. Full CPU q words and scale bits are compared directly without duplicating full stores. Preserve input weights/locks and GPU source buffers; exclude unwritten/reused CFV scratch from indiscriminate raw comparisons, while validating actual exploitability output. Checkpoints140/160/180/200 are mandatory. These are instrumented-vs-native controls; the final preserved binary anchor supplies an independent historical check.

The cloned graphs refer to the instrumented solver's live buffers, module, context and stream. Own cloned execs/graphs/events in a diagnostic RAII owner whose borrow/lifetime cannot outlive that solver. Explicitly complete the stream before destruction; destroy execs, then cloned graphs, then events, then let the solver release its ordinary graphs/buffers. Keep original borrowed handles untouched. On error preserve evidence and stop; an error is not permission to retry a partially advanced solve. Best-effort cleanup must not mask the first CUDA failure. Raw graph APIs and all GPU operations are serialized under the existing root lock/preflight; no concurrent builds or GPU jobs, no server writes.

## Interpretation and alternatives

Report per-node and per-kernel-family sums/medians/ranges across exactly the three final-replay samples, their graph envelopes, and the between-graph gap. The sum of intervals is an event-perturbed partition, not pure kernel execution time. Keep seed/copy_root separate from down/up families. Require finite nonnegative times; near-resolution zeros are retained and labeled unresolved, not treated as proof that a kernel is free. Outer20-iteration envelopes include all event nodes plus normal discount upload/host scheduling gaps; native-vs-instrumented envelope ratios disclose perturbation. They are not end-to-end speedups and cannot update accepted-performance/deployment status.

| Alternative | Benefit | Limitation | Decision |
|---|---|---|---|
| Two outer events around original graphs | Smallest change, actual device envelope | Cannot rank individual kernels | Include as native control |
| Clone actual graph + shared event boundaries | Preserves original launches, exposes node intervals | Many event nodes alter scheduling; requires topology validation | Recommended bounded D033 |
| External event records while capturing traversal | Official API, same boundary concept | Requires instrumenting traversal/capture source and extra hook coverage | Reserve if clone API cannot work, separate revised design |
| Custom CUPTI activity tracing | Can expose original kernel activity | New SDK/loading/buffer/graph-correlation complexity; availability unproved | Defer |
| D029 synchronized eager timings | Existing preserved data | Host waits and non-captured path | Context only |

If dense instrumentation materially perturbs the envelope or fails topology/API checks, preserve that result as an invalid/limited diagnostic. A later sparse-event experiment needs its own fixed protocol; do not silently substitute it. No performance claim, acceptance gate, tuning or live deployment follows from D033.

## Evidence and next step

`protocol.json` freezes workload/schedule; `anchor-rainbow.json` preserves the exact historical target; `source-manifest.json` records current accepted inputs and API source hashes. Root must authorize implementation after the independent source/design critique. Later execution must capture source/archive/patch/binary/build manifest, graph descriptors/topology/event counts, all raw timing and exactness records, commands/environment, admission numbers, errors and cleanup status. Compare pre/post protected file hashes and restore test-only wiring. This design itself performed only source/report reads and official documentation lookup.
