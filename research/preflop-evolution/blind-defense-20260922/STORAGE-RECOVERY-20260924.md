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

A separate repository inventory found another 34.799 GB of logical files
under `research/preflop-evolution` and 1.438 GB under `research/autoresearch`.
These were outside the two large storage roots in the initial inventory.
The global admission wrapper includes the whole repository research directory
as well as both external roots; it measures allocation rather than assuming
logical size equals space occupied.

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

Binary checkpoint storage behaves differently. A copy of the 634,475,312-byte
`entry-111-generation-0.bin` record used 537,894,912 bytes with NTFS compression
(15.2% reduction). Windows transparent LZX used 355,512,320 bytes (44.0%
reduction). The LZX control compressed, hashed, decompressed, hashed, then
recompressed the copy; every logical SHA-256 matched the original. The original
file was unchanged. This is a storage roundtrip, not a native full-checkpoint
restore test or a collection-wide savings estimate.

## Recovery

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

The T: pass completed successfully in 1,024.297 seconds. All 18,398 files
were verified unchanged. Reported allocation fell from 75,236,980,271 to
29,146,038,865 bytes, recovering **46,090,941,406 bytes (46.1 GB)**. No files
were deleted. The final result and per-file journals preserve the measurement
and content checks.

After that job completes, `hu_completed_checkpoint_lzx_20260924.py` can process
one reviewed S: checkpoint at a time. Its allowed names are only the eight
strategic snapshots listed above. Each file must match the SHA-256 in the
original successful segment review before and after compression. The script
keeps names, logical bytes, modification times and all checkpoint files;
per-file allocation journals live separately. The first intended checkpoint
is `strategic-weighted112-500-v1`. A source file remains directly readable
through the Windows filesystem; no archive extraction or path substitution
is introduced. Do not infer a completed S: recovery until its result exists
and its process has exited successfully.

The first S: checkpoint compression completed after the successful T: pass.
All 227 files matched their original reviewed hashes. Allocation fell from
61,718,677,567 to 35,329,917,287 bytes, recovering **26,388,760,280 bytes
(26.4 GB)** in 1,123.516 seconds. Combined verified recovery from these two
completed passes is **72,479,701,686 bytes (72.5 GB)**. These are gross savings;
the active pilot and copied controls also consume space.

`hu_checkpoint_storage_queue_20260924.py --run` now watches that first process
by its PID and creation time, then runs the seven remaining reviewed snapshots
sequentially. Its order is weighted/equal at 500, 1000, 1500 and 2000 iterations.
It verifies every completed worker's per-file receipt against the original
review hashes. The queue has a 12-hour ceiling and stops on production activity
or the first failure; there is no automatic retry or deletion.

A separate second T: pass is prepared in
`hu_completed_evidence_compression_v2_20260924.py`. It targets only the completed
`exact-initial-wider-study-v1/evaluation` directory. Its copied-file control
passed with unchanged hashes. Do not start this pass until the S: queue exits;
keep compression jobs sequential. Its full result does not yet exist.

The authoritative progress and outcome are in
`completed-evidence-compression-v1-status.json` and, on success,
`completed-evidence-compression-v1-result.json`. Do not infer completion from
this document or from the presence of a registration alone.

## Admission rules for subsequent work

- Finish the already running fixed-budget pilot and its independent audit.
- Do not automatically launch another large evaluation from the current
  continuation watcher; it runs the training audit only.
- New wider-evaluation storage must inherit NTFS compression from creation.
- Use the new global storage admission wrapper for the next full evaluation.
  The three research roots, the full planned allocation cap and a 2 GB allowance
  must fit within 800 GB; finish further lossless compression if needed.
- Measure the actual candidate's output allocation in a small admission batch,
  include a conservative margin, and register both allocation and free-space
  limits before a full evaluation. A fixture's compression ratio is insufficient.
- No unbounded retention of new intermediate files. Record expected growth and
  retention needs in the next evaluation plan before launch.
- Preserve the expensive complete all-in cache, current model/checkpoint bank,
  final results and independent readback evidence. Removing older checkpoints
  or scratch files requires a separately documented dependency decision.

The first successful three-root admission check measured 946,134,332,868
allocated file bytes while training and compression continued. With the full
46,090,941,406-byte planned evaluation cap and 2 GB allowance, its projected
total was 994,225,274,274 bytes. Admission correctly returned false against
the 800 GB limit. This moving snapshot is a refusal check, not a launch receipt;
the wrapper must measure storage again before allowing the next full study.

The small two-model wider CPU control is an integration check, not a new
large evaluation or a poker-strength claim. It uses a new compressed directory,
338 training deals and 128 evaluation deals and has the existing 40 GB reserve.
It has now passed: all 195 output files inherited compression, with logical
size 193,561,122 bytes and reported allocation 56,433,576 bytes (70.8% less).
Independent scalar readback reconstructed all six comparison intervals and
all 169 response choices, with maximum numerical discrepancy
1.14e-13 bb. It checked stored native payoffs, not an independent implementation
of poker traversal or neural inference. The run took 143.938 seconds.

## Interpretation

This storage work does not improve range accuracy. It makes the continuing
accuracy experiments practical without discarding their evidence. The new
root-retention pilot still needs its complete audit and independent evaluation
before any accuracy claim or deployment decision.
