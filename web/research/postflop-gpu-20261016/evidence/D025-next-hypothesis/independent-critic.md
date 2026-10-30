# D025 independent source critique

Verdict: **PASS for a bounded candidate implementation**, conditional on retaining the proposed invalidation and graph-selection rules. No blocking dependency, current ownership, or graph-capture hole was found. This is source review, not runtime proof or performance acceptance. No production edits, builds, tests, CUDA compilation, GPU work, or server operations were performed.

The accepted E015 source and D025 copies were independently byte/hash checked before this review. Source references below are to those copied files, not a future candidate.

## Dependence and zero-count proof

E015's second p1 down recomputes reach0 after p0 updates regrets0. Its subsequent upward pass receives only regrets1/strategy1 as writable learning buffers (mod.rs:975-978), while reach buffers are read-only. The next ordinary p0 down would therefore recompute reach0 from unchanged roots0, regrets0, locks and tree metadata. Discount and public iteration/algo values do not enter down_action/down_chance. This makes the proposed cross-pair reuse mathematically plausible without changing addition order or precision.

The nh0=0 variant is symmetric to E015's nh1=0 path: copy_root accesses player0 only under k<nh0; down_action's actor0 regret, lock-sigma, child-reach and parent-reach accesses occur inside i<nh_a; down_chance's player0 dereferences occur inside i<nh0 (kernels.cu:16-24,28-94,124-140). There is no division by a hand count or barrier in those kernels. Zero-scaled reach pointer arithmetic produces the valid allocation base without dereferencing it. Real allocations, upward hand counts and player1 downward counts must remain intact. Distinct reach-owner slots (plan.rs:412-426) are not recycled CFV scratch.

## Lifecycle and graph findings

- Consume the prior validity before any fallible ordinary/profiled iteration work; preserve that consumed value for selecting p0 full versus p0 reuse. Mark true only after a complete ordered p0/p1 pair queues successfully. Warm/new constructors start false even when solver.iteration is nonzero.
- Three fixed graph variants are sound: full-p0, reuse0-p0 and reuse1-p1. Capture itself executes no training update and must never establish validity. A first warm call may capture immediately; it must execute full-p0 then p1. Capturing and selecting graph variants are separate decisions. Lock invalidation must drop all variants together, and both ordinary and profiled callers must obey the same state transitions.
- Clearing only inside eval_down is insufficient: mod.rs:500 directly replays a cached evaluation graph. Invalidate at exploitability entry as well as direct eval_down, as the draft explicitly requires. Evaluation graph capture can itself call invalidating host code; do not let that disturb a saved training-mode decision inside unrelated graph construction.
- Generic standalone sweep must clear and never re-enable the flag. Standalone p0 is especially important: its upward pass changes regrets0 after its own down computation. A valid prior cache must not survive that call. Standalone p1 also clears conservatively.
- The public continuation bridge uploads roots before invoking generic sweep (mod.rs:178-193). Clear before the first upload so an early/partial upload error cannot leave valid=true. Pure argument rejection before mutation need not preserve validity for performance.
- update_locks (mod.rs:1046 onward) must clear before its first fallible wait/upload; existing graph-pointer invalidation remains necessary. This is independent of whether the changed lock belongs to player0 or player1.
- Successful sync_to_cpu, sync_strategy and synchronize only read device state or wait; no mathematical invalidation is needed. Clearing cache validity after an error does **not** make a partially applied CFR iteration recoverable. In particular, an asynchronous CUDA error observed during readback/wait must not be treated as healthy evidence for continuing cached iteration. The candidate should not add isolated-sweep retry semantics.

## Direct mutation and ownership audit

Direct mutations outside mod.rs were inspected, including paths preceding the bridge:

- continuation.rs:25-26 privately owns a freshly constructed GpuSolver; constructors at37-65 validate fresh unlocked state. Its public sweep at121-135 calls the full generic bridge, then project/transport. The latter mutate learning arenas at139-168, but cannot inherit a true ordinary-pair cache because this wrapper never calls iterate/iterate_profiled and exposes no inner solver accessor.
- continuation_paging.rs:28-29 privately owns a fresh solver created at69-85. take/swap at36-55 replace reach/learning buffers; sweep at102-111 swaps and uploads before the bridge. Those mutations occur while validity remains false by construction and ownership, including upload failures before the bridge. Existing poisoning/synchronization on failures remains relevant.
- continuation_storage.rs:145-148 privately owns the symmetric wrapper. Constructor164 onward creates that wrapper; sweep314-342 swaps, imports/zeros/restores arenas and transports canonical values before the generic bridge. copy_canonical at286-297 can write learning buffers. This wrapper likewise has no ordinary paired iteration path, so validity cannot become true through public APIs. Checkpoint import changes parked state, subsequently consumed by the full bridge.
- Private descendant tests do directly replace/upload buffers (continuation_replay_tests, host/SSD paging tests and E015's raw-proof test). Any new test that first establishes valid=true and then mutates those private buffers must explicitly invalidate before expecting an ordinary iteration. Existing privacy is an implementation invariant to preserve; a future inner-solver accessor or ordinary iteration API would require invalidation at every swap/import/project site.

A repository search found no production wrapper path that takes an already-used ordinary GpuSolver and injects it into these wrappers. Thus a mod.rs-only candidate is feasible under the current ownership rules; explicit wrapper-file edits are not required merely to clear a flag that can never be true there.

## Required next evidence

Require raw reach0 bits to match across prior p1 down/up and the next legacy full p0 down. Extend E015's raw-device lifecycle comparison to inspect validity and graph choice after eager/captured evaluation, each lock update, first warm capture, consecutive pairs, mixed profiled/ordinary calls, and standalone p0/p1 with changed roots. Continue treating poisoned/workspace controls as simulated unless actual paging is run. Exercise early error exits without claiming partial-update recovery. Freeze the evaluator, include extra graph setup in complete-cycle timing, and retain the per-fixture regression gate. Structural loop counts and the prior E015 result justify an experiment, not an expected speedup.

## Verified source identities

- `source/mod.rs` SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`.
- `source/kernels.cu` SHA256 `8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0`.
- `source/plan.rs` SHA256 `aca00f163db77af01960cd55cb5484226f25c7c58bae325d4c50ebc44672b680`.
- `source/continuation.rs` SHA256 `cfee0f3f84fa0d2bc7d5ad749b76eadbb9884091fe3483b9e25cf9bbe051bc00`.
- `source/continuation_paging.rs` SHA256 `6a7c5241a6c1b600f32376d58267f45ccb8f08365858d1fa5d2b8fb9d072b5ec`.
- `source/continuation_storage.rs` SHA256 `a06d496233ef7dba7f9cf05db5658c872e2fd50a8f013e72035a9c39c14727cc`.
