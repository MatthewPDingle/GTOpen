# Automatic follow-up for the fixed board-root study

The identified trainer is PID 55356, creation time 1790520940.3691776. Its two
arms retain the fixed 78-update endpoint. The follow-up runner started hidden
as PID 52928 on 2026-09-28 at 00:48 Adelaide time and was verified live while
waiting for that trainer. This is an operational snapshot; check process
identity again before any recovery action.

The queue waits for the original process to exit and verifies the completed
training and resource-wrapper results. It then runs these prepared stages once,
in this order:

1. `board_matched_complete_readback_v2.py --workers 8`
2. `board_evaluation_resource_wrapper_v1.py --stage control --run`
3. `board_complete_control_readback_v1.py --run`
4. `board_evaluation_resource_wrapper_v1.py --stage evaluation --run`
5. `board_complete_study_readback_v1.py --run`
6. `board_final_findings_v1.py --run`

The scientific drivers and registered settings are unchanged. The numerical
control uses the existing 64-deal control sample. The prospective comparison
remains exactly 65,536 fresh deals, seed 9281101, followed by complete independent
readback and an all-outcomes report. The final plot still needs visual review,
and the complete results need scientific interpretation. No deployment or
GitHub push is part of this queue.

Each stage retains its existing resource and storage admission. The dispatcher
also waits for spare CPU, RAM, GPU resources where applicable, idle production,
and clear research locks. It polls every 30 seconds while waiting and does not
hold a GPU allocation. Each child has a bounded invocation; the complete queue
has a 48-hour limit. A timeout or stage failure stops the dispatcher and preserves
evidence. It does not retry, delete stale locks, restart training or terminate
the upstream trainer. Cleanup can terminate only an identified child process
tree launched by this dispatcher.

The synthetic queue control checked all eight combinations of dependency
liveness/success/failure, process-ID reuse, preservation of a mismatched process,
cleanup of its own test process, and every stage's order and arguments. It
started no scientific stage. Evidence:
`board-full-followup-queue-v1-control-result.json`.

Read-only readiness before launch passed. Live operational files are:

- `board-full-followup-queue-v1-registration.json`: immutable source bindings.
- `board-full-followup-queue-v1-status.json`: current state and owned child.
- `board-full-followup-queue-v1.log` and `.stderr.log`: dispatcher logs.
- `board-full-followup-queue-v1-<stage>.log`: individual stage output.
- `board-full-followup-queue-v1-result.json` or `-failure.json`: terminal evidence.

Do not launch any of the six stages separately while this dispatcher is live.
After interruption, inspect the original process identities, immutable results,
partial attempts and lock owners before choosing an explicit recovery path.
