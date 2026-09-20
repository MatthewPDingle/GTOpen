# Whole-study checkpoints before day-long training

Design registration only; not implemented or qualified. Per-continuation SSD parking is not a whole-study checkpoint. Do not describe its files as a restartable solve.

An unapplied implementation proposal is now recorded in `checkpoint-v1-proposal.json` and the associated `checkpoint-v1-*-proposal.rs` files. It targets the all-RAM 112-board study: SSD is used for explicit checkpoints, while per-sweep SSD parking is unchanged. Export/import refuses a disk-backed entry rather than silently adding unmeasured disk-copy memory or writes. Extending checkpoint support to spill-backed training would need its own resource and exactness qualification; it is not required to resume the currently planned all-RAM study.

## Required state and identity

At a completed two-player iteration boundary, retain every continuation's four canonical f32 arrays and iteration, plus every preflop regret, accumulated strategy and current policy f64 array. Save raw little-endian float bits, rather than relying on JSON decimal round trips. Retain the absolute completed iteration so the next update uses the original discount schedule. The fixed incoming ranges, exact ordered board list and weights, subtree, all game/tree settings, solver algorithm, suit projection policy and executable/source identity belong in the checkpoint identity. Verify all against the requested resume inputs before exposing restored state.

Do not persist GPU addresses or driver handles. Rebuild GPU metadata from the identical input, then load and verify each canonical array against the rebuilt shapes. Reject any unavailable, corrupted, duplicate, mismatched or unexpected record. Verify allocation bounds from trusted rebuilt shapes before reading payload lengths. Avoid keeping a second whole forest in RAM.

## Commit and failure behavior

Use a fresh uniquely named checkpoint directory under S:/GTOpen-research. Write each bounded per-game record with identity, shapes, iteration, payload checksum and explicit file length. Flush and verify all records. Write the preflop state and final index, then publish a complete marker only after every record is committed and verified. A loader accepts only complete checkpoints, never a directory merely containing some state files. Preserve the previous complete checkpoint until the new one has passed an independent reopen check. Do not overwrite or delete production saves. A checksum detects accidental damage; it is not an authenticity claim.

Checkpoint at announced coarse intervals, rather than after every player sweep. Include checkpoint reads and writes in the run's storage budget. A 62 GB state snapshot is already expensive enough to measure; record actual full save and restore costs before choosing a long-run cadence. Preserve any interrupted candidate directory for diagnosis and never treat it as complete.

## Qualification before broader training

On the existing three development boards, compare an uninterrupted 500-iteration run with a split run saved at 100, process-exited, reloaded in a fresh process, and continued through 500. All scientific checkpoint values must match the original trajectory exactly. Check full preflop and continuation float bits immediately before save and immediately after load, including signed zero. Check a second split point so the discount schedule is exercised independently. Keep timing outside the correctness comparison.

Negative controls: missing final marker; missing record; truncated, flipped or appended payload; swapped board/pot files; wrong weights/subtree/algorithm/executable identity; wrong shapes/iteration; stale mixed-generation index; failed write leaving the previous complete checkpoint intact. Production must remain idle for guarded research, and only owned research processes may be stopped.

Only after these checks may a long study rely on resume. This gate does not establish poker accuracy or qualify any change to the research solver's numerical method.

## Integration outline

Use the qualified explicit stored solver. Extend its existing per-game disk format with a verified reopen descriptor rather than persisting GPU handles. Rebuilt game shapes and the expected board/pot key must constrain the descriptor before payload allocation. Export or import one continuation at a time, retaining only one game's temporary copy, and check that every continuation is at the same completed iteration. Keep the checkpoint directory independent from any SSD parking directory so replacement of live parked generations cannot retire a checkpoint file.

In the research example, persist the preflop `regrets`, `sums` and current `sigma` arrays as raw f64 bits with shape and checksum checks. Recompute fixed entering weights and the root normalizer from the identical inputs, then verify their bits against the checkpoint. Guard the native process with externally verified executable/input hashes; the checkpoint index must carry those identities. Resume the loop at completed iteration plus one, using the original absolute iteration in every discount calculation. Evaluate once at the restored boundary to compare the resumed scientific output with the uninterrupted boundary, then continue normally. Timing counters and output history are not solver state and must be identified separately.

The second split point should be outside the existing reporting schedule (for example 37) to detect accidental reliance on reporting boundaries. Check that a fresh process can open the complete checkpoint; merely restoring into the still-running process is insufficient. Do not deploy this as an ordinary saved-game format.

## Proposed executable qualification sequence

Apply and compile only after the phase diagnostic has finished and its result has been reviewed. Preserve one immutable executable for every run. Supply a guarded identity file containing the executable, frozen source manifest, subtree and board-manifest SHA-256 values; the native helper also fingerprints its actual executable and raw input files. This is accidental-mismatch detection, not an authenticity guarantee.

Use the existing three development boards and all-RAM mode. Run an uninterrupted 500-iteration reference with a final checkpoint. Run separate fresh processes to 100 and 37, save each, then restore each in another fresh process and continue through 500. Immediately after each restore export a distinct copy before training; compare all preflop and per-continuation record bytes against the saved originals. Compare the final two resumed snapshots byte-for-byte with the uninterrupted final snapshot, and compare every overlapping scientific checkpoint against the original retained trajectory. A zero-training restore at its saved iteration is useful for failure controls but cannot replace the continued-trajectory tests.

Use fixed derived filenames, raw f32/f64 payloads, independently rebuilt array shapes, per-record checksums, an index checksum and a completion marker written last. The loader rejects unexpected or missing directory entries. Any restore error terminates the research process before it can use a partly imported study. No production load/save API changes. Limit the entire initial three-board qualification to 16 GiB of checkpoint writes, track actual bytes across every saved and restored-copy directory, and retain all prior complete snapshots. The per-sweep state-write cap remains zero. The proposed native per-snapshot cap must be accompanied by an outer cumulative qualification budget.

The proposal has not been compiled or run. A successful parser check alone would not qualify its format, resource bounds or numerical behavior.
