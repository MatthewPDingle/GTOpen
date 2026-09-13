# D04: cross-player average-check sharing inventory

Register before running the diagnostic. Follow D04_PROPOSAL.md on the same
immutable small and large native saves used by C01. This does not benchmark
speed or alter the solver's dispatch.

One common `down(1, -1)` matches queue_evaluation. Normalize each player's
complete compact span with gate=0. Skip only zero-mass distributions. Intern
all 169 f32 bits across players; a hash only locates a bucket. Check repeated
source blocks yield identical identities. Preserve both learning arenas,
average reach values/masses and iteration exactly. No up/discount/iterate.

Report all pairwise overlaps, all 105 disjoint pairings for eight players,
natural adjacent pairing, minimum total CDF-row pairing (tie-break memory then
lexical groups), global union and both static/observed unique capacities.
Classifier tests force collisions, signed zero and single-bit differences;
enumeration tests cover 1-9 seats and one singleton for odd counts.

Memory: sum every plain device buffer and add retained C01 classification
scratch. Plan replacement CDF/normalized/classification allocations at the
largest static pair union, unchanged batch32, stride170 and 1024 particles.
Keep existing learning maps; add all pair maps/worklists, another probability
buffer and an entire second d_val. Add 256 MiB driver/module reserve. Report
steady/preplanned initialization and allocate-before-release replacement peak
separately. Preplanned allocation would need a constructor change: do not claim
the current engine can replace its buffers within that lower peak. Observed
unique capacity is informational, never used for the safe static budget.

Admission: at least 25% fewer CDF rows across the full large check and a static
preplanned total including reserve <=23,000,000,000 bytes. Enumerate all
pairings before selecting the best qualifying one. This only admits a future
prototype, still requiring bitwise numerical tests, paired complete timings
and regression qualification. No reduced cache or samples allowed to pass.

Serial guarded run07 runner. Build/test cap240 seconds; each inventory cap180.
No source edits/builds while GPU diagnostics run. Port56708 read-only, abort
owned workload if app solving/building/reporting. Freeze metadata/input/source
hashes and retain unsuccessful runs. Output paths must be new.
