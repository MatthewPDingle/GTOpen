# Later-action target integration: diagnostic before training

The matched root-only integration trials did not demonstrate stable ordinary call/raise ranges. Paired continuation diagnostics showed material later-policy differences as well as large remaining card-sampling uncertainty. The next accuracy hypothesis is that integrating future actions in the later training targets may reduce one source of noise in those learned continuations.

## Preserve the sampling experiment

Freeze the existing policy before each batch. Keep the original physical deals, action seed, external-sampling traversal, visit order, record identifiers, reservoir insertion order, and reservoir replacement draws. Run the original walker unchanged and retain its raw output. Separately evaluate all legal future action paths at each fixed physical deal, using the same visible-information policy at each decision. Export conditional action values and centered advantages keyed by physical deal and original record position.

At an updating player's visited node, the original walker enumerates that player's actions and samples opponents' future actions. Conditional on the sampled cards and the random choices preceding that visit, replacing its future-action estimate with the full policy expectation preserves the conditional expectation under the usual independent-random-draw sampling model. The event of visiting the node depends on past draws, not the future draws being integrated. This argument does not integrate hidden cards or future boards, change which nodes are visited, justify replacing a node value with a best response, or guarantee improved finite-sample learning. The actual deterministic pseudorandom generator is retained for replay.

Both players' policy probabilities are used in the full expectation: the updating player's descendants were already enumerated by the sampled walker. Hidden cards and the sampled runout affect terminal training labels only. They must not be added to observable policy features.

## Preserve stronger existing estimators

The trace's pair-conditional preflop all-in values are not a replacement for the existing population-integrated initial BB jam/BTN response estimators. Keep those exact initial-policy tables and the separately typed BB root accumulator. The first candidate should replace only positive-tag **postflop** reservoir records, leaving preflop records, all exact initial overrides, opponent-policy records, and all sampling decisions unchanged. Any broader target replacement requires a separately reviewed estimator.

## Diagnostic gates

1. On saved replication batches at updates 1, 26, and 78, reproduce every original sampled root and record exactly and compare full integrated root values against the existing full-policy evaluator.
2. Independently verify every node/action of one physical-deal uniform-policy fixture by forcing that action through the established full-policy evaluator. Its root-value change must equal the original reach times the trace's conditional action-value difference. Check both players, all legal actions, and all streets; require positive reach so a zero-mass branch cannot make the check vacuous. The established evaluator also checks forward cashflow and conservation.
3. Reconstruct all exported centered targets from action values and visible policy probabilities. No fitting, range selection, or production changes in this diagnostic.
4. Before training: add typed postflop-only target ingestion with exact original insertion/RNG replay, independent readback, and explicit estimator/checkpoint metadata. Then register a matched learning comparison with unchanged training budgets and separate unseen evaluation data. Training-fit losses alone cannot qualify poker accuracy.

A successful implementation control only permits further testing. Card-sampling noise, representation error, shallow action abstractions, and slow adaptation can still prevent better ranges.
