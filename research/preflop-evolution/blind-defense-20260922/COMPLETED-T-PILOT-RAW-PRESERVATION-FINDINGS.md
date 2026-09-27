# Another 9.13 GB recovered without discarding evidence

All 3,744 admitted raw JSON files from the completed `root-retained-fresh-pilot-v1`
and `exact-initial-fresh-pilot-v1` runs were preserved with NTFS compression.
A separate full-file readback verified every SHA-256, logical length,
modification time and final allocation. No original files were deleted, moved
or renamed, and no model/checkpoint objects or active registered inputs were
included.

| Measurement | Result |
|---|---:|
| Logical bytes, unchanged | 12,687,188,989 |
| Final allocated bytes | 3,560,566,784 |
| Allocation recovered against the original manifest | **9,126,622,205 bytes (9.13 GB)** |
| Successful version-2 compression invocation | 53.328 seconds |
| Separate full-file readback | 4.766 seconds |
| CPU/I/O workers | 4 |

The first version passed its six-copy test, then stopped because the
owner-activity check mistook its own `compact.exe` child for an active study.
It published no successful batch journals. Version 2 kept the failed attempt
and reverified all original file hashes and metadata. Twenty-one files had
already been compressed, recovering 57,105,363 bytes; this is included in the
cumulative 9.13 GB above, not counted again as retry-only savings.

The corrected check exempts only the current controller's direct System32
`compact.exe /C /Q` children. Six synthetic process-list checks covered that
exemption and rejection of another compactor, a different executable, a different
operation and a historical worker. The new six-copy compression test and its
separate readback passed before the originals were resumed.

The final operation result SHA-256 is
`1c4f04769b19a6833084eec0a3b30cb6ae24dd64ca2e402947f43e5dc9d72816`.
The independent review binds that result and its registration, verifies the
batch journals, and reopens all originals. The `completed-t-pilot-raw-preservation`
version-1 and version-2 manifests and evidence preserve the entire sequence.

This is storage preparation, not evidence of stronger poker play. The fixed
evaluation continued with the same process and settings. Historical storage
timings for the compressed directories now describe their old physical form.
The full next training study still requires its actual-budget prefix, independent
audit and measured storage projection before admission.

## Refreshed global allocation

The read-only version-3 inventory measured 772,945,870,881 allocated bytes outside
the live evaluation directory. It reserved that evaluation's entire
2,179,678,720-byte budget rather than racing its transient files, plus 6 GB for
the queued GPU control, 4 GB for the actual-budget two-arm training prefix, 2 GB
for the throughput control and 2 GB of metadata/headroom.

The resulting projection is **789,125,549,601 bytes**, leaving
**10,874,450,399 bytes (10.87 GB)** below the 800 GB research ceiling. These
reservations fit; the full 78-generation study remains unadmitted. Each future
launch still repeats its source, scientific, resource and fresh storage checks.
The inventory completed in 141.953 seconds and verified the original evaluation
process was still live at both boundaries.
