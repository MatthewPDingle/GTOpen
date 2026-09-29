# Bring the relative hand inputs into complete continuation training

Status: implementation plan, not an admitted scientific run or a promoted model.
The equity-pricing comparison and its existing readback must finish unchanged.

## Decision and evidence

Return the next learning comparison to actual betting-conditioned ranges and
complete betting continuations. Do not keep treating improvements in the
uniform-opponent terminal Fold/Call diagnostic as the end goal. The required
outcome is better preflop decisions under a specified complete continuation
game, eventually across positions, stack depths and opponent models.

The earlier relative-input study independently verified 46.11% and 23.87%
reductions in its restricted fresh-test loss. Both missed the absolute limit,
validation did not favor the candidate, and large tail errors remained. This
supports testing the representation in the real trainer; it does not justify
installing those diagnostic weights, relaxing gates or claiming better poker.
Balanced-board fitting failed its primary test. The current equity-pricing
comparison is separate and must receive its full adverse-results analysis.

Already completed, so do not repeat:

- `river_range_reference_v2.py` qualifies weighted terminal river arithmetic.
- `river_range_policy_binding_v1.py` and its independent readback qualify actual
  current-policy histories, restored suit mappings and common opponent weights.
- The posterior64 native/export/weighted-ingestion path is already qualified
  and was used in a completed matched full-policy continuation comparison.
- The 362- and 387-input context registries and CPU model-object interfaces
  already passed retained-native-observation checks at seven stack depths.

Read the corresponding FINDINGS documents, not the obsolete next-step paragraphs
in earlier plans. The real-policy binding finished on 29 September before the
latest diagnostic studies. It is not outstanding work.

## Concrete integration gaps in the current code

`stack_context_relative_policy_v1.py` is only a model-object/inference adapter.
It has context-local weighted preflop tables, but it is not the complete training
model: `board_training_policy_v1.py` also applies an exact BTN response table and
a sampled-board root accumulator. The shared-context model must retain both
overrides, their precedence, context identity and generation identity.

`river_training_pipeline_v1.py`, `board_training_checkpoint_v1.py` and
`weighted_training_graph_fit_v2.py` still bind one game, 302-input networks and
per-reservoir target scaling. Changing only the input width would lose important
state and make cross-stack targets inconsistent. Keep all executed sources
immutable; add separately versioned integration modules.

## Implementation sequence

1. Add a complete shared-context model contract for both the 362-input control
   and 387-input candidate. Each fitted game owns its weighted tables, board-root
   accumulator and exact BTN accumulator. Apply the existing override precedence
   after shared-network inference. Reject missing, swapped or stale local state.
   A held-out context may not acquire learned overrides or fitting state.

2. Add the training-data bridge and objective. Retain the exact context hash,
   visible keys, actor, legal actions, native public prices and private-card
   features. Do not merge identical numeric keys belonging to different games.
   Preserve source-deal importance weights and the visit reservoir sampling
   distribution. Normalize advantage targets by starting stack; normalize context
   contributions explicitly so row counts or deeper pots cannot silently decide
   the curriculum. The choice of context weights must be fixed before fitting.
   Do not invent own-history paths from a reservoir that did not retain them:
   fitting-row encoding and played-policy reach evaluation need distinct inputs.

3. Add atomic joint-cycle checkpointing. Every fitting context retains its own
   physical sampler, action RNG, two reservoirs and both root accumulators.
   Freeze the same shared played model while collecting every context in a cycle;
   then fit both player networks and publish only the complete joint result.
   Checkpoints bind registry, configuration, objective units, model schema and
   source identities. The final unplayed model remains outside the played bank.
   Preserve optimizer/RNG state if the chosen fit algorithm carries it forward.

4. Adapt native-query, board-worker, posterior64-worker and evaluation inference
   to this full model contract. Keep actual betting-conditioned targets and all
   legal actions on all streets. Keep exact initial/all-in terms. The weighted
   terminal reference is an oracle where applicable; it does not replace the
   full future-action tree or become a uniform-opponent default.

5. Qualify one real complete training cycle before a scientific comparison.
   Verify CPU/CUDA raw scores, action conversion, local overrides and own-reach
   averaging. Exercise interruption before publication and exact checkpoint
   replay. Compare retained source order/weights, sampler state, reservoir RNG,
   target geometry and all played model identities. Demonstrate that changing
   the river continuation can affect upstream preflop values. Test 2/3/4-action
   nodes, both actors and every street; terminal Fold/Call alone is insufficient.

## Scientific comparison to register after integration

Use the already defined BB/BTN family at 20/40/100/200/400bb for fitting and
60/150bb for transfer evaluation, with fresh board/deal groups and matched seeds.
These depths are held out of fitting, not globally unseen research geometries.
This remains a heads-up continuation family, not all multiway preflop spots.
Register exact source ranges, rake, action menus, initialization, context weights,
training budget and storage/runtime caps before admission.

Compare full 362-input and 387-input training with common physical deal streams,
the same continuation target method, model update schedule and optimizer budget.
State the extra parameter count. No reuse of the terminal diagnostic weights.
No checkpoint selection against the final evaluation or tuning on old failures.

Keep separate evidence for held-out continuation prediction, actual complete
policy value on common physical deals, and upstream preflop decisions. Evaluate
complete played mixtures with own-history reach weights and keep rare costly
mistakes visible. Fixed-opponent value gains are not an equilibrium certificate;
a GTO Wizard range comparison requires genuinely matched game assumptions.
Predeclare acceptance and uncertainty rules after the implementation/runtime
qualification, before scientific labels are created. No implied pass is claimed
by this plan.

## Resource and scope limits

Prefer the existing streaming native workers, CPU preparation overlap and CUDA
gradient reuse. Use measured complete-cycle cost to size the comparison; do not
infer its duration from the short terminal diagnostic. Preserve the approved
light-desktop sharing policy and yield to active solves or heavier workloads.
Stay within the existing 800GB allocated research cap and 40GB free-disk floor;
inventory before admitting a new store. Retain evidence and avoid copying large
old stores merely to change a model format.

The current independent readback owns the research lock. This document launches
nothing, changes no registered experiment and does not modify production 56708.
No deployment, GitHub push or broad-goal completion follows from a control pass.
