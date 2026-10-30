# Storage check during the matched training run

25 September 2026. Read-only inspection; no files deleted, no service or
filesystem settings changed, and no training parameters changed.

At completed update 60, the first action-integrated trial's store contained
15,002,941,642 logical bytes and 4,749,383,023 allocated file bytes. All 4,561
files carried NTFS compression. T: reported 126,414,774,272 free bytes, above
the active 40 GB volume reserve. Available host RAM was approximately 107.8 GB.

A subsequent full sweep of the declared research roots measured:

| Root | Logical bytes | Allocated file bytes |
| --- | ---: | ---: |
| S:/GTOpen-research | 868,156,116,776 | 606,969,327,570 |
| T:/GTOpen-research | 273,807,351,582 | 116,648,538,833 |
| T:/Dev/GTOpen/research | 36,260,355,832 | 36,260,355,832 |
| Total | 1,178,223,824,190 | 759,878,222,235 |

The store was still growing during this sweep, so its individual counters are
not simultaneous with the update-60 measurement. The whole-root total is below
the 800 GB research-file ceiling. Each next trial still needs a fresh inventory
and its complete new-store allowance plus the 2 GB reserve before launch.

## Whole-volume free-space discrepancy

T: had reported approximately 146.56 GB free before the short control and
126.41 GB at this check. Declared research allocation grew from approximately
755.16 GB to 759.88 GB over roughly the same period. These are not synchronized
snapshots, but the whole-volume decline is substantially larger than the new
research-file allocation. Do not equate the two, or claim that this check
explains all whole-volume usage.

The allocated-size function was reviewed: it uses Windows
GetCompressedFileSizeW, including its high word and error checking. The current
store's compression flags were independently enumerated. Known repository
directories outside the research root were checked for files modified after
the worker started: cache, target, output and saves had none; .git had about
6.4 MB of modified files. This was not a complete inventory of all other T:
contents, and existing file sizes are not proof of newly allocated bytes.

The available account could read volume capacity but could not complete the
low-level volume/shadow-storage diagnostics. No privilege escalation was
attempted. A short process I/O sample was inconclusive; those counters can
include non-disk I/O and do not identify the destination volume. No other
application is identified as responsible by this evidence.

The discrepancy remains unattributed. Both independent safeguards remain
active: the measured research-file allocation cap and the whole-volume free
space floor. The latter covers usage not represented by research file sizes.
Do not disable compression, remove checkpoints, alter user files or stop other
applications based on this inspection.

## First training completion and read-only audit observation

The first trial completed all 78 updates with exit code 0. Its terminal storage
inventory records 19,522,212,293 logical bytes and 6,150,430,526 allocated bytes,
with all 5,860 files compressed. These records are committed in `ab3b0b10`;
the separate full training audit is still pending.

At the transition into that audit, T: reported 120,421,941,248 free bytes.
Approximately six minutes later, with the reader through update 9, it reported
120,420,679,680 free bytes: a decline of only 1,261,568 bytes. The audit process
was live and advancing. The interval also included the Git commit/push of the
completed result records, so this is not an isolated filesystem experiment.

Free space was substantially steadier during this short read-only interval than
during training. That observation does not identify the earlier excess usage
or establish that it came from another application. No data has been deleted or
filesystem settings changed in response. The next trial retains both resource
admission gates.
