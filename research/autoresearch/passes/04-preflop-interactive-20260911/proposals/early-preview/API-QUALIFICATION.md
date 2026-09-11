# Isolated API preview qualification

Prepared source only. Root must run serially after the active hardware queue completes. No live mutation or deployment. Every private POST verifies the retained child PID, process creation time, executable path and SHA. A background GET-only guard monitors live56708 preflop/postflop/report activity and kills only the owned child if the user starts work. Children are hidden and use unique private directories/free ports. The hard stop is02:53:27UTC, ten minutes before the research deadline.

Example (substitute the verified candidate executable, exact SHA and declared build source):

```powershell
python research/autoresearch/passes/04-preflop-interactive-20260911/proposals/early-preview/verify_api.py --id preview-api-a --exe '<candidate.exe>' --sha256 '<sha256>' --binary-source-ref '<build commit or recorded dirty-source manifest>' --execute
```

`--cases small-api` selects only the small functional test; `--cases reference-control reference-preview` selects the exact reference comparison; `--cases fast-preview` selects the same-eight fast build. `--iterations 50` is default (positive multiples of50 only). All large cases pin default-equivalent check_every50, target0.005,16threads,the frozen equity cache header sample count (currently20000), and23000MBGPU budget. A case is capped at600seconds (small240seconds). Enough time for every selected worst-case bound plus120seconds must remain before starting. No automatic retries or cap relaxation.

The input is the exact eight-seat native0 fixture pinned by pass03`build-owned-confirm-a-protocol.json`, with the same cache and realization fit. Reference false/true cases load identical native bytes. Fast builds the same JSON config explicitly via`?multiway_model=coupled_preview64_v1`; native0 must differ only by that model identifier. Full input/native/cache/binary/source/runner/guard hashes are frozen in a new exclusive protocol before any server launch. Current source hashes are labeled separately from the declared binary build provenance, so a binary built before later diagnostic tests is not mislabeled.

The runner records raw status and request responses, solve acknowledgment latency, first published snapshot interval, first root strategy response and first export response. Navigation uses only positive-frequency actions: fold nonblinds, then passive blind actions or the smallest nonjam raise, bounded to18nodes. An unavailable branch is recorded explicitly and retried on later publication; it is not manufactured from uniform fallback. Publication metadata records the actual snapshot served, which may advance during navigation. These latency observations include polling and API overhead, not just kernel timing. The reference cases require exact native headers and every byte of both arena streams (SHA256), plus exact final gap/EV/publication checkpoint fields. Transient wall timing/status fields are excluded; no numerical tolerance is applied. This does not establish early-policy or fast-model accuracy against the reference game.

All final native snapshots are loaded and saved again; every header field and arena SHA must match. The separate tiny3 fast case proves unknown model/query/duplicate query rejection leaves the existing session and native state unchanged, refuses a save while running, explicitly stops after observing a published preview, saves the paused native state, reloads it and saves again exactly. Reload must retain the fast model, tag the actual native iteration and report accuracy as unmeasured. No full-run parity claim is made for the paused case.

Each case retains raw responses/server log/result under worktree`target/interactive-api/<id>/<case>`. Small summaries and immutable protocols remain beside this document. Failures retain completed observations and stop the selected run. Disk reserve includes input, initial, final and roundtrip native copies for all selected cases. The implementation does not invoke the solver comparison executable: exact full native metadata plus all raw arena bytes supplies a stricter zero-tolerance representation gate for these identical all-solver inputs. A separate policy comparator may be run by root if desired.

Pure tests (no network, GPU, or solver):

```powershell
python research/autoresearch/passes/04-preflop-interactive-20260911/proposals/early-preview/test_verify_api.py
python -O research/autoresearch/passes/04-preflop-interactive-20260911/proposals/early-preview/test_verify_api.py
```

## Cache-header correction after preview-api-a began

The first runner inherited the earlier APIqualification fixed1024sample setting. The frozen sourcecache is actually20000samples; the server load_or_build rebuilt the privatecache to1024. Consequently baseline-eight-50-a and preview-api-a must be treated as a separate1024cache configuration. Their artifacts/protocols remain unchanged, and the ongoing preview-api-a pair is still a useful same-configuration preview parity test. It is not directly comparable to the20000sample interactive benchmark trajectory.

The original runner is preserved in archive/verify_api-before-cache-header-fix.py. New runs derive PREFLOP_EQ_SAMPLES from the frozen cache header, record the4byte header SHA and wholefile SHA, and verify both equity/fit files immediately after load/build, after roundtrip and afterchildshutdown. Any cache alteration fails thecase while retaining actual hashes. The next20000samplequalification must use a newrunID. No priorresults are rewritten.

## Corrected20,000-sample run completed

`preview-api-b` passed all four cases on source `cfbdb8e`, server SHA `bc6c837ec6a274e55dbda6028bfc2be81e00be346c27095de8f5231162baa3cc`. Both caches remained exactly frozen after load, roundtrip and child shutdown. Full reference preview off/on produced the same native SHA `6162be87527d2263ad1655c6565b91f8805d169190f99ec18c8eae0a15b51a5e`, identical to the standalone full50 benchmark, and exact summed gap1.4955166257076455. Fast64 also matched its standalone native SHA `54d354a65929de2427e7a6c83e2ce9d60711c28fd3c4288d087674d748771290`.

| Mode | First published strategy | First root response | First successful export |
|---|---:|---:|---:|
| Full, early publication off |307.531s|307.562s|307.781s|
| Full, early publication on |12.469s|17.516s|66.187s|
| Experimental64, early publication on |3.750s|3.953s|8.109s|

Full early publication is24.66times earlier for the observed snapshot, but only4.65times earlier for this navigated export workflow. Export observes iteration10, not the initial iteration2 snapshot. These are availability timings, not validated strategy quality. The uncompressed learning trajectory remains exact. Experimental64 retains its independent physical/local gate failures; latency alone does not qualify it.

The small API case also passed invalid-query immutability, running-save rejection, stop, exact native roundtrip and loaded-model identity/unknown-accuracy metadata. Raw responses remain in the ignored private run directory; the complete compact summary and immutable protocol are beside this document. Live56708 was read-only throughout.

## Detached-compute run completed

`preview-api-c` on8c37f18 passed all four cases. Both full cases again produced the exact old-server/standalone full50 native SHA; fast64 also matched its old-server/standalone native SHA. `preview-api-c-cross-version.json` explicitly checks these predeclared hashes. Cache, publication, mutation rejection and save/stop/load checks passed.

| Mode | First published strategy | First root response | First successful export |
|---|---:|---:|---:|
| Full, early publication off |298.844s|298.875s|299.078s|
| Full, early publication on |12.063s|12.094s|12.266s|
| Experimental64, early publication on |3.750s|3.766s|4.000s|

Releasing the CPU snapshot mutex during GPU work removed the roughly5second wait on each navigation request. The full preview path's recorded node/export request durations were0..16ms at the timer's resolution; this does not mean zero actual request latency. Full export availability improved5.40times relative to APIb's66.187seconds and24.38times relative to the paired no-preview control. It now exports the internally coherent iteration2 snapshot. Final full50 strategies remain exact; iteration2 accuracy is unmeasured. This qualifies the interaction/trajectory change, not the early policy's decision quality or the experimental64 evaluator.

The independent lifecycle review then identified cancellation/terminal-publication edge cases. Source6a7b484 hardens those paths; it is not part of this timing run and must pass its focused tests and a new small API check before deployment. No live server was changed by these tests.
