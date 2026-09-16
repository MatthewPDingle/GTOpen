# N23: lightly weighted range-diversity training

Fixed training-only follow-up to N22's rejected sensitivity penalty. Keep N15's
104-feature linear base, two width-8 residuals, seeds, 500 training steps, .1
output penalty and .75 final shrinkage. Add N03's 36 synthetic training-range
contexts at one of two fixed per-context weights: .05 or .2. The .2 weight
reflects their 20-board versus original 100-board sample count; .05 tests a
more conservative use of this noisier, synthetic evidence. Original 24 training
plus two development contexts retain weight1. Control0 excludes all added data
and must reproduce N15 within1e-9. No extra reference solves or test labels.

Apply weights consistently to ridge feature normalization, ridge loss and
neural training loss. Keep ridge penalty .1 divided by total effective case
weight. Neural centering uses each context's genuine compatible hand mass,
not its training weight. Keep seeds, step counts, output/parameter penalties
and all inference work unchanged. CPU float64, one OpenBLAS/two Torch threads.

Leave out each complete source family, including all its interpolated contexts.
Validate on the unchanged original26 cases. Evaluate local sensitivity on the
same six 1% range-mixture directions as N22. Use N22's unchanged joint gate:
mean and every-family error <=5% worse than N15; mean >=5% better than the old
linear control; mean sensitivity >=25% lower than N15, with no family increased.
Choose the eligible weight with smallest mean error. Do not extend the grid or
relax thresholds. This gate explores maintaining accuracy while improving
stability; sensitivity alone still does not prove faster convergence.

Freeze before fitting. If eligible, fit all62 contexts with the selected weight
and freeze the candidate before separately registering fresh evaluation.
Identical inference shape does not prove runtime, correctness or convergence.
No deployment or production changes. Run only while GPU reference generation
is active or GPU is idle, never alongside isolated GPU timing. Preserve the
fixed20:49:02UTC deadline and all earlier sources and gates.
