# Fresh-board check for the expanded-data alternatives

Prepared before N03 training completes and before N06b/N08 selection results exist.
This is a reserved evaluation, not a running GPU job.

Both fixed training screens must finish before registration. Register every eligible
N06b/N08 candidate together, including its frozen model and training-screen hashes.
If neither qualifies, generate no references. Do not refit, change thresholds or
choose another model using this evaluation's outcomes.

Use the same eight historical held-out case identities as N03, from the two source
families excluded from fitting. Select 50 new canonical flops: ten from each of
five texture strata, using a fixed hash order. Exclude all previous pilot, audit,
original overnight, N01 development/evaluation and N03 training/evaluation flops,
including reserved but ungenerated flops. Weight by suit multiplicity and inverse
inclusion probability. This does not estimate the full 1,755-flop universe without
bias: the evaluation domain excludes previously used boards.

The 400 references use the unchanged zero-rake, half-pot bet/full-pot raise menu,
one raise per street, no added all-in, threshold 0.85, and at most 2,000 iterations.
Both CPU and GPU full-query gaps must be at most 0.1% of pot. Check numerical
finiteness, manifest agreement, hand-to-aggregate reconciliation and pot accounting.
All reference timestamps must follow model registration.

For each registered model separately, require at least 15% lower equal-case mean
hand-value error than Balanced in each held-out family, with no case more than
10% worse than the previous frozen predictor. Report paired 90% board-bootstrap
intervals and rare-hand best-response diagnostics. Shared new references allow a
paired comparison, but do not turn a training-selected model into a production
release. New runtime, changed-policy and implementation checks remain necessary.

Case identities were evaluated historically: this is prospective board evidence,
not an untouched new-context test. Intervals condition on fitted models and cached
equities. They exclude training uncertainty. Value accuracy does not establish
action-frequency accuracy or full-game exploitability.

Run only after N03 GPU work has stopped. Observe the existing live-app guard,
single GPU workload rule and fixed 20:49:02 UTC deadline. Do not alter port 56708.
