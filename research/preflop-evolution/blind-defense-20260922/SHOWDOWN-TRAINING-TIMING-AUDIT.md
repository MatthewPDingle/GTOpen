# Where the current training time goes

This is an observational audit of completed baseline updates 1–48. It does not
change the registered experiment or inspect fresh evaluation outcomes. The source
metric files are bound to their completion-marker hashes in
`showdown-training-timing-audit-0048-v1.json`.

The 48 updates took 7,317.89 seconds in total, averaging 152.46 seconds each.
The last eight averaged 156.63 seconds. Each update supplies 512 physical deals
and runs the unchanged 512-step CUDA fitter for each player.

| Recorded work | Total seconds | Share of update time |
|---|---:|---:|
| CUDA optimizer step loops | 313.25 | 4.28% |
| Fitter data setup | 275.65 | 3.77% |
| CUDA graph capture | 41.24 | 0.56% |
| Root action integration | 554.15 | 7.57% |
| Remaining work, not individually timed | 6,133.61 | 83.82% |

Optimizer loop duration is wall time, not measured GPU utilization. The remaining
work includes native traversals, policy inference, JSON transport, target and
reservoir ingestion, model publication, checkpointing, and lossless archives. This
audit does not identify any one of those as the dominant component. It does show
that speeding the optimizer alone cannot substantially shorten this workload:
even eliminating its measured time entirely would save only about 4.3% here.

At the whole-prefix baseline rate, 312 updates project to about 13.21 hours,
leaving roughly 47 minutes inside the existing 14-hour worker limit. At the recent
eight-update rate, the projection is about 13.57 hours. Neither is a guaranteed
ETA: corrected training, reservoir growth, checkpoint restore and guard overhead
can differ. Do not extend the deadline silently or stop based on intermediate
range appearance.

Storage snapshots also require care. Live output scans can include hundreds of MB
of native JSON awaiting compression. A later scan may therefore be smaller after
verified retirement, even while training advances. Use complete-update archives
and explicit working-space allowances rather than extrapolating a single live
directory-size sample.

After this fixed comparison, the performance priority is a separately instrumented
replay of the native traversal, inference, transport, ingestion and archive stages.
Then test batching or parallel preparation of independent subbatches while
preserving original random streams, ingestion order, model bytes and target
values. Qualify equivalence before adopting a faster driver. Do not replace this
experiment's driver mid-run or attribute transport improvements to better poker
accuracy.

## Archive-stage probes

The CPU-only `training-transport-timing-probe-v1-result.json` measured batch 00
from completed baseline updates 8, 24 and 48. Each contained roughly 35 MB of raw
JSON. Mean verified archive decoding was 0.214 seconds; parsing all JSON was
0.698 seconds. Diagnostic Python encoding of all documents was 0.506 seconds,
but some documents are native-written in training, so that is not an exact
serialization-cost attribution.

Recreating the original XZ6 archive took 8.442, 7.468 and 7.210 seconds. All three
compressed outputs were byte-identical to the original archives. At that mean
rate, compression of eight batches would take about 61.65 seconds, a substantial
part of a 152-second update. This is a small concurrent-workload probe, not an
instrumented full-update benchmark; it excludes writing, manifests and retirement.

`training-parallel-xz-probe-v1-result.json` then compressed these same bundles
with worker counts fixed in advance to 1, 3, 3, 1. Sequential passes took 21.51
and 24.10 seconds; three-worker passes took 8.98 and 9.26 seconds. Every pass
produced the same original archive bytes. Mean speedup for this compression-only
test was 2.50x. No GPU work, new deals, source-file writes or live driver changes
were involved.

This identifies a concrete next throughput experiment: parallelize independent
batch archival with bounded worker count, serialize guard checks, and retain the
existing full readback-before-retirement rules. First qualify actual durable
archive/manifest and interrupted-failure behavior; then measure a whole replayed
update. The compression speedup must not be reported as a training or solver
speedup, and must not change this already-registered comparison mid-run.
