# Reusing earlier checkpoint objects during a continuation

Native checkpoint publication validates the entire played bank and republishes
nested model envelopes. A new continuation directory containing only the latest
model cannot save a complete checkpoint. Copying the full history would also
consume scarce storage. `checkpoint_overlay_store_v1.py` supplies a scoped,
dedicated-process adapter: reads may use authenticated predecessor objects;
identical publication requests reuse those objects; genuinely new objects are
written only inside the caller's new owned directory. Original objects are never
linked, rewritten, retired, or deleted. The returned provenance records the
predecessor and every reused object. The resulting directory is not standalone:
its predecessor must remain available and authenticated.

## Discovered first-checkpoint recovery defect

The first CPU test failed before checkpoint publication. At update 8, the
original training cadence archived **four** reservoir objects: the two empty
initialization objects and the two trained objects. The earlier compact restore
adapter required exactly two archive members. Its previously qualified cases
(baseline 72/78 and corrected 16) did not exercise this first boundary.

The failed `checkpoint-overlay-control-v1` registration and result are retained.
The existing restore implementation remains unchanged. The separately versioned
`compact_checkpoint_restore_v2.py` accepts the four-object layout only at update
8, loads exactly the two checkpoint-referenced reservoirs, and independently
validates that the other two objects are empty, have the configured capacity and
players, and retain their original configured RNG states. It does not silently
select a reservoir by filename or discard arbitrary extra objects.

## Completed CPU control

`checkpoint-overlay-control-v2-result.json` passed in 173.891 seconds including
storage admission. The fixed cases were first-seed baseline update 8 and
first-seed corrected update 8. For each case:

- Restore from the original compact archive using the version-2 adapter.
- Save through the native checkpoint writer and new object overlay.
- Require the exact original checkpoint reference and byte hash.
- Restore through the native reader and compare the complete played bank,
  next model, all retained reservoir arrays, sampler/RNG states, and root/exact
  response accumulators.
- Verify historical played models were reused and absent from the new directory.
- Reject a publication request aimed at the original source directory and
  restore the process's readers/writer after that failure.

The baseline reused 40 immutable objects; the corrected case reused 30. Each
published just two reservoir objects (13,300,804 and 13,576,090 bytes respectively).
No earlier played models were copied. Both cases validated the two extra startup
reservoirs without loading them as the current training state.

Admission excluded the actively changing training directory from its inventory
and reserved that run's entire registered 4.250 GB output cap instead. With the
new control's 160 MB cap and the existing 2 GB reserve, projected allocation was
799,896,792,700 bytes, below the unchanged 800 GB ceiling. All other research
roots were counted. The control ran at below-normal CPU priority with CUDA
disabled, preserved original frozen inputs, and did not interrupt training.

## Limits and next steps

This qualifies the two stated checkpoint round trips using original raw
predecessor objects. It does not qualify an overlay over an archived predecessor,
a resumed fitted update, a continuation controller, or better poker ranges.
The GPU fit replay remains pending while training is active. If recovery is
needed, the continuation must bind its predecessor, retain the original failure
and charged runtime, replay completed updates exactly, and complete all four
78-update arms before the unchanged fresh payoff evaluation.
