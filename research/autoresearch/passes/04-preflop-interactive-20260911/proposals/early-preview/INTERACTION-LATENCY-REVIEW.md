# Snapshot availability versus navigation latency

Read-only source/evidence review after corrected `preview-api-b`; no new timing run.

The full model first publishes at **12.469s**, serves root at **17.516s**, and exports at **66.187s**. Its nine sequential node requests cost **5.032, 4.922, 5.062, 5.000, 5.156, 5.328, 5.469, 5.875, 5.782 seconds**; export costs **5.906s**. The first seven node responses all use publication **2**, with no absent-strategy note. The last two and export use publication **10**. The analogous64-particle requests cost roughly0.39–0.45s after root, with the publication10 transfer request0.687s. This pattern supports repeated iteration-lock waiting, not a need for ten iterations to make the line usable. It does not prove every unseen descendant was usable at iteration2.

Sources: [API summary](preview-api-b-summary.json), [API protocol](preview-api-b-protocol.json), private `target/interactive-api/preview-api-b/{reference-preview,fast-preview}/result.json`. Raw request bodies contain a logging alias: the same mutable path list is appended then extended, so all serialized node bodies show the final path. Response history lengths1..9 and chosen actions demonstrate the actual incremental traversal. Preserve those artifacts; fix future logging by copying request bodies before storing them.

## Concrete cause

`crates/server/src/main.rs` takes the CPU solver mutex before `g.try_iterate(&mut s, ...)` and keeps it across the complete device iteration and synchronization. `pf_node` and `pf_export` require the same mutex. `pf_yield_to_waiters` hands off to requests already waiting, but the next sequential HTTP request arrives after the worker has re-acquired the lock. Each click/request therefore pays another iteration even while reading unchanged CPU snapshot2. Export repeats the wait; its repeated `node_view` calls are secondary work, not the demonstrated five-second bottleneck.

`crates/solver/src/preflop/gpu.rs::try_iterate` only accesses the CPU solver to increment/read `s.iteration`; device buffers own the learning state. GPU accuracy evaluation also needs no CPU solver. Current transactional `sync_to_cpu` already stages both arenas and copies them under exclusive access.

## Proposed bounded change — unimplemented

Extract the existing GPU iteration body into a method receiving an explicit mutable iteration counter; keep the existing `try_iterate(&mut PreflopSolver, ...)` wrapper for callers/tests. Preserve exactly when the counter advances, discount arithmetic, stop checks, launch order, error behavior and graph reuse. The server maintains a worker counter, performs GPU iteration and GPU gap evaluation without the CPU snapshot mutex, and takes that mutex only for synchronized snapshot publication/finalization/fallback. Set CPU iteration and publication metadata together with the successfully copied arenas. Keep the CPU solver path exclusively locked as today. Every node/export continues to acquire that mutex and apply all current absent-strategy/history/reach checks.

No new solver clone, repeated arena copy or second2GB snapshot is needed. Existing staged downloads remain unchanged. Consecutive HTTP responses may intentionally have different publication tags; each individual node/export must remain internally coherent. This does not pin a multi-click user session to one generation.

Implementation estimate: roughly30–60 minutes for the narrow GPU/server refactor plus focused tests, excluding large parity/API timing runs. Main risks are GPU-error-to-CPU fallback, interrupted-iteration counters, lock ordering and tagging a failed download. Avoid simultaneously changing publication cadence or solve stopping criteria.

Acceptance: exact full arena/checkpoint parity with the existing APIb reference control; deterministic old/new wrapper parity including stop/error paths; concurrent node/export cannot observe partially copied arenas or mismatched publication tags; mutation/save remain rejected while running. Repeat the same API navigation rule, recording mutex-wait versus node-render/export time separately. A speed claim requires that measurement; source review only predicts improvement. GPU initialization and actual snapshot copies may still temporarily block browsing.

## Source implementation prepared after parent released the build freeze

The lab now contains the bounded refactor in `gpu.rs` and server `main.rs`. Existing GPU `try_iterate` delegates to `try_iterate_counter`; discount and sweep arithmetic/order are unchanged. Server releases the host mutex around both device iterations and device accuracy passes, retaining a separate device counter. `pf_publish_gpu_snapshot` tags host iteration/publication only after the existing transactional download succeeds. CPU fallback after a failed download keeps its last coherent host counter, and the accuracy metadata uses the generation actually evaluated. Stop cleanup now waits for a brief concurrent reader rather than silently leaving the stop flag attached when `try_lock` loses.

Host mutation audit: table/HERO/point-lock/unlock/evaluate routes retain the running409 guard while holding solver→status locks. Save checks running before and after locking. Build/load stop and join the worker before replacing the session. Model-generation and node/export/session access are read-only. No new arena clone or transfer is introduced.

Added tests (not executed by this source-only agent): `detached_iterations_preserve_exact_trajectory_stale_host_stop_and_resume` compares the original wrapper and detached counter for full/64 models, graph warmup, pre-sweep stop, unchanged stale host arenas, final sync and reconstructed-engine continuation. `failed_snapshot_keeps_host_generation_and_readers_see_one_successful_commit` checks failed publication and excludes a concurrent reader during arena/metadata commit. `detached_running_session_reads_snapshot_but_rejects_policy_mutations` verifies stale host data remains marked unavailable and running mutations remain blocked. Syntax parsing and diff checks passed; parent owns compilation and hardware/API parity.

Future API logs now deep-copy request bodies before retaining them; the existing eight pure runner tests pass, including mutable nested-path regression. APIa/APIb raw records were not modified.
