# Storage sizing for future evaluations

This is a read-only transport/storage diagnostic on eight existing numerical-
control batches: offsets 0, 32, 64, 96, 128, 160, 192 and 224, for 128 deals.
It changes no policy, estimator, original evidence, or current evaluation.

| Retained JSON artifacts | Bytes | Fraction of original |
|---|---:|---:|
| Original | 56,787,631 | 100% |
| Gzip level 1 | 11,714,142 | 20.6% |
| Gzip level 6 | 9,334,108 | 16.4% |

Both compressed forms round-trip to the exact original bytes for every file.
Measured artifacts are batch, queries, profiles, native result and summary.
The full measurement and source hashes are in
`sampled-evaluation-storage-diagnostic-v1.json`. Compression was in memory;
source artifacts remain untouched. This is not a solve-speed benchmark.

At this measured geometry, 131,072 deals would retain approximately
58.2 GB uncompressed or 12.0 GB at level 1, before
extra CPU controls, manifests, checkpoints and conditional-equity caches.
These are planning projections, not a worst-case capacity guarantee. Larger
menus or additional profiles would change the estimate.

For a future registered evaluation, compressed evidence should retain both
compressed and uncompressed hashes. The reviewer must decompress and verify
identical bytes before parsing. Native executables can continue to use a
small per-batch working directory. Only new owned temporary files may be
removed after verified archival; existing registered runs remain unchanged.
No compressed execution or deletion path has been deployed by this diagnostic.

The current fixed-count all-in evaluation retains its original artifacts and
sampled-board estimator. A future larger conditional evaluation needs its own
protocol, fresh streams, both-player response tests and resource controls.
