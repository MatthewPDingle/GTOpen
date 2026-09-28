# Fresh-deal conditional river target-learning probe

This is a new, bounded supervised feasibility experiment following the 80-case
conditional-river diagnostic. That diagnostic revealed local Fold/Call costs,
including rare paths dominated by initialization. It did not identify target
noise as the sole cause, establish equilibrium, or validate better preflop ranges.

## Fixed data and split

Generate 96 new full physical deals with PhysicalDeals seed 9289911 and the
unchanged 200bb BB-versus-BTN context. Deal indices 0-63 are training; 64-95 are
final evaluation. Freeze this partition before selecting observations or
running learned inference. Verify canonical full-board groups and complete
visible observation keys do not overlap between partitions. Fail explicitly
if they do; do not move or redraw individual cases after observing labels.

Use the unchanged complete native query exporter separately for each deal.
Select up to two eligible river Fold/terminal-Call observations per actor and
pot band (under 10, 10-50, 50-100, 100-200, 200+ bb), ordered by the SHA256 of
9289912|deal_index|hi|lo. Preserve short and empty strata. There are at most
1,280 training and 640 evaluation observations. Keep repeated selections within
one partition with their deal identity; this is a balanced diagnostic sampling
design, not game-reach sampling. No final evaluation result selects settings.

## Frozen teachers and three targets

Use both complete original 78-model banks, A and B, as separate fixed opponents.
For each selected visible state, enumerate all 990 legal opponent combinations
with the already qualified native exporter. Match entry weights, visible-card
removal, actual opponent action likelihoods, and configured rake exactly.
Preserve every selected state. Label unsupported opponent histories and zero
hero reach; do not replace them or invent a posterior. Unsupported targets are
excluded from fitting/scoring with counts disclosed. Report initialization
contribution separately; do not discard it or change bank averaging weights.

The target is delta = Call payoff - Fold payoff at the river. Compare:

1. The exact posterior expectation.
2. One opponent sampled from that posterior.
3. The mean of 16 independent samples from the same posterior, including the
   first sample used in arm 2.

Use three paired repetitions, with model seeds 9289921, 9289922, 9289923.
Per-case label sampling uses PCG64 initialized by the first 128 bits of SHA256
of 9289913|case_id|bank|repetition. Its stream is independent of processing order.
Retain sampled opponent indices. Check the analytic expectation and variance
of this finite distribution and deterministic support cases before collecting
labels. No hidden opponent cards, outcomes or posterior equity enter features.

These sampled labels are unbiased for this explicitly defined conditional
target. They are NOT a claim about the unbiasedness or variance of the existing
CFR advantage estimator, whose reach and importance weights differ.

## Learner and evaluation

Train a separate network for each frozen bank and acting player. Reuse the
302-input, 64/64 hidden-layer, four-output visible network and its seeded
initialization. Regress the difference of output 1 and output 0 onto delta /
400.5; the scale is the fixed maximum branch total for this context. Minimize
equal-row squared error on that contrast, using full-batch Adam at 0.003 for
exactly 512 steps. Other output heads are not supervised. These heads are not
interpreted as CFR regrets or immediately turned into production policies.

Use identical training states, visible features, initial parameters, optimizer,
budget and scale for all three target types within each paired repetition.
There are 36 fits (2 banks x 2 players x 3 repetitions x 3 targets). Do not tune
on final evaluation data or introduce clipping, extra inputs or early stopping.
Retain training losses and all final model weights. Validate the new contrast
loss and CPU/GPU gradients on controlled inputs before fitting.

Only after all models are frozen, score final evaluation deals against exact
conditional targets. Primary metric: unscaled squared error in bb. Secondary:
the local Fold/Call decision cost |delta| when the predicted sign is wrong,
using half that cost for an exact zero prediction. This compares a two-action
decision only, not a full best response when raising is legal. Also report
directional agreement, mean signed error, a zero-value baseline, and original
policy restricted Fold/Call costs. Preserve results by bank, actor, repetition,
pot band and initialization support. Query-balanced summaries are not bb/hand.

Advancement to a separate estimator-integration experiment requires the exact
target arm to beat both sampled arms in aggregate held-out MSE and two-action
decision cost, with non-increasing decision cost against each bank separately
(averaging paired repetitions and actors). Treat this as a descriptive pilot
gate, not statistical proof, production qualification or a full-game EV test.
If it fails, report whether fitting/generalization is still the limiting issue;
do not extend the evaluation or pick a favorable repetition.

## Execution, evidence and limits

Keep sources and registrations immutable once run. Hash every case archive,
retain policies and posterior information needed for independent CPU readback,
and resume only completed cases with matching identities. Preserve failures.
Prefetch at most four native exports and use at most two archive workers to
overlap CPU work with GPU inference. Keep both frozen banks resident and reuse
query preparation. Existing full-bank averaging and native poker code remain
unchanged. No production server changes or new application windows.

New files are capped at 2 GB, within the global 800 GB allocated-storage limit.
Maintain a 4 GB CUDA allocator cap, 2 GB external headroom, more than 24 GB free
system RAM and volume free-space guards. Share light browser/video use, yield
to heavier GPU activity and active production solves. A collection invocation
is limited to two hours; checkpointed continuation may resume the same fixed
cases. Check the first eight cases' timing and compressed size before admitting
the full collection. Stop safely if projected collection exceeds two hours or
2 GB; change execution only, not the chosen data or target definitions.

The existing ~716-720 GB archive is preserved. Compact case archives replace
only their own verified transient copies. No historical files are removed.
Independently reconstruct labels and held-out metrics before reporting results.

If this probe succeeds, derive a correct integration into self-play sampling
and test it before full retraining and fresh-deal complete-policy evaluation.
The broader goal remains accurate, flexible preflop play across stacks,
positions and trees; a successful river regressor alone does not meet it.
