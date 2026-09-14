# R04 integration progress

R04 puts retained C23's static rank-boundary tables in the normal GPU selector.
The application on 56708 still runs R03. This is not a deployment receipt.

## Implementation and initial qualification

The selector promotes its fresh retained engine, preserving its context,
cohort plan, batches, policies and arithmetic. On promotion failure the private
engine is dropped, then the retained layout is rebuilt; the prior normal-GPU
fallback still applies. Selection metadata identifies static storage and any
promotion fallback. Fault injection and evidence-file output are test-only.

The initial source-rewrite helper refused an unmatched guard expression before
any build. Its partial gpu.rs edit was verified and restored from the archived
original, the expression corrected, and preparation completed. No failed build
or GPU run was hidden or overwritten.

Three selector tests (including real allocation failures at all three stages),
10 integrated numerical/save/stop/recovery tests, and 20 normal GPU tests passed.
CUDA source, PTX, resource reports, saved games and interrupted continuation
artifacts match the qualified C23 outputs byte-for-byte. The normal GPU test
asserts that supported cases actually select static tables.

Frozen benchmark SHA256:
`3e102a6478b4952d2d56dcf08a553569949d37600506276292c66bee674c6546`.
Source snapshots and the complete source hash map are preserved in
`artifacts/r04-v1` and `raw/r04-initial-verified.json`.

## Normal selection overhead

Both paths run in the same frozen executable: the private C23 constructor is
the control; normal application selection is the candidate. Three alternating
pairs per fixture use the full six-sweep/check workload and original saved
states. All checkpoints, complete arena fingerprints, table layouts and cohort
plans match C23. Selection reports confirm static tables with no fallback.

| Fixture | Candidate/control ratios | Median overhead |
| --- | --- | --- |
| Small | 0.95844, 1.02437, 1.00940 | +0.94% |
| Large | 0.99665, 0.97315, 1.02077 | -0.34% |

Both pass the registered maximum 3% median integration-overhead gate. Negative
overhead here is not credited as another optimization. The timings support
preserving C23's benefit when selected by the normal app constructor.

## Release qualification complete

R04 is ready for deployment, but is not deployed. Port 56708 remains R03 with
its stopped iteration-53 session.

Both immutable saved fixtures match the qualified six-iteration saves and the
next iteration after reload exactly. The normal selector uses static tables
on initial construction and reload. The default solver suite passed 181 tests;
the server suite passed 20 tests, with one ignored. The earlier native GPU suite
passed 20 tests. The normal server build succeeded.

An isolated server on port 56710 completed both fixtures, saved and reloaded
them, then stopped during actual running work. Resuming directly and resuming
from the interrupted save produced identical results. All ten server solves
selected static tables without fallback. Postflop, report and library state
remained unchanged. The isolated server closed after qualification.

The independent final checker verified source and executable hashes, exact
saved checkpoints, stop/reload replay, guarded logs and server cleanup.
See `raw/r04-release-verified.json` and `check_r04_release.py`.

Frozen server SHA256:
`dcffd57887bb0a6e070b64d713222ff4d5d7cc7d9e55fa3cf986b29e72824025`.

C23's measured improvement is 13.95% less large-game runtime and 5.03% less
small-game runtime. R04 adds no separately credited speed improvement: it
qualifies that implementation for normal app use. The broader convergence
quality and 10x goals remain open. A production switch must preserve the
current user session, rather than restore an older deployment backup.
