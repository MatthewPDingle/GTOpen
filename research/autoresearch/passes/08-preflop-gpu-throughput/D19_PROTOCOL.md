# D19: static sampled-rank CDF storage screen

Registered before calculation. Whole ordered-opponent caching was reviewed
against D01 and declined without repeating that inventory: its large current
weighted duplicate fraction is only 2.84%, average 0.319%. C22's global product
pipeline also failed. This proposal changes CDF storage, not product sharing.

The fixed CoupledDeck partitions 169 classes into ordered tied rank groups.
Terminal evaluation only reads each group's lower and upper cumulative prefix.
Store the original scan outputs at those exact boundaries, including prefix0.
Keep every original scan/carry operation; do not infer equal neighboring prefix
values, renormalize, prune positive ranges or change samples/precision. A static
hand-to-group map makes reads direct: lower=g, upper=g+1. Unlike C04, there is no
value-dependent run detection, mask/popcount lookup or dynamic compaction.

Count required prefixes over all 1,024 samples. Each sample uses G+1 floats.
Use one fixed row stride equal to the largest sum of required prefixes in ANY
contiguous interval of up to32 samples, including unaligned starts. Within that
row, static cumulative sample offsets locate a sample relative to batch start.
This keeps batch32, supports shorter/last batches, and never overlaps row slots.

Static arrays: 1024*170 u32 prefix-to-packed maps (UINT_MAX for unused prefixes),
1024*169 u32 hand-group maps, and1025 u32 cumulative sample offsets. Existing
rank and order arrays remain allocated. Keep all other C14 buffers, cohort
groups, caches, update rules and launch counts unchanged. The fresh candidate
constructor must replace its private original CDF allocation before allocating
the compact one if simultaneous buffers exceed budget. Failed construction
returns no partially configured engine; no live engine may change layout.

Admission: at both saved fixtures >=30% reduction in declared CDF allocation,
>=30% reduction in logical CDF float stores across the fixed1024 samples,
static maps <=4MiB, final declared total plus existing256MiB reserve <=23,000MB.
Count old+new overlap separately; do not pretend it fits when it does not.
No arithmetic or runtime improvement follows from these counts. The writer
gains mapping loads/predicates and the reader gains sample-offset loads.

Independent validation: reconstruct every rank partition and required prefix
set, map every hand's lower/upper index back to the exact original indices,
check prefix0/169, all short and32-sample windows, disjoint row ranges and u32
element bounds. Reconcile original sizes with both C14 allocation inventories.
Guarded host-only census, cap180s, no GPU or production mutation. A pass admits
separately registered C23 GPU prefix/terminal/full solver qualification, followed
by the unchanged complete-time gates. It does not resolve convergence or10x.
