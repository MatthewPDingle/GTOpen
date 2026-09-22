# GPU betting and showdown primitives qualified

Two isolated GPU components now pass their registered reference checks. They
are prerequisites to a sampled trainer, not new learned ranges or a speed result.

## On-demand betting transitions

The GPU port matched the previously qualified CPU reference for all **1,131
betting-history templates** across the actual three BB continuation branches:
465 at pot/stack 4.5/198, 409 at 12.5/194 and 257 at 36.5/182. Checks covered
node kind, player, street, ordered legal actions, chip amounts and terminal
winner/loser/tie payouts. All integer fields matched and maximum numeric error
was zero. Repeated launches were bit-identical. Maximum path depth was 14.

The earlier CPU reference was checked against all 231,143,136 legal native
public nodes over the full 112-flop panel. Card identities do not affect legal
betting transitions, so this GPU port check factors them out while retaining
every distinct betting history. This is a test reduction, not a policy merger:
the eventual information key must still include private hand and visible cards.

The CUDA header deliberately implements the registered experiment's exact
menu: 50% bets and donks, pot-sized raises, one raise per street, 0.85 all-in
threshold and no separately added jam. It is not a general-size UI backend.
Pot, stack and rake come from each registered branch. Different menus require
their own implementation and qualification; they are not silently rounded to
this menu. The source is `research_sampled/postflop_state_v1.cuh`.

## Physical showdown evaluation

The integer GPU evaluator matched the native seven-card evaluator on **203,297
valid hands**, twice. Coverage includes 200,000 deterministically generated
hands, named examples of all nine hand categories, and all 24 suit permutations
with reversed card order for 137 examples. An independent five-card evaluator
that checks all 21 subsets also matched 4,096 of these cases.

This includes wheel straights, a full house from two trips, three-pair kicker
selection, flushes and straight flushes. Exact encoded strengths preserve both
ordering and ties. It evaluates each sampled physical showdown directly; it
does not use an approximate multiway strength distribution or a large precomputed
river equity table. The source is `research_sampled/evaluator_v1.cuh`.

The deterministic test-card generator is only a coverage fixture, not the game
sampler. These checks establish hand ranking, not that the trainer deals cards
with the right conditional probabilities or estimates equity accurately.

## Next integration work

Combine legal transitions and physical showdowns with the qualified chance
law and frozen-batch update contract. The implementation must preserve these
requirements:

- Public cards are revealed at the correct street even if a full runout is
  sampled in advance. An early policy must not see later cards.
- Each information key retains the full public action history, exact private
  hand, visible board and continuation identity. Keep tables scoped to a fixed
  game configuration. A public board's suit-relabelling ID is not additional
  observable information: equivalent physical observations must share a key.
- Hash collisions must compare full keys; they cannot merge unrelated decisions.
  Unseen keys begin with the specified default policy. New or repeated keys must
  not cause policy changes within a batch or drop accumulated updates.
- Overflow must stop the run with evidence instead of deleting learned state.
  Sampled traversal must still enumerate every updating-player action, including
  actions with zero current probability.

Then measure actual state growth and throughput before attempting a convergence
comparison. None of these component passes demonstrates that the full policy
table fits, that convergence is fast enough, or that BB ranges have improved.

## Evidence and production

Registrations, inputs, results, guard records and logs are retained under
`sampled-geometry-gpu-v1-*` and `sampled-showdown-gpu-v1-*`. The existing
fail-closed production-idle guard ran both probes. Thirteen frozen inputs for
the transition probe and eleven for the ranking probe were checked afterward.
Both jobs exited successfully. Production code, sessions and player ranges
were unchanged; the isolated examples are not linked into the server.
