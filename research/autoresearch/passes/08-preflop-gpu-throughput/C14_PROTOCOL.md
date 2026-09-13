# C14: construct the narrowed kernels directly

Not implemented or measured. Baseline remains retained C01+C07+C09. C13's exact
terminal rewrite cut large complete time by 6.3%, but duplicate module startup
made small complete work 3.67% slower and failed the 3% regression limit.

Carry forward the same bounded element-index arithmetic from archived C13.
Change the construction path so it compiles and loads each selected module once,
rather than constructing C09's exact/cohort modules and replacing their terminal
functions afterward. Keep the base ordinary GPU module required for other phases.
Preserve the old constructor as the unchanged control. Use a new research-only
constructor; no production/default or R01 automatic-selection behavior changes.

Make the narrow flag part of each research module's compiler-cache key. Check
the actual CDF element count before enabling narrow code, including any cohort
capacity expansion. Do not mutate dimensions, particle batch, HU cache, scratch
sizes, samples, arithmetic ordering or policies to make the prototype fit.
The CDF/classification entry points now come from the selected module: explicitly
verify their output against the retained path rather than assuming a terminal
rewrite cannot affect them. Build all function/allocation state before publication.

Reuse C13's 48 wide-address witnesses and 420 partial-batch cases. Verify baseline
PTX remains identical to C09 and narrowed kernel PTX remains identical to C13.
Extend full arena/prefix/terminal comparisons to the integrated path, including
2-8 opponents, odd/partial batches, zero reach/recovery, locks/frozen seats,
captured execution and stop. Check full device allocations on both saved fixtures.
Candidate arithmetic output must match C09 exactly before timing.

Time complete initialization plus six sweeps/checks, synchronization and arena
fingerprinting through the existing guarded frozen benchmark. First large pair
requires at least 1% improvement; retention requires three alternating pairs,
at least 3% median large benefit, no more than 3% median small regression, and
full native GPU/default solver regressions. Startup must stay in the metric.
Do not rerun until the small result passes or relax the threshold. All failed
versions and measurements remain archived. No time-to-convergence claim follows.

Use run07's serial process ownership/idle guards: initial build cap300s,
numerical suites cap240s and saved benchmarks cap180s each. No source edits during
work, no parallel GPU loads, no new ten-hour deadline, and no change to 56708.
