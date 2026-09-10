# CDF stride 170 versus 192: assessment only

Read-only review of the normalized/direct CDF kernels and terminal readers after
the live-terminal worklist proposal. No source changes, compilation or hardware
measurement. Recommendation: **do not spend the next experiment on plain192
padding**. Its main supposed alignment benefit is absent in the current writer.

## The +1 matters

Each warp constructs one particle CDF in six tiles. For each full tile, 32 lanes
write `cdf[base + tile + lane + 1]`. Entry0 is written separately. The source
weights are gathered from the same169-element normalized vector in particle
rank order, followed by the unchanged warp scan.

A 170-float stride advances row bases by two float words modulo eight. The
first nonzero CDF store therefore starts at word residue1,3,5 or7 relative to
a32-byte boundary. All are misaligned for a128-byte contiguous warp store.
Rounding stride to192 makes every row base aligned, but the `+1` makes the first
store start at word residue1 again. It still crosses five32-byte sectors.

Pure address-count calculation over16 successive rows gives the same result
for both strides: five full tiles times five sectors, plus two sectors for the
nine-value tail =27 sectors for the169 output writes. The separate entry0 store
is excluded and is the same for both. This is a conceptual address-coverage
count, not a measured GPU memory transaction counter; cache merging and device
behavior can differ. It establishes that simply aligning row bases does not
align the hot full-tile stores.

Terminal reads use class-specific `lower/upper` rank boundaries, so lanes do
not generally read consecutive CDF entries. Plain padding does not turn those
gathers into contiguous loads. A complete useful170-float row spans22 modeled
32-byte sectors with either layout. Padding does not reduce normalized-vector
gathers, shuffle scan arithmetic or the number of prefix values produced.
Packed rows can share cache-line/sector boundaries with adjacent particles;
padding increases the overall footprint and can reduce that reuse.

## Exact memory cost at compact capacity388082, batch32

| Item | Stride170 | Stride192 |
|---|---:|---:|
| One particle, bytes |263,895,760|298,046,976|
| Batch32 scratch, bytes |8,444,664,320|9,537,503,232|
| Separate normalized reach, bytes |262,343,432|262,343,432|

Added scratch: **1,092,838,912 bytes**, about1.018GiB /1,092.84 decimal MB,
or12.94% more CDF storage. The current roughly13,075MB total would become
roughly14,168MB if all other allocations/batch choices remained fixed.

The minimum direct one-particle allocation rises by34,151,216 bytes; normalized
one-particle minimum rises by the same amount. With only the previous32-particle
scratch budget, a192-stride layout fits28 particles instead of32, increasing
the1024-particle batch count from32 to37. An implementation must retain the170
path whenever padding changes the chosen batch, normalization mode, optional
HU cache or minimum fit. The user23GB budget likely has headroom, but universal
padding would regress smaller-memory capability.

## If alignment is investigated later

A real store-alignment experiment needs to align **entry1**, not entry0. For
example, a constant leading bias plus an adequately padded allocation could
align `base+1` and keep the logical CDF indices0..169. That is a different
experiment requiring explicit guard/tail allocation and consistent reader
bases, not a one-line stride substitution. Do not combine it with the current
worklist or base-hoisting candidate.

Any future layout trial must parameterize storage stride separately from the
logical170 prefix length: scan the same169 weights, write the same170 values,
preserve identical carry order and sample/rank indices, and change only storage
addresses. Padding must never enter the scan or be read as a CDF value. Update
both normalized/direct writers, every terminal reader/base, planner, memory
estimator and poison/boundary tests. Require unchanged full arena/gap/EV bits,
including batch1/7/32 and the final short batch.

Given identical modeled full-tile store-sector coverage, increased footprint
and nontrivial fallback requirements, plain192 padding has a weak benefit-to-
complexity case. Finish the narrowly targeted terminal worklist/base-hoist
measurements first. Hardware counters or generated-code inspection would be
better evidence for choosing a later alignment experiment.
