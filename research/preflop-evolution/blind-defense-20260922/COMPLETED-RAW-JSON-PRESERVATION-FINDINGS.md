# Completed evidence preserved; storage overrun corrected

First-time NTFS compression preserved all 16704 admitted raw JSON files across
the seven completed research owners. No files were deleted, moved or renamed.
Every logical SHA-256, length and modification time matched before and after.
Model/checkpoint objects, user files and current registered evaluation inputs
were excluded.

| Measurement | Result |
|---|---:|
| Logical evidence bytes | 58065212295 |
| Allocated bytes before | 58065212295 |
| Allocated bytes after | 20233162752 |
| Recovered allocation | **37832049543 bytes (37.83 GB)** |
| Compression wall time, four workers | 164.48 seconds |
| Separate full-file readback, four workers | 24.00 seconds |

The preliminary eight-copy control also passed, reducing 25652049 bytes to
8642560 allocated bytes. Its separate reader verified every copy. Wrong-hash
and outside-evidence-path checks rejected the invalid requests.

The full operation result SHA-256 is
`d342b34fd249480d3ef0feab505d726f55efd62cf7e812a12fcdae4b93508d6e`.
The separate reader binds that result and registration, checks every batch
journal, and reopens all 16704 files to independently hash their complete logical
contents and verify metadata/allocation. See the
`completed-raw-json-preservation-v1-*` manifest, registrations, result and
independent-review files, plus the immutable per-batch journal directory.

## Fresh total allocation

The post-preservation inventory measured **782050681736 bytes** outside the
active evaluation directory. Reserving that evaluation's full 2179678720-byte
budget, the queued GPU control's full 6 GB budget and the existing 2 GB reserve
gives **792230360456 bytes**, below the 800 GB ceiling. The inventory took
30.75 seconds. `board-next-study-storage-snapshot-v2.json` contains the per-root
measurements. The queued control will repeat its own global gate before launch.

This admits the next bounded control, not the entire proposed matched training
study. The latter still needs measured allocation projection and adequate global
headroom; unused control budget can only be released after its actual completed
allocation is known.

The main evaluation process stayed live and advanced during preservation. One
overlap snapshot showed 29% total CPU utilization and 12% GPU utilization; these
are utilization samples, not a performance benchmark or proof of zero slowdown.
No GPU training, model update or production session change was performed by the
preservation operation. Its four CPU/I/O workers finished before the separate
four-worker readback began.

Historical disk-throughput measurements on the compressed directories now
describe their old physical form. The logical scientific evidence remains
identical, but any future storage benchmark must disclose the compression.
