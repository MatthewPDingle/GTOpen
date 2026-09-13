# D05: bounded cross-player cohorts, registered before execution

Follow D05_PROPOSAL.md using D04's frozen small/large saves and exact ungated
average-policy identity inventory. Add histograms of the player membership
mask of each unique distribution and static slot. Compute every subset union
by summing intersecting masks; verify singletons, every pair and the full set
against independent explicit-set unions. Repeat D04 arena/reach preservation.

Enumerate every set partition with groups of size1-4, including singletons:
3,795 partitions for eight players. Test coverage/uniqueness for1-9 players
against a separately computed restricted Bell recurrence. Use synthetic
overlap sets to check all subset union counts, including the empty set.

Selection must be deployable without downloading changing strategy arrays:
choose minimum summed STATIC union work among plans fitting23GB, then total
memory, then lexical group masks. Report the best observed-identity plan only
as an upper bound. The admission gate applies to the statically selected plan.
Report all partition costs, natural adjacent2/3/4-player groups, and the Pareto
frontier of observed CDF rows versus memory. No cherry-picked subgroup.

Memory replaces CDF/normalized/classification buffers at max(original capacity,
largest static group union). Keep all learning maps; add group maps/worklists
and(max group size-1) complete d_val and probability buffers. Add256MiB reserve.
Batch32, stride170,1024 particles and existing HU cache unchanged. Report both
constructor-preplanned peak and allocate-before-release peak. A prospective
implementation must add constructor planning; current enable-in-place does
not automatically fit the lower memory estimate.

Admission remains >=25% fewer full large-check CDF rows and static preplanned
peak<=23,000,000,000bytes. No speed claim. A later prototype needs exact kernel
and whole-solver equivalence, graph/lock/zero-reach tests, paired fixed-work
complete timings and required regressions before retention. Average checking
only; no learning or sampling changes.

Run serial via run07; build/test cap240s, inventory cap180s. Preserve raw logs
and immutable input/source/executable hashes. No source edits while work runs.
Port56708 read-only and guard-stop only owned research if user work starts.
