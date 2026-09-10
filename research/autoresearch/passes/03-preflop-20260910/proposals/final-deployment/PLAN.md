# Session-preserving final deployment plan

Prepared only. No build, save, smoke launch, restart or solve has been performed by this proposal. Source accepted by parent: research4878044; main production still1b8 implementation at review time. Run only after final integration/tests and all hardware queues finish.

Read-only live check confirmed port56708 ownerPID99216, executable T:/Dev/GTOpen/target/multiway-build/release/gto-server.exe, SHA2569c095b6e654867dd0965366a7443442c2f65db906b384759cfe9424a3c8070be, cwdT:/Dev/GTOpen. Preflop status is stopped73, but /api/preflop/session reads authoritative native solver74 (8seats, coupled_deck_v1). Postflop is done210, boardKd6s5c. Default compressed postflop storage; no explicit memory/thread/fit overrides. Reverify these before acting: never impose this snapshot on newer user work.

## Verified routes and comparisons

POST /api/preflop/save {name} rejects running state and returns {ok:true,iteration:74}. POST /api/save {name} rejects running state and returns {ok:true}; it first ensures symmetric postflop state. Saves are native saves/preflop/NAME.gtop and saves/NAME.gto, relative to server cwd. Unique helper names contain only safe alphanumeric/space/hyphen characters.

POST /api/preflop/load {name} restores config, profiles, payoff model, frozen/hero/locks and arenas; returns config, nodes/action_nodes, iteration, seats. It resets status to stopped with native iteration; old gaps/history are not persisted. GET /api/preflop/session exposes authoritative iteration74, profiles/hero/frozen. POST /api/load {name} validates then replaces postflop state, restores iteration210/locks/labels and sets done; GET /api/status reconstructs spot_request/tree. No solve is required or started.

Status alone cannot prove lock preservation. session_guard.py additionally saves restored sessions to unique verification files, compares EVERY native header field (sorting only map-like lock lists) and SHA256 of every exact length-prefixed arena. It covers optional pre-hero backup arenas, postflop lock labels, board/ranges/sizes/rake and iterations. Any precision/storage/serialization mismatch fails closed, with no tolerance fallback.

## Exact usage, later only

First register final tests and build the final desktop executable through the parent workflow. Compute its SHA256 independently and use the final absolute path below. The helper never builds. It refuses active.json unless explicitly running=false and checks for live lab executables/known queue controllers. Both --execute and --queues-complete are mandatory attestations, not automatic permission inference.

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/final-deployment/session_guard.py smoke --candidate ABS_FINAL_EXE --candidate-sha256 FINAL_SHA256 --expected-pid 99216 --expected-old-sha256 9c095b6e654867dd0965366a7443442c2f65db906b384759cfe9424a3c8070be --port 56708 --execute --queues-complete
```

Smoke snapshots latest idle sessions, makes uniquely named backups, archives the old executable, copies backups plus equity/realization caches to a new private working directory and launches a hidden candidate server on a free port. It validates ownership after binding, so a free-port race cannot target another process. It loads and saves both sessions privately and compares exact native state, then terminates ONLY its own child. Existing live server is never stopped. Read private server.log on failure. Success writes smoke-passed.json and prints backup.json under target/research-deployment/UNIQUE_NAME. All originals and failure artifacts remain.

Immediately before cutover, verify latest native state again, including locks that may change without iteration/config changes:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/final-deployment/session_guard.py check-live --manifest ABS_BACKUP_JSON --expected-pid 99216 --expected-sha256 9c095b6e654867dd0965366a7443442c2f65db906b384759cfe9424a3c8070be --port 56708 --execute --queues-complete
```

This makes new recheck saves without overwriting backups. If changed, stop deployment and rerun smoke with fresh backups; do not restore older state. There is no server-wide maintenance transaction: user activity after this check still requires rechecking. Cut over immediately while idle and abort if any work begins.

Parent performs the separately verified cutover: confirm smoke-passed.json, final candidate hash, latest check-live, and oldPID/create_time/executable hash. Stop only that owned server if permitted. Start the tested final executable hidden with cwdT:/Dev/GTOpen, PORT56708, original whitelisted storage/memory/thread environment and .cuda-nvrtc/nvidia/cuda_nvrtc/bin on PATH. Preserve the old executable and both backups. Do not use a broad kill-by-name or infer PID ownership from a stale number.

The launcher uses PORT argument/default3737 and returns early when a server is ready, before compiling. Thus double-clicking it cannot update the old56708 process. Inspect the existing Start Menu shortcut arguments, preserve56708 and its target/working directory; use explicit final build+start. Do not change browser origin unless forced by a tool restriction, because browser-local UI state belongs to the origin.

After verifying the NEW listener PID and final executable SHA, restore only to the empty server:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/final-deployment/session_guard.py restore --manifest ABS_BACKUP_JSON --expected-pid NEW_PID --expected-sha256 FINAL_SHA256 --port 56708 --execute --queues-complete
```

The helper refuses nonempty/running sessions. Preflop empty state is actually an empty string from derived Default, not always literal idle; this is handled with iteration0/frozen-empty guards. Success leaves preflop stopped at authoritative74 and postflop done210/Kd6s5c, with exact native verification saves. Both remain unsolved beyond their original state. Inspect read-only UI and report status; do not call evaluate/solve for cosmetic status restoration. GPU/gap/history timing displays may reset on load, as native saves do not store them.

## Rollback

If private smoke fails, old server remains active and no rollback is needed. If cutover launch/restore fails, retain logs/verification saves, identify and stop ONLY the newly launched candidate process, then restart archived previous-gto-server.exe from backup.json with original cwd/port/environment. Verify its original SHA/PID, then run the same restore command using ORIGINAL_SHA256 and the rollbackPID. Do not replace existing user backups or delete the failed installation. If policy blocks stopping either process, leave it intact and report the exact block; alternate-port installation must be explicit and preserve both native sessions before any shortcut change.

## Limits to retain

- These scripts are source-reviewed with three pure tests normal and -O, not integration-tested against an actual server. Parent must review and run explicitly later.
- Compression is preserved from the live process. A postflop compressed save/load resave mismatch is a STOP, not a reason to widen comparison tolerance. Do not switch to F32 silently.
- Smoke needs spare disk/RAM for duplicated sessions and load staging while old app remains alive; no memory-cap override is applied. It can safely refuse capacity.
- Cache copies prevent native equity loader writes to source caches. Compare actual loaded calibration provenance with known pinned versions if caches changed since the old process started; native files do not serialize realization-cache contents.
- API snapshots do not preserve browser-only navigation, unsaved Setup form edits, selected report row or hover state. Keep browser and same origin open; no UI migration is required.
- Saving is the only permitted live mutation in helper preparation/recheck. No build, solver execution, stop route, profile mutation, report run or automatic live cutover exists in its allowlist.
