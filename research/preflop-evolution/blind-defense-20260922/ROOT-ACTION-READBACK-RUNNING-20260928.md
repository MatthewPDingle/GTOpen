# Direct readback recovery and next diagnostics

This supersedes the queued handoff for live status. Recorded 2026-09-28;
recheck live processes before relying on the identities below.

## Completed replay

All 65,536 deals / 2,048 batches completed in 1,709.36 seconds. Maximum mixture
identity difference: 5.684341886080802e-14 bb. Retained allocation: 510,745,757
bytes. Final checkpoint:
`checkpoint-002048-818e7a2801bd53e1bff847d19b51205010fc59ef4549545db41f6a8346a11779.json`.
Summary SHA-256:
`012d4b032689624ec01d1b164f7c8741a96c5215189f875749fe11f8a5c8612e`.

## Failed handoff, preserved

Pipeline v1 PID 64544 exited. Its status writer incorrectly reused the immutable
`atomic_json` publisher for a changing status filename. The first transition
raised FileExistsError; the failure-status update encountered the same error.
Its newly spawned verifier was killed by the owned-child cleanup before creating
a readback registration. The old `waiting_for_existing_replay` status file is
stale and must not be treated as live evidence. Preserve the source and error log.

After confirming that the replay, pipeline and verifier were all terminal, that
no readback registration/result existed, and that the research lock was absent,
the unchanged qualified verifier was started directly:

- PID **87376**, creation time **1790563394.5222905**.
- Command: Python `-B tools/research/board_root_action_replay_readback_v1.py --run`.
- Logs: `board-root-action-replay-readback-v1-initial.log` and matching
  `.stderr.log` in this directory.
- The live check confirmed all 12 workers near one core each and no stderr.
- Last observed checkpoint for this note: **16,384 / 65,536 deals verified**.
- Do not restart it on an observation timeout. It owns the existing shared lock.

The report was not automatically queued after this direct recovery. Once the
verifier is terminal and its passing result exists, run the already saved
`board_root_action_interpretation_v1.py`. It requires that result and binds all
inputs. Then run the new `board_root_action_effects_v1.py --run` after its resource
and ownership admission. Its known-factorial-effect control has passed; the full
paired analysis has not run. It separates old/new BB later-policy effects from
old/new BTN effects within each seed, covering every hand and root action.

## Work completed during verification

`board_later_fit_diagnostic_v1.py` checked all 156 generation metric files / 312
player fits and saved `board-later-fit-diagnostic-v1.json` plus
`BOARD-LATER-FIT-DIAGNOSTIC.md`. Relative training-loss reduction falls from about
59–61% to 47–48% for BB and from 76% to 47–50% for BTN. These are training-target
fit measures, not accuracy percentages or EV losses. The zero-prediction baseline
uses the actual loss normalization; it must not be assumed equal to one.

`BOARD-LATER-FIT-HOLDOUT-PLAN.md` proposes a fixed-data test of extra optimization
with input-disjoint train/validation/test splits. It is not implemented or launched.
Read the completed root-action results before deciding the next substantial run.
No new training, GPU work, production update or new GitHub push occurred.
