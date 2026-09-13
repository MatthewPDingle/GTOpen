# C21 rejected: exact sparse scan does not improve complete runtime

| Large fixed-work run | Retained C14 | C21 | Candidate / control |
|---|---:|---:|---:|
| Complete seconds | 53.1591 | 53.6308 | 1.00887 |
| Warm learning median | — | — | 1.02930 |
| Warm accuracy-check median | — | — | 0.99836 |

The first complete pair is 0.89% slower and fails the 1% improvement gate.
No extended campaign or retention regressions were run. This single pair is
not a precise estimate of the true slowdown, but provides no qualifying gain.
The integration is removed; the four retained improvements remain unchanged.

The standalone kernel passes all 1,008 exact prefix/guard cases. C21 reduces
static PTX instructions from C20's 408 to 280 (original writer324), retaining
26 registers, zero spills and zero shared memory. Six real zero-vote branches
skip the five scan steps, each using the shuffle's validity predicate and
round-to-nearest addition. All20 original compiled kernel entries are unchanged.
Smaller static code and real skipped arithmetic did not yield a complete gain.

Nine expanded solver tests pass, including3..9 seats, fixed/learning players,
batch5/32, full terminal/prefix/arena comparisons, graph/eager evaluation,
zero recovery, stop and constructor failure recovery. Pointer-selection checks
verify sparse learning and original accuracy-check writers; cohort checks still
call the original function. Small/large declared device allocations remain
313,945,632 / 20,178,315,124 bytes, with batch32 and unchanged caches.

Every one of the six saved checkpoints agrees with retained C14, including
gap/EV/iteration data and all529,900,514 final arena entries, fingerprint
`27b4d2870b404cae`. Frozen benchmark executable SHA256:
`7f2991df4893b9c8a4536e668f0bccfe9da8bc4e6ac9043988233f49451f34be`.

Guarded qualification took198.547 seconds including compilation; the9-test
device suite took66.62 seconds. Small/large allocation checks took2.141/9.110
seconds. First-pair guarded wall times were56.937/56.984 seconds. Complete
reported timings include cold setup and synchronization, not just the kernel.

Evidence: `check_c21_screen.py`, `check_c21.py`, immutable prefix/timing
verification files, source archivesv1/v2, raw logs/layouts/benchmarks and
`raw/c21-restoration.json`. A Python generator quoting error was corrected
before it executed; no failed GPU trial or numerical correction was hidden.

No runtime change is retained; only the manual diagnostic module remains.
Port56708 and the qualified R03 executable were untouched. This does not
resolve the large-game convergence or tenfold performance goal.

Next investigation should target work volume rather than another unchanged
scan shortcut. One unqualified possibility is a bounded two-kernel pipeline
for shared rank products, avoiding C18's per-sample block barriers; its scratch,
launch and exact accumulation-order costs need screening first. C18 and C21
must not be rerun unchanged in search of a favorable timing result.
