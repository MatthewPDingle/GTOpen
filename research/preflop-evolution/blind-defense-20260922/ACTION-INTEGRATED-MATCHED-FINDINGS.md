# Averaging root action paths did not resolve range instability

25 September 2026. Both predeclared trials completed all 78 updates / 39,936
physical deals and passed full independent training readback. Both complete
restricted endpoint evaluations and their independent readers also passed.
The study changed only BB root call/raise regret targets, integrating opponent
action paths on each sampled deal while preserving the original sampled
reservoir stream. It used the two earlier training seed sets for matched
comparisons, not a fresh accuracy holdout.

## Primary result

The complete played-bank, linear/linear, incoming-mass-weighted cross-seed
total variation was **47.03437 percentage points**, compared with **46.31984**
for the previous root-retention estimator: a **0.71453-point increase**.
This does not demonstrate a stability improvement. Two runs do not establish
statistical significance or prove the estimator cannot help with other budgets.

Total variation here is half the sum of absolute differences among fold, call,
raise and jam probabilities, averaged across all 169 classes using the same
incoming mass and opponent-range card removal. It is not a percentage of
incorrect poker decisions or a full exploitability measure.

| Diagnostic | Previous pair | Integrated pair |
| --- | ---: | ---: |
| Weighted total variation, percentage points | 46.31984 | 47.03437 |
| Classes differing by more than 50 points TV | 81 | 73 |
| Incoming mass in those classes | 43.1423% | 43.8749% |
| Classes with different most frequent actions | 96 | 90 |

Some descriptive counts improve while the primary weighted measure does not.
Do not select a favorable count or an attractive chart as the conclusion.

## Aggregate strategies

| Method / run | Fold | Call | Raise | Jam |
| --- | ---: | ---: | ---: | ---: |
| Previous first | 43.0999% | 41.1231% | 15.3288% | 0.4483% |
| Previous repeat | 45.7938% | 38.6108% | 14.8131% | 0.7822% |
| Integrated first | 38.9260% | 45.4851% | 14.7112% | 0.8777% |
| Integrated repeat | 45.1120% | 41.7921% | 12.4526% | 0.6432% |

Within each matched seed the old/new policies also change substantially:
37.55880 and 38.96419 points of weighted TV. Similar overall frequencies do
not establish reliable individual-hand recommendations.

Illustrations from the new pair, with all 169 classes retained in the result:

- 22: first folds 99.88%; repeat calls 96.67%.
- 44: first folds 95.62%; repeat calls 99.89%.
- KQs: first calls 69.72% / raises 30.25%; repeat folds 94.76%.
- AJs: first raises 84.54%; repeat calls 61.61% / raises 18.94%.
- AQs: first raises 99.42%; repeat folds 27.95%, calls 36.09%, raises 5.67%
  and jams 30.29%.
- Some hands become consistent: 88 raises 99.25% / 99.81%; AKs raises
  99.89% / 99.83%. 85o calls 95.00% / 94.78%; this consistency by itself is
  explicitly not evidence that the calling policy is accurate.

## Restricted all-in endpoint gains

All entries are bb per incoming entry. BB may reallocate only its current
fold/jam mass; call and raise are held fixed. BTN may change only its response
to the initial BB jam. These are not whole-game best-response gaps and do not
validate ordinary calls or raises. Smaller is better within this diagnostic.

| Pairing | Previous first BB / BTN | Integrated first BB / BTN | Previous repeat BB / BTN | Integrated repeat BB / BTN |
| --- | --- | --- | --- | --- |
| equal/equal | .074294 / .017246 | .073766 / .027710 | .072837 / .028396 | .067491 / .023944 |
| equal/linear | .074823 / .002504 | .072082 / .006629 | .075856 / .003833 | .068720 / .003908 |
| linear/equal | .005367 / .018746 | .006292 / .036971 | .007836 / .037276 | .005580 / .028841 |
| linear/linear (primary) | .007994 / .010040 | .007974 / .017613 | .012499 / .017961 | .008290 / .012833 |

The primary first-run BB number is nearly unchanged and its BTN number worsens;
both repeat-run numbers improve. This mixed endpoint result does not override
the negative stability finding.

## Verification and resource cost

First/repeat training worker times were 12,220.594 / 12,647.859 seconds.
Full readbacks took 4,546.750 / 4,747.906 seconds. Each store occupies about
6.15 GB measured allocated file space (about 19.5 GB logical); originals remain
preserved. Both training readbacks reconstructed every root and full reservoir
state. Maximum root-state discrepancies were below 4.6e-12. Endpoint readers
reproduced gains within 2.9e-16 bb and cash conservation within 1.5e-14 bb.

Passing these checks supports implementation consistency, not strategic
accuracy. The independent readers share model loading/inference components;
they are not independent implementations of all parts of the learning system.

## Decision and next work

Do not deploy this as a range-quality improvement. Do not launch a larger
training run merely because some charts look better. Integrating root action
paths removes a real conditional noise source, but it was insufficient in these
matched runs. Card/board sampling, sparse class coverage, learned continuation
error and changing opponent policies remain candidate explanations; this
experiment does not separate them.

First address the measured research-pipeline inefficiency described in
RESEARCH-HARDWARE-UTILIZATION-20260925.md. Use bounded saved-data profiling and
equivalence controls, preserving the finished scientific artifacts. That work
should make subsequent discriminating tests cheaper rather than replace them.
Then select a prospective diagnostic that separates remaining chance noise from
continuation learning error before another expensive range-quality trial.
Any new wider response test needs its own uninspected data, declared policy,
resource admission and interpretation. No production changes were made.

## Authoritative records

- `action-integrated-seed-comparison-v1-result.json`, SHA-256
  `d1e6ba6d3ebefc923fee30dfcdff7ee1e08960ca36c539d7975461667af58262`.
- `action-integrated-matched-sequence-v1-result.json`, SHA-256
  `a56dc88206386d52d5e28ffe16fb691342bf517a26abcfcae21a010fe983de1d`.
- `action-integrated-first-exact-v1-independent-review.json`, SHA-256
  `978071c7701da2d95feabefe13e9be14a33fa3f9f3c3f14e70d24cbd21e2a23c`.
- `action-integrated-replication-exact-v1-independent-review.json`, SHA-256
  `a4b99dd12836dc9435fd68e9e3ec0bec7a3d8a9f8c507f2c5760936b83d69465`.
- The comparison continuation result records all child result identities,
  successful exits and timings. The frozen plan is
  `ACTION-INTEGRATED-ENDPOINT-COMPARISON-PLAN.md`.

Scope remains BB versus a BTN 2 bb open, 200 bb effective, 5% rake capped at
2 bb. No conclusion about other positions, stacks, multiway trees or agreement
with GTO Wizard follows from this experiment.
