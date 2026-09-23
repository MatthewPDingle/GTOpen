# Research storage recovery

The user flagged unexpectedly high storage use on 24 September. Storage
management now takes priority over launching another large evaluation.

## Inventory

Read-only inventory, before recovery (decimal GB; logical file sizes):

| Location or artifact | GB |
| --- | ---: |
| S:/GTOpen-research, all experiments | 868.156 |
| T:/GTOpen-research, all experiments | 161.879 |
| Eight strategic segment checkpoints on S: | 493.749 |
| Strategic weighted seed on S: | 61.719 |
| Wide cold replay on S: | 55.046 |
| Long checkpoint experiment on S: | 36.587 |
| Partial older wider evaluation on S: | 33.699 |
| SSD benchmark payload on S: | 17.180 |
| Exact-initial wider evaluation on T: | 75.294 |
| Earlier wider recovery evaluation on T: | 75.237 |

The eight strategic checkpoints each contain approximately 61.719 GB, at
500/1000/1500/2000 iterations for each of two weighting schemes. Equal sizes
do not prove duplicate contents. Do not delete them or substitute hard links
without a dependency and content audit.

At inventory time S: had 83.537 GB free and T: had 110.320 GB free. Logical
file sizes are distinct from actual allocation and will remain unchanged by
transparent compression. The active pilot continues to grow within its
existing 40 GB output cap and 40 GB free-space reserve.

A subsequent allocation sweep measured 820.979 GB for the S: research root;
some older files were already compressed or sparse. In particular, the
33.699 GB partial wider evaluation occupies approximately 13.066 GB. The
493.749 GB strategic checkpoint collection remains uncompressed. The T:
sweep overlapped active compression and training, so it is not a fixed
before/after baseline; use the per-file recovery journal for savings.

## Verified storage controls

`ntfs-evaluation-storage-control-v1` copied six files from a completed batch
into plain and newly compressed directories. All hashes and parsed JSON
matched. Native deterministic replay matched in both directories. Reported
file allocation fell from 27,597,646 to 10,712,441 bytes (61.2% reduction).
This is one fixture, not a guaranteed reduction for all artifacts.

`completed-evidence-compression-v1-control` exercised in-place NTFS
compression on a separate 19,324,472-byte copy. Allocation fell to 8,347,648
bytes. SHA-256, size and modification time were unchanged. A second invocation
exercised verified resumption. No original artifact was changed by this control.

## Recovery in progress

`hu_completed_evidence_compression_20260924.py --run` applies reversible NTFS
compression only to the already completed
`T:/GTOpen-research/later-average-wider-recovery-v1/evaluation` directory.
It first verifies the successful evaluation registration/result relationship.

The job records each file's SHA-256 and allocation before compression, checks
the same hash, logical size and modification time afterward, and journals
verified batches outside the original evidence directory. Resumption checks
the same inventory and contents. It runs below normal priority, checks that
production is idle, and requires 40 GB free. No files are deleted or renamed.
No model, source code, poker data, user save or production session is edited.

The authoritative progress and outcome are in
`completed-evidence-compression-v1-status.json` and, on success,
`completed-evidence-compression-v1-result.json`. Do not infer completion from
this document or from the presence of a registration alone.

## Admission rules for subsequent work

- Finish the already running fixed-budget pilot and its independent audit.
- Do not automatically launch another large evaluation from the current
  continuation watcher; it runs the training audit only.
- New wider-evaluation storage must inherit NTFS compression from creation.
- Measure the actual candidate's output allocation in a small admission batch,
  include a conservative margin, and register both allocation and free-space
  limits before a full evaluation. A fixture's compression ratio is insufficient.
- No unbounded retention of new intermediate files. Record expected growth and
  retention needs in the next evaluation plan before launch.
- Preserve the expensive complete all-in cache, current model/checkpoint bank,
  final results and independent readback evidence. Removing older checkpoints
  or scratch files requires a separately documented dependency decision.

The small two-model wider CPU control is an integration check, not a new
large evaluation or a poker-strength claim. It uses a new compressed directory,
338 training deals and 128 evaluation deals and has the existing 40 GB reserve.

## Interpretation

This storage work does not improve range accuracy. It makes the continuing
accuracy experiments practical without discarding their evidence. The new
root-retention pilot still needs its complete audit and independent evaluation
before any accuracy claim or deployment decision.
