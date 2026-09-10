# Optional source-key counts

`key-stats.patch` adds one host helper and one constructor call guarded by
**`PREFLOP_MW_KEY_STATS=1`**. Other values and an absent variable do nothing.
The patch touches no CDF geometry, kernels, layout selection or arithmetic.
`key-stats-baseline.json` records the inspected source hash. The generator can
refresh the two anchored hunks after other GPU changes; it never writes source.

The patch passes `git apply --check` against the inspected research worktree.
It has **not been compiled or executed**. Parent should compile and run the
diagnostic on frozen fixtures when scheduled. Constructor initialization time
with the flag enabled includes counting and must not be used as an unqualified
performance result. Unset the flag before production timing comparisons.

Output is one JSON record after `preflop mw key stats: `. It includes per-seat
tasks/unique keys/duplicate groups, multiplicity and opponent-count histograms,
a frozen-average-check union, cross-seat-only group examples, and additional
cross-seat savings beyond within-seat duplicates. Up to three per-seat duplicate
examples and five cross-seat examples contain full ordered source keys/node IDs.

The implementation reserves one record per live terminal/traverser task, sorts
the records in place, and counts runs. It does not sort opponents inside a key,
hash policies, read reach values, calculate equity or access the GPU. The
record payload size is reported from `size_of::<Record>() * capacity`; this is
an estimate of dominant temporary storage, not RSS. Auxiliary histograms and
JSON are small but excluded. Allocation failure prints a diagnostic skip and
returns to the unchanged constructor. All temporary storage drops on return.

One-batch cache estimates assume one169-f32 sum per duplicate group. Optional
all-batches estimates are shown for batch sizes1/7/32 to expose frozen cross-seat
retention costs. These are cache-only estimates: metadata/scatter/activity work
is additional. Null estimates indicate checked arithmetic overflow. Static key
counts do not establish active-reach duplication or runtime benefit.

Suggested checks after applying (parent only): absent flag and values0/true
produce no stats; flag1 prints once per GPU construction; baseline arena hash,
gaps/EVs, selected CDF layout and memory remain identical. Compare the first
small fixture's task total with its live-terminal worklist total. Source0 and
zero padding must remain distinguishable through the explicit key length.
