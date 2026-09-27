# Storage admission before the next board-root experiment

The 27 September inventory found a regression in storage admission: the recent
stratified training and evaluation checked their own output budgets and free
volume space, but did not retain the earlier global 800 GB research ceiling.
The queued GPU pipeline control had the same omission. Volume headroom remains
substantial; that is not a substitute for the established allocation budget.

The read-only inventory measured these file allocations:

| Root | Allocated bytes |
|---|---:|
| S:/GTOpen-research, excluding the active evaluation | 627585481816 |
| T:/GTOpen-research | 157816582756 |
| Repository research directory | 34447826821 |
| Total excluding the active evaluation | **819849891393** |

The running evaluation has a separately reserved maximum output of 2179678720
bytes. The inventory deliberately excluded its mutable directory and uses that
whole budget instead. It scanned 317483 other files in 55.31 seconds. See
`board-next-study-storage-snapshot-v1.json`. These are the existing Win32 file
allocation measurements; free-volume guards still cover filesystem overhead.

## Immediate correction

The idle pending queue v1 (PID 4172, creation time 1790500308.735831) was stopped
after verifying that its only child was its console host. It had not started
either output stage. The current evaluation PID 2172 and parent queue PID 4396
were preserved. `board-training-pipeline-queue-v1-superseded.json` records this.

Queue v2 replaces it. After the current evaluation and independent readback, it
can still render the final report. Before starting the GPU pipeline control it
now inventories all three roots and requires room beneath 800 GB for the
control's full 6 GB output bound plus 2 GB reserve. It waits if that check fails;
it does not delete evidence or relax the ceiling. Its separate registration and
source preserve the original queue evidence and all frozen experiment inputs.

The prospective matched experiment likewise requires global storage admission.
No candidate training has started.

## Preservation candidates identified, not yet changed

First-time NTFS compression may recover room while preserving file names,
logical bytes and modification times. A metadata-only scan found approximately
58.1 GB of uncompressed `queries.json`, `profiles.json`, `policies.json` and
`updates.json` in these completed S: research owners:

- sampled-physical-dense-evaluation-v1
- sampled-physical-allin-evaluation-v2
- sampled-physical-hybrid-evaluation-v2
- sampled-physical-dense-pilot-v1
- sampled-physical-allin-pilot-v1
- sampled-physical-hybrid-pilot-v1
- sampled-physical-hybrid-allin-pilot-v1

All three evaluation result records are terminal with 16384 completed test deals;
all four training result records are terminal with 78 completed updates. The
scan excludes files directly bound by the current evaluation and replacement
queue registrations. It does not yet certify the candidates for mutation.

Next prepare a separate preservation amendment and exact per-file hash manifest,
verify owner/result provenance and absence of active owners, and qualify the
compression operation on representative copies. Only then compress the admitted
raw evidence with bounded parallel CPU/I/O work and verify all logical hashes
and metadata afterward. Exclude model/checkpoint objects, user saves, hand
histories, packed archives and active evidence. Disclose the changed physical
storage if historical I/O timings are reused. No deletion or relocation is planned.

Actual savings remain unmeasured. Re-inventory after preservation; do not assume
this candidate set suffices for both the control and the full next experiment.
