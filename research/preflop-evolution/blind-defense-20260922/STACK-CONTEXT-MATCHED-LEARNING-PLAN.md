# Matched complete-continuation learning across stack depths

Status: prepared protocol; admission requires the population readback and the
complete-cycle archive control to pass. This is not a production deployment.

## Question and scope

Does adding 25 explicit river hand-versus-board features to the 362-input
history/hand/public-price model improve the resulting complete policies?
Both versions learn the full existing preflop/flop/turn/river action tree.
Neither starts from the fitted terminal Fold/Call diagnostic weights.
The 25 additional features are active on the river; their effects on earlier
decisions must propagate through the continuation learner.

Use the exact verified fixed-entry population in stack-context-population-v1:
BB facing a BTN min-raise, SB folded, 0.5 BB dead money, 5% explicit rake capped
at 2 BB. Preserve each depth's actual action geometry. Fit 20/40/100/200/400 BB,
and hold 60/150 BB out of fitting. The retained 200 BB BTN entry range is held
constant across depths to isolate continuation effects; it is not an optimal
opening range for every depth. This is heads-up continuation research, not a
complete multiway preflop solution or a matched GTO Wizard accuracy claim.

## Fixed training design

Run two independent seeds, each with a 362-input baseline and 387-input candidate.
Use 64 complete joint cycles per arm, from scratch; evaluate the complete played
bank at that fixed boundary. Do not choose a checkpoint based on test results.
The final generation-64 fit is unplayed and excluded from policy-value evaluation.
Played generations 0..63 receive the existing linear weights 1..64, with each
generation's own-action reach and complete local table overrides preserved.

In every cycle, freeze one model while collecting all five fitting contexts.
Each context contributes 169 class-stratified physical deals, in 13-deal batches,
and one complete sampled-board root calculation. Keep posterior64 river targets,
exact preflop all-in terms and all legal 2/3/4-action menus. Preserve ordered
reservoir insertion. Each actor/context reservoir holds 32,768 visits. Both
actors then receive 256 full-gradient Adam steps, learning rate .003, chunk512,
fresh matched initialization, equal one-fifth context weights and targets in
BB divided by starting stack. The candidate adds 1,600 parameters per actor
(25 inputs times 64 hidden units); all other widths and fit settings match.

Seeds, action streams, physical deals, root boards and reservoir seeds match
between representations within each replication. The independent replication
uses separate seeds. The extra input columns start at zero, with all shared
initial parameters matched. Use four CPU target workers and one board worker,
plus CUDA policy scoring and gradient fitting. These are supported parameters
of the qualified pipeline; no new arithmetic or target estimator is introduced.

## Fresh complete-policy evaluation, fixed before training

After training, freeze all four played banks. For each of the seven depths, draw
4,096 independent physical deals from its registered compatible-card entry law,
using seed 9309000 + depth. No evaluation deals are used for fitting or selection.
Use all eight within-seed crossed BB/BTN profiles, exact conditional preflop
all-in values and the existing full-action sampled-board native evaluator.
Keep both actors, all legal actions, real own-action histories and all streets.

For each depth report the eight paired player gains in BB per entry. Use the
existing bounded empirical-Bernstein intervals at one final look, allocating
family alpha .05/7 per depth (overall 56 contrasts). Also report an equal-depth
mean of each contrast in starting-stack units; derive its interval by averaging
the simultaneous per-depth interval endpoints. This is conservative and retains
dependence between contrasts. Positive fixed-opponent value is not a best-response
bound, exploitability estimate or equilibrium certificate.

A replicated policy-improvement claim requires positive lower bounds on all eight
equal-depth normalized gains and no negative per-depth point estimate. Otherwise
report mixed, adverse or inconclusive evidence; do not relax the rule after the
results. Report each depth and seed, negative-deal fraction, 95th/99th percentiles
of paired losses, worst observed loss and individual-deal maximum values. A normal
approximation with Bonferroni over 56 contrasts may be shown as exploratory only.
No deployment is authorized by a statistical pass.

Export complete averaged preflop action matrices for all seven contexts and both
seeds/arms. Show hand-class differences, weighted action totals and support; these
are upstream changes, not accuracy measurements against an external oracle.
The two held-out stack depths test behavioral transfer without local fitted tables.

Keep continuation-prediction evidence separate: the regret network does not predict
calibrated action EVs. Comparing its raw outputs to one final policy's action values
would be invalid. A separate fresh-target regression/decision diagnostic must have
its correct target and protocol fixed before its labels are generated; it remains
outstanding and is not silently replaced by training loss or the full-policy score.
The study and broader goal are not complete merely because training finishes.

## Durable execution and storage

Preserve every training model, checkpoint and complete source evidence. Compress
new cycle evidence using the qualified exact XZ wrapper; authenticate restored
original bytes before retiring only new owned raw duplicates. Do not delete or
rearchive historical stores. Maintain immutable per-cycle manifests and explicit
progress after complete checkpoint and archive publication. Recover a completed
cycle without repeating collection; a partial scientific cycle is not automatically
retried or skipped. Preserve failures.

Admission reserves at most 45 GB of new logical evidence against the 800 GB global
allocated cap. Keep 40 GB free on S:, 28 GB available RAM at admission and 24 GB
while running, with at most 2 GB own CUDA reservation. Use 12-hour invocations that
stop at completed cycle boundaries and resume the same registered attempt. Limit
total training wall time to 72 hours. Share light desktop use, yield to active
production solves/heavier workloads, and leave production 56708 unchanged.

The controller initially implements training and exact retention. Evaluation is
a separately implemented consumer of the fixed banks and the protocol above;
its source must be pinned before the first fresh evaluation draw. No evaluation
or prediction result is inferred from an implementation check.
