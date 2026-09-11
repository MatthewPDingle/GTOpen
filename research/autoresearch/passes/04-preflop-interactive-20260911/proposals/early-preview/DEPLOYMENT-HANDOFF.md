# Curated exact-preview deployment handoff

Prepared source only. Do not execute until the root has recorded passing production tests, private API qualification and the 1280px UI check against the **same staged GPU executable**. No live POST, process action, build or hardware job was performed preparing this handoff.

Source: `53ce9dec08de9fa2f93f246d7f5efcccc8c22c68`. Candidate: `T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911/target/qualification/gto-server.exe`. Use the runtime SHA in the actual completed qualification manifest, verified against the file. Do not substitute the shared Cargo target's last server EXE: CPU test builds follow GPU staging.

## Preconditions

1. End all pass04 hardware/build/API/UI queues. `active.json` must truthfully say `running:false`; never edit it to bypass a live queue. Review the completed production `*-result.json`, API final-arena equality/stop tests, and UI screenshot. A build manifest alone is not a test pass.
2. Integrate the nine curated files to main using the parent's reviewed Git workflow. Main implementation remains full-reference-only, with no preview64/128 selector or payoff changes. Preserve the pre-integration main commit as a rollback reference. Confirm main `web/css/app.css` and `web/js/{api,app,preflop_lab,preflop_preview}.js` have exactly the curated source hashes. The server serves `ServeDir::new("web")` relative to its cwd, so an EXE-only change does **not** install the UI. Private restore smoke intentionally tests API/native semantics; the separate private UI qualification must already have passed.
3. Inspect the existing shortcut target, arguments and working directory read-only; preserve origin `http://127.0.0.1:56708` and cwd `T:/Dev/GTOpen`. Do not use the launcher for cutover: `tools/launch.ps1` reuses a ready port without rebuilding, and can otherwise rebuild an unqualified executable. It currently targets `target/desktop-runtime/release/gto-server.exe` for future launches. The explicit cutover below runs the staged qualified EXE; preserve that file. A later launcher rebuild must use the integrated exact source.
4. Keep sufficient free disk for both fresh native backups, private copies and resave verification (multiple GiB). Do not delete old saves or failed-run evidence for capacity. Existing native iteration may be one ahead of the old UI counter; **fresh `/api/preflop/session` and newly written native headers are authoritative**. The last observed preflop101/status versus possible102/native and postflop210 are context only, never restore inputs.

## Fresh ownership and smoke (parent executes later)

From `T:/Dev/GTOpen`, obtain fresh GET status/session and process identity; this first command is read-only and makes no saves:

```powershell
$deploy = 'T:/Dev/GTOpen/research/autoresearch/passes/04-preflop-interactive-20260911/proposals/early-preview/deploy_qualified.py'
$candidate = 'T:/Dev/GTOpen/target/autoresearch/preflop-interactive-production-20260911/target/qualification/gto-server.exe'
python -c "import sys,json;sys.path.insert(0,'research/autoresearch/passes/03-preflop-20260910/proposals/final-deployment');import session_guard as g;print(json.dumps({'owner':g.owner(56708),'sessions':g.snapshot(56708)},indent=2))"
```

Record the returned PID, creation time, executable path/SHA, cwd and whitelisted environment. Require cwd to be the main repo and the listener to be the expected user's app; inspect any surprise instead of accepting it because it answers HTTP. Set `$oldPid`, `$oldSha` and `$candidateSha` to those reviewed values and the qualification manifest's runtime SHA. The wrapper does not infer qualification success.

```powershell
python $deploy smoke --candidate $candidate --candidate-sha256 $candidateSha --expected-pid $oldPid --expected-old-sha256 $oldSha --port 56708 --execute --queues-complete
```

This reuses pass03 `session_guard.smoke` without replacing its preservation logic. The thin pass04 adapter additionally rejects active current-pass queues/production tests. Smoke creates a fresh unique `Before preflop deployment DATE-TIME-TOKEN` name, archives the exact old EXE, saves **both current sessions**, records native headers/every arena SHA, copies caches and natives to a private cwd, and launches a hidden candidate on an unused port. Only that owned private child is terminated afterward. No solve/evaluate/build is invoked. Copy the printed absolute `backup.json` path to `$manifest`; do not pick an older successful backup.

Inspect its `smoke-passed.json` and logs. Exact preservation includes config, profiles, frozen seats, HERO/backup arenas, all point locks, postflop labels/board/ranges/bet menus/rake/storage and authoritative native iterations. API timing/history/gap metadata is deliberately not a native identity gate. Different serialization/arena data is a failure, not an invitation to add tolerance.

## Cutover and automatic rollback

```powershell
python $deploy cutover $manifest --execute --queues-complete
```

This invokes the existing `cutover.py`. It requires smoke success, verifies both archived-old and candidate hashes, saves fresh final-recheck natives and compares them to the fresh smoke backups, then verifies PID/create-time/EXE/SHA/cwd again. Any user state change (including locks without iteration change) aborts: redo smoke with a new unique name. There is no server-wide maintenance transaction; root must keep this interval short and abort/recheck if user activity appears.

Only the verified old process is stopped. The qualified staged EXE starts hidden on56708 with main cwd and preserved storage/thread/GPU/equity/fit settings. Research override variables are removed; no new memory budget or solve is introduced. Both freshly saved sessions load into the empty server, then are saved again to unique verification names and compared with all native bytes. The new live owner/SHA and restore records are retained in the backup folder.

If candidate start or restore fails, the existing helper stops only its own child and launches the archived old EXE with its original environment/cwd/port, restores both same fresh backups, and records `rolled_back`. Preserve all logs. If rollback itself fails, do not start a second ad-hoc server or restore older sessions; inspect the owned listener and failure first. A process-policy rejection is a stop, not permission to bypass it.

Because UI is served from main/web, executable rollback does not itself revert the integrated UI. Retain the pre-integration Git commit and parent-owned asset backup. The curated frontend feature-detects `early_preview_v1`, so it disables early publication against an older server; a complete UI rollback, if needed, must restore only the reviewed curated web file set from that recorded baseline (including removal of newly added helper only if baseline lacked it), preserving unrelated user changes. Do not use a broad reset.

## Final read-only verification

Repeat the read-only ownership/session command and verify against the manifest: live candidate SHA and correct cwd/port, preflop stopped at fresh native iteration, postflop original done/stopped state and native iteration/board/locks. Check `/api/preflop/capabilities` exposes early_preview_v1 and only coupled_deck_v1. Inspect existing browser at the same origin: full-width publication row, readable actor/evidence at1280px, capability-aware checkbox and Setup export warning. Loaded measured accuracy may be absent until a later evaluation; never run a solve/evaluate merely to repopulate a badge. Browser-only selections/unsaved Setup form edits are not serialized by native saves; keep the existing browser/origin intact and do not invent restoration of those values.

Qualification driver adjustment: the redundant standalone CPU runtime build was removed. Non-GPU server test compilation already exercises that cfg/main path; full CPU solver/server tests and doctests, staged GPU runtime and targeted GPU integrations remain scheduled.

Unexecuted adapter limitation: syntax-reviewed only; operational queue/ownership/native helpers have prior pass03 execution evidence, but this pass04 adapter must still be root-reviewed before use. It adds no new save/restore/process implementation.
