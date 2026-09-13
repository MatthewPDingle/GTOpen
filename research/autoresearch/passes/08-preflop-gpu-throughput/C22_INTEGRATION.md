# C22 integration schedule

Before full solver testing: retain the original CDF modules and append one
producer and one consumer to a separate narrow exact-reuse module. One mapping
flag selects the original traverser versus cohort slot formula; aliases remain
unchanged. Producer copies the original ordered opponent-base preparation into
44 bytes of shared metadata, with one initial block barrier. There are no
per-sample barriers or shared products. Consumer derives the live opponent
count directly and reads the original prepared probability.

Scratch is allocated for the original batch capacity (32), even when tests
temporarily use batch5. Its per-terminal stride uses the current batch, always
within the fixed allocation. Tile allocation follows D18. No extra device
metadata is introduced beyond its four rank maps and product scratch. The
existing 256 MiB allocation reserve is retained inside the 23,000 MB budget.

Select the candidate only through an explicit test constructor. Partial
allocation failure must leave a supplied retained engine usable, free local
allocations and allow a later retry. Kernel and standalone resource gates apply
to computation; integrated metadata permits exactly the producer's 44 shared
bytes. Preserve all original PTX entries in the appended module.

Repeat existing cohort whole-arena/terminal/prefix/zero-recovery/stop tests
with a seventh candidate mode. Add candidate eager-versus-graph tracing and
constructor failure/recovery tests, including late enable refusal. Audit both
saved-game allocations, then six complete large sweeps and checks against the
control. Continue only through C22_PROTOCOL's unchanged timing gates.
