# Does board-integrated root training improve the ranges?

Prospective design, prepared while the preceding fixed evaluation is still
running. This is not a launch authorization from an admission checker: the
complete GPU training control, its independent readback and storage admission
are still required. No candidate training or new payoff evaluation has started.

## Question and scope

The fixed-policy precision checks found substantially less noisy root action
values when a public board is evaluated across all compatible private hands.
That does not prove better learning. Test whether replacing only the BB root
regret estimate improves learned play and reproducibility at a fixed learning
budget. Keep the same restricted 200bb BB-versus-BTN context and incoming
ranges. This does not answer full-ring, multiway or other stack-depth questions.

## Matched treatment

Use the two completed, independently audited stratified arms
`9266201-stratified` and `9266301-stratified` as historical controls. Keep their
configurations, except for the explicit new policy/checkpoint type and board
root configuration. Do not choose a comparator after viewing the current
evaluation's gains.

For each candidate arm:

- Train exactly 78 generations, starting from the same initial uniform policy.
- Preserve the corresponding control's physical sampler, action, fit and
  reservoir seed identities. The physical source deals therefore match, but
  policies and sampled action paths can diverge as learning progresses.
- Keep 512 stratified private-deal samples per generation, eight 64-deal
  subbatches, reservoir capacity 262144 per player, 512 Adam steps per fit,
  chunk size 4096, learning rate .003 and the existing 302/64/64/4 networks.
- Keep weighted physical targets, preflop tables, exact BTN initial-shove
  responses, conditional postflop targets and inference precision unchanged.
  The neural root training targets remain unchanged; the explicit root table
  receives the new board-integrated regret update.
- Sample four independent uniform public boards per generation using the
  qualified generation-keyed chance algorithm. Board seeds are **9281001** and
  **9281002**, in control-arm order. Four is a fixed operational budget, not a
  count selected from observed learning outcomes.
- Combine exact preflop terms with the public-board average under the original
  compatible-pair and incoming-class weights. Scale regrets by 512 times the
  original class mass. Do not renormalize the population for each board, invent
  private-hand visits, or add the old sampled root regrets as well.

This matches learning updates, optimizer work and physical sampling. It is
**not** an equal wall-clock or equal total computation comparison: board
calculations add work. Report elapsed time, board wait, GPU fitting time,
physical preparation time and peak storage alongside the quality results.

## Fixed outcomes

Average every played generation 0–77 with weights 1–78 and each player's own
action reach. Exclude the final unplayed generation 78. Do not select favorable
checkpoints, attractive hands or a preferred seed.

Use a fresh common sample of **65536 deals, seed 9281101**, and the unchanged
crossed-policy payoff evaluator. For each matched seed, compare candidate BB
against control BB against both BTN policies, and candidate BTN against control
BTN against both BB policies: eight contrasts total. Use the existing bounded
empirical-Bernstein simultaneous 95% intervals, Bonferroni across all eight,
at one fixed final look. Paired ordinary standard errors are secondary.

Primary descriptive stability remains original-entry-weighted cross-seed BB
root total variation. Report all 169 classes and all eight payoff contrasts,
including unfavorable and inconclusive results. Lower variation alone does not
establish stronger play. No increased sample count or extra learning generations
may be chosen in response to a nearly significant result; any follow-up needs
its own prospective design and fresh evaluation.

## Admission, storage and recovery

Before launch, require successful complete GPU training/recovery control and
independent trained-state readback, unchanged source bindings and idle production.
The separate native-board readback control has passed; the full trained-state
audit has not run yet. Preserve the current evaluation.

Inventory all three research roots before committing new storage, account for
all already-running and queued output budgets, and retain the established
800 GB research allocation ceiling plus a 2 GB reserve. A volume's free space
alone is insufficient admission. Target a new compressed S: research directory;
do not consume the limited remaining T: headroom or modify/delete historical
evidence to make the experiment fit. The final allocation budget must come from
measured full-budget generation sizes, with evaluation/readback reserves.

Use bounded CPU board work overlapped with physical preparation and GPU fitting.
Start with the qualified two physical workers and four board workers; the
mechanical control checks two-versus-four physical-worker equivalence. Select a
faster worker count only from an equivalent fixed-input timing comparison, never
from different ranges. Respect active user workloads, GPU/RAM/volume headroom
and the existing research locks. Keep processes hidden.

First run two generations at the actual full budget and independently verify
their targets, saved state and deterministic restart. They count toward the
fixed 78-generation arm, not a disposable pilot that can be cherry-picked. If a
mechanical fix changes the algorithm, register a new experiment rather than
mixing old and new generations. Preserve failed attempts, resume only the last
complete checkpoint, and maintain the fixed scientific endpoint across bounded
invocations. No automatic deployment follows training or this comparison.
