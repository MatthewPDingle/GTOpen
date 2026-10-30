# Fit counter-strategies using known action values

23 September 2026. Post-hoc diagnosis of the already inspected combined
269-input evaluation. No new deals, current-candidate reads, GPU inference,
training changes or production modifications.

The previous responder chose each sufficiently sampled hand class's highest
sample-average action return. Its fold/shove values can instead be calculated
exactly against the frozen opponent. This diagnosis replaces only those two
training means, retaining every original call/raise observation, the minimum
16-example threshold, baseline fallback, and first-maximizing-action tie rule.

Source policies, checkpoints and old batches were matched to their prior audit
hashes. The original responder and held-out mean were reproduced, with numerical
error below 2.78e-16 bb. Both versions use the same 8,192 training observations
and previously inspected 16,384 test observations.

| Descriptive measure | Original fitting | Exact-aware fitting |
| --- | ---: | ---: |
| Half-sample eligible classes | 89 | 89 |
| Disagreeing action choices between training halves | 45 | 41 |
| Population mass in those disagreeing classes | 36.10% | 34.01% |
| Exact-plus-residual training mean, bb | +0.517 | +1.505 |
| Exact-plus-residual old test mean, bb | -0.187 | +0.484 |
| Old test residual sample variance | 179.61 | 189.92 |

The exact-aware full-sample responder changes 16 classes covering 7.24% of
population mass. Most notably, its selected shove mass falls from 6.69% to
0.55%; fold rises from 53.91% to 55.43%, call from 27.26% to 28.69%, and ordinary
raise from 11.86% to 15.05%. The remaining 0.28% keeps baseline due to insufficient
training support. These are a fitted deviation's choices against one frozen
candidate, not recommended poker ranges.

The positive old test mean is not fresh confirmation of exploitability or a
comparison between solver candidates. Both streams were previously inspected,
and training estimates are selected on their own outcomes. No new confidence
interval is claimed. The variance also increases slightly, so replacing exact
means is not a promise of better precision for every selected responder.

The practical conclusion is limited but useful: avoid sampling already-known
fold/shove means when fitting a future responder. However, the modest reduction
in disagreement leaves the ordinary call/raise fitting problem intact. The
next wider evaluation should retain the planned substantial per-class training
coverage, freeze its exact-aware responder before drawing new test deals, and
publish stability and coverage alongside independent-test uncertainty. A larger
test sample alone is insufficient.

No additional study is launched by this result. The active equal-versus-linear
averaging study continues under its existing fixed plan; its completed screen
and audits determine the next step. This diagnosis ran in 0.88 seconds and has
not received a separate full audit of its own.
