# Checkpoint transfer control

The CPU-only pilot control passed on September 25. Eighteen immutable objects
(13.18 MB) reachable from the audited two-update pilot's final checkpoint were
copied from T: into a new directory on S:. Every copied object retained its
content hash, and the original objects remained unchanged.

Restoring both copies produced identical complete played histories, current
models, initial-action accumulators, reservoir contents and random-generator
states. The next 64 action-generator values and eight pilot training deals
also matched. No GPU work or new effectiveness evaluation was performed.

Five boundary tests also passed: complete dependency copying preserves the
source, and corrupted objects, escaping paths, insufficient copy budgets, and
existing destinations are rejected without overwriting destination contents.

This is a state-transfer control, not a qualified continuation of an interrupted
full trial. If the live replication reaches its disk reserve, a continuation
still requires:

1. Confirm terminal processes and identify the last durably completed checkpoint.
   Preserve the unfinished attempt and exclude its incomplete update.
2. Authenticate and independently audit the completed prefix, including its
   original metadata, raw batches, checkpoint, random streams and played bank.
3. Register a new S: continuation with the same original 78-update budget and
   seeds, charge elapsed work against the original runtime allowance, and keep
   the original batch identities. Do not choose a checkpoint based on ranges.
4. Copy only the reachable state objects. Keep earlier raw evidence in its
   original location, with an explicit immutable mapping for the combined
   prefix and continuation. Account for copied bytes and all future reserves.
5. Qualify continuation replay and the combined evidence reader before drawing
   further training samples. Require the complete 78-update audit before the
   registered comparison; no partial-run substitute or automatic deployment.

The active study and its supervisor remain unchanged. Older benchmark archive
compression has been proposed separately and is awaiting approval. This control
does not authorize moving or deleting any existing archive.

Evidence: `checkpoint-volume-copy-control-v1-registration.json` and its passed
result. Registration SHA-256:
`82402630eaf8d45e936ff9b5623fdf3bbcc6a82b7583e510a15ef7bd288faa6f`.
