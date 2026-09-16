# Conservative value blending (N33)

Training-family screen registered before computing blend results. This tests a
different accuracy/settling tradeoff, not a claim to beat the full N15 predictor.
The practical objective remains more accurate values than ordinary Balanced
while approximately maintaining end-to-end solving performance.

Reproduce N15's exact four held-out-family fits on the original 26 training
contexts. Keep architecture, seeds, fitting settings and 0.75 neural correction
unchanged. For each held-out context blend predicted gross pot shares as:

`(1 - alpha) * Balanced + alpha * N15`

Fixed strengths: 0, 0.125, 0.25, 0.5 and 1. The endpoints are controls. Require
all 26 alpha=1 errors to reproduce N15 within 1e-9. Both models already conserve
compatible-mass total pot share, so their convex combination must also conserve it.

The lowest nonzero tested strength whose mean family error improves at least 15%
over Balanced and improves each family by at least 5% is worth a subsequent
settling experiment. Report its full loss versus N15, with no assertion that it
passes N15's distinct predictor-selection gate. Do not adjust thresholds or add
strengths after results. This screen uses only training labels, not N15/N20/N21
evaluation labels. A selected blend requires new prospective accuracy references,
a GPU correctness check, and end-to-end settling/runtime validation before use.

No runtime improvement is assumed: the full predictor still has to be evaluated.
CPU training must finish before the queued N32 GPU timing work starts. No live
application access, deployment or production-model writes.
