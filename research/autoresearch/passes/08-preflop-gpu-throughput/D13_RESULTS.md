# D13: equal sampled ranks admit a GPU prototype

Unlike D12's repeated opponent pairs, equal hero ranks provide substantial exact
reuse. The 169 classes average 57.19 distinct rank groups per sample. Compacting
those groups could remove about 56% of terminal source arithmetic in the large
fixture, before coordination costs. Both registered schedules pass their work
screen. No GPU speed improvement has been measured or retained.

| Schedule | Groups over 1024 samples | Logical gather reduction | Large learning arithmetic reduction | Large check arithmetic reduction |
| --- | ---: | ---: | ---: | ---: |
| Compact rank groups | 58,566 | 66.16% | 56.65% | 56.27% |
| Original 32-class warps | 105,329 | 39.14% | 33.51% | 33.29% |

Without sharing there are 173,056 hand/sample evaluations. Compact groups range
from 3 to 104 per sample, median 59. Warp-local groups range from 14 to 152,
median 105. Small-fixture source arithmetic reductions are about 54.7-54.8% for
compaction and 32.4% for warp-local reuse. Required large reductions were 30%
and 20%, respectively, in both learning and checks.

## What remains identical

Only hands with the exact same lower and upper CDF indices in a sample share
opponent products. Every hand must still perform its original quadrature and
sample additions into its own accumulator. Sharing a completed running sum, or
summing weighted contributions before adding them, would change rounding.
All 1024 samples, opponent order, CDF scan arithmetic and precision remain fixed.

Probability-table construction is unchanged. The work count omits leader
selection, mapping, scratch traffic and barriers. Warp-local sharing reduces
active lane work, which does not necessarily reduce issued warp instructions.
Compact sharing needs synchronization and may lose the apparent advantage to
coordination or occupancy. These counts are not DRAM traffic or timing claims.

## Evidence and next experiment

The guarded test-only export passed in 129.63 seconds including compilation;
the test itself took 0.04 seconds. It validates every sample permutation, group
boundary and hand membership, plus all-equal/all-distinct and warp-boundary
synthetic cases. Independent Python set and sorted-run counts reproduce every
sample and reconcile operation totals with D11. Full compressed table, frozen
source, executable hash and input hashes are archived. No runtime kernel changed.

Try compact groups first because its optimistic work reduction is larger.
C18 must demonstrate exact kernel outputs across all opponent counts, partial
batches and mismatched per-hand accumulation histories, then exact complete
saved-game outputs and actual paired timing. Admission is not retention.
The qualified R03 executable and port 56708 remain untouched.

[Protocol](D13_PROTOCOL.md), [verified counts](raw/d13-verified.json),
[checker](check_d13.py), [table manifest](raw/d13-ranks-manifest.json).
