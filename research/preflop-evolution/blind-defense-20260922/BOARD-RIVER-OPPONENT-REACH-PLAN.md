# Conditional river reference: proposed next diagnostic

This plan was written while the fixed 4,096-deal river-bounds pilot was running,
before its payoff results were read. It is not a claim that bounds improve play
or an authorization to promote either research policy to production.

## Why this addresses the larger modeling problem

Longer fits overfit the saved training data. Explicit public geometry, pot
rescaling and five river-strength inputs did not pass their advancement gates.
Uniform-opponent river values were substantially worse overall, despite exact
card enumeration. The completed error audit could not identify a noise floor:
almost every river training input occurred only once.

The next reference should condition on the *frozen opponent's actual action
likelihoods*. At a river Fold/terminal-Call decision, enumerate the 990 legal
opponent combinations, weight each by its original entry weight and its own
probability of taking every action in the observed history, and calculate
Call minus Fold exactly for that fixed policy and visible state. This can
separate a noisy single-opponent outcome from a policy-conditioned expectation.
It cannot by itself establish equilibrium, solve earlier streets, or supply
correct ranges for other stacks or positions.

## Initial bounded implementation and controls

- Create a separate research-only native exporter; preserve all existing native
  query and payoff executables and their sources. Reconstruct public states
  using `research_sampled/state.rs` and `Observation::legal_actions`.
- Input is one canonical visible river observation and the immutable context.
  Enumerate all legal opponent pairs. Export only genuine decision ancestors
  along that public path plus the actor's current decision, with the existing
  own-history links. A queried player must never see the other private cards
  or unrevealed later board cards in its feature vector.
- Use `poker_reference_v1::key` and `policy_bank_v1::own_history`. Deduplicate
  canonical observations while preserving ancestor closure. Cross-check the
  export against the existing complete query exporter on sampled legal pairs;
  compare ancestor identities by key rather than differing row numbers.
- Reuse the qualified full 78-model policy banks and per-model own-reach
  averaging. The conditional opponent likelihood is the product of the
  resulting behavioral probabilities along its actual prior actions.
- Match `PhysicalDeals` entry weights exactly: class mass divided by physical
  combo count, its original per-seat normalization and its existing 1e-5
  support convention. Apply visible-card blockers before normalization.
  Do not introduce a new threshold or silently drop very small reaches.
- Hero-action likelihood cancels when conditioning on the hero's fixed cards
  and the public history, because that policy does not see the hidden opponent
  cards. Verify this with constructed action-independent and mixed policies.
  Public board likelihood is equal over legal pairs under the fixed full-deck
  chance law. Folded players' card information is still absent from this game.
- With zero opponent posterior mass, label the state unreachable for that
  policy; do not invent a uniform posterior or an oracle action.
- Record the hero's own history likelihood too. If it is zero, distinguish a
  counterfactual opponent-reach calculation from an on-path conditional range;
  cancellation cannot justify conditioning on a zero-probability hero history.
  Preserve these selected cases with an explicit off-path label.
- Check uniform policies against direct entry-weighted enumeration, a single
  supported opponent against known win/tie/loss values, royal-board ties,
  card blockers, suit relabeling, and posterior normalization. At every state
  verify native fold/call endpoints and configured rake.

The exact conditional contrast is

`equity * (pot + incremental_call - rake) - incremental_call`.

This includes ties as half-equity. A positive contrast favors Call over Fold;
it does not prove that either beats an available Raise. Report comparisons of
these two actions only, or the payoff of a precisely specified mass transfer
between them. Do not describe this as a full best response when raises exist.

## Fixed diagnostic selection before inference

Select from the old 32-hand archive already used for transport control, not
from the new pilot's outcomes. Use actor and current-pot strata: under 10,
10-50, 50-100, 100-200, and 200+ bb. Select at most eight unique eligible
observations per actor/stratum by a fixed hash of the canonical observation
key and seed 9289902, giving at most 80 cases. Preserve empty or short strata.
Record exact source hashes, selected keys and the selection algorithm before
evaluating the learned policies or conditional values.

Evaluate both completed original banks separately. Report posterior mass,
effective opponent-combo count, conditional equity and call value, the
original and bounded Fold/Call probabilities, and any probability mass on
other legal actions. Query-balanced diagnostics are not dealt-hand or game
reach-weighted frequencies. This reused-control diagnostic has no population
confidence claim and cannot replace a fresh complete-policy evaluation.

## Resources and decision

Process one visible state at a time, retaining both banks in GPU memory and
sharing preparation. Parallelize independent native enumeration/readback on
CPU where useful; do not compete with the running pilot for GPU ownership.
Case selection and source preparation may run on CPU while the pilot finishes;
start learned-policy inference only after its completed analysis. Use the existing 4 GB CUDA allocator
cap, 2 GB external headroom, heavy-work yielding, shared locks and global
800 GB allocated-storage ceiling. Reserve at most 0.5 GB of new outputs and
one hour for the first diagnostic. Check a single case's cost before admitting
the full set; changing execution batching must not change the selected cases.

If the reference exposes meaningful wrong-way calling decisions, design a
separate targeted training/variance-reduction comparison. If it shows little
local policy benefit or proves too costly, record that and return to the
larger data/generalization problem. Do not turn a small terminal-street
improvement into a claim of better preflop opening or defending ranges.

## Existing implementation references

- `crates/solver/examples/research_sampled/observation_v1.rs`
- `crates/solver/examples/research_sampled/policy_bank_v1.rs`
- `crates/solver/examples/hu_sampled_bank_bridge.rs`
- `crates/solver/examples/hu_river_value_reference_v1.rs`
- `tools/research/sampled_physical_deals_v1.py`
- `tools/research/board_river_bounds_bank_v1.py`
- `BOARD-LATER-FIT-NEXT-STEPS.md`
- `BOARD-LATER-ERROR-AUDIT-FINDINGS.md`
- `BOARD-RIVER-VALUE-FINDINGS.md`

