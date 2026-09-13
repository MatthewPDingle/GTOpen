# C07 proposal: bounded three-player cohorts with more memory headroom

C06 preserved numerical results but worsened complete time41%, checks33% and
unchanged learning62%. Its22.655GB allocated working set is a suspect, not a
proven cause. Test whether substantially more headroom rescues sharing before
discarding the whole mechanism.

Use C06's archived dispatch/allocation approach with at mostTHREE players per
group and a20,500MB cohort-plan ceiling INCLUDING256MiB reserve. Continue to
construct the ordinary reference layout with23,000MB so the baseline's32-
particle batch and HU cache remain identical. Apply the tighter cap only when
selecting/allocating added cohort storage; do not shrink sampling or caches.

Choose minimum static union work among fitting <=3-player partitions, then
memory and lexical masks. Verify the selected groups/memory against D05's
membership histograms before timing. Require at least25% fewer observed large
check CDF rows for this static plan. D05 shows several candidates around31%
reduction below20.5GB; do not choose based on measured timings.

Register a separate protocol before implementation/runs. Add missing seven-
player, no-multiway rejection and pointer restoration after explicit errors to
the retained numerical qualification plan. Keep C06's exact prefix/terminal/
arena/capture/frozen/zero-recovery comparisons. First paired large screen and
extended retention gates remain unchanged. If it passes, repeated alternate-
order pairs and full regressions remain required. If it fails, archive/reject.

Record available device memory and clocks before/after each owned run using
read-only queries outside timing, if available. They are context, not proof of
residency while running. Do not attribute the C06 slowdown to paging without
direct evidence. No simultaneous profiler work. Port56708 remains untouched.
