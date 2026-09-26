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
