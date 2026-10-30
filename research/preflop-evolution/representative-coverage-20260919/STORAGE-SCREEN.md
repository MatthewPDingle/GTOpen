# Lossless storage screen

Research only, 19 September 2026. No production changes and no changes to the
running 47-flop reference or its frozen inputs.

## Why test this?

The separate [menu feasibility screen](MENU-FEASIBILITY.md) estimated 97.39 GB
of full host action arrays for 47 flops with both 50% and 75% bets. That does
not fit the current host reserve. Lossless compression might reduce stored
arrays without changing the game, numerical precision, or learned strategy.
This is a feasibility screen, not an integrated solution.

## Fixtures and verification

`continuation_storage_fixture` generated two CPU turn-board solves, with
the same supported entry hands as the registered subtree but **uniform
weights on that support**. Boards were KhQd9d2c and 8c7c4h2d, with pots/stacks
39.5/182 and 93.5/155. Both used 50%,75% bets and donks, pot raises, one raise
per street, 4% rake capped at 6, CFR+, F32 arrays, and no future-card
isomorphism. States were saved at iterations 1 and 100.

The two boards contain 15,541,120 bytes of raw regret and average-strategy
arrays per checkpoint. Every tested codec restored every byte of all four
snapshots. Additional tests covered arbitrary bit patterns, positive and
negative zero, subnormals, infinities, and NaN payloads. These are byte
codecs; they do not perform arithmetic on stored floating-point values.

The block screen used 1 MiB blocks and raw fallback when compression did not
shrink a block. Its nine-byte header stores original length and encoding
choice. LZ4 4.4.5 and zstandard 0.25.0 were installed only into the ignored
`target/storage-codecs` directory. No app dependency or global installation
was changed.

## Later-checkpoint results

Combined iteration-100 states; times include Python allocation and copying.

| Method | Stored / raw | Encode seconds | Decode seconds |
|---|---:|---:|---:|
| Raw blocks | 100.00% | 0.006 | 0.007 |
| Zero bitmap, whole arrays | 100.96% | 0.020 | 0.032 |
| DEFLATE level 1, whole arrays | 75.76% | 0.399 | 0.061 |
| Byte shuffle + DEFLATE 1, whole arrays | 69.53% | 0.342 | 0.082 |
| LZ4 fast blocks | 86.63% | 0.041 | 0.022 |
| Byte shuffle + LZ4 fast blocks | 76.70% | 0.057 | 0.052 |
| Zstandard level 1 blocks | 78.38% | 0.071 | 0.031 |
| Byte shuffle + Zstandard level 1 blocks | 69.58% | 0.076 | 0.056 |

Early states were much more compressible. For example, plain Zstandard
stored 13.27% of iteration-1 bytes versus 78.38% at iteration 100. Early
zeros therefore cannot justify a memory budget for an evolving solve.

These are single-pass measurements while the main GPU reference was running.
Small fixtures may fit CPU caches. No codec ranking or throughput here is
an isolated performance result. Turn-board storage also does not establish
full-flop compression, evolving-range behavior, or capacity on all 47 boards.

## Decision and next gate

Lossless compression merits a larger storage experiment. Omitting zeros
alone does not. The tested faster codecs trade compression ratio against
copying and compression overhead; none is integrated into the native pager.
The full 47-flop richer-menu solve remains **not cleared to launch**.

Before such a launch, measure later full-flop states, including changing
entry ranges; bound decompression buffers and allocation peaks; then verify
native repeated paging is bitwise equivalent to uncompressed state. Measure
end-to-end runtime separately. A slower but exact bounded-memory research
path could still be useful, but no speed benefit is claimed.

## Reproduction and evidence

Build `continuation_storage_fixture` with the default solver features in a
separate target directory. Run with two Rayon threads, the registered
`conditional-hu-20260919/subtree.json`, and a new output directory. Then run
`tools/research/continuation_storage_screen.py` and
`tools/research/continuation_fast_storage_screen.py`, each with that directory
and a new output JSON path. Fast codecs require the pinned packages above
in `target/storage-codecs` (binary wheels, no dependencies).

- `storage-fixtures-freeze.json`: generator, solver and input hashes.
- `storage-fixtures-status.json`: successful bounded CPU run.
- `storage-fixtures/fixtures.json`: generated-state metadata.
- `storage-screen.json` and `fast-storage-screen.json`: full measurements,
  script hashes and raw arena hashes. Generated `.gto` states stay local.
- Official codec APIs: [python-lz4 block](https://github.com/python-lz4/python-lz4/blob/master/docs/lz4.block.rst)
  and [python-zstandard](https://python-zstandard.readthedocs.io/en/latest/compressor.html).

This work supplies storage evidence only, not new poker strategy labels or
evidence of convergence or preflop accuracy.
