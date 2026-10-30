# Full-context policy integration: first CPU checks passed

The separate stack_context_full_policy_v1.py model wrapper carries both existing
preflop corrections into the shared 362/387-input policy path. Weighted retained
tables apply first, then exact BTN first-response regrets, then the sampled-board
BB root strategy. Context, source, matrix, accumulator generation and complete
cycle identities are checked. Played-mixture reach uses the final overridden
policy, not the underlying network alone.

Four CPU tests passed in 7.642 seconds against retained real model fixtures from
both earlier seeds. Generations 0/1 tested the initial played-mixture average;
generation 77 tested the mature policy. Neutral input extensions preserved
all-street policies, both root overrides and own-history weighted averages to
absolute tolerance 1e-10. Content-hashed model roundtrips and missing/stale state
and incomplete-bank rejection also passed. No model was fitted.

These fixtures zero-extend the old inputs only to test inference behavior. They
are not resumed checkpoints, a conversion of target units or trained shared-stack
models. This control covers one actual fitting context and both input formats.
CUDA parity, multiple-context isolation, held-out local-state exclusion in real
queries, fitting/data ingestion and transactional full-cycle restart remain
unqualified. Do not use this wrapper in production or a scientific comparison
until those integration requirements are met.

The command-observation record is stack-context-full-policy-v1-cpu-tests.json.
It records the executed command, successful unittest output, duration and current
source hashes. It is not a separately preregistered scientific result or an
independent implementation of the reused exact/root arithmetic.
