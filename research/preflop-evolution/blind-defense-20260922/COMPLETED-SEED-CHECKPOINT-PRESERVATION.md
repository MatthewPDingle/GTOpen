# 27.84 GB recovered from the completed seed checkpoint

The historical `strategic-weighted112-seed-v1/iteration-20` checkpoint is now
stored with transparent Windows LZX compression. Its original 227 paths and
logical contents remain unchanged. No original file was deleted, relocated or
rewritten into a different checkpoint format.

| Measurement | Result |
|---|---:|
| Original logical bytes, unchanged | 61,718,677,329 |
| Allocated bytes before | 61,718,677,329 |
| Allocated bytes after | 33,882,267,769 |
| Allocation recovered | **27,836,409,560 bytes (27.84 GB)** |
| Compression and per-file checks | 445.718 seconds |
| Separate complete readback | 23.843 seconds |
| CPU/I/O workers | 4, below normal priority |

The historical seed had already passed its original 20-iteration, 112-board
save/restore check. Its existing review and snapshot provide the expected
SHA-256 of every file. Before this preservation pass, the exact file set and
completed owner were checked, and all four current evaluation/follow-up
registrations were checked for directly bound inputs in this checkpoint.
No historical owner process was active. The running evaluation and its queues
were preserved.

The compression operation uses the same Windows LZX command as the earlier
qualified checkpoint compression. Four low-priority workers verify the
historical hash, logical size and modification time before and after each
file; metadata files are checked without compression. Every file has a journal.
Path checks reject traversal and unrecognized checkpoint names, and the owner
check exempts only this controller's exact compression children.

The separate reader reopens all 227 originals, independently recomputes every
historical hash, and checks sizes, timestamps, allocations and journals. Its
result binds the operation result and registration. This is byte preservation;
it does not repeat a native model restore or establish new poker accuracy.

Evidence:

- `completed-seed-checkpoint-preservation-v1-registration.json`
- `completed-seed-checkpoint-preservation-v1-result.json`
- `completed-seed-checkpoint-preservation-v1-independent-review.json`
- `completed-seed-checkpoint-preservation-v1/` per-file journals

The operation result SHA-256 is
`b89dc41bb363a9ccbad044d5e7f5639e0bd931a7849485ba9ad4eb45f81aff61`.
The original process identity is retained in the launch record; the operation
and separate reader have now finished.

## What this changes for the next study

This recovery adds 27.84 GB of allocation headroom. It is additional to the
earlier raw-JSON preservation savings, not a recount of them. Some of the large
binary candidates were already transparently compressed even though their
ordinary file attributes did not carry the NTFS compressed flag. Actual file
allocation, existing results and current metadata were used to distinguish
them; their logical sizes were not credited as new potential savings.

No new full-training admission is asserted here. The queued prefix still makes
its fresh global inventory and retains its 4 GB allowance plus reserve. The
78-generation continuation still needs actual prefix measurements, independent
readback and a full storage projection. Historical checkpoint I/O timings now
refer to the earlier physical storage form and should not be reused as current
performance measurements without remeasurement.
