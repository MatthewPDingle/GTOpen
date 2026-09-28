# Supplemental deal-level robustness review

Register this before any final scoring in the equal-budget coverage study.
It adds descriptive analysis only; the frozen training, final set and original
two advancement gates are unchanged. It cannot turn a failed gate into a pass.

For broad-exact versus dense-exact and broad-exact versus broad-sample16:

1. Reconstruct squared error and local Fold/Call decision cost from saved
   predictions and exact targets. Reconcile each model's primary metric and
   its fixed equal-model aggregate with the published result.
2. Group by the physical deal, preserving dependence between its states and
   both banks. Report how many of the 32 deals favor broad-exact, the median
   per-deal difference, and its range. Per-deal values average the corresponding
   state means equally over all bank/actor/repetition models. If unsupported
   targets change counts, report that these deal summaries have different
   weighting from the primary fixed model/state aggregate.
3. Remove each physical deal in turn from ALL models, recompute each model's
   mean over its remaining states, then average models as in the primary
   evaluation. Report the 32 leave-one-deal-out differences and their range.
   This shows sensitivity to individual deals; it is not a confidence interval,
   hypothesis test, scaling law or significance claim.

Positive differences mean the reference arm has greater error/cost, so broad
exact is better. Do not use these diagnostics to select a repetition, edit
training, drop final deals, add data, change gates or declare full-policy EV
improvement. Preserve aggregate findings even if the descriptive sensitivity
looks unfavorable. No board identity will be used to tune the current study.

Implementation controls use small hand-calculated arrays before registering
the analysis. Execution is CPU-only after the main evaluation and independent
report readback have completed, within 60 seconds and 1 MB added evidence.
Source, plan, frozen study plan, and membership manifest hashes are retained.
