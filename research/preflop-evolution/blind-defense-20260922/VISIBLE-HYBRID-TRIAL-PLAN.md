# Visible hand-and-board representation: fixed research trial

## Question and comparison

Does explicitly describing visible hand and board structure help the sampled
postflop model learn better continuation values and allocate preflop actions?
The immediate comparator is the completed combined 269-input model, not Wizard
or the separate UTG/LJ preview. That model called 31.42% under the complete entry
prior, but individual hand choices remained uneven. More calling is not success.

Use the same BB-versus-BTN 200 bb conditional game, fixed incoming ranges,
action menu, rake, full physical-card sampling, exact preflop all-in training
labels, direct retained preflop tables, and played-policy averaging. Earlier
folded cards remain omitted. This does not solve a general preflop game.

## Intervention and fixed budget

Append 33 summaries derived solely from the player's cards and visible board
to the original 269 network inputs. The added columns are zero preflop and their
initial weights are zero. All original initial weights, hidden layers, optimizer,
loss and seeds are preserved. Input width becomes 302, increasing parameter
count from 21,700 to 23,812 per player. This tests features plus added capacity;
it does not isolate poker summaries from an equally large generic network.

Start from scratch for exactly 78 updates of 512 deals (39,936 total), 512
fitting steps per player/update, and the original 262,144-record reservoirs.
Use the complete equally weighted, own-action-reach-adjusted bank of played
generations 0..77; exclude unused generation 78. No latest-only selection,
hand-specific patches, intermediate selection, extra fitting or budget extension.
The format-3 visible checkpoints identify the exact representation. Reservoirs
retain original observations; no hidden cards or outcome labels become inputs.

All short visible-feature controls must pass first, including the four-update
integration replay, exact saved-policy replay, CPU/CUDA bank checks and the
actual sampled-payoff adapter control. Failed control versions remain recorded.

## Evaluation fixed before training

Fresh response-training/test seeds are 99101/99102, with 8,192/16,384 deals.
They are distinct from the already inspected experiments. Preserve the primary
sampled-board evaluator; conditional evaluation is a separate future experiment.
Before opening the held-out stream, check the complete trained bank against
CPU float64 policies/payoffs on 256 response-training deals, and publish the
trained per-class responder. Fewer than 16 response-training observations
retains the original policy; BTN response selection also needs positive jam reach.

Five BB-root alternatives: trained first-action response and always fold, call,
raise or jam. Three BTN-versus-jam alternatives: trained response, always fold
or always call. Each family uses alpha .025, one final look, and the existing
bounded paired-deal intervals. Independently audit both families, every chance
stream, policy artifact and cashflow identity after completion.

Report all comparisons, intervals, unsupported classes, and all 169 preflop
hand-class action distributions. Aggregate mixes must distinguish sampled hand
mix from full-prior weighting. Compare allocations descriptively against the
269-input model. Different seeds and jointly changed opponents/continuations
prevent a paired cross-candidate significance or direct EV-quality claim.

A profitable restricted deviation with positive lower bound is adverse evidence.
No detected positive deviation is not proof of accuracy: these intervals can
be wide, and these alternatives do not upper-bound a full best response. Better
fitting, wider calling or resemblance to Wizard alone do not qualify promotion.
No automatic deployment is permitted. If uncertainty remains broad, retain the
experimental label and evaluate variance reduction or more coverage separately.

## Resources and integrity

Training has a three-hour cap and 40 GB store cap; evaluation has its existing
two-hour cap and 30 GB store cap. Maintain 20 GB host RAM, 3 GB VRAM and 40 GB SSD
free. Stop for production activity, integrity/numerical failure, resource limits
or deadlines. No automatic retry. Preserve failed evidence and registered bytes.
A wrapper runs training, audit, admission, BB evaluation/audit and BTN evaluation/
audit sequentially. Production 56708 and the range preview stay unchanged.

## Stack-depth scope

Stacks affect this fixed game, but this model has no learned cross-depth
behavior. The required follow-up is specified in `STACK-CONTEXT-PLAN.md`.
Do not interpret this trial as stack-general preflop modeling.
