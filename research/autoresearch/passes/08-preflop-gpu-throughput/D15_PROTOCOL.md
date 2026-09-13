# D15: empty scan-tile feasibility bound

Registered before computing support bounds. GPU preflop only, C14/R03 retained,
port 56708 read-only. Candidate mechanism: before each 32-class prefix scan,
use a warp-wide zero test to skip the shuffle/add chain when all its input
values are zero. Loads, detection, carry handling and CDF stores remain. Do not
skip merely because the hero's own reach is zero. No approximation or pruning
of small positive values; future exactness tests must cover subnormal and
signed-zero behavior before implementing this mechanism.

First reuse immutable D10 support histograms and normalized-identity witnesses;
no new GPU extraction. A 169-class row has five 32-class tiles and one nine-class
tile. With K positive entries, at least ceil(K/32) tiles are nonempty, so
6-ceil(K/32) is an optimistic bound on empty tiles, independent of sampled order.
Verify this capacity bound by exhaustive combinations of the six tile sizes
for every K from1 through169. Positive-mass distributions never have K=0 here.

Learning rebuilds distinct CDF rows independently for each traverser: sum that
seat's unique support histogram. Average checks use retained C14 cohorts:
decode each seat's exact baseline identity set, union within each cohort and
count each identity's cohort multiplicity. D10 preserves global newly-interned
support histograms but not the per-ID support assignment. To upper-bound the
check schedule, sort the largest support-derived empty-tile allowances with
the largest multiplicities (rearrangement bound). Do not present that pairing
as the actual correspondence. Independently audit with capacity layers.

Reconcile row totals with D11, both immutable saved configurations and D10
witness hashes. Report small and large learning/check bounds separately.
All1024 sampled orders are covered by the capacity bound; it is not a measured
zero-tile count. Additional bounded-classifier duplicate rows are outside this
distinct-row model and cannot be claimed as avoided work.

Admission to a NEW actual-support/order inventory requires a bound of at least
20% empty tiles in both large modes. Failure rules out this particular mechanism
at that work-volume gate before further extraction. A pass admits only further
measurement, never a GPU prototype or speed claim. The actual schedule could
have no empty tiles. Even free scans retain CDF writes and terminal evaluation.
No retuning the threshold after seeing the bound.

One guarded host census capped at180 seconds. Independent struct/array witness
decoders, immutable inputs and script/protocol hashes. No runtime edits, builds,
driver settings or production changes.
