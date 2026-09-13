# D07 proposal: static terminal-order locality inventory

C11's explicit L1 preference regressed despite identical compiled kernels.
Do not stack more cache preferences. Instead, measure whether the original
terminal order already has good probability-row locality before spending a
GPU implementation trial on reordering it.

Existing code gives every terminal a unique value slot. Prepared probabilities
are indexed by terminal-list index; a later prototype could permute the existing
`mw_terms` list once before upload, using the same list for preparation and
terminal evaluation. This would add no GPU arrays, launches, queue-building
kernel or per-terminal lookup. It differs from rejected static live-player lists,
C02's active queue, and pass03's specialized opponent-count launch groups.

Propose one fixed topology-only ordering: lexicographic `(live mask, ordered
source vector, node id)`, putting a sentinel in the source vector for folded
seats. Do not reorder opponent multiplications or select an order from current
strategy probabilities. Source identities come from `reach_sources`; retain
exact coverage and unique value slots as hard invariants. Ordinary terminal
lists and CDF work/alias mapping remain unchanged.

Before implementation register an inventory protocol. Use the small and large
frozen saves. For each traverser, scan its live terminals in baseline and
candidate list order and feed ascending live-opponent source IDs into a simple
LRU row-reference simulator, at capacities 64 and 256 CDF rows. Also report
adjacent/shared-row counts, permutations changed, and source/full-key reuse.
These are explicitly scheduling proxies, not measured GPU hit rates or speed.
A whole row covers the existing batch footprint; hardware concurrency, alias
reuse and partial cache-line accesses are not represented.

Admission proposal: exact coverage/no duplicate value slots, a nontrivial
permutation, and at least 10% fewer total simulated misses on the large fixture
at BOTH capacities, with no more than 3% increase on small. If those gates fail,
reject this ordering without a GPU prototype. Do not search many keys against
these fixtures to manufacture an admission pass. If it qualifies, register a
separate exact-GPU comparison and complete-work timing protocol against C09.

This is a host-side structural diagnostic for GPU scheduling, not CPU preflop
performance work. Run it under run07 guards, serially, with immutable source/
input evidence. No changes to port 56708. Not implemented or measured yet.
