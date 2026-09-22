# Bounded physical-query cache

The per-batch query cache passed its implementation control. It identifies all
observable inputs needed for a bounded set of sampled deals, allowing a later
bridge to evaluate those inputs as neural batches. It does not persist regrets
or construct the full board-by-history strategy forest. Batched tensor inference
and training orchestration still need to be connected to this cache.

## What is retained

For each sampled physical deal, enumerate every legal public decision history
in the registered BB/BTN subtree. Keep a mapping from raw visible-history keys
to canonical visible observations and legal-action counts. Private opponent
cards and future board cards never enter the observation features. Do not prune
decisions just because a current policy gives an earlier action zero probability.

The cache is bounded by an explicit raw-query limit. Canonical observations
cannot outnumber raw queries. Exceeding the limit returns an error and drops the
partial cache. Missing queries return no result and must fail the traversal;
they must not silently fall back to uniform play. Empty batches, zero budgets
and invalid physical deals are rejected.

This is geometry only. Callers must bind its lifetime to the exact game context
and batch; recompute policy outputs whenever model parameters change. Outputs
from different retained models cannot be reused interchangeably. Global suit
canonicalization retains the prior context restriction: class-symmetric ranges,
not arbitrary suit-specific locks.

## Executed control

The same 16 frozen physical deals produced 7,280 raw queries and 7,277 canonical
observations. A dense float32 feature matrix would occupy 7,830,052 bytes;
float64 four-action policies occupy 232,864 bytes. These payload figures exclude
map/vector overhead, weights and runtime allocations. The fixtures are not a
representative training sample, and their three merged queries do not establish
a substantial compression benefit.

Two weight sets were checked: the original synthetic networks and the weights
from the GPU fixed-data fit. For each, test normal scores, all-negative scores,
all-zero ties and a deliberately highest illegal action. Cached and on-demand
policies match exactly for every query. Across 256 traversals, all 7,712 records,
root values and random-generator states also match exactly. All four streets
are exercised. Eighty preflop hidden-card changes leave lookup inputs unchanged.

Repeating a batch adds no new queries; reversing deal order preserves every
query's observation despite potentially different numeric row IDs. Budget,
empty-input and invalid-card checks pass, as does missing-query handling.
The CPU control took 0.50 seconds. This is an implementation identity, not a
performance benchmark or a physical-poker strategy result.

Evidence prefix: `sampled-batch-queries-v1`; 15 input hashes are frozen and
verified. The live server and both registered accuracy experiments were unchanged.

## Next step

Connect the query rows to batched tensor inference and transport the resulting
legal probabilities back into the sampled traversal. Preserve the mapping and
fail-closed behavior, then qualify the combined data path. During learning,
hold both player models fixed across both updater passes and retain each sampled
visit with its correct multiplicity. Clear or bound batch data between iterations.
The ongoing finite-game accuracy gates still precede a physical self-play pilot;
none of these cache checks establishes that poker ranges have improved.
