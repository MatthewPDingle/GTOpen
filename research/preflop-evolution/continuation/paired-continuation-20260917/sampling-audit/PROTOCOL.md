# Paired board-sampling uncertainty and one independent repeat

Registered design, 17 September 2026. Research only; production stays unchanged.
The previous 72-choice development screen failed and remains failed. This study
cannot promote a model or change that screen's gates.

## Existing-data audit

For each of the four completed families, resample boards within their original
five texture strata, 5,000 times. Preserve each board across all three connected
branches. Recompute legal-pair-mass ratio estimates, both direct and with the
existing equity control variate, then propagate them to BB call-versus-3-bet
values using the existing terminal coefficients. Keep the original qualification
mask and parent decision masses fixed. Unit resampling must reproduce point
estimates. Report weighted target standard errors, pointwise percentile widths,
branch contributions and aggregate error variation. Show unpaired quadrature
only as a diagnostic of covariance, never as the actual uncertainty estimate.

Reconstruct the previously rejected best-mean screen choice once, leaving each
family out as before. Freeze its four coefficient sets before new labels. These
are diagnostic controls selected on development results, not eligible candidates.
Intervals condition on fixed coefficients and do not include training or model
selection uncertainty. Do not refit on bootstrap samples or repeat labels.

Choose one repeat family, from linear and polar only, by the largest original
qualified-mass-weighted adjusted target standard error. Repeat ALL three linked
contexts, not just the context that happens to help a candidate.

## Prospective repeat

Use ten new draws per texture stratum, 50 boards total, shared across the three
contexts (150 solves). Seed: `paired-sampling-independent-panel-v1`. Draw from the
full canonical population, without inspecting results or searching seeds. Allow
and report incidental overlap with the original ten-board panel. The two panel
draws use independent seeds; the underlying per-board solver is deterministic.
Do not exclude old boards, which would change the target population.

Copy the exact ranges, preflop policy and postflop action menu from the selected
family. Keep CPU and GPU gap limits at 0.1% pot and maximum iterations at 2,000.
Validate every label, metadata and input hash. The existing two-ULP metadata
adapter may normalize inclusion-probability serialization only; never labels.
One offline GPU job at a time. Check the app's preflop, postflop and reports
status before starting each job. Wait if busy. No server rebuild or app mutation.

Bootstrap the fresh panel with seed 2026091720; bootstrap the old panel separately
with seed 2026091721. Keep the old qualification weights for the comparison and
report any new BR-quality failures. Report target shifts, uncertainty, unchanged
baseline error, and fixed rejected-control error. Summaries of pointwise intervals
are descriptive, not family-wide multiple-comparison significance tests.

## Interpretation and stopping

Stop after these 150 labels, even if the conclusion is inconclusive. No automatic
extra sampling, model search, native integration or deployment. A fresh-panel
control reduction interval crossing zero means direction remains unresolved.
Nonzero residuals against a better measured target motivate a representation
experiment; they do not establish the specific missing feature. Noise estimates
are not estimates of the fraction of model error caused by noise.

Stratified percentile bootstrap is approximate, especially with only two old
boards per stratum. No finite-population correction is used. Intervals describe
board sampling only, not solver bias, abstraction error, cached equity error or
generalization to different stacks/ranges. Selection of the noisiest family also
limits broad claims. This is a target-quality diagnostic, not a fresh model
selection test, and no claim of full-game real-world EV improvement is permitted.
