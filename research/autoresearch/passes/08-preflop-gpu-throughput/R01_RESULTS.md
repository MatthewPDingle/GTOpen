# R01: memory-aware selection and saved-game continuation

The new research-only constructor can select the retained C01+C07+C09 GPU path
when current free memory permits, or return the normal GPU solver with a reason
for fallback. The normal application constructor and port 56708 are unchanged.

The cohort limit is the minimum of configured budget, current free memory minus
512 MiB, and 20,500 MB. The existing cohort planner additionally accounts for its
256 MiB reserve. The original configured budget still selects the particle batch
and heads-up cache. A lower optional-sharing limit cannot silently change that
reference layout. All-singleton plans are refused. Failure to query memory or
construct the optional engine falls back to a fresh normal GPU construction;
failure of both returns both error descriptions.

Qualification passed:

- Pure selection checks cover budget/reserve boundaries, failed memory probing,
  construction-error fallback and failure of both constructors.
- Two/four-player numerical fixtures cover optimized selection, low-memory and
  failed-probe fallback, frozen seats, point locks, captured execution and stop.
  All compared strategy/regret arrays and root results match bit for bit.
- The immutable six-player (23,038 nodes, age 1,000) and eight-player (1,567,754
  nodes, age 1,050) saves each ran through retained, automatic, normal and forced
  fallback paths. Six iterations/checks match the archived C09 results. Saving,
  reloading and taking another iteration also match across all four paths.
  Saved files are byte-identical per fixture. Config/model, seat policies, locks
  and hero fields checked by the harness are preserved.
- All 19 native GPU regressions and 181 default solver tests pass on this source.

| Large fixture path | Six-step diagnostic time | Selected engine |
| --- | ---: | --- |
| Explicit retained | 55.51 s | C01+C07+C09 |
| Automatic selection | 55.65 s | C01+C07+C09 |
| Normal | 65.31 s | Normal GPU |
| Forced low optional budget | 65.91 s | Normal GPU |

These single timings exclude input loading and the later save/reload check.
They are a sanity check, **not** a new paired benchmark or progress-graph gain.
The smaller fixture's times were 0.96-1.11 s. Full saved-run process times and
inputs are recorded separately. The established retained gain remains unchanged.

Evidence: `check_r01.py`, `raw/r01-verified.json`,
`check_r01_regressions.py`, and `raw/r01-regressions-verified.json`. Version 1's
source is archived because version 2 adds the frozen-save harness; both sets of
source/input hashes are checked. The saved outputs are local ignored artifacts
with recorded SHA256 hashes; original saves were never overwritten.

Remaining before production promotion: test recovery after partially completed
optimized GPU allocation (current construction-error test is injected, and the
low-memory test rejects the plan before device allocation), separate the retained
modules from unrelated research features, integrate/report selection in the app,
and validate the actual server build in an isolated instance. No live update is
authorized by this qualification. The broader convergence/large-speedup goal is
still open. [C13](C13_PROPOSAL.md) is the next proposed throughput experiment.
