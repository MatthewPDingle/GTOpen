# Matched river pilot: explicit wait-handling amendment

2026-09-28. Scientific configuration, source states, four-worker counts, test
budget and fresh test seed are unchanged. No final evaluation deals were drawn.

The original process 94808 exited with TimeoutError while awaiting a live CPU
worker during the qualification replay. The parent used a 120-second one-shot
wait; observed completed candidate workers already took 115-153 seconds in the
earlier successful update. The old attempt and its interruption record remain.
Both baseline scientific updates are complete and will be reused. The candidate
scientific progress marker is still the original complete boundary 78.

guarded_training_future_v1.py polls in two-second intervals, preserving resource
checks and propagating actual task errors, including a child's own TimeoutError.
Pending work has a bounded 1,200-second parent wait, aligned with the existing
worker lifecycle limit. Native-call deadlines, worker limits, GPU/production
priority, memory/storage limits and four-hour invocation limit are unchanged.
Finished work is not turned into failure merely because admission delayed its
readback. Six direct checks of these cases pass.

The two versioned wait pipelines differ from the original AST only at the
physical/board future-wait calls and the helper import. Policy generation,
targets, RNG, fitting, ordered insertion and joint publication are unchanged.
The explicit resume wrapper registers new source hashes alongside the original
scientific registration; original sources and registration remain frozen. Final
results will name and hash the execution amendment.

Resume validates the fully published qualification update 79 as an oracle and
runs one fresh update from the published source-78 state. It must reproduce the
entire oracle state, checkpoint and subbatch artifacts exactly before training
continues. The failed replay is never adopted as training. The preserved v1
source/control flow and complete oracle establish that the earlier deliberate
stop and caller-state comparison passed before the later observation timeout.

This avoids repeating both completed baseline updates and all three qualification
attempts. Qualification replay/recovery costs remain separate from scientific
training. The earlier failed invocation's total qualification wall time was not
retained precisely; report the recovery time and known complete-update time
separately, without inventing a combined total.

The prepared eight-worker dispatch is NOT enabled by this amendment. Its runtime
parity check was deferred due CPU load and remains pending. Old eight-worker
pipeline copies still contain the old wait calls and must not be used as-is.
Qualify wider dispatch from these corrected wait pipelines in a later version.

No deployment, extra GitHub push, source-data deletion or production changes.
