# Shorter large-game screening

Host-only retrospective, following the user's suggestion to accelerate research.
The small-game audit missed two retained wins. A different option keeps the
large fixture and its GPU working set, but reduces the number of timed sweeps.

`audit_short_screen.py` reads 20 historical large-game candidates and their own
paired controls. It subtracts the recorded iteration and accuracy-check time
for omitted rows from total runtime, keeping all other recorded costs. The
first two rows remain warmups. This is an estimated runtime, not a measurement
of a shortened executable. It retains the original end-of-six-row sync and
fingerprint cost rather than pretending to have measured an earlier sync.

| Total sweeps/checks | Steady rows | Median estimated pair time / original | Missed retained wins at 1% screen |
| --- | --- | --- | --- |
| 3 | 1 | 54.44% | 0 of 4 |
| 4 | 2 | 69.58% | 0 of 4 |
| 5 | 3 | 84.81% | 0 of 4 |

All three proxies agree with the original 1% large-game screen classification
for these 20 candidates. That includes small gains which passed screening but
did not meet final retention requirements. It does not mean all were retained.
Several candidates have only one pair; this is selected retrospective evidence,
not independent validation or a confidence bound. Compilation time is excluded
from the potential saving. Fewer rows may increase timing noise or alter clock
and synchronization behavior.

## Next validation

Prefer testing the three-row large-game proxy before spending GPU time creating
a medium fixture. Keep all samples, precision, players, actions and input state.
Run actual three-row and six-row versions with the same executable, alternate
their order, and compare both exact intermediate checkpoints and timing. Include
a known large win which the small fixture missed and a near-threshold loser.
Then test a prospective candidate before adopting this as a default screen.

The current C23 executable and registered six-row protocol remain unchanged.
Its forthcoming first timing pair provides prospective evidence for the proxy
without an extra GPU run. Do not silently replace that trial with three rows.
Even if a shortened screen is adopted, final retention still requires the full
paired benchmark, complete correctness qualification and regression tests.

Evidence: `raw/short-screen-audit.json` contains the ratios, individual pairs
and input hashes. No live application state or solver source was changed.

## First prospective candidate: C23

The recipe and historical audit were recorded in `03eb8aa`, before C23 timing.
`check_c23_short_proxy.py` checks that those exact registered files are unchanged
and applies the three-row recipe to C23's three subsequently completed pairs.
All three screening decisions agree: C23 remains a clear win. Median estimated
pair time is 63.08 seconds versus 113.14 seconds in the complete benchmark.

The proxy reports 11.52% less runtime versus 13.95% in full timing, a difference
of 2.44 percentage points. This is useful caution: even an apparently stable
screen can alter the size of the gain. It is not evidence that a 1% cutoff would
reliably classify a near-threshold candidate. Actual shortened runs and a
near-threshold comparison remain untested. Preserve the full final retention
gate; do not use this single clear win to declare the shorter screen calibrated.

Evidence: `raw/c23-short-proxy-verified.json`. This additional check used no GPU
work. The candidate's small-fixture and native/default checks are still pending.
