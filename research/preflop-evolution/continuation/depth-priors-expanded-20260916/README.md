# N12b: unchanged depth priors with the new training coverage

Specified before N03 training completes or either prospective evaluation
starts. N12's original-data screen improved 4.05% over N09, missing the fixed
5% requirement. Do not alter that result or its parameters. Repeat the same
N12 model once with the 36 new range/depth contexts, alongside an unchanged
N09 model fitted to those same expanded training inputs.

Use 62 training contexts with equal context weight and the unchanged original
26 validation contexts. Exclude the entire source family, including related
synthetic and development cases, in every fold. Keep all optimizer settings,
depth knots and penalties fixed. Require at least 5% lower equal-family mean
error than both same-data N09 and original-data N09, at least 15% lower than
Balanced, and no family more than 5% worse against any of those controls.

Fit a final model only if eligible. Freeze its coefficients and register for
evaluation before generating any corresponding references. Reserve the same
400 future physical queries as the N06b/N08 expanded-validation protocol
under a separate candidate registration. If those references are generated,
reuse their unchanged validated files and record hashes. If no N06b/N08 model
qualifies, generate these queries separately for N12b. Never combine partial
source outputs or relabel existing files. The registration must precede every
source reference; previously observed results cannot be reused as fresh tests.

The prospective gate is unchanged: each held-out family must improve at least
15% versus Balanced and no case may be more than 10% worse than the earlier
frozen conditional predictor. Report paired conditional 90% bootstrap
intervals. GPU arithmetic, repeated runtime and changed-policy checks remain
separate prerequisites. No deployment; preserve the original fixed deadline.
