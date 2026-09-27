# Equivalent CPU parallel training control

Replay generation two of the completed weighted training pilot from its immutable
generation-one checkpoint. Compare one, two and four CPU workers, then repeat four
workers once after libraries and filesystem caches are warm. Each run includes a
fresh worker pool's startup/shutdown, query generation, identical CUDA inference,
ordered reservoir insertion, the original fit and checkpoint publication.

Each worker receives the admitted cache, frozen target policy and complete
weighted generation. It performs native updates, tracing, full target validation
and root integration for one subbatch, returning ordered insertion events and
source-bound audits. The coordinator limits pending batches to twice the worker
count and commits in original subbatch/visit order. Workers take no reservoir RNG
draws. Their numerical library thread count is one; only the coordinator uses CUDA.

Require exactly the serial reference's checkpoint/model, native artifact hashes,
reservoir arrays (including weights), RNG states, sampler state, played bank and
fit diagnostics other than timings. Check that all worker processes exited.
Report total wall time, pipeline wall time and worker stage totals separately:
overlapping worker times cannot be summed as elapsed time. One development run
with two workers may precede the registered benchmark in a separate directory.

Before admission and each measured run, require CPU below 50%; require the app
idle or closed, both research locks free before acquisition, 20GB free host RAM,
4GB free VRAM and GPU below 20%. The coordinator owns the exclusive research lock;
workers check application activity and available RAM. Keep 40GB disk headroom.
Use compression inherited by files in a newly created research directory. Cap
the complete control at 900 seconds and 2GB logical output, with no production
changes or deletion/recompression of prior evidence.

A faster result qualifies execution throughput only. It must not be described as
improved convergence or stronger preflop ranges. Select a worker count only after
examining measured time and memory; the subsequent accuracy study remains needed.
