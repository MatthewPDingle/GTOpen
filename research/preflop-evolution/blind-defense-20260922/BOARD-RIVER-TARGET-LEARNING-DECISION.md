# Decision after conditional targets and coverage controls

The result points to a generalization problem, not merely noisy training
answers. The unchanged network can fit exact answers for the training deals
closely, but much of that accuracy does not transfer to unseen deals.

The registered fresh-deal comparison reduced held-out MSE by 38.2% and local
decision cost by 27.8% versus one sampled opponent. Against 16 sampled opponents,
the improvements were only 3.6% and 4.3%. Bank A decision cost was slightly worse
with exact targets, so the predeclared integration gate failed. That result is
preserved. Nothing is qualified for self-play integration or production.

Exact-target training MSE was 3.312 bb squared while final MSE was 4088.710.
The large gap is consistent with fitting/memorizing the narrow training sample;
it does not identify a single representation defect or prove more data alone
will solve the problem. This is also not a measured preflop-range improvement.

The separate training-only curve provided a useful next clue. Expanding from
8 to 48 distinct fit deals reduced development MSE by 25.2% and local decision
cost by 33.1%, with the same architecture and 512 steps. The overall trend was
positive, although bank/actor subgroups were not uniformly monotone. This is
exploratory evidence from 16 development deals, not a scaling law or an
independent confirmation of the original final result.

## Next bounded comparison

Test broader deal coverage at the SAME total number of training rows. This
separates the value of more distinct private-hand/board situations from merely
adding more decisions or optimizer steps. Keep the current architecture,
exact target definition, pot/actor quotas and fit budget fixed initially.

Reuse eligible labels from the original 64 training deals where practical,
while adding new physical deals and reserving new evaluation deals. Never use
the spent original 32 final deals to choose settings or claim fresh validation.
One practical design to work out is 1,152 training cases spread across roughly
192 deals versus the current 64-deal set, preserving aggregate actor/pot-band
counts. Exact versus 16-sample targets can remain a separately specified
comparison on the broader set; define all gates before collecting new labels.

The exact partition, deterministic state selection, source identities,
resource estimate and tests must be registered before executing that new
comparison. This note is a direction, not that registration. Preserve overlap
identities for any reused training rows. New boards and observation keys must
be separated from training and earlier final evaluation as specified by the
new plan. Retain all proposed/accepted deal identities when deduplicating.

If that fails to improve transfer, inspect representation or regularization
with a separate development-only design. If it succeeds, first derive and
qualify the estimator integration described in the integration notes; then
retrain and evaluate complete policies on fresh deals. Local prediction gains
must eventually translate to reliable preflop calling/raising values.

## Resource evidence

The main collection took 40.2 minutes and retained about 0.51 GB. Its 36 fits
took 53.3 seconds; the subsequent 48-fit coverage diagnostic took 63.9 seconds
and added 4.64 MB. Collection, rather than network fitting, dominates this test.

A timing inspection of the first 96 training cases found median native export
time 1.265 seconds and median combined teacher inference, posterior/label
calculation and NPZ-save time 1.234 seconds. Four native exports already overlap;
two archive writers overlap GPU-side work. These inclusive timings do not
isolate GPU kernels and are not a controlled speed benchmark. More export
workers alone are unlikely to remove the serial model/label/save bottleneck.
Profile that stage before promising a speedup for a larger collection.

Both result plots were rendered and visually inspected. All completed model
artifacts and primary metrics passed independent readback. Detailed evidence
is in BOARD-RIVER-TARGET-LEARNING-FINDINGS.md and
BOARD-RIVER-GENERALIZATION-CURVE-FINDINGS.md and their linked JSON records.

No production settings, solver behavior or historical archives were changed.
The broader preflop research goal remains active.
