# Check the estimator on the complete existing evaluation sample

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

The audit will replay the original deal stream, verify cache assembly and
unchanged policies/responder, reconstruct all five difference series and use an
independent statistics implementation to check means and variances. It does not
repeat every exhaustive board enumeration or neural inference.

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

Registration and subsequent result/readback artifacts use the prefix
`sampled-physical-allin-population-diagnostic-v1`. Large reproducibility files
are stored under that prefix in `S:/GTOpen-research`.
