# Resource use while training and auditing overlap

A five-minute observational sample followed the original trainer and the first
arm's audit by PID and creation time. Both stayed live. Training advanced from
update 10 to 16 of the second arm; the audit advanced from update 13 to 24 of
the completed first arm.

Twenty samples at approximately 15-second spacing showed:

| Measure | Observed value |
| --- | ---: |
| Mean whole-system CPU use | 21.82% |
| Mean sampled GPU utilization | 14.45% |
| Maximum sampled GPU utilization | 92% |
| Maximum sampled VRAM use | 2,566 MiB |
| Minimum available system RAM | 110.62 GB |

The GPU readings are snapshots and the CPU readings cover one second each.
This is not an isolated benchmark or a continuous GPU occupancy measurement.
The early second-arm fitting phase is shorter than fitting with full reservoirs,
so this should not be generalized to the entire training run. Nevertheless,
substantial hardware headroom remains; CPU/GPU work is visibly phased.

## Overhead outside the recorded update timer

For completed second-arm updates 10-16, the recorded update work averaged
34.70 seconds, while consecutive directory-creation boundaries averaged
47.14 seconds. The difference averaged 12.45 seconds (about 26% of that elapsed
time). These filesystem timestamps are an approximate boundary measurement.
The difference includes checkpoint restoration/verification, storage scans,
resource guards and other loop overhead. It is not all attributable to scanning.

Inspection found that each storage scan rebuilds Win32 bindings and resolves
paths repeatedly for every file. A separately versioned candidate caches the
binding and uses directory-entry metadata, while keeping logical size, allocated
size, compressed-file counts and guards. It also rejects reparse points rather
than following directory junctions.

## Completed-arm scan control

An original / candidate / original sequence scanned the same completed first
arm, containing 7,415 files. All four reported totals and the explanatory note
matched exactly across all three scans. The candidate also rejected the broad
research root and a path outside it. No files were changed.

| Scan | Seconds |
| --- | ---: |
| Original before | 5.657 |
| Cached directory scan | 1.296 |
| Original after | 6.985 |

This is a measured improvement in the storage check, not in end-to-end training.
Concurrent training/audit activity and guard cost affect the timing. The live
trainer remains on its registered implementation; no restart or in-process
patch was made. Use this candidate in a future qualified execution version and
measure whole-update time before claiming a training speedup.

Evidence: `weighted-overlap-resource-sample-v1.json`,
`weighted-update-overhead-observation-v1.json`, and
`ntfs-storage-scan-v2-control.json`. None is evidence of improved poker accuracy.
