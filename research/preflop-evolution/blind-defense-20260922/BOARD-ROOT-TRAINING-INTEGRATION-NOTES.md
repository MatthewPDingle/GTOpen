# Conditional next step: board-based BB root learning

Status: design notes only. The independent precision repeat and the current
stratified study's final evaluation are still pending. No trainer, checkpoint,
model admission rule or production process is changed by these notes.

## Preserve the learning objective

The current weighted root accumulator sums physical-deal advantages, weighted
by `N * entry_class_mass / sampled_class_count`. Consequently the expected
increment for class c in one generation is:

`N * entry_class_mass[c] * (Q[c, action] - sum(policy[c] * Q[c]))`.

The proposed root estimator supplies a complete 169-by-4 value matrix from the
mean of independent board contributions plus exact preflop terms. Apply the
same expected scaling and the **played** root policy to obtain its advantage
increment. Keep N fixed at the registered physical training budget (512) when
comparing against the current trainer. This reproduces its expected increment;
it does not make the two noisy paths identical or establish convergence.

One public board provides correlated estimates for every class. Do not count
that as 169 independent samples, and do not manufacture 512 physical root
observations to satisfy the old checkpoint checks. Board-blocked combinations
have zero contribution on that draw; retain the original class denominator.

## Required new typed state

- Separate root-estimator identity, board seed/RNG state, number of completed
  board draws, and per-generation board/value/policy bindings.
- Retain exact fold, initial shove and other preflop-only terms. Record their
  matrix and played-policy identities separately from the board component.
- New root checkpoint and model type. Existing `WeightedRootRegrets` and
  `weighted_training_checkpoint_v1` enforce physical sample counts and must
  continue rejecting an incompatible board-based document.
- Checkpoint publication only after all registered boards, physical target
  ingestion, both network fits and the exact BTN update have completed. Resume
  from that boundary; preserve interrupted evidence and both chance streams.
- Explicit new root-policy override and model reader. Continue to apply sampled
  preflop tables before the root override, and preserve the exact BTN response
  override. Do not silently reinterpret old models or saved averages.

The relevant current code is `weighted_root_accumulator_v1.py`,
`weighted_training_parallel_graph_v2.py`, `weighted_training_checkpoint_v1.py`,
and `weighted_training_policy_v1.py`. These are frozen dependencies and are not
to be edited in place for this experiment.

## Isolate the experimental change

Keep the stratified physical deals and sampled neural/postflop targets. Replace
only the BB root target estimator in the experimental arm. Keep the exact BTN
update, action menus, native postflop tree, network features, fits and averaging
schedule identical. Apply any separately qualified storage/recovery speedups
to both comparison arms, or omit them from both.

Start with a bounded mechanical control: known policies and exact terms,
independent scalar reconstruction of every root increment, malformed or
duplicate board rejection, interrupted update recovery, and a round-trip
checkpoint followed by a common continuation. Check that rejected inputs do
not mutate root state or either RNG. Then run a small matched training trial
with fresh chance seeds and the same evaluation policy for both arms.

Board count per generation must be selected prospectively from precision and
runtime evidence, not from attractive resulting ranges. A single or a few boards
may suffice for a useful trial, but the 32-board pilot alone does not establish
the best count. Postflop network learning may remain the dominant error even
after the root estimates improve.

## Performance scope

Current board controls use CPU inference and JSON transport. For production-
scale research, test bounded GPU batches for the saved current policy, reuse
public topology and precomputed rank/card-removal indices, and avoid emitting
an 80 MiB tree per board. Each optimization needs equivalence checks against
the existing float64 control. Prioritize one clearly measured bottleneck at a
time; do not interpret unused RAM as a reason to allocate unnecessary arenas.

Success requires improved range stability and useful held-out payoff evidence
per elapsed training time. A lower estimator variance or a faster component
alone is insufficient for deployment.
