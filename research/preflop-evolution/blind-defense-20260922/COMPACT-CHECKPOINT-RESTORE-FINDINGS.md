# Restoring compact checkpoints without disk extraction

`compact_checkpoint_restore_v1.py` adds a read-only adapter for the existing
checkpoint restoration code. It verifies the completion marker, metric,
checkpoint pointer, reservoir archive, and requested object hashes. Reservoir
bytes are supplied from the archive in memory. Model objects can be read from
their originals or an authenticated completed-object archive.

The adapter temporarily replaces only the current process's byte readers while
calling the original checkpoint validators and state reconstruction. It restores
those readers on success or failure. It must run in a dedicated process;
concurrent use in that process is rejected. It changes no running worker's code,
performs no extraction or deletion, and does not start or resume training.

## Completed CPU control

`compact-checkpoint-restore-control-v1-result.json` passed in 212.875 seconds:

| Snapshot | Verification |
| --- | --- |
| Seed 9266201 baseline, update 78 | Same state as the native restore from original raw files, including every retained reservoir array, both reservoir RNGs, action RNG, deal sampler, accumulated root/exact-response state, complete played bank, and next model |
| Seed 9266201 baseline, update 72 | Exact archived reservoir arrays; next 512 physical deals and all eight action seeds reproduce saved update 73 |
| Seed 9266201 corrected, update 16 | Exact archived reservoir arrays; next 512 physical deals and all eight action seeds reproduce saved update 17 |

Non-checkpoint and boolean update indices, an unknown treatment, and a changed
fit configuration were rejected. The byte readers were restored after the
rejection checks as well as successful restorations. No files were extracted
or retired; the GPU and production app were untouched. The two replayed chance
streams are already-used training data, not new evaluation samples.

The registration hash is
`ac3f2b369ef02149692915614f4d8515c79feb5da4b9f3bd92a92351f136f570`.
The result contains source-object identities for each snapshot. A supplemental
post-completion source-integrity record checks the original frozen training
inputs and identifies the newer archive-reader dependencies; it is not an
independent scientific audit or a retrospective pre-run registration.

## What is still required for continuation

This control qualifies restoration and preservation of the next chance stream.
It does not qualify a resumed neural fit, a replacement training controller,
terminal-state detection, interrupted-update routing, or composite trial
provenance. Before using it to continue a resource-stopped run, require a real
fit replay and the quiescent, separately registered continuation procedure
described in `SHOWDOWN-COMPLETED-STORAGE-REVIEW.md`. Preserve the original
configuration, fixed 78 updates per arm, seeds, prior runtime charges, and all
completed evidence. Current matched training remains unchanged.

## Prospective GPU fit replay

`compact_checkpoint_fit_replay_20260926.py` is prepared but has **not run**.
After original training is terminal and the research GPU lock is free, its
fixed cases restore baseline 72 and corrected 16, then repeat the original
updates 73 and 17 with the unchanged CUDA fitter, configuration, native
executables, chance streams, and batch labels. It requires:

- Exact next-model content hashes, scientific metrics, and every archived
  original batch artifact's bytes. There is no numeric tolerance.
- Exact parsed initial-policy values. Only JSON object key order may differ;
  each initial file is separately checked against its metric hash.
- Only the four explicitly named elapsed-time fields may differ in metrics.
- Original source hashes unchanged, production idle, RAM/GPU/disk reserves,
  exclusive lock ownership, 30-minute worker limit, and a 400 MB output cap
  admitted under the existing global 800 GB limit and metadata reserve.

The control writes a separate owned replay directory. It never edits original
training evidence, resumes an arm, or draws fresh evaluation deals. New replay
batch duplicates may be retired only after exact comparison and durable archive
readback. A storage admission failure requires quiescent owned retention or a
new plan; it does not authorize increasing the limit.

`compact-fit-replay-preflight-v1-result.json` records completed **CPU-only**
preflight checks: an actual `--run` invocation refused the live training lock
before creating any replay artifacts, and the original controller remained
alive. Comparisons rejected changed model hashes, batch hashes, fit losses,
initial probabilities, and an unexpected metric field for both fixed cases.
Named timing changes and initial reference key ordering were accepted. All 930
original frozen inputs were unchanged. These checks do not establish that a
GPU fit will replay exactly; that remains the next recovery qualification.
