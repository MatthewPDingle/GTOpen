# D025: retain current player0 reaches between consecutive training pairs

**Recommendation:** test one host-only extension of E015: skip player0 reach propagation in the first sweep of a subsequent ordinary iteration, only while an explicit validity flag proves its inputs unchanged. This is a source-only design. No candidate implementation, build, GPU execution, server mutation or speed claim is included.

The parent selected the fully qualified E015 implementation as the basis. `manifest.json` preserves its exact current source (`mod.rs` SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`) and evidence identities; `source/` contains fetchable copies. Existing comparison-helper status fields are preserved as originally written and do not represent a new acceptance decision by this audit.

## Why this is the next bounded candidate

E015's repeated comparison reports a 3.9827984% complete-cycle improvement over E004. Independent review found solve-span improvements in all nine paired fixture comparisons and mean paired suite saving of 540.4788 ms in solve versus 549.6834 ms in total. That supports investigating the same duplicated reach work further; it does not prove an individual kernel cause or predict another gain.

D020's older, synchronized E004 profiles rank down_action third on both flops: median host spans 5.5964 ms rainbow and 4.0396 ms two-tone, with 26 launches per profiled pair. The larger action-up/showdown spans have already motivated unsuccessful specialization/register experiments. D020 is not an E015 device-time profile: eager construction and per-launch waits distort the spans, and E015 already removes some down work. Do not assign an ordinary solve percentage from them.

This proposal removes another independent recomputation without changing arithmetic, launch count, kernel source, plans, precision, device payload buffers, or stopping criteria. It avoids the previously rejected direct arity kernels, launch bounds, and host readback approaches. It does add one captured graph variant and host invalidation bookkeeping, whose costs must remain inside the complete-cycle measurement.

## Source proof

References use the copied E015 source.

1. `mod.rs:393–434` queues the ordinary p0 then p1 sweeps on one stream. E015 leaves p1 down's player0 propagation full (`mod.rs:763–845`), using regrets0 after the immediately preceding p0 update.
2. `kernels.cu:28–94` propagates each actor's reaches from only that actor's regrets, root/parent reach, locks and immutable tree data. Chance propagation (`124–140`) is likewise independent per player.
3. The p1 upward update receives only regrets1/strategy1 as writable learning buffers (`mod.rs:975–978`; `kernels.cu:328–403`). It reads reaches and never modifies regrets0, roots0, locks or reach0. The final player0 reaches therefore remain the exact current regret-matching reaches at the start of the next ordinary p0 sweep.
4. Discount and iteration changes do not enter the down kernels; the next discount upload does not invalidate player0 reaches. No floating-point regrouping is proposed. Saved bit patterns, including signed zeros and nonfinite results if present, are reused exactly. Runtime validation remains required.
5. `plan.rs:412–426` retains distinct reach-owner storage, separate from parity-reused CFV scratch. Later upward work cannot overwrite those reaches through a scratch alias.
6. A zero `down_nh0` is symmetric to D023's proved zero `down_nh1`: copy_root's player0 loop is guarded by `k<nh0`; actor0 down_action has no hand iterations, divisions by hand count or barriers; chance's player0 accesses lie inside `i<nh0`. Existing valid allocations/pointers remain. The player1 loops retain their true count. All upward counts and real `self.nh` remain unchanged.

## Minimal implementation boundary

Keep the change in `gpu/mod.rs` if implementation confirms the ownership audit below. Add a private `player0_reach_current` bool, initialized false, and an explicit down-reuse mode (`None`, `Player0`, `Player1`) or equivalent mutually exclusive flags. A debug assertion should permit player0 reuse only for p0, and player1 reuse only for p1. Generic standalone `sweep` always uses `None`.

Ordinary `iterate` and `iterate_profiled` consume the validity with `mem::replace(flag, false)` **before their first fallible operation**. They pass player0 reuse only when the consumed flag was true; p1 retains E015's player1 reuse. Set the flag true only after both ordered sweeps/graphs are queued successfully. The flag denotes a valid ordered-stream result, not completion; no extra wait is necessary. Any returned error leaves it false. Do not add isolated p1 retry/recovery.

False-on-error prevents stale reuse; it does not make a partially applied CUDA learning update mathematically recoverable. Neither that flag nor a readback/synchronize error authorizes continuing from a partially failed solver state. Preserve existing error handling and discard/reconstruct unusable state rather than advertising retry support.

Preserve graph replay by capturing three variants: full-p0, reuse-player0-p0, reuse-player1-p1. Each iteration launches exactly one p0 variant and then p1. Capture is not execution, so never mark validity true while merely constructing a graph. Warm construction can capture on its first call and must choose full-p0. The existing lock-driven `graphs=None` invalidation should discard all three variants together. No runtime kernel compilation or function-load changes are needed.

Only three downward `nh0` argument sites change. Keep `nh_p`, `nh_o`, `nh_max`, upward dispatch, evaluation arithmetic, actual reach allocation sizes, 128-thread blocks and graph launch ordering intact.

## Required invalidation and compatibility rules

| Boundary | Required behavior |
|---|---|
| New/warm GPU construction | Start false, even if iteration is nonzero. |
| `exploitability` entry (`456`) | Clear before eager or captured evaluation. **Clearing only in eval_down is insufficient:** later evaluation graph replay does not call it on the host. |
| Direct `eval_down` (`545`) | Clear before queuing; internal tests/private callsites may bypass public exploitability. |
| Generic `sweep` (`759`) | Clear before full propagation and never re-enable it. A standalone p0 update makes reach0 stale. |
| Continuation bridge (`178–193`) | Clear before the first root upload, not only when sweep is reached: a partial upload error must not retain valid=true. |
| `update_locks` (`1046`) | Clear before its first wait/upload, including error paths; graph invalidation remains intact. |
| Sync/readback/synchronize | Successful operations only read device learning state or wait. They do not require invalidation. Do not interpret an ignored asynchronous CUDA failure as safely reusable state. |
| Profiled paired iteration | Same consume/restore logic as ordinary iterate; mixed eager/profiled/graph calls must agree. |

Paged/stored/symmetric continuation wrappers construct a fresh, privately held GpuSolver and call the generic continuation bridge, not ordinary iterate. They therefore keep this flag false throughout workspace swaps, projection/transport and uploads; a failure before reaching the bridge cannot turn it true. See `continuation_paging.rs:69–128`, `continuation_storage.rs:301–359`, `continuation.rs:121–168`. Do not grant these wrappers reuse based on coincidentally alternating players. If any future API exposes their inner solver to ordinary iteration, the buffer/learning mutation sites require explicit invalidation. This is an ownership restriction to preserve and test, not a reason to optimize continuation.

Public `algo` and `iteration` changes alone do not change regret-matching inputs; all original full-up arithmetic remains in force. Root/learning/lock device buffers are private. Direct mutation in GPU internal tests must either call an invalidating entrypoint or explicitly clear validity before testing subsequent ordinary iterations.

## Complete-cycle plausibility and limits

`work-counts.json` derives counts from D023's unchanged-plan census. With frozen checks every 20 iterations, 19 of 20 p0 sweeps are eligible; the first sweep after each check remains full. At unchanged stops this is 190/200 flop and 57/60 river iterations.

| Fixture | E015 down-action hand visits/iteration | Avoidable visits per eligible iteration | Average reduction versus E015 at check_every=20 |
|---|---:|---:|---:|
| rainbow | 220,593,222 | 70,623,857 | 30.4147% |
| two-tone | 134,713,588 | 43,140,954 | 30.4230% |
| river | 4,476 | 1,398 | 29.6716% |

Flop chance hand loops fall by approximately 29.31% versus E015 under the same schedule. These are hand-loop counts, not elapsed-time savings, action-weighted FLOPs, traffic, or a 30% solver claim. CTAs still execute metadata prologues and the same launches remain. The avoided work is comparable in scale to E015's successful removal, so the 2% complete-cycle gate is plausible enough to test; it is not guaranteed. Extra graph capture/instantiation can erase a small-tree benefit, and the per-fixture regression guard still applies. No constructor, readback or destructor boundary shift is intended.

The frozen optional profiled iteration runs immediately after evaluation, so its first p0 sweep would intentionally be full. That one sample cannot characterize steady reuse; do not change the frozen evaluator to manufacture a favorable profile. If needed, a separate explicitly excluded diagnostic can compare invalidated and steady paths.

## Minimum proof and qualification obligations

- Independently capture raw reach0 after old p1 down, after p1 up, and after the next legacy full p0 down; require bit identity. Compare raw learning/reach arrays against unchanged full-sweep reference iterations before compression. Do not compare uninitialized CFV scratch.
- Extend E015's bounded DCFR/CFR+, F32/compressed, full/compact and action-menu controls. Assert actual validity transitions, selected graph variants, unchanged first eager iteration, capture and replay, and consecutive optimized iterations.
- After eager and captured evaluation, after each actor's lock update, after warm reconstruction, and after standalone p0 **and p1** with changed roots, require the next p0 to be full and exact. Test mixed profiled/ordinary calls. A single standalone p0 is a crucial new invalidation case because it changes regrets0 after computing reaches.
- Exercise simulated workspace/learning replacement only through explicit invalidation, and preserve the existing feature-gated continuation, paging and storage control suites. Check errors before/after root uploads leave validity false; no GPU work must be retried from a lone reused sweep.
- Reuse the frozen complete-cycle benchmark and serialized alternating cohorts against accepted E015. Keep all repetitions, exact fingerprints/exploitability/iterations, provenance and new graph setup cost. Require the same aggregate and repeated fixture-regression gates before broader F32/state/menu/resume qualification. Resource/source reasoning is not acceptance.

Historical scope: the preserved D023 search found prior reach storage compaction and fixed-strategy evaluation reuse, not this cross-iteration training cache. E015 explicitly avoided cross-iteration state. This proposal is a distinct extension with additional invalidation obligations; no claim is made about unsearched branches.
