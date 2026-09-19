# SSD storage study — in progress

Production 56708 is unchanged. This study tests storage for the isolated connected preflop/postflop research solver.

## Completed gates

- **Exact disk parking:** all 720 board/player passes matched resident reference values and all four state arrays bit-for-bit. Nine format/failure checks passed. Unused candidate pinned staging was released. Six small states occupy 113.24 MB rather than 180.13 MB before suit-based packing. The guarded run took 97.89 seconds; buffered reads may hit Windows cache. See `ssd-paging-v1-review.json`.
- **Physical SSD I/O:** both 16-GiB write/read repetitions passed full CRC checks using aligned unbuffered, write-through access to a new regular scratch file on S:. Combined direct I/O rates were 1.489 GB/s write and 1.485 GB/s read. Including verification and guard checks, rates were 0.941 and 0.935 GB/s. Total writes and reads were 32 GiB each. This bypasses Windows file caching, not the SSD's internal cache; it is not a drive-wide sustained benchmark. See `physical-v1-review.json`.
- **Initial additional compression screening:** exact zero-word masking would save only 2.9% on the small 60-iteration snapshots. Zlib level 1 reduced them to 42.4% of original size; its measured encoding cost is too high to assume useful solver throughput. LZ4 default mode reduced them to 50.6%, with exact decompression, encoding 113 MB in 0.140 seconds and decoding in 0.089 seconds in this Python screen. Larger and mature states still need checking. See the registered codec protocol and machine-readable results.

## What the SSD result means

Space is ample, but repeated writes can dominate. With the current full-record-per-player design, just 20 GB of cold state over 2,000 iterations would read and write 80 TB each. Applying this short test's direct I/O rates gives approximately 30 hours of I/O alone, before solver work and storage processing. No such long run has been launched or authorized by this estimate.

## Connected comparison: exact results, unacceptable first-version overhead

All four variants produced exactly equal scientific checkpoint outputs at iterations 1 and 20 on the registered three development boards, with both called pots and evolving preflop ranges. Native probability, rake conservation and gap checks passed. This is equivalence evidence, not a converged poker solution.

| Storage | Total seconds, including setup/evaluation |
|---|---:|
| Resident explicit reference | 13.46 |
| Canonical parked RAM | 135.43 |
| Canonical parked SSD | 392.65 |
| 800 MB RAM budget plus SSD | 247.30 |

The sequential pilot is not a controlled production benchmark, but the overhead is clearly unacceptable. The first integration repeatedly reconstructs full host strategies, even for all-in equity, which does not depend on strategy arrays. Both disk variants together wrote 86.40 GB of strategy payload, within the registered 128-GiB bound. Their reported read counters count training sweep loads only and omit evaluation/all-in rereads. See `connected-v1-review.json`.

A registered follow-up is testing direct GPU scatter/gather of the same exact canonical blocks, keeping explicit traversal and original policy tying. It also avoids strategy reconstruction for all-in equity and drops duplicate retained CPU planning tables. Full device arrays as well as outputs must match. No large training or deployment is justified yet.

## Larger-state codec screening

On all six completed 20-iteration connected states (1.376 GB), LZ4 default stored 0.923 GB (67.0%) with exact round trips. Encoding took 2.19 seconds and decoding 1.06 seconds in the Python screen. Fast mode stored 0.937 GB and encoded in 1.78 seconds. Zero-word masking again saved only about 2.9%. Zlib level 1 stored 0.761 GB but took 27.14 seconds to encode. These are early states and include Python allocation; they do not establish native throughput or a mature 164-board capacity bound. Fast lossless compression is promising for capacity, but its repeated cost must be measured before adoption.

## Reproduction and evidence

Protocols: `PROTOCOL.md`, `CONNECTED-PROTOCOL.md`, `LOSSLESS-CAPACITY-PROTOCOL.md`, `FAST-CODEC-PROTOCOL.md`. Tools live under `tools/research/ssd_*_20260920.py`. GPU guard logs and resource samples are in the sibling `representative-coverage-20260919` directory. Installation of the codec is isolated under `target/ssd-codec-python`; the wheel version and hash are recorded in `lz4-install-report.json`.

Scratch files are confined to named directories under `S:/GTOpen-research`. They are research artifacts, not user saves or a crash-resumable whole-game checkpoint format.
