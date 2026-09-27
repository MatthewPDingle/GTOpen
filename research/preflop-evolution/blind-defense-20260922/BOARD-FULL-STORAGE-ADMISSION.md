# Storage check for the complete board-root study

The full continuation now has a prepared storage-admission command:

```powershell
& 'C:\Program Files\Python312\python.exe' tools/research/board_full_storage_admission_v1.py
```

The default is read-only readiness. Add `--run` only after the genuine two-arm,
two-generation prefix, its independent readback and the follow-up queue finish.
It writes `board-matched-full-storage-admission-v1.json` only if the complete
remaining 78-generation experiment fits. It does not launch training.

The calculation includes:

- All existing candidate files, including restart replays and failed attempts.
- The largest actual candidate or mature historical generation archive, with
  50% growth allowance and an extra 4 KiB per file for allocation rounding.
- Two full 262,144-row sample buffers at every remaining generation. Each row
  uses 137 bytes; each serialized buffer receives another 64 KiB for metadata.
  The estimate takes no credit for future filesystem compression.
- Model and checkpoint JSON growth, using both candidate and mature controls.
- At least 2 GB for temporary writes and growth, 8 GB for full readback and
  evaluation, 2 GB for the separately prepared timing experiment, and 2 GB
  of global headroom.

All 152 remaining updates are budgeted. Existing candidate bytes are already
part of the global inventory and are charged only once. Both the 800 GB global
research ceiling and available S: space must pass. A rejected projection is
preserved separately and cannot act as admission. The continuation repeats its
own fresh checks and enforces storage limits at generation boundaries.

Archive and JSON growth allowances are estimates, not mathematical worst-case
bounds. If real growth exhausts the admitted budget, preserve the checkpoint
and reassess storage; do not reduce the registered generation count or silently
discard evidence. Full sample-buffer payload is explicitly bounded by capacity.

## Validation

`board_full_storage_admission_control_v1.py` passed in 0.36 seconds using CPU
only. The production serializer wrote a full buffer of 35,917,004 bytes, below
the 35,979,264-byte per-buffer allowance. Empty and one-row buffers also fit.
Checks covered mature-generation growth, retained failed attempts, avoiding
double counting, rejecting a full disk budget, invalid inputs, and refusing to
publish admission while the actual prefix is missing.

Evidence: `board-full-storage-admission-control-v1-result.json`. This qualifies
the preparation and sizing mechanics only. No actual full-study admission or
training launch has occurred, and this provides no evidence of playing strength.
