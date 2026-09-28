# Replay the complete saved sample, after throughput qualification

This follows the successful two-batch root-action control and its independent
readback. It is an exploratory diagnostic of the existing complete-policy
evaluation, not new training or a fresh confirmatory test.

## Fixed data and calculation

Use every original batch from `test-000000` through `test-065504` in order, exactly
65,536 physical deals from the already completed evaluation. Authenticate each
archive through its completed checkpoint route. Never replace an averaged bank
with one generation or change its subsequent behavior. Preserve all eight crossed
profiles, four BB root actions, two player values and expected rake.

The qualified native evaluator remains unchanged. For every deal and profile,
the original root probabilities times the four root-action values must reproduce
the archived mixed value for both players and expected rake within 1e-10.
Retain the original native conservation checks. The two control batches already
have independently reviewed action values; any reuse must bind those exact files.
Replaying a fixed input for timing never increases the scientific sample size.

Report all 169 classes, evaluation counts, action means and paired action
differences for each crossed profile. Clearly separate evaluation counts from
training support: numeric per-observation own-reach support was not retained in
the original archive. Keep unfavorable results and sparse classes. Disputed hands
may illustrate the full report but must not define its scope.

The same sample cannot both select an action and prove that action is superior.
Any best-looking action or interval from this replay is exploratory. The old eight
registered payoff comparisons remain inconclusive and unchanged. Promising
questions require separately specified fresh validation.

## Throughput gate

`board_root_action_workers_v1.py` times 1, 4, 8 and 12 workers on the same 12-job
sequence: the two qualified batches alternating six times. Each job must reproduce
the qualified compact values and forced native output exactly. Select the lowest
worker count within 5% of the fastest measured time. This is an operational timing
choice, not an outcome-based scientific selection. The benchmark retains receipts,
native outputs and compact values while retiring only its verified, newly owned
temporary input copies; old archives remain untouched.

The full replay cannot start until every timing case passes and the results are
reviewed. Scale workers downward or defer if other substantial workloads are
present. No GPU computation is needed for this replay.

## Full replay launch requirements

Before launch, register the exact source checkpoint, native binary, adapter,
selected worker count, immutable input hashes and output location. Verify research
ownership/activity locks and the production idle state. Check fresh global
allocated storage across all three research roots, with a proposed maximum of
4 GB additional allocation and a two-hour overall deadline. Qualify bounded
scratch retirement and crash/readback behavior before relying on them for replay.

Keep each completed batch's compact values, native output and authenticated input
references. Publish completion only after all expected batches exist, all mixture
checks pass, and an independent all-class readback agrees with the summary.
Continue to label the results as root-only deviations with fixed continuation
play; do not present them as a full-game accuracy qualification.

At plan creation the two-batch correctness control was complete, the worker
benchmark was running, and no full replay had launched.
