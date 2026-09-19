# SSD storage study — in progress

Production 56708 is unchanged. This study tests storage for the isolated connected preflop/postflop research solver.

## Completed gates

- **Exact disk parking:** all 720 board/player passes matched resident reference values and all four state arrays bit-for-bit. Nine format/failure checks passed. Unused candidate pinned staging was released. Six small states occupy 113.24 MB rather than 180.13 MB before suit-based packing. The guarded run took 97.89 seconds; buffered reads may hit Windows cache. See `ssd-paging-v1-review.json`.
- **Physical SSD I/O:** both 16-GiB write/read repetitions passed full CRC checks using aligned unbuffered, write-through access to a new regular scratch file on S:. Combined direct I/O rates were 1.489 GB/s write and 1.485 GB/s read. Including verification and guard checks, rates were 0.941 and 0.935 GB/s. Total writes and reads were 32 GiB each. This bypasses Windows file caching, not the SSD's internal cache; it is not a drive-wide sustained benchmark. See `physical-v1-review.json`.
- **Initial additional compression screening:** exact zero-word masking would save only 2.9% on the small 60-iteration snapshots. Zlib level 1 reduced them to 42.4% of original size; its measured encoding cost is too high to assume useful solver throughput. LZ4 default mode reduced them to 50.6%, with exact decompression, encoding 113 MB in 0.140 seconds and decoding in 0.089 seconds in this Python screen. Larger and mature states still need checking. See the registered codec protocol and machine-readable results.

## What the SSD result means

Space is ample, but repeated writes can dominate. With the current full-record-per-player design, just 20 GB of cold state over 2,000 iterations would read and write 80 TB each. Applying this short test's direct I/O rates gives approximately 30 hours of I/O alone, before solver work and storage processing. No such long run has been launched or authorized by this estimate.

The next gate is a four-way connected comparison: resident reference, parked RAM, parked SSD, and a bounded RAM/SSD split. The source is frozen while it runs. Exact scientific checkpoint comparisons and measured runtime will decide what is usable. Capacity is not sufficient justification to accept a major slowdown.

## Reproduction and evidence

Protocols: `PROTOCOL.md`, `CONNECTED-PROTOCOL.md`, `LOSSLESS-CAPACITY-PROTOCOL.md`, `FAST-CODEC-PROTOCOL.md`. Tools live under `tools/research/ssd_*_20260920.py`. GPU guard logs and resource samples are in the sibling `representative-coverage-20260919` directory. Installation of the codec is isolated under `target/ssd-codec-python`; the wheel version and hash are recorded in `lz4-install-report.json`.

Scratch files are confined to named directories under `S:/GTOpen-research`. They are research artifacts, not user saves or a crash-resumable whole-game checkpoint format.
