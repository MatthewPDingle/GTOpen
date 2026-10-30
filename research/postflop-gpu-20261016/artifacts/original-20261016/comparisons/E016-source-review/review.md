# E016 independent source review

**PASS: no actionable source defect found.** Reviewed frozen mod.rs SHA256 `0ca68663e9eeaf168b6769b36bd266d59ddc0c0d4838641ce0dd350c40d2abed` against accepted E015 SHA256 `7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a`. Working source matches its archive exactly. No production edits, builds, tests or GPU work were performed by this reviewer.

## Lifecycle and graph selection

- iterate (406-453) consumes prior validity before the first fallible operation. It selects full-p0 or reuse0-p0 using that saved value, then runs reuse1-p1, enabling validity only after the complete ordered pair queues. Returned errors leave false; this does not promise recovery from partial learning updates.
- Capture (417-441) creates full-p0, reuse0-p0 and reuse1-p1 in the order expected by graph indexes0/1/2. Capturing does not execute updates or enable validity. A fresh warm constructor starts false and may capture immediately, then executes full-p0 first. Both p0 variants are retained for later invalidation without rebuilding graphs.
- iterate_profiled (458-471) has the same consume/pair/enable behavior. Mixed graph/profiled calls use the current validity and do not rewrite the cached graph modes.
- exploitability invalidates at478 before eager evaluation or cached replay at522. Direct eval_down invalidates at568. Generic sweep clears at783 and always uses full propagation. The continuation bridge clears at192 before validation/root uploads; update_locks clears at1076 before waiting or uploading, and still drops all training/evaluation graphs.
- DownReachReuse makes player0/player1 reuse mutually exclusive and debug-asserts matching traversers. Exactly three downward nh0 arguments gain the new override. Training up dispatch, eval_up and readback blocks were independently byte-compared to E015 and are unchanged. Real upward counts, actual allocation sizes, kernel source and arithmetic are unchanged.

## Ownership and error scope

D025's independent ownership audit remains applicable. Private continuation, paged and stored wrappers construct fresh GpuSolver objects, never run ordinary paired iteration, and expose no inner solver accessor. Their direct root/arena uploads, projection/transport and buffer swaps cannot inherit valid=true. No wrapper or payload-layout change is needed. Additional graph capture/instantiation overhead remains a real cost inside the frozen complete-cycle benchmark.

Successful device readback/wait operations do not mutate reach inputs and need no invalidation. An asynchronous CUDA error observed there is not evidence that partially applied learning can safely continue. The implementation adds no partial-update retry semantics.

## Numerical test coverage

The expanded lifecycle matrix compares entire raw device regrets, strategies, reaches and root weights against legacy full sweeps. It covers DCFR/CFR+, F32/compressed, actual full/compact arenas, first eager iteration, capture/replay, consecutive reuse, three evaluation calls each beginning valid (eager/capture/cached replay), profiled/ordinary mixing, direct evaluation invalidation, standalone p0 and p1, both-actor locks/recapture, and fresh construction from warm state.

These numerical comparisons are sufficient to detect stale-cache graph selection after invalidation. Source inspection verifies index selection from the consumed bool. Implementation-mirroring graph counters are not required: always selecting full propagation would reduce performance rather than mathematical correctness, and the frozen benchmark measures that consequence.

The independent original full-down test remains separate from the new helper. It now checks both players' raw reach invariants around the opposing up update, plus isolated p1 refresh after changed roots and NaN-poisoned reaches, including signed-zero roots. Uninitialized CFV scratch is deliberately excluded.

The third test requires **preflop-research** in addition to gpu. It exercises actual continuation validation failures, changed-root standalone p0/p1, root-CFV bits and a subsequent ordinary iteration. A gpu-only run executes two tests, not this third path; runtime claims must preserve that distinction.

Limits: warm resume is in-memory reconstruction rather than disk loading; actual paging swaps rely on ownership analysis/existing separate controls; arities1-5 are covered collectively, not every arity in every matrix cell. No synthetic upload/capture CUDA fault is injected; placement before fallible work is source-verified. None is a source blocker.

## Identity

Only mod.rs has a tracked checkout diff. Ten protected inputs independently match their recorded hashes: kernels, plan, arena, continuation/swap implementations, capacity accounting, store, frozen evaluator and fixture input. review.json records their identities and the frozen patch hash. Compilation and runtime qualification remain the parent's next steps; this review makes no speed or acceptance claim.
