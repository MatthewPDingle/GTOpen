# Action-integrated matched training: implementation and admission

25 September 2026. This implements the already frozen
ROOT-ACTION-INTEGRATED-TRAINING-PLAN.md. It does not amend its learning algorithm,
seeds, counts, accuracy criteria, or resource budgets.

## Completed control evidence

`action-integrated-joint-gpu-control-v1` passed two complete CUDA updates
(1,024 fresh physical deals), plus a replay of update 2 from its preceding
checkpoint (512 replayed deals). Restart reproduced model, reservoir, random
stream and raw native artifact identities. The two updates included the full
8-by-64 sampling geometry and 512 fit steps for each player. CPU/CUDA maximum
policy discrepancies were below 8e-14. Three old or incomplete metadata inputs
were rejected. No production state was changed.

The control, including restart, policy comparisons and storage admission,
took 312.953 seconds. Its 248 files occupy 199,238,288 bytes on disk
(661,139,131 logical bytes); every file is compressed. This is a short
feasibility measurement, not a projection of a complete run's duration.

The independent readback passed all 1,024 root decisions and replayed the
22,795 BB / 3,981 BTN original sampled reservoir insertions. It independently
reconstructed integrated root values, exact jam replacement, centered targets,
policy overrides, random streams and checkpointed state without refitting.
Maximum root-state discrepancy was 3.41e-13 and maximum target discrepancy
5.69e-14. It took 104.329 seconds. The readback reuses the stored native
traversal outputs; it is not a second implementation of poker traversal.

These results qualify execution and restart, not poker accuracy. See the
control registration, result, readback registration and independent-review
JSON files for identities and complete numerical records.

## Execution

`hu_action_integrated_matched_sequence_20260925.py --run` runs, once in order:

1. First matched seed trial, followed by its complete independent readback.
2. Replication matched seed trial, followed by its complete independent readback.

The trainer is `hu_action_integrated_matched_trial_20260925.py --run first`
or `--run replication`. The latter requires the first trial's full readback.
The separate reader wrapper selects the same frozen independent reader for
either output prefix. This sequence does not run wider response evaluations,
select favorable checkpoints, or deploy a result. Any failure stops the queue;
there is no retry. Preserve incomplete evidence for a separate recovery decision.

Each training run has a 21,600-second execution ceiling. The queue also bounds
admission and startup by allowing at most 22,800 seconds for the entire training
controller. Each readback retains its 7,200-second internal ceiling and a
7,320-second supervisor ceiling. These allowances do not add training updates.

The trainer flushes the completed iteration's raw evidence and checkpoint pointer
before publishing `latest.json`. Checkpoint objects themselves are flushed by
the immutable object writer. This reduces exposure to a reboot; it does not
make an incomplete iteration resumable. The short control verified restoration
at a completed iteration boundary.

## Storage and activity

An inventory after the control measured 755,161,224,859 allocated file bytes
across the three research roots. A fresh global inventory is mandatory before
**each** training run: actual use + the full 12 GB allocation cap + 2 GB reserve
must fit within 800 GB. Each run also has a 40 GB logical-file cap. A compressed
store is created before writing any outputs. Runtime monitoring checks space,
allocation and compression; completion checks every file again.

Require at least 40 GB free on T:, 20 GB available host RAM and 3 GB available
GPU memory. The first start also reserves its whole 12 GB allowance beyond
the free-volume floor. The shared research lock serializes GPU training; the
sequence holds that lock during the CPU readback. Production 56708 must remain
idle throughout. No production process is restarted or modified.

After both audited trials, the next work is the preregistered restricted endpoint
evaluation and all-class cross-seed comparison. A reduction in random-seed
disagreement alone cannot establish accurate call/raise ranges.
