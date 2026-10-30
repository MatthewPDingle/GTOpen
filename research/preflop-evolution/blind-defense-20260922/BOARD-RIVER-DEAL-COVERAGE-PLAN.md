# Equal-row-budget deal coverage comparison

This follows the failed advancement gate in BOARD-RIVER-TARGET-LEARNING-PLAN.md
and the exploratory training-only coverage curve. It tests whether distinct
deal coverage improves transfer, without adding training rows or optimizer
steps. It does not retroactively reverse either earlier result.

## Data and immutable partitions

Keep the original 64 training deals and their 1,152 independently checked
states as the dense training set. Use no training rows from the original 32
final evaluation deals. Reuse existing verified labels without alteration.

Generate 160 new full physical deals with PhysicalDeals seed 9289962, in the
unchanged 200bb BB-versus-BTN context. New accepted deals 64-191 are the 128
additional broad-training deals; deals 192-223 are 32 fresh final evaluation
deals. Reject a proposed deal before query selection or learned inference if
its canonical full-board group occurs among ANY original 96 deals or earlier
accepted new deals. Retain every proposal, rejection reason, sampler checkpoint
and accepted index. Admit at most 1,000 proposals, then fail. This new rule is
fixed here, not a change to the earlier experiment's collision rule.

The broad set has 192 deals: original 64 plus new 128. Sort these 192 indices
by SHA256 of 9289961|deal_index. Assign successive triples of deals to the
following three schedules, repeating 64 times. Each schedule selects one
state per listed pot band for EACH actor:

- under10, 10to50, 50to100
- 10to50, 100to200, 200plus
- 50to100, 100to200, 200plus

Each broad deal contributes six states; aggregate actor/pot-band counts are
identical to the dense set: 64 under10 and 128 in each remaining band per actor.
Broad has 1,152 training rows, of which 384 reuse original labels and 768 are
new. For an original deal, choose the scheduled band's lowest-original-score
state from the existing one/two selected states. For a new deal, order eligible
states by SHA256 of 9289963|deal_index|hi|lo and choose the first in each assigned
band. The source score mechanisms are both predetermined uniform hash orders;
labels are not consulted. No replacement for a short/empty required stratum:
fail and preserve evidence instead.

For each of the 32 fresh final deals, choose up to two states per actor and pot
band using the same new hash rule. Require the expected one under10 and two
per other band, yielding 576 final states. Verify full canonical-board and
complete visible-key separation between all training and all evaluation data,
including the previously spent final set. Save a complete membership manifest
for both training sets and fresh evaluation before collecting labels.

New collection: 768 broad-training plus 576 final states = 1,344. Historical
data remains external and read-only. Original 64 training deals may have been
used in prior development work; only the 32 new final deals are fresh evidence.

## Four matched arms and fixed learner

Compare dense-exact, broad-exact, dense-sample16 and broad-sample16. Separate
models per bank A/B and actor BB/BTN; three paired model seeds 9289971, 9289972,
9289973, totaling 48 fits. The inherited teachers are unchanged complete
78-generation original banks, with the same entry ranges, blocker handling,
opponent histories, rake and exact posterior delta = Call minus Fold.

New-case sample16 targets use the same qualified finite-posterior sampler,
PCG64 seeded by first 128 bits of SHA256 of 9289964|case_id|bank|repetition.
The first of these 16 draws is retained as audit information, not a fifth arm.
Reused case labels keep their ORIGINAL registered seeds and draws (9289913);
they are not regenerated or selected using favorable outcomes. Shared rows
use the same labels across dense and broad arms. Model initializations and
training budgets are matched within each repetition.

Use the unchanged 302-feature, 64/64 hidden, four-output visible network.
Regress output1-output0 against delta/400.5 with full-batch Adam 0.003 for
exactly 512 steps. Equal row weights, no clipping, extra features, tuning,
warm starts, early stopping or additional training. Reuse the independently
qualified contrast loss and check CPU/GPU controls against the current sources.
Save all weights and training losses; freeze all 48 models before final scoring.

Keep unsupported states with explicit support flags; exclude them only where
no posterior is defined and report counts. If support makes effective dense/
broad row or pot quotas differ, report that failure of the equal-budget design
and do not assert a clean diversity-only comparison. Do not discard rare paths
or initialization-dominated teacher states.

## Metrics and advancement gates

Primary comparison: broad-exact versus dense-exact on all 576 NEW final states.
Metrics: mean squared error in bb squared and local binary Fold/Call decision
cost (wrong sign costs abs(delta), zero prediction costs half). Average equally
over bank/actor/repetition models; report every subgroup, pot band, prediction
bias, directional agreement and initialization contribution. Retain predictions
and independently recompute model outputs and metrics. These query-balanced
costs are per selected decision, NOT bb per hand or full-game EV.

Coverage gate: broad-exact must strictly improve aggregate MSE and local
decision cost over dense-exact, with non-increasing cost in each bank separately.
Target gate: broad-exact must strictly improve both aggregate metrics over
broad-sample16, with non-increasing cost in each bank separately. Dense-sample16
is a declared secondary factorial comparison, not an alternative winner if a
gate fails. All comparisons average all three paired repetitions; no favorable
seed picking. Do not increase data after examining final results. Report the
two descriptive gates separately, with no statistical significance claim.

Only if BOTH gates pass should a separately qualified estimator-integration
experiment proceed. Even then, these two-action local regressors are not CFR
regrets, a complete policy or a deployable preflop improvement. The reach,
sampling and unbiasedness controls in BOARD-RIVER-TARGET-INTEGRATION-NOTES.md
remain required, followed by fresh full-policy evaluation.

## Resource and evidence controls

New store: S:/GTOpen-research/board-river-deal-coverage-v1. Added storage cap
2 GB, global allocated archive cap 800 GB. Reuse original data by hashes rather
than duplicating archives. Four native export workers, two compact archive
writers, one shared GPU research owner. The existing 4 GB CUDA allocator cap,
2 GB external headroom, 24 GB free system RAM and production-solve guard remain.
Light desktop/browser/video use is authorized; heavier work takes priority.

Selection is CPU-only and capped at ten minutes. Collection uses the existing
per-case archive/recovery protocol and a two-hour invocation cap, with the
first eight cases' conservative size/time admission before continuing. At
the previous rate 1,344 new states suggest roughly 31 minutes; this is an
estimate, not a promise. Eight CPU readback workers (two if machine busy);
training and evaluation expected to take minutes, with fixed limits registered
before execution. Do not modify production or historical archives.

Keep registered/executed source bytes immutable. Any correction receives a
new version and retains failure evidence. Hash all source, plan, membership,
input, archive and model identities. Code implementing later stages may be
written during collection but must preserve this frozen analysis plan and
register its source identities before fitting or scoring.
