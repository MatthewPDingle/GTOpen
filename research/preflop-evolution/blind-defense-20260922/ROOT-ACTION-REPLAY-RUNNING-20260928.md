# Root-action replay launched, 28 September 2026

The full saved-sample replay is running. Its correctness, restart and all-class
statistics controls passed; the implementation is committed locally at
`c3532801dcce99112629880d5398fd6851fa9c52`.

## Live identity at this handoff

- Controller PID: 51220; process creation time: 1790561572.256763.
- Command: Python312 `-B tools/research/board_root_action_replay_v1.py --run`.
- Attempt: `attempt-d0bba05e85864d4790e60824c3b45597`.
- Store: `S:\GTOpen-research\board-root-action-replay-v1`.
- Registration SHA256:
  `224aaef02de74c1191cce8bcdade3718481528f98bd7146a8002c1b3242846cf`.
- Logs: `board-root-action-replay-v1-initial.log` and `.stderr.log` in this directory.
- Twelve CPU workers. Initial storage admission: 716.067609587 GB allocated across
  the three research roots. Reserved 4 GB for replay plus 2 GB for overhead/readback.
- Live process identity was rechecked. A sample during replay showed 13 descendants,
  49.3% total CPU use and about 70.35 GB available RAM. These are observations,
  not fixed limits or performance guarantees.
- Committed checkpoints had reached at least 2,048 of 65,536 deals. The second
  1,024-deal block took about 21.9 seconds; extrapolation suggests roughly 25 minutes
  for the replay work, subject to workload changes, followed by independent review.

Revalidate this PID plus creation time and command before relying on these details.
Read the latest immutable checkpoint or log for progress. A timeout is not evidence
that work stopped. Do not restart a live invocation. The existing research lock
belongs to this controller; never remove it by age.

## What remains

The replay output is `board-root-action-replay-v1-replay.json`. It deliberately
has `complete: false` and `independent_review_required: true` when native replay
and its own summary finish. Do not call the study complete merely on that file.
The summary is `summary.json` in the store. Its 169-class statistics are in native
class order, with fold/call/raise/jam values for BB, BTN and expected rake, six paired
BB action contrasts, sample counts, and explicit missing-class values.

Prepare an independent full readback while this runs. Use the authenticated source
archive routes, retained forced native results, receipts and compact action values.
Verify all batches/classes and aggregate counts/moments independently. The existing
replay control used a separate 40-digit decimal calculation (largest error 2.84e-14,
9,072 moments checked) and is useful as a two-batch qualification fixture for the
new readback. Do not edit any now-frozen replay/control source.

Useful sources: `board_root_action_replay_worker_v1.py` (new root-only transport and
native evaluation), `board_root_action_replay_store_v1.py` (append-only prefix and
owned scratch handling), `board_root_action_statistics_v1.py` (Welford summaries),
`board_root_action_replay_control_v1.py` (real interruption and Decimal controls).
The older `board_root_action_decomposition_v1.py` contains the qualified adapter;
its `compare` accepts an original replay argument, but the full replay deliberately
uses the archived original twice and removes `maximum_replay_error`. It explicitly
records `original_native_rerun: false`; do not claim a fresh original-policy solve.

If interrupted, first verify that the controller and its workers are terminal.
An explicit `--run --resume` resumes the same committed prefix, preserving all
partial attempts. The registration's deadline is absolute; do not silently extend
it. Source/digest disagreement is a failure, not a reason to discard old evidence.
A summary already published before interruption is reused only if byte-identical.

After verified replay, interpret all hand classes and paired action differences.
This is exploratory reuse of the original evaluation; choosing the sample's best
looking action does not establish a best-response or exploitability bound. Old
registered payoff tests remain inconclusive. No production changes or improved
range-accuracy claims are justified yet. The broad research goal remains active.

Publication: commits after approved/pushed `69b8f082` remain local. Do not broaden
that prior GitHub push approval. Keep Jev deferred and never open a Serena window.
