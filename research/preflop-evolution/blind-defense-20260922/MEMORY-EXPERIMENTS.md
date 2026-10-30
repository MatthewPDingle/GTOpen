# Compression and GPU eviction controls

Two engineering experiments followed the full BB capacity rejection. Neither
changes the production application or establishes a new blind-defense strategy.

## Trained-state compression: insufficient evidence for admission

The codec screen selected six board indices by a recorded rule covering paired,
rainbow, two-tone and monotone flops plus the middle and last indices. It examined
both continuation branches and both weighted/equal checkpoints at iteration
2,000: 24 immutable checkpoint records in total. All four stored arrays were
sampled at their beginning, middle and end, giving 288 blocks / 75.50 MB.

Twelve combinations covered raw, byte-shuffled and XOR-plus-byte-shuffled
layouts with zstd levels 1/3, LZ4 and zlib level 1. Raw zstd3 had the best sampled
ratio, 1.71x. Every decoded block matched the original bytes exactly. Additional
controls preserved signed zero, infinity and NaN payload bits and rejected a
corrupted encoded block through decoding or digest mismatch.

A follow-up compressed **every payload byte in all 24 selected records** in
1 MiB independent chunks. It read 6,485,195,136 raw payload bytes per codec and
verified exact reconstruction and unchanged source-file hashes. Encoded frames
were checked in memory; no checkpoint was replaced or deleted.

| Codec | Whole-record ratio, with framing allowance | Encode MB/s | Decode MB/s |
|---|---:|---:|---:|
| zstd1 | 1.618x | 303 | 685 |
| zstd3 | 1.665x | 150 | 604 |

The ratios include an allowance of 64 extra bytes per chunk and the original
record header. Timings are this single-process codec screen, excluding disk
writes and GPU transfers; they are not an end-to-end solver benchmark.

These records come from the original narrow-range context, so their ratios
cannot establish compression of the wider BB game. They do show that typical
trained floats should not be assumed to compress like initial zero arrays.
Even optimistically applying the 1.665x ratio to all 1,105.40 GB of the new
forest's parked state leaves about 664 GB, before host structures, checkpoints
or temporary buffers. That does not solve the current storage shortfall.
Do not admit the wide forest based on compression extrapolation.

Dependencies are isolated at `S:/GTOpen-research/python-codecs-20260922`:
zstandard 0.25.0 and lz4 4.4.4. Production dependencies were not changed.
Registration, per-block results, complete-record results and source hashes are
stored alongside this report.

## Cold recovery: exact in the compact control

The new research example uses the existing checkpoint API without modifying
the GPU solver or storage implementation. A resident reference and a candidate
receive identical changing reaches. After every candidate player sweep, its
state is saved and both its GPU object and workspace are dropped. Before its
next sweep, a fresh object restores the prior state. The reference stays
resident throughout.

All **48 player sweeps** passed exact bit comparisons for counterfactual values
and every materialized regret/strategy array. The three cases cover the flop
suit textures and the BB context's three pot/remaining-stack pairs. They also
include a temporarily zero own range and its subsequent reentry. The control
used compact hand ranges and no postflop raises, so it is an engineering control,
not a smaller substitute for the intended wide-range comparison.

The guarded run finished in 12.36 seconds (11.08 seconds inside the example).
Reconstruction took 4.11 seconds and serialization 3.29 seconds. These figures
describe the small control and must not be extrapolated as wide-game throughput.
Its 48 new immutable snapshots total 1,146,860,928 bytes and remain on S:; their
hashes are in `cold-replay-v1-review.json`. The run preserved the 20 GB RAM and
3 GB VRAM guard reserves, checked production idleness throughout, and left
56708 untouched.

## Full-support qualification completed

The [wide control](WIDE-RECOVERY-RESULT.md) used the actual BB/BTN entry support
and the complete call continuation on KsQd9d. Reference and candidate occupied
the GPU sequentially. All eight player updates matched in both returned values
and complete saved arrays, including zero own reach followed by reentry.

This establishes exact recovery for this full-support branch, not an efficient
full-forest scheduler. The candidate spent 51.02 seconds reconstructing/loading,
6.11 seconds sweeping and 129.40 seconds exporting its eight snapshots. File
comparison and reference work add further overhead. The full 112-board
blind-defense experiment remains unadmitted; no strategic run has started.
