# Full-flop lossless storage screen: passed

Completed19 September2026 in3072.95seconds (51.2minutes), within the registered
one-hour bound. All six states and all codecs passed exact byte restoration.
No live app, GPU implementation or frozen accuracy-study input was changed.

## Scope

The two registered full-flop cases used fixed uniform weights on the same
supported entry hands, a50/75 bet/donk menu, CFR+, F32 arrays, and no future-card
isomorphism. They are storage fixtures, not preflop accuracy labels. No
convergence claim is made from their1000 iterations.

| Case | Nodes | Raw arrays | Time to1000 iterations and save |
|---|---:|---:|---:|
| 5c2h2d, pot39.5 | 1,283,337 | 1.898GB | 2510.6s |
| AcQd9d, pot93.5 | 279,425 | 0.305GB | 405.2s |

Snapshots at1,100,1000 contain6.608GB of raw arrays in total. The bounded CPU
generator took2921.6s; the subsequent codec screen took151.3s, including all
checkpoints, codecs, file reads, hashing and restoration assertions. Minimum
observed free host memory was62.13GB; minimum free disk was283.42GB.

## Results at1000 iterations

The following times cover the combined2.203GB of raw arrays at this one
checkpoint. They are concurrent, single-pass Python/native-library
measurements including allocation/copy costs, not isolated native-pager
throughput benchmarks. Bytes include block headers and any raw fallback.

| Codec | Stored / raw | Saved | Encode seconds | Decode seconds |
|---|---:|---:|---:|---:|
| Raw blocks | 100.001% | — | 0.901 | 0.872 |
| LZ4 fast | 85.04% | 14.96% | 4.185 | 2.183 |
| Byte shuffle + LZ4 | 76.82% | 23.18% | 5.485 | 5.661 |
| Zstandard1 | 76.94% | 23.06% | 7.383 | 3.404 |
| Byte shuffle + Zstandard1 | 69.37% | 30.63% | 8.460 | 5.910 |

Byte-shuffled Zstandard stored70.28% on the largest low paired case and
63.73% on the high two-tone case. The combined ratio is therefore dominated
by the larger case, not an equal average of board percentages.

At iteration1 the same codec stored12.48% of raw bytes; at100 it stored66.91%;
at1000 it stored69.37%. The large initial savings were not representative of
later states. Even100 iterations slightly overstated later savings here.

## Implication

The earlier turn-board result was not just an artifact of tiny arrays:
useful lossless compression remains at full-flop scale on these two cases.
However, these fixed ranges do not characterize all94 continuations or
changing external ranges. No measured ratio is a worst-case capacity bound.

Compression on every board switch could also add substantial work: the
best-ratio method took14.37seconds to encode and decode just these2.203GB in
this harness. The richer47-board menu has97.39GB of full arrays. This is not
an end-to-end slowdown estimate, but is enough to reject treating memory
compression as a free performance improvement. A native implementation,
buffer strategy and measured whole-solve cost would need separate study.

**The richer47-board menu remains not cleared to launch.** Raw fallback
protects the codec from expansion but does not bound the total below raw
storage. Capacity checks must include trees, compressed states, the active
decompressed state, compression scratch space, GPU staging and the20GB host
reserve. Repeated native paging must retain exact state and counterfactual
values. The failed compact-bridge changing-range test remains unresolved;
these storage checks do not override it.

## Evidence

- [Registration](FLOP-STORAGE-PROTOCOL.md) and `flop-storage-freeze.json`.
- `flop-storage-status.json`: both subprocesses exited0; passed=true.
- `flop-storage-fixtures/fixtures.json`: all six snapshot records, complete=true.
- `flop-fast-storage-screen.json`: byte checks, individual arena results,
  package versions and source/arena hashes.
- `flop-storage-generation.log`, `flop-storage-codecs.log`, and resource log.

Generated `.gto` snapshots remain local. The main47-board accuracy solve
continues separately; this experiment changes no strategy evidence.
