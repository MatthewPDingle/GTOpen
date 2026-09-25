# Faster research averaging with identical policies

25 September 2026. The verified bulk feature builder now has a separately
versioned CUDA averaged-policy runtime. Both complete action-integrated banks
(78 played generations, linear weights 1–78) produced byte-identical action
probabilities and own-reach support to the original runtime in every repetition.

| Bank / saved query batch | Observations | Original repetitions | Bulk repetitions |
| --- | ---: | --- | --- |
| First / train-000000 | 29,080 | 4.438 s, 4.031 s | 0.890 s, 0.938 s |
| Repeat / train-010752 | 29,068 | 3.953 s, 3.907 s | 1.203 s, 0.906 s |

This includes the complete `average` call: feature preparation, legal-action
and history checks, table overrides, GPU inference, own-reach weighting and
output transfer. It is a two-batch implementation control, not a whole-study
speed benchmark. Original bank loading still took about 36.6 seconds each.

The original and bulk calls alternated order. Both retained double-precision
inference, exactly widened stored float32 weights, TF32 disabled, model chunk
size 8 and the original sequential accumulation order. No model, table, policy
rule, training result or production binary changed. The source copy differs
from the original CUDA bank only in its description and feature import; the
new wrapper composes the same exact-BTN and integrated-BB table overrides.

The first control attempt failed before comparison because a saved *training*
query file lacks the own-history links required for behavioral averaging. Its
registration, failure status and log are retained. Version 2 uses authenticated
full-history query files from the completed earlier wider evaluation. It
finished successfully in 124.11 seconds of worker time.

Evidence: `bulk-average-control-v2-result.json`, both registrations/status
files, and both logs. The new scientific use is specified in
`PAIRED-CONTINUATION-DIAGNOSTIC-PLAN.md`; this control does not supply evidence
of improved poker accuracy. A synthetic additive factorial check also verified
the reducer gives exact 6/4/2/0 diagonal/BB/BTN/interaction effects with zero
paired standard error when common card noise cancels.
