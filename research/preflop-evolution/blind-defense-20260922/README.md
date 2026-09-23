# Second-context study: BB defense

## Current findings — 23 September 2026

This is a separate BB-versus-BTN research context. The range preview still shows
the earlier UTG-versus-LJ study. Neither research candidate replaces the live
preflop model, and no blind-defense candidate is qualified for deployment yet.

- **A fresh output-averaging experiment is now training.** The fixed equal and
  later-weighted schedules, fresh four-update training replay, and all four
  exact player-pairing controls passed. See the
  [execution controls](LATER-WEIGHTED-AVERAGING-CONTROLS.md) and
  [frozen full-run plan](LATER-WEIGHTED-AVERAGING-PLAN.md). The first full-run
  update completed and its live worker was verified. This tests averaging on
  one new 78-update bank; it does not select a checkpoint from the old trace.
  `later-average-study-v1-status.json` and the training log hold local progress.
- **The wider call/raise test has a checked variance-reduction component.**
  On all old inspected test deals, replacing sampled fold/shove contributions
  with exact values lowered fitted-response variance by 68.8%, while the
  always-raise comparison became 11.5% noisier. The independent arithmetic
  review passed. This is evaluation preparation, not new strength evidence;
  see [the residual diagnostic](ROOT-RESIDUAL-DIAGNOSTIC.md).

- **The generation audit locates much of the all-in error in early policies.**
  For the newer candidate, the initial policy and first 25 updates contribute
  88.8% of measured BB error and 75.3% of BTN error against fixed final opponents.
  All 78 prefixes passed independent reconstruction. Later policies still err;
  no checkpoint or tail was selected. See the
  [attribution findings](ALLIN-GENERATION-ATTRIBUTION-FINDINGS.md) and the
  [prospective averaging design](LATER-WEIGHTED-AVERAGING-DESIGN.md).
- **Exact checks now expose concrete all-in mistakes in both candidates.**
  Complete private-pair calculations and independent audits found a +0.15188 bb
  BTN fold/call improvement and a separate +0.15399 bb BB fold/shove improvement
  for the new model, per original entry into the fixed spot. These are unilateral
  deviations against frozen opponents, not a full-game bound or simultaneous
  win rate. See [exact findings](EXACT-ALLIN-ENDPOINT-FINDINGS.md). The complete
  generation attribution is now independently verified, as described above.
- **Latest completed comparison: visible features changed the policy, but did
  not establish better accuracy.** The 302-input candidate completed 78 updates
  and both player audits. BB calling rose from 31.42% to 36.60% relative to the
  combined 269-input candidate, while the learned-response intervals remained
  broad and inconclusive. The original training wall-time cap was exceeded by
  a separately declared completion extension. See the
  [full findings and all 169 classes](VISIBLE-HYBRID-COMPLETION-FINDINGS.md).
- **Sharper measurements are next.** The
  [complete all-in response plan](EXACT-BTN-RESPONSE-PLAN.md) replaces noisy
  sampled BTN fold/call tests with an exhaustive private-pair calculation.
  The candidate-independent equity table and its audit are complete under the
  separate v2 registration after a [status-writing repair](EQUITY-CACHE-STATUS-REPAIR.md).
  The [BB exact-component control](EXACT-BB-COMPONENTS-PLAN.md) also passed on
  the old fixture; the full restricted fold/shove deviation check also passed. None
  of these narrow checks substitutes for full-game or cross-stack validation.
- **More training data helped one diagnostic, with substantial uncertainty.**
  The completed 39,936-deal candidate's tested BB root-response gain was
  +0.389 bb, with a conservative interval from -0.990 to +1.768 bb. This is
  encouraging relative to the earlier pilot's point estimate, but it is not
  a paired improvement test, an equilibrium certificate or evidence that all
  hands are correct. See [dense findings](SAMPLED-PHYSICAL-DENSE-FINDINGS.md).
- **The opponent's response still matters.** A subsequent diagnosis found
  weaknesses and sparse-hand uncertainty in BTN's response to BB jams. It used
  already evaluated data and is explicitly post-hoc. See
  [BTN diagnosis](DENSE-BTN-JAM-DIAGNOSIS.md).
- **One current experiment separates preflop fitting error from sampling error.**
  The [hybrid plan](SAMPLED-PHYSICAL-HYBRID-PLAN.md) uses retained preflop values
  directly while keeping neural postflop decisions. All 39,936 training deals
  completed and the [independent training replay passed](SAMPLED-PHYSICAL-HYBRID-TRAINING.md).
  The first evaluation stopped on a CPU/CUDA numerical mismatch before drawing
  test deals. A [checked float64 repair](HYBRID-NUMERICAL-REPAIR-STATUS.md)
  completed with a passing independent evaluation audit. It has
  [not demonstrated better ranges](SAMPLED-PHYSICAL-HYBRID-FINDINGS.md): the
  estimated BB response gain was +0.798 bb (-0.899 to +2.495), with more jamming.
  The candidate is not promoted.
- **A separate estimator removes avoidable all-in board noise.** Exact physical-
  pair all-in values passed payout and transport checks. On a small fixture
  with the last played learned strategy, summed preflop advantage variance fell
  about 73%; this is not a speed or range-accuracy claim. See
  [all-in controls](ALLIN-BRIDGE-CONTROL.md).
- **A separate evaluation control also passed.** The
  [conditional all-in evaluator](ALLIN-EVALUATION-CONTROL.md) preserves independent
  chip accounting and removes preflop all-in board noise on fixed fixtures.
  Non-all-in paths are unchanged. The complete learned-bank diagnostic also
  passed: paired board variance fell about 89% to 99.7% on 16 private-pair
  fixtures. This is separate from the active trial and is not a population
  precision or poker-strength claim.
- **The reduction also holds on the complete inspected test sample.** The
  [full-sample diagnostic](ALLIN-POPULATION-DIAGNOSTIC.md) retained all 16,384
  original deals, all 169 classes and the frozen response choices. Variance fell
  about 72% to 88% across the five paired comparisons, including about 81% for
  the trained response. The readback passed. This supports a more efficient
  future fresh evaluation; it is not a new independent accuracy result, and the
  hybrid candidate remains unqualified.
- **The follow-up all-in candidate completed training and its replay.** All
  39,936 deals and 78 updates finished; both saved sample buffers and random
  states reproduced exactly. It preserves the dense recipe and changes only
  the all-in estimator. [Training evidence](SAMPLED-PHYSICAL-ALLIN-TRAINING.md)
  is complete, and both fresh player tests and audits have now passed after a
  [checked precision repair](ALLIN-NUMERICAL-REPAIR.md). The [completed findings](SAMPLED-PHYSICAL-ALLIN-FINDINGS.md)
  show shoving falling from 7.3% to 1.8%, with calling almost unchanged at 26%.
  Neither player test demonstrated a profitable alternative, but their restricted
  scope and broad intervals do not qualify the ranges. Most remaining averaged
  shoving originates in early training; later hand behavior is still uneven.
  No candidate is promoted. See the [frozen plan](SAMPLED-PHYSICAL-ALLIN-PLAN.md)
  for the original protocol; the new evaluation estimator stays separate.

For the first response shown in the UTG/LJ preview, the
[root-action diagnosis](ROOT-ACTION-DIAGNOSIS.md) explains the missed calls and
the inherited-range limitations. That finding is separate from the BB trials.

## Earlier qualification log

The entries below preserve the sequence of earlier investigations. Statements
such as "pending" or "now training" describe that earlier stage; use the current
findings and linked result documents above for the latest completed evidence.

Status: export and accounting qualification passed. Full-panel memory planning
also finished and rejects the existing storage design for this wide context.
See `CAPACITY-FINDINGS.md`. No independently validated blind-defense policy is
ready for preview or deployment.

The [sampled evaluation contract](SAMPLED-EVALUATION-CONTRACT.md) now has passing
paired-estimate and payoff-bound controls. It distinguishes evidence for a
profitable tested deviation from an upper bound on best-response gain; this is
evaluation infrastructure, not a newly qualified physical-poker range.

The [physical fit/reload control](SAMPLED-PHYSICAL-FIT-CONTROL.md) also passed:
real card-and-history observations feed the neural fit, and trained weights
reproduce reference action probabilities after engine reload. It is a fixed-data
integration test, not a completed physical-poker self-play study.
The subsequent [GPU fit/reload control](SAMPLED-PHYSICAL-GPU-CONTROL.md) passed
inference, gradient and trained-weight transport checks on the same observations.
The [bounded batch-query cache](SAMPLED-BATCH-QUERIES-CONTROL.md) now reproduces
direct policy queries and sampled traversal records exactly. Connecting its
query rows to batched tensor inference and back to traversal now passes the
[version-2 bridge control](SAMPLED-BATCH-BRIDGE-CONTROL.md). Version 1's false
context-identity rejection is preserved as failed evidence. This execution uses
CPU inference; the full-query CUDA data path and physical self-play remain pending.
The [bounded physical replay storage](SAMPLED-PHYSICAL-RESERVOIR-CONTROL.md) now
preserves per-visit multiplicity and passes sampling, split-batch and checkpoint
continuation checks without a growing information-set dictionary. Its subsequent
[bounded fitting integration](SAMPLED-PHYSICAL-STREAM-FIT-CONTROL.md) passes
full-gradient and engine-reload checks. Combined CUDA execution and physical
self-play integration remain pending. The [combined CUDA pipeline control](SAMPLED-PHYSICAL-GPU-PIPELINE.md)
is queued behind the current strategic experiment under the shared GPU lock.
The [resumable physical sampler](SAMPLED-PHYSICAL-DEALS-CONTROL.md) now reproduces
the existing panel and separately supports full-deck public cards. Both chance
laws and checkpoint continuation pass their controls; full-deck training is not
yet a completed experiment or a qualified replacement policy.
The [iteration-boundary checkpoint control](SAMPLED-PHYSICAL-CHECKPOINT-CONTROL.md)
also passes: a restored tiny CPU learning iteration exactly reproduces the
uninterrupted deals, updates, fitted weights and random states. This is resume
integration evidence, not convergence or a deployed player model.
The [streaming played-model reader](SAMPLED-PHYSICAL-BANK-BRIDGE.md) also matches
an independent physical root-model mixture, preserving own-reach weighting and
excluding the unused final fit. It prepares policy evaluation, not a strength claim.

The [compression and eviction controls](MEMORY-EXPERIMENTS.md) subsequently
verified exact GPU-state recovery over 48 compact sweeps. Whole-record lossless
compression reached only 1.665x on selected trained source checkpoints; it does
not justify admitting the full wide-range forest. The subsequent
[full-support recovery control](WIDE-RECOVERY-RESULT.md) also passed: eight
player sweeps matched the resident reference exactly. Persistent storage size
and reload cost remain unresolved; this is not a completed strategic study.

The [public-chance census](PUBLIC-CHANCE-SCREEN.md) then reconciled all 336
continuations and found 99.43% of reachable persistent state on the river.
Lazy card sampling delays allocation but does not cap eventual storage. River
decomposition was then screened: the [frontier census](RIVER-FRONTIER-RESULT.md)
found 11.5 million subgames and 160 GB even for bare f64 boundary values. A naive
full-panel re-solve loop is not being implemented. A separately registered
wide-state [maturity/compression probe](WIDE-MATURITY-RESULT.md) completed: exact
compression reached only 1.415x at 2,000 iterations, while discarding negative
regrets after projection improved the size-only result to 1.720x. The latter
has not passed resumed-GPU equivalence. Neither admits the full forest.
These are storage probes, not strategic training runs.

The next algorithm candidate is [sampled decisions with full support](SAMPLED-UPDATES-DESIGN.md).
Its exact joint-deal probability oracle passed on both full 112-board contexts.
The subsequent [sampled-update oracle](SAMPLED-UPDATES-RESULT.md) passed exact
regret and average-policy identities on a finite imperfect-information control,
including zero own reach and re-entry. The isolated [GPU batch reference](SAMPLED-GPU-BATCH-RESULT.md)
also matched that control, preserving frozen policies and duplicate updates.
The [on-demand transition reference](SAMPLED-GEOMETRY-RESULT.md) then matched
all legal native public histories across the actual 336-game BB panel. The
[GPU transition and physical-showdown components](SAMPLED-GPU-POKER-PRIMITIVES.md)
now pass their reference checks too. The subsequent
[integrated sampled-poker check](SAMPLED-POKER-INTEGRATION.md) matched all
653,847 updates and root values over six small batches exactly. It combines
physical sampling, full subtree traversal and frozen sparse strategy lookup.
Persistent state grew to 521,394 entries; capacity and practical convergence
remain unqualified. These short correctness batches are not a trained replacement.

The subsequent [fresh-deal growth screen](SAMPLED-GROWTH-RESULT.md) retained
7,944,848 entries after 186,368 deals and stopped before its registered entry
cap. Hardware still had ample free memory. Late-street reuse was extremely low;
an exact suit-orbit census reduced occupied entries by only 1.087x overall.
Larger tabular runs are deferred pending a convergence control and a
[bounded-model candidate](SAMPLED-FUNCTION-APPROXIMATION.md). No new strategic
accuracy claim or preview policy follows from this resource test.

The subsequent [finite-game convergence control](SAMPLED-CONVERGENCE-CONTROL.md)
passed its independent target for full traversal and all eight sampled runs.
This establishes a working learning loop on the small nonphysical oracle game;
it does not resolve the full poker study's storage or late-street reuse problem.

The first [bounded neural candidate](SAMPLED-NEURAL-CONTROL.md) completed all four
registered runs but failed the finite strategic target. Matched table controls
were substantially more accurate. A frozen-data fitting probe identified an
approximation-sensitive uniform fallback when all predicted advantages are
negative. The isolated highest-regret fallback comparison subsequently reduced
all four candidates' gaps by 56.9–73.4%, but still missed the target. A longer
[retained-model-bank control](SAMPLED-NEURAL-BANK.md) completed all four runs:
implementation checks pass, but none passes the strategic target. The subsequent
[larger-reservoir exact-mean comparison](SAMPLED-NEURAL-MEAN-CONTROL.md) completed
with all four CPU runs passing their registered targets. The matched GPU
candidate's first completed run fails its fixed target (0.01040 versus 0.01000);
the remaining GPU cases continue unchanged. No new range or production model
is qualified by these finite-game results.
The [GPU counterpart of the revised method](SAMPLED-NEURAL-MEAN-GPU-CONTROL.md)
is running the same four cases and strategic stopping rule, with independent
saved-model replay checks. Its full review is pending, but the completed failure
already prevents an all-four pass.

A [root-action diagnostic](ROOT-ACTION-DIAGNOSIS.md) of the completed original
study localizes 99.62% of UTG's residual gap to its first response to the 3-bet.
Several meaningful calling hands are undervalued by the frozen policy on unseen
boards, while other hands overcall. This is post-hoc diagnosis, not a new
confirmation or an instruction to tune on the reserved evaluation panel.

The completed independent 190-flop comparison supports weighted training in
one three-bet response situation. The next question is whether that benefit
transfers to a BB facing an open, including the calling hands the application
has historically undervalued. Success means lower independently evaluated
deviation gains in the new situation, not making a chart look looser or adding
mixed strategies by hand.

## Qualified candidate

The read-only export comes from `7max 200bb corrected multiway 20260910.gtop`:
UTG through CO fold, BTN raises to 2 bb, SB folds, and BB acts with 1 bb posted.
There is no straddle. BB calls one additional bb; no third player remains live.

- Seven-player source, 200 bb stack, 0.5/1 blinds, no ante, 5% rake capped at 2 bb.
- OOP is BB, IP is BTN, regardless of their original numerical seat indices.
- Root pot 3.5 bb; folded SB contributes 0.5 bb of dead money.
- BB retains all 169 classes. BTN has 96 classes above the existing negligible
  entry-weight cutoff. Do not narrow BB's support to make memory admission easier.
- Three distinct postflop continuations: pot/remaining stack 4.5/198,
  12.5/194, and 36.5/182 bb. All-in showdown pot is 400.5 bb.
- The postflop-to-preflop utility adjustment is 0.25 bb per player here, not
  the original study's 1.75 bb. BB folding at entry loses its posted 1 bb;
  BTN receives a net 1.5 bb. These values sum to the 0.5 bb dead contribution.

The incoming BTN range inherits a **calibrated approximate preflop solve** at
iteration 578. It is a reproducible conditional input, not measured player
behavior, a GTO Wizard range, or a newly validated opening range. Using it can
test continuation methods given that range; it cannot validate the upstream
opening strategy or the whole seven-player game. Folded players' private cards
remain omitted. This candidate is currently qualified for geometry only.

## Evidence completed

`conditional_hu_context_export` derives player order, terminal types, pots,
remaining stacks, and utility offsets from saved-game nodes. It leaves the
original hard-coded exporter and research executables intact. Source save and
equity-cache hashes are identical before and after export; in-memory strategy
arenas are also checked for mutation.

`export-audit.json` records independent Python checks of all action transitions,
live-player masks, topology, investments, strategy normalization, fold outcomes,
and terminal chip/rake conservation. Seven intentionally corrupted inputs were
rejected, including the old pot offset, wrong seat order, and a third live player.

As a regression check, the new exporter reproduced the original 12-node study's
incoming ranges and all saved strategies exactly. Its two postflop leaves still
derive to 39.5/182 and 93.5/155, with the original 1.75 bb offsets. Terminal actor
and winner fields that do not apply are now null rather than arbitrary seat
labels; decision actors and fold winners match exactly.

## Work before the next experiment

The storage investigation and sampled-method controls are documented separately:
[fresh-deal growth](SAMPLED-GROWTH-RESULT.md),
[finite convergence](SAMPLED-CONVERGENCE-CONTROL.md),
[neural approximation checks](SAMPLED-NEURAL-CONTROL.md),
[retained-model comparison](SAMPLED-NEURAL-BANK.md), and
[physical observation inputs](SAMPLED-OBSERVATION-CONTROL.md).
The [matched table control](SAMPLED-TABLE-BANK-CONTROL.md) separates limitations
from retaining a small sample and fitting that sample with a neural network.
An [eightfold reservoir-capacity comparison](SAMPLED-RESERVOIR-CAPACITY.md)
improved the finite exact-mean controls and supports the next fitting diagnostic.
The [fixed-data fitting controls](SAMPLED-LARGE-FIT-CONTROLS.md) verify a way
to remove training-minibatch noise without changing the squared-error objective.
A [neural self-play control using those gradients](SAMPLED-NEURAL-MEAN-CONTROL.md)
completed with all four CPU cases passing. The matched CUDA comparison ended
at its four-hour cap with two passes, one target miss and one incomplete case. The original
small-reservoir GPU bank comparison finished with four strategic-target failures.
The completed no-rake/seed-17 CUDA case also missed the revised target. A
[residual and checkpoint diagnosis](SAMPLED-NEURAL-RESIDUAL-DIAGNOSIS.md) locates
its extra error in public-card decisions and documents fluctuating continuation
values; it does not alter stopping rules or qualify physical poker.
A [matched learning-rate schedule diagnostic](SAMPLED-SCHEDULE-FIT-CONTROL.md)
rejected the tested cosine decreases at both fitting budgets; existing runs
retain their original settings.
The [physical policy-adapter and model-bank controls](SAMPLED-POKER-POLICY-CONTROLS.md)
passed with synthetic weights; trained poker strength is still unqualified.
A [physical fixed-profile evaluator](SAMPLED-PROFILE-EVALUATION-CONTROL.md)
now verifies complete-deal EVs, independent chip accounting and saved-model
mixture payoffs. Its fixture checks are not a new poker-strength evaluation.
A [root-deviation evaluator control](SAMPLED-ROOT-DEVIATION-CONTROL.md) checks
training-only action selection and separate evaluation with frozen downstream
play. It prepares a direct test for missed profitable calls without selecting
actions from the test outcomes; no new poker-strength result is claimed.
The [end-to-end fresh-deal evaluation path](SAMPLED-PHYSICAL-ROOT-EVALUATION.md)
now connects that responder to saved physical model banks, full-deck sampling,
native tree expectations and paired uncertainty estimates. Its tiny control
verified the pipeline; insufficient class coverage forced baseline fallback
throughout its test and provides no accuracy evidence.
The [first substantive physical root evaluation](SAMPLED-PHYSICAL-ROOT-STUDY.md)
is now registered for 8,192 responder-training and 16,384 fresh test deals.
It awaits the pilot's terminal review and freezes checkpoint selection, class
coverage rules and comparisons before outcomes. No new test deals were drawn.
A [bounded full-deck physical training pilot](SAMPLED-PHYSICAL-PILOT.md) is
now training after the finite comparison stopped and the
[combined CUDA pipeline](SAMPLED-PHYSICAL-GPU-PIPELINE.md) passed.
It keeps the full saved BB/BTN support, checkpoints to the SSD, and has a fixed
one-hour/128-iteration ceiling. It is diagnostic, not a qualified new model.
The exact table grew too quickly for the broad BB problem; a bounded neural
alternative is under qualification. No actual-poker neural policy has passed
evaluation. The pilot's first completed checkpoint has been verified; production
and the preview are unchanged.

1. Plan memory for the wide BB/BTN support and all three continuation branches.
   The three texture probes are resource checks only, not a training/test panel.
2. Introduce a separate context-driven training/evaluation executable. Replace
   fixed leaf indices, two-branch allocation, player order, rake, chip bounds,
   and four-action root-report assumptions. Keep completed evidence reproducible
   with its original binaries and snapshots.
3. Validate the generalized executable against the original context and against
   independent BB fold/call/raise/jam cashflow controls. Verify exact imported
   policy preservation for evaluation.
4. Freeze the chosen incoming range, action menu, training panel, disjoint test
   panel, weights, budgets and stopping rules before inspecting new outcomes.
   Compare weighted and equal training under otherwise identical conditions.
5. Train only after actual RAM/VRAM admission with reserves and a live idle guard.
   Do not use reduced entry support or an easier action tree as a substitute for
   the stated blind-defense question.

Production port 56708 is untouched. All work in this directory is research;
no production solver logic or player model is changed.
