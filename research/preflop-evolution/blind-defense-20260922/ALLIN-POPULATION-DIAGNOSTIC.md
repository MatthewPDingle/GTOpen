# Check the estimator on the complete existing evaluation sample

## Completed diagnostic

All 16,384 saved test deals completed. The five saved policies and original
trained responder were unchanged. The new native evaluator preserved root
mixtures (maximum discrepancy 2.85e-14 bb) and independent forward cashflows
(maximum discrepancy 4.84e-13 bb). The original sampled means and variances were
reconstructed before comparing the conditional estimator.

| Comparison versus baseline | Original mean (bb) | Conditional mean (bb) | Conditional / original variance |
|---|---:|---:|---:|
| Frozen trained response | +0.7980 | +1.2536 | 0.1854 |
| Always fold | +0.7340 | +0.5419 | 0.1941 |
| Always call | +0.4718 | +0.2796 | 0.2416 |
| Always raise | -7.8068 | -7.6369 | 0.2806 |
| Always jam | -25.6385 | -24.6102 | 0.1233 |

Unlike the earlier repeated-board fixtures, these variances include differences
between private-card pairs across the complete original sample. The reduction
is about 72% to 88%, and about 81% for the trained-response difference. These are
descriptive sample results, not guaranteed future variance reductions. The
changed means are not evidence that a policy changed: the same policy is being
valued with less board noise. The cleaner diagnostic still points to remaining
weakness in the hybrid policy; it does not support promoting that policy.

The run took 1,088.6 seconds (18.1 minutes): 543.4 seconds through cache assembly,
then about 545.2 seconds for the full saved-policy evaluation and final checks.
There were 13,021 unique suit-canonical private pairs: 8,474 reused reviewed
labels and 4,547 required new exact enumeration. Native exact enumeration took
501.1 seconds. These timings **exclude new neural inference** because the saved
profiles were reused; a future fresh evaluation must account for that cost.

For planning only, substituting the trained-response variance into the original
five-comparison formula gives hypothetical counts of 46,469 / 123,175 / 511,170
deals for radii of 0.50 / 0.25 / 0.10 bb. The original sampled-variance planning
counts were 107,397 / 353,000 / 1,899,223. These calculations assume the observed
variance persists. They are neither achieved confidence intervals nor an adopted
new protocol. Candidate changes, response fitting and label cost still matter.

The complete saved-artifact audit passed in a further 301.2 seconds. It checked
5,591 source/artifact hashes, replayed all 16,384 deals, retained all 169 hand
classes and the original 90 baseline-fallback deals, verified exact cache
assembly and unchanged policies, and independently reconstructed the descriptive
statistics. Its result is recorded separately under the same prefix.

## Scope and method

The small learned-bank control reduced board variance, but held private cards
fixed within each group. It therefore could not tell us how much total
evaluation uncertainty would fall across the complete incoming ranges.

This follow-up retains **all 16,384 deals** from the completed hybrid evaluation,
including every hand class, and changes only the treatment of preflop all-in
terminals. It reuses the saved policies without neural inference or training.
The responder's action for each class remains exactly as selected on the
original separate response-training set. Sparse classes still use their original
baseline fallback. No response is selected from these inspected test results.

The following paired differences are reconstructed with both estimators:

- The frozen trained response versus the saved baseline.
- Always fold, call, raise and jam versus that same baseline.

Means and sample variances are descriptive. This is **post-hoc reuse of an
already inspected test sample**, not another independent confirmation or a new
confidence statement. The original published result is preserved. Any fresh
evaluation using this estimator must declare its candidate, responder training,
new chance stream, sample count and statistical rules separately.

## Exact values and controls

The existing reviewed training cache covers part of the required private-card
pairs. There are 4,547 missing role-preserving, suit-canonical pairs; one CPU
worker enumerates all 1,712,304 remaining boards for each missing pair. The
original cache is not modified. New counts and reused counts are assembled into
a separate cache with exact private-card binding and no approximation fallback.

For every batch the new evaluator retains the original profile rows, original
private cards and original runout. Reverse expectation and independent forward
cashflow accounting must agree. Root fold/call paths must be unchanged, expected
rake and terminal mass must match, and the root mixture must reconstruct its
baseline. All source batches and outputs are hashed.

The audit replays the original deal stream, verifies cache assembly and
unchanged policies/responder, reconstructs all five difference series and uses
an independent statistics implementation to check means and variances. It does
not repeat every exhaustive board enumeration or neural inference.

## Resources and next decision

This diagnostic has a 90-minute ceiling, one CPU equity worker, no GPU allocation,
20 GB free RAM and 40 GB free SSD reserves, and a 16 GB new evaluation-artifact
limit. It stops if production becomes active or any integrity check fails. The
main all-in training study and its registered evaluation remain unchanged.

Record cache-construction and evaluation costs as well as variance ratios. A
large variance reduction can still be a poor trade if labels are too expensive
to obtain. Conversely, a reusable exact cache may make later evaluations cheaper.
The result informs whether to prepare a fresh evaluation with this estimator;
it does not qualify either existing range model for deployment.

A subsequent [direct conditional evaluation component](CONDITIONAL-ROOT-PIPELINE.md)
passed its complete-bank CPU integration check against the earlier reviewed
fixtures. It prepares fresh evaluation without requiring an extra sampled-payoff
pass; admission of a new strategic evaluation remains separate.

There is also a sample-count limitation independent of observed variance. Under
the original five-comparison interval rule, bounds of -400.5 to +400.5 bb and
16,384 deals leave a 0.6835 bb radius term even at zero sample variance. At least
44,794 deals would be needed for a 0.25 bb radius under that same rule even in
the hypothetical zero-variance case; positive variance requires more. These are
algebraic planning limits from the existing formula, not achieved confidence
or a replacement stopping rule. Lower-noise payoffs alone cannot make the current
16,384-deal result arbitrarily precise.

Registration and subsequent result/readback artifacts use the prefix
`sampled-physical-allin-population-diagnostic-v1`. Large reproducibility files
are stored under that prefix in `S:/GTOpen-research`.
