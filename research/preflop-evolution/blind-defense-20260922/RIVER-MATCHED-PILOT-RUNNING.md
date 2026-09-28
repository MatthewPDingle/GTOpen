# Matched river pilot operational handoff

Updated 2026-09-28 21:31 Adelaide. Goal remains active; no range-quality claim.

Runner source is committed at 4ffc7421. Registration exists:
`river-matched-training-pilot-v1-registration.json` in this output directory.
Executed sources and registered inputs are now frozen. Fixes require a new
version and preserved failure evidence, not edits to registered code.

Live runner launched with `--run --wait`:

- Exec session: 34932.
- PID: 94808; process creation Unix time: 1790596846.2597828.
- Latest verified state: waiting_for_resources, GPU 100% occupied.
- Status: `river-matched-training-pilot-v1-status.json`.
- No training updates or fresh test deals have run at this checkpoint.

Poll the existing exec handle and status. Never start a duplicate merely because
an observation times out. Verify the process identity before any recovery.
If it actually terminates, read any interruption evidence and complete progress
markers before using `--run --resume --wait`. Preserve partial attempts.

Fresh storage inventory completed successfully: 718,622,677,422 allocated bytes
across the three research roots. With 10 GB reserved this is below 800 GB.
Runner performs another inventory at actual admission. Study cap 8 GB plus 2 GB
reserve; preserve historical data. No deployment or additional GitHub push.

User approved sharing with light desktop/video use. Admission permits below
65% external GPU utilization, 4 GB own CUDA cap and 2 GB external headroom;
active production solves and heavy workloads retain priority. Initial wait is
bounded to 12 hours; actual invocation is bounded to four hours. CPU generation
uses bounded pools of four workers with single-thread BLAS.

The pilot forks two complete 78-update source states into baseline/candidate
pairs, tests full update interruption/restart, runs two updates per arm, then
compares full played-policy averages on 1,024 fresh common deals. Qualification
cost is recorded separately. Unplayed model 80 is excluded. This is preliminary
one-context evidence; old bank/reservoir content dilutes the treatment. An
independent analysis, equal-time comparison and broader contexts remain needed.

Follow RIVER-MATCHED-TRAINING-PILOT-PLAN.md for the prospective design. Its
preparation-time statements that the runner is not yet written/registered are
superseded by this handoff; do not edit that now-registered plan.

## Live continuation at 21:48 Adelaide

The same runner/session 34932 and PID 94808 are live. Resource admission passed
at 21:36:59 after GPU utilization dropped; the fresh inventory was
718,622,783,901 allocated bytes. A-baseline completed updates 79 and 80 in
60.625 and 61.907 seconds. A-river is executing the full-update/restart
qualification. Its deliberate interrupted attempt completed all eight physical
batches, reached the intended stop, and the complete replay phase is now active.
No complete candidate checkpoint or evaluation result is available yet.

Review is prepared in `tools/research/river_matched_pilot_review_v1.py` (commit
1939d243). Its read-only preflight passes; comparison of source model 78 against
itself also passes with zero root/BTN differences. Run it with `--run` only
after the pilot result exists. It validates full state, replays chance/archives
on four CPU workers, and recomputes scalar gains; it does not rerun neural
inference or an independent poker engine. It preserves registered intervals.

Read RIVER-PILOT-INTERPRETATION.md: the two-update pilot can change postflop play
but cannot yet change the evaluated BB root or exact BTN initial shove response.
Those changes need at least three/four new joint updates respectively to enter
the played bank. Only 2.4691% of the present bank's unconditional mixture weight
can differ. Its generic confidence interval is also too wide to establish small
edges. Size a longer matched continuation from actual runtime/storage, using
fresh registration and evaluation; do not promote this pilot as range accuracy.

Commit c89eea47 derives and checks a prospective shared-policy payoff bound.
PAIRED-MIXTURE-BOUND.md records its proof, assumptions and limitations. The
128-tree CPU control passes; current pilot intervals remain unchanged. A future
evaluation still needs verified full bank identities, common inference/context,
and a prospective numerical-error policy before using the tighter bound.

No production changes, pushes or historical deletions. Goal remains active.

## Recovery execution at 22:13 Adelaide

The v1 process/session 94808 / 34932 terminated with exit code 1 during the
qualification replay: `future.result(timeout=120)` raised TimeoutError. This is
confirmed terminal, not an observation assumption. Interruption evidence is
`river-matched-training-pilot-v1-interruption-21eaeebd.json` and is committed.

One complete candidate qualification update is available (366.141 seconds;
307.281 seconds physical pipeline, 36.328 fitting, 11.406 publication). Its
workers took 115-153 seconds, exposing the too-short parent wait. The failed
replay never published a checkpoint or advanced scientific candidate progress.

Commit 32ba09aa adds guarded future waiting and an explicit recovery wrapper.
Six direct wait/failure/deadline/priority checks pass. New wait pipelines differ
only at the future-wait calls and helper import. Existing worker/native limits
remain; parent polls every two seconds with a bounded 1,200-second wait.

NEW live runner:

- Exec session 22398; PID 72252; creation Unix time 1790599187.0651104.
- Command: river_matched_training_resume_v2.py --run --wait.
- Execution amendment: river-matched-training-pilot-v1-execution-v2-registration.json.
- Same scientific registration, study store, four workers and fresh test design.
- Last verified live via exec handle AND process identity. Acquired its lock and
  was refreshing global storage inventory; old status may remain visible until
  admission/restoration finishes. Do not interpret stale status as process death.

Resume reuses A-baseline's complete updates 79/80. A-river restarts from its
published source-78 state and performs ONE fresh replay against the previously
complete qualification-79 oracle. It must match full state/checkpoint/artifacts
before actual training continues. Original failure evidence is preserved. Prior
incomplete qualification costs are not precisely recoverable; do not invent a
combined qualification time. See RIVER-PILOT-WAIT-RECOVERY.md.

Use river_matched_pilot_review_v2.py --run after the amended result completes.
Its default read-only preflight passes. V2 verifies amendment identities and
reports recovery and known prior qualification costs separately. The source v1
review remains intact but does not account for the amended timing metadata.

An eight-worker dispatch was prepared in commit 00bdb7df, but its v1 control was
rejected BEFORE registration by CPU admission (subsequent probe: production idle,
58.8% CPU, 86.2 GB RAM free). No eight-worker runtime parity has passed. Its v2
control can wait until verified successful pilot termination, or run during
excluded qualification with spare resources. Old `*_pipeline_eight_v1.py` copies
still contain the short waits; do not use them as-is. Base later eight-worker
copies on the corrected wait pipelines and version their control accordingly.

The active goal remains incomplete: no full preflop range-quality improvement
has been established. Continue the existing live session, not the dead v1 one.

## Qualification passed at 22:19 Adelaide

The guarded recovery completed successfully. A-river/qualification.json records
exact restart replay, full checkpoint/state/subbatch agreement with the retained
oracle and 297.546 seconds for this recovery replay/readback. This excludes the
earlier failed attempts and is not an end-to-end speed measurement. The same
session 22398 / PID 72252 is now training A-river iteration 79; A-baseline's
completed updates remain reused. Do not start another runner.

Commit b61a6cc2 adds guarded eight-worker pipeline copies v2 and control v3.
The control passed all 32 repeated fixture tasks (524 events) in 14.875 seconds,
with byte-identical artifacts, no new poker deals and no GPU use. It ran entirely
during the pilot's excluded qualification with verified spare CPU/RAM. Four
pools requested eight workers; 16 distinct workers across pools handled work
(three to five per pool, since these fixtures finish quickly). This does not
prove eight-way simultaneous throughput or full-update speedup.

Use board_training_pipeline_eight_v2.py / river_training_pipeline_eight_v2.py
for a future bounded full-update parity/timing qualification, not the obsolete
v1 eight-worker copies. See EIGHT-WORKER-GUARDED-WAIT-PLAN.md. Do not change
worker counts in the currently registered four-worker pilot. The executed
sources and registration/result raw bytes were checked against their commit.

User reconfirmed light desktop/video GPU sharing. The active runner already
honors that preference while yielding to production solves/heavier use. No
deployment, additional push or historical deletion occurred. After the current
pilot completes, run river_matched_pilot_review_v2.py --run and interpret its
short-horizon/power limits before any longer prospectively registered run.
