# C18: compact equal-rank products rejected

The first large complete-work pair was **43.67% slower**, despite identical
numerical results. Do not extend this implementation to repeat pairs or claim a
speed gain. Candidate runtime code is removed; retained C14/R03 is restored.

| Measurement | Result |
| --- | ---: |
| Retained complete work | 53.130 s |
| Compact complete work | 76.331 s |
| Complete candidate/control | 1.43667x |
| Warm learning candidate/control | 1.29009x |
| Warm accuracy check candidate/control | 1.59638x |
| Extra global mapping storage | 2,080,768 bytes |

Complete work includes construction, six sweeps and checks, synchronization and
warmup. Warm ratios compare medians of the four post-warmup rows. Both warm
operations regress, so the loss cannot be explained solely by extra construction.
One pair is sufficient for rejection under the registered >=0.99 screen; no
extended campaign or full runtime-retention regression campaign was started.

## Exactness and allocation evidence

- 5,040 isolated cases pass bit for bit, including all 2-8 opponent templates,
  real/synthetic ranks, zero/dense/sparse probabilities, partial batches,
  nonzero per-hand accumulation histories and 23 untouched output guard slots.
- Eight final integration tests pass: 3-9 player fixtures, fixed/learning seats,
  batches 5/32, complete regret/average arenas and roots, graph capture/replay,
  zero-mass clearing/recovery and stop preservation. Budget/duplicate-enable/
  post-capture rejection checks also pass without changing state.
- Both immutable saved-game layout checks match every original buffer and
  cohort plan, adding only the four declared rank-mapping arrays. Final measured
  checkpoint gaps, EVs and complete arena fingerprints match retained C14.
- Only the selected terminal entry differs in each integrated module. Other
  compiled entries match the retained PTX. No local spills were reported.

## Implementation corrections preserved

The first isolated helper was exact. Initial full integration also passed its
seven tests, but an edit-script assertion stopped before benchmark/memory
reporting was added. That intermediate source is archived as v2. Reporting and
an eighth guard test were completed in v3; its compiler audit found 15,592 bytes
of shared memory, because template specializations owned separate arrays.

The final v4 passes one explicit shared array from the terminal entry to the
helper, matching the proposed storage bound: 3,380 bytes plus 44 bytes of existing
metadata, 3,424 total. Registers are 44. The corrected helper repeated all 5,040 cases;
the final frozen executable repeated all eight integration tests. All initial
source snapshots, compiler outputs and successful intermediate runs remain in
the record. Timing uses only this corrected v4 executable.

## Interpretation and next constraint

D13's arithmetic-reuse count was valid, but it did not predict runtime. This
implementation adds block barriers, rank mapping and shared-memory traffic.
The measured total cost is worse; available evidence does not isolate a single
hardware cause. No hardware counters were enabled or driver settings changed.

A future reuse schedule would need to avoid this repeated cross-warp coordination
cost and still preserve each hand's original accumulation order. Warp-local
reuse remains a distinct D13-admitted possibility, but fewer active lanes alone
do not imply fewer issued warp instructions. It needs its own design review
and registered screen; do not combine it into C18 after rejection.

[Protocol](C18_PROTOCOL.md), [independent audit](check_c18.py),
[verified results](raw/c18-verified.json), [guarded runner](run_c18.py),
[restoration receipt](raw/c18-restoration.json). The qualified R03 executable's
hash is unchanged. Port 56708 and the user's sessions were not modified.
