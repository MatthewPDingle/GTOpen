# Preparing a less noisy follow-up evaluation

The combined hybrid/all-in trial keeps its registered sampled-board primary
evaluation. The following components prepare a separate future conditional
evaluation; they do not replace that primary result, draw fresh test deals,
train another candidate, or alter the running experiment.

## Exact labels for separate streams

`sampled_conditional_cache_builder_v1.py` accepts an explicitly supplied deal
stream and a hash-checked base cache. It retains only required physical private
pairs, reuses existing exact counts, and enumerates missing pairs with one
bounded native CPU worker. It preserves player roles, the original unlabelled
deals, integer counts, native artifacts and cache provenance. Resource/deadline
checks come from the caller. Invalid deals and excess new-key counts are rejected
before creating an output directory. Existing evidence is never overwritten.

The control used 256 already inspected deals plus eight player-role reversals.
It reused 175 keys and recomputed 88, matching the prior exact counts. Reversing
players reversed wins/losses; all 192 suit transformations preserved equity.
Reuse-only assembly was exact and eight invalid inputs were rejected. Native
enumeration took 10.2 seconds; the control took 12.5 seconds. These are fixture
timings, not a forecast for a large new sample.

A future caller must build responder-training labels first, freeze the
responder, and only then supply its held-out stream. The builder has no sampler
or access to a policy bank. It does not enforce stream separation by itself.

## Both players' deviations

The existing conditional root evaluator supplies BB's four first-action values.
`sampled_conditional_btn_response_v1.py` now reconstructs BTN's response to a
BB shove using exact equity, independently checks it against the native output,
and exposes separate response-learning and test-difference functions. Decisions
are selected by jam-reach-weighted training values. Fewer than 16 training deals
or zero total jam reach keeps the original strategy. Ties fold. Reported gains
are weighted per original BB entry, not presented as gains per shove.

Its control checked all 256 existing repeated-board fixtures: maximum native
payoff discrepancy was 5.69e-14 bb, and all preflop all-in rows were unchanged
across runouts. Five synthetic cases exercised weighted choices, ties, zero
reach, insufficient support and a profitable call. Five invalid training inputs
were rejected. No fixture-derived response is a research candidate or independent
accuracy result.

## Still required before a fresh conditional study

Freeze the candidate, new seeds, sample counts, error budgets and both-player
comparisons. Add a guarded controller, enforce response/test separation, verify
candidate CPU/CUDA agreement, and provide a complete independent artifact audit.
If larger samples require compressed storage, integrate the separately tested
archive reader into the full audit rather than deleting raw evidence ad hoc.
The current helpers alone do not establish accurate ranges or convergence.

Evidence prefixes: `sampled-conditional-cache-builder-control-v1` and
`sampled-conditional-btn-response-control-v1`. Local fixtures and cache outputs
remain under `S:/GTOpen-research`.
