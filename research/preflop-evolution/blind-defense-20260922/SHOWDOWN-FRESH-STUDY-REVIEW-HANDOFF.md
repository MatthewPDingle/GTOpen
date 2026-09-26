# Automatic independent review after the fixed study

The separately registered `showdown_study_review_handoff_20260927.py` watches
the exact admitted study controller and worker by PID, creation time, command,
role, and parent relationship. It does not change the running evaluator or draw
samples. Live identity, reused-PID rejection, and incomplete-study rejection were
checked before launch. Status updates use the previously tested atomic writer.

After both study processes exit, the handoff requires the completed successful
65,536-deal result, successful controller status, correct registration hash,
2,048 archived batches and summaries, unchanged registered handoff inputs,
released research locks, and idle production. It then runs the existing
independent reviewer with `study`. The reviewer retains its full chance-stream,
transport, archive, payoff/statistical consistency checks and six-hour limit.

The wait ceiling is 86,520 seconds, allowing the study's unchanged 24-hour cap
plus exit overhead. The review outer ceiling is 21,720 seconds, allowing its
unchanged six-hour cap plus startup/exit overhead. The wrapper cannot retry,
alter a failed study, extend the sample count, promote a result, or deploy a
model. It preserves failure evidence. It is a local process and does not survive
a reboot. On success, interpret all final contrasts and the descriptive stability
comparison; successful review alone is not a poker-strength finding.
