# Fixed stratified batches: rejected before learning

Construction checksum (FNV-1a over little-endian u32 indices):
`d903d0261a1f2cc9`. The manifest was written before the GPU numerical test and
hashed as its immutable input. No construction seeds were searched.

The permutation/stratum/table-row checks passed. All twelve GPU fixtures tested
every native 64-sample cyclic offset and all sixteen candidate batches; all 169
hand means stayed within 0.0002 bb of the canonical full evaluation. Restoring
canonical table order reproduced the full GPU values exactly. These are static
payoff tests, not captured learning or large-game conditional qualification.

| Players | Flat variance ratio | Pair-heavy | Mixed |
|---|---:|---:|---:|
| 3 | 0.9130 | 0.9280 | 0.8820 |
| 4 | 0.9240 | 0.9299 | 0.8942 |
| 6 | 0.9203 | 0.9377 | 0.9107 |
| 8 | 0.9117 | 0.9496 | 0.9142 |

Overall pooled ratio: **0.919466**. Eight-player subset: **0.922751**.
The registered requirement was <=0.9 overall with no fixture above 1.25.
The first requirement failed. No learning integration, convergence trials,
large-game trial or deployment followed this fixed-batch screen.

`check_particle_batches.py` independently reconstructs partition coverage,
batch membership, checksum and frozen-manifest hash, per-hand bias/variance
gates, combo-weighted fixture variances, both pooled ratios and the rejection.

## Next diagnostic registered before execution

Keep exactly the same frozen 64 strata. Measure the variance that would result
from choosing one of sixteen particles **independently in each stratum**,
rather than selecting one of the sixteen fixed cross-stratum combinations.
This separates partition quality from covariance introduced by fixed pairings.
It is a new estimator; it does not turn the rejected fixed batches into a pass.

For each of the twelve existing fixtures, obtain each canonical particle's
payoff from the unchanged GPU terminal kernel, using one particle at a time.
Check the average of all 1,024 against the full canonical payoff for every hand
within 0.0002 bb. For stratum l, compute its population variance V_l from all
sixteen outcomes. Independent selection has exact variance `sum(V_l) / 64^2`;
its expectation is the mean of the 64 stratum means, equal to the canonical
mean. Compare with native 64-sample cyclic variance at all 1,024 offsets.

Report every hand and all twelve fixtures. Keep the same numerical gate:
overall pooled ratio <=0.9 and no fixture above 1.25; report the eight-player
subset separately. This diagnostic alone cannot qualify a sampler: actual
selection, equal inclusion, table mapping, fixed constraints, zero reach,
capture/eager execution, same-accuracy learning trials and large-game global
and conditional validation would still be required. No coefficient fitting,
new construction seed, partition changes or live server mutations.

## Independent-selection diagnostic: also rejected

The unchanged GPU kernel evaluated all 1,024 individual particle outcomes and
all 1,024 native 64-sample cyclic windows on all twelve fixtures. Every hand's
particle-average bias stayed below 0.0002 bb; the mean of the 64 stratum means
matched the full particle mean within 1e-10 bb. Canonical full evaluation was
restored exactly. No independent-selection learning sampler was implemented.

The exact independent-stratum variance ratio was **0.955515** overall and
**0.961022** on the eight-player subset. Eight-player fixture ratios were
0.9694 (flat), 0.9945 (pair-heavy), and 0.9296 (mixed). This also fails the
registered <=0.9 gate. The fixed cross-stratum pairings were not the underlying
problem: this rank-based partition itself explains too little payoff variation
to justify further integration under the current screen.

`check_particle_independent.py` reconstructs the variance formula and weighted
gates, checks every hand's mean/variance, checks the immutable manifest hash,
and verifies that the recomputed native control matches the earlier screen.
It reports verified evidence and a failed numerical gate. No learning or large
trial, no production changes, and no claimed convergence improvement.

Both numerical experiments used the existing GPU payoff kernel. Partition
construction and moment calculations are offline research calculations, not
CPU preflop performance optimization. Since no runtime sampling path changed,
the directly applicable checks are the construction/row mapping test and the
two GPU numerical tests; the previous checkpoint's production regression suite
remains the last full regression run.

Return priority to the unresolved conditional/global consistency problem.
Earlier compact refinements substantially improved local checks but damaged
the unrestricted global gap. None of these variance experiments resolved that.
The next implementation should first test whether training can cover low-reach
branches without replacing their parent ranges after the fact, with full native
global and all-27 conditional evaluation. This is a direction to investigate,
not a qualified algorithm or deployment recommendation.
