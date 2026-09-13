# D13: fixed sampled-rank reuse screen

Registered before extracting tied-rank counts. GPU preflop scope only; port
56708 read-only. Retained C14/R03 remains runtime baseline. This is a static
source-data diagnostic, not CPU optimization or a change to equity sampling.

Different hero hand classes with exactly equal (lower,upper) rank boundaries
within the same sample have identical opponent products. They can potentially
share those products before each hand performs its original ordered quadrature
additions into its own running sum. Never share the running sum or reassociate
quadrature/sample additions: histories can differ between hand classes.

Measure two fixed schedules on the existing seed-90210, 1024-sample, 169-class
table: (A) compact all distinct rank groups per sample; (B) reuse only within
existing contiguous 32-class warps, including the last 9-lane partial warp.
No new sampling, hand sorting across samples, normalization or CDF arithmetic.
A could compute products into shared scratch followed by per-hand lookup and
ordered addition, with two block barriers per sample. B would elect per-warp
leaders; fewer active lanes do not necessarily reduce issued warp instructions.
Both leave probability-table construction unchanged.

Export the exact table from a test-only Rust entry point. Verify every order is
a permutation, each (lo,hi) interval contains its hand and exactly covers the
matching group, and groups partition ranks. Include synthetic all-equal,
all-distinct, partial-warp and boundary-spanning cases for the count routine.
Archive compressed full table, hashes and source. Independently decode in Python
using sets and sorted unique runs, matching all per-sample global/warp counts.

Apply D11 large opponent-count histograms to operation counts. Only the per-
opponent portion O+3*Q*O can be shared; original 2*Q ordered accumulation work
still happens for every hand/sample. Count logical gathers likewise, while
excluding synchronization, scratch traffic, election/mapping and allocation
costs. This is an optimistic work screen, not a timing or hardware forecast.

Admit A for a separately qualified prototype only if source terminal arithmetic
falls at least 30% in both large learning and checks. Admit B only if the same
reduction is at least 20% in both. Thresholds/schedules fixed before counting;
no retuning after results. Report small case descriptively. An admitted prototype
still needs exact adversarial kernel/full-arena checks before alternating timings
and normal retention gates. Rejection leaves production kernels untouched.

One guarded build/export at a time; cap300 seconds. Source edits stop while it
runs. Host verification follows terminal exit, no repeat hardware-counter access.
