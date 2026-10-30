# D022: wide three-action supplemental control

Source-only design and new standalone ignored integration test. No build or GPU execution was performed for this artifact. This is a correctness control, not a benchmark or performance claim. The same test bytes must be frozen and compiled against accepted E004 and the direct3-only candidate before comparison. Existing primary benchmarks and controls remain unchanged.

## Gap and fixed workload

The existing flop/turn state and saved-resume controls use one bet size and no raises or added all-in, hence no three-action decisions. Existing varied action-menu controls are river-only and far below the 4096-action level threshold. They therefore cannot establish specialized three-action lock/resume correctness, even when their exact fingerprints agree.

The new workload is KsQs2d, OOP AA,KK,QQ,JJ,AKs,AQs,AKo and IP AA,QQ,TT,77,AQs,KQs,AQo; pot 10, stack 100, 5% rake capped at 1; both players use 33% and 75% bets on every street, no raises/donks or additional all-in, threshold .85, and explicit carry_aggressor_through_checks=false. Inputs are literal in the test and emitted in every completed case. Narrow ranges limit device buffers while the flop tree supplies wide levels. Actual eligibility has NOT been measured: the test must fail, rather than silently skip, if this fixed tree does not qualify.

The eight ordinary cases cover F32/compressed x explicit/compact isomorphism x DCFR/CFR+. Before CUDA construction, the test rebuilds GpuPlan using the baseline public API, counts NA=3 nodes per actor in each aggregate action span with count >=4096, and requires both actors to qualify. It selects the deepest common eligible level with at least two NA=3 nodes per actor and exactly two card steps, then the lowest original node ID for each actor. Selection is independent of a candidate's within-level partition ordering. Every selected node must be active and its reconstructed action/card path already canonical. Paths are reconstructed from original tree edges; no guessed action sequence or synthetic node IDs. The actual lock API must create exactly one entry at the selected ID.

The deepest shared level bounds CPU node-view work. Both owner locks are exercised separately, leaving other NA=3 nodes of both actors unlocked. Each complete training iteration sweeps both traversers, so each selected node is visited in both the traverser and opponent roles; each lock is exercised with both traversers. Direct3 dispatch itself is inferred from the candidate's reviewed threshold/classification code, not observed through a new production instrumentation flag.

## Execution and exact comparisons

For each case:
1. Start cold, execute three iterations: eager, graph capture+launch, replay.
2. Download full state; record every CPU arena value (raw f32 bits or q words plus every scale bit), per-arena/combined FNV-1a fingerprints, cheap root strategy bits, and three exploitability results (eager evaluation, graph capture, replay), requiring finite and identical exploitability bits.
3. Materialize suit copies, query both selected deep paths, record complete serialized NodeViews plus hashes and a full materialized-state fingerprint. Download again and require restoration to the same raw state. Save and stream-hash all saved bytes. This checkpoint contains the raw restored inactive representation; the materialized query representation is fingerprinted separately and is not the saved checkpoint.
4. Freeze owner 0's selected node through its real path. update_locks invalidates existing graphs. Run three iterations and snapshot. Destroy GpuSolver, reload the saved state, explicitly restore algorithm/isomorphism (GTOSOLVE2 omits them), check iteration/config/lock-sigma bits, fingerprint loaded host state, construct a fresh GPU solver and run three more iterations. The first warm resumed iteration captures immediately. Snapshot again.
5. Repeat step 4 with owner 1, replacing the old lock. Clear all locks, update device lock metadata, run three iterations and snapshot unlocked state.

There is only one lock/label at any time because the current save header serializes HashMaps in unsorted iteration order. Multiple locks would make raw file hashes nondeterministic across independent processes. Raw compressed state before and after loading is recorded as separate stages; the test does NOT incorrectly assume f32 save decoding/re-encoding preserves the pre-save q+scale representation. Compare corresponding stages across baseline/candidate.

The optional second test, compiled only with preflop-research, uses F32, explicit suits and CFR+, the same eligible fixture and deterministic nonuniform root reaches. It runs three eager continuation iterations per phase, first unlocked and then with each deep owner locked, recording both root-CFV vectors as raw bits, full state and saves. It never invokes ordinary exploitability with these custom reaches. This checks the shared eager sweep path; it does not claim stored-device paging/swap coverage. Existing paging tests remain useful but their one-size menu does not enter the new NA3 specialization. A wider paging-specific control is deferred unless the final source modifies storage/transport contracts.

FNV fingerprints are deterministic equality evidence, not cryptographic proof against intentional collisions. Artifact/file identity uses SHA256. Completed JSON contains original inputs, eligibility census, paths, stage fingerprints, exact exploitability bits, root bits, and full query payloads. Treat any missing completed case, assertion failure, unexpected eligibility census, or field mismatch as a failed control. Do not ignore a failed auxiliary stage merely because the primary three workloads match.

## Build/run procedure (parent only, serialized)

Copy the reviewed frozen test into crates/solver/tests/postflop_direct3_controls.rs in each version to be built. No Cargo.toml change is needed. Build explicit --test postflop_direct3_controls targets with the same release/features/toolchain used for both versions. The ordinary test needs gpu; using preflop-research also enables the optional continuation test. Preserve source/test SHA256 and binary SHA256 before running.

Set POSTFLOP_DIRECT3_CONTROL_DIR to an absolute unique directory under the run's evidence folder and invoke the immutable binary with:

    postflop_direct3_controls --exact --ignored --nocapture --test-threads=1

The optional separate test command is:

    postflop_direct3_continuation_control --exact --ignored --nocapture --test-threads=1

The test creates new graph-resume and continuation child directories and refuses to reuse either. It emits METRIC_JSON coverage and completed records to captured stdout. It retains one latest .gto checkpoint per ordinary case (the same case file is replaced at each stage; each stage's byte hash and size are retained in stdout), and one .gto file per continuation phase. Preserve stdout, stderr, exit status and final files. Keep all other GPU jobs stopped, use the existing runner GPU lock, and preserve enough S: space for eight expanded f32 save files plus temporary save replacement and three continuation files. These saves always contain expanded f32 arenas even when host stores are compressed; estimate bytes from emitted fixture tree data sizes before broad runs. No writes to live server data, reports or scenarios occur.

For comparison require exactly eight ordinary completed records and one optional continuation completed record when requested. Match by case and compare all deterministic fields, including coverage and full snapshots, ignoring only external run metadata. No baseline expected values are embedded, and a single version passing alone does not prove candidate equivalence. This control does not replace the frozen three-fixture complete-cycle performance gate, per-fixture regression gate, other unit/server suites or a review of budget/host metadata accounting.

## Production review checklist

Keep action_spans aggregate and stable node coverage; only partition original action_nodes within eligible levels. Direct3 prefix counts are host-only and must use retained vector capacity accounting. Kernel ABI/math, arena offsets, child order, reach/CFV mapping and block size stay unchanged. Load any direct3 kernel before capture, including a warm resume that captures without an eager first iteration. Use both partial launches only in training up-action; down-action and evaluation retain aggregate spans. Account each actual profiled launch separately. Lock replacement continues to drain old pointers and invalidate training/evaluation graphs. Continuation sweeps use the same eager dispatch; mutable storage swaps must not swap immutable partition metadata. Capacity/layout tests need 4095/4096/4097, all/none/mixed NA3, stable partition coverage and exact host retained-byte formulas.

E005 already covered a mixed NA2 prefix/remainder partition; it was not homogeneous-only. This control and the new hypothesis are direct3-only and do not reintroduce the rejected NA2 specialization.
