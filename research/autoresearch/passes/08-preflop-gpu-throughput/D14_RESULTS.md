# D14: decline warp-local rank sharing

The remaining D13 proposal does not reduce either of its claimed mechanisms at
warp granularity. Every original warp retains at least one rank-group leader;
every original lower/upper load still requests the same words and sectors.
It fails the registered 10% execution-model admission gate in both large modes.
No GPU prototype, speed measurement or runtime change was made.

| Quantity across 1024 samples | Original | Warp-local leaders |
| --- | ---: | ---: |
| Active hand/sample product tasks | 173,056 | 105,329 |
| Nonempty sample/warp cases | 6,144 | 6,144 |
| Modeled original arithmetic slots | 100% | 100% |
| Modeled lower/upper requested sectors | 100% | 100% |

D13's 39.14% logical-gather and roughly 33% large active-lane arithmetic
reductions remain correct. They count lanes, however, rather than warp-level
instruction paths or distinct memory sectors. Keeping one copy of every exact
(lower,upper) pair in its original warp keeps the complete address set of each
load. Lower and upper were counted separately, without merging opponents,
samples, warps or successive loads. The comparison covers all eight possible
float-aligned base offsets modulo 32, including the last nine-lane partial warp.

Independent verification elects leaders by sorted runs and uses bit vectors
for word/sector sets, against the census's first/last-leader and set methods.
All 6,144 cases, both saved-game opponent histograms, D13 active-lane counts,
source/input hashes and the unchanged runtime source pass. The guarded host
census completed in 1.062 seconds; four synthetic patterns cover identical,
distinct, alternating and warp-boundary groups.

This is a source/architecture screen, not native instruction or DRAM counters.
It assumes the same product arithmetic path, with other lanes disabled. It
does not rule out compiler, register, scheduling or sub-warp effects. Those
would require a distinct proposed mechanism. Leader election and shuffle costs
are omitted here, which favors this proposal rather than understating its cost.

NVIDIA documents the relevant [32-byte coalescing behavior](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#coalesced-access-to-global-memory)
and [predication scheduling](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#branch-predication).
These support the model assumptions; they are not a benchmark of this GPU.

## Next research constraint

Do not implement D13 B merely because its lane count passed. C18 already tested
global rank compaction and regressed complete time by 43.67%; D14 now declines
the unmodified warp-local alternative. A new reuse schedule must remove whole
scheduled work groups, reduce distinct probability-table requests, or identify
a separate compiler/latency mechanism. Both probability-table construction and
terminal evaluation remain material costs in D11, so a one-phase optimization
alone cannot deliver the requested order-of-magnitude complete improvement.

Retained C14/R03 remains the qualified best. Port 56708 and all solver runtime
sources are unchanged. No candidate contributes a new speed point to the graph.

[Protocol](D14_PROTOCOL.md), [census](d14_warp_census.py),
[independent verifier](check_d14.py), [verified result](raw/d14-verified.json).
