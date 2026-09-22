# Second-context study: BB defense

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
completed with all four CPU cases passing; the matched CUDA comparison continues. The original
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
registered and queued behind the finite GPU comparison and combined CUDA check.
It keeps the full saved BB/BTN support, checkpoints to the SSD, and has a fixed
one-hour/128-iteration ceiling. It is diagnostic, not a qualified new model.
The exact table grew too quickly for the broad BB problem; a bounded neural
alternative is under qualification. No actual-poker neural policy has passed
evaluation. The revised finite GPU comparison remains running; production and the
preview are unchanged.

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
