# Separate conditional-all-in training comparison

Status: prepared, not admitted. The exact cache and the ongoing hybrid study
must finish and pass their respective independent reviews before admission.

## Question and unchanged settings

Does reducing preflop all-in label noise improve the learned policies, holding
the dense trial's game and training recipe fixed? This is separate from the
direct-preflop hybrid hypothesis. The only estimator change is to replace a
sampled full-board result at a **preflop all-in terminal** with exact remaining-
board equity for the physical private pair. Postflop decisions still use the
sampled board and only information visible at that decision.

Use the same BB-versus-BTN context and incoming ranges, 78 complete iterations,
512 fresh physical deals per iteration in eight 64-deal subbatches, and the
dense trial's deal/action/reservoir/initialization seeds. Preserve both frozen
updater passes, the two neural networks, reservoir capacity, fitting objective,
512 full-gradient Adam steps, learning rate, cached CUDA fitting and ordinary
equal-iteration averaging. The sole candidate is the complete played bank
0 through 77; generation 78 is unused. No checkpoint selection by strength.

The exact cache contains 23,891 suit-canonical private-pair keys covering all
39,936 scheduled training deals. It preserves player roles. Admission requires
its complete independent coverage/count review. A missing key, incorrect hash
or mismatched label stops the run; there is no approximate fallback. Cache
identity and estimator version are included in checkpoint configuration.

Format-3 documents explicitly identify the estimator. The adapter checks the
cache against every batch and requires native lookup and cash-flow controls
before ingesting any advantage records. It preserves per-visit reservoir
sampling and visible-only model inputs. No existing trial input is changed.

## Required gates

1. The earlier conditional-board reference and bridge controls remain immutable.
   Uniform and last-played learned-policy noise controls passed, with separate
   readbacks. Their small-fixture results are not accuracy or speed claims.
2. The new adapter control checks suit/within-hand symmetry, player orientation,
   explicit protocol routing, malformed-input rejection and exact reservoir
   arrays/RNG state against direct per-visit insertion.
3. The prepared pipeline control must verify the unchanged training math and
   evaluation flow, the two error-budget allocations, new seeds, and all stage
   sources before registration. It must not launch a GPU experiment.
4. The exact cache finishes and passes independent review; the hybrid study
   finishes all its existing stages and releases the shared GPU lock.
5. The new training controller performs its own production-idle and resource
   admission checks, then freezes sources, cache and control evidence. Stop at
   78 iterations or three hours, or on resource/activity/integrity failure.
   Preserve failure evidence; no automatic extension, retry or partial candidate.

Reserve at least 20 GB host RAM, 3 GB VRAM and 40 GB free SSD. Training store cap
40 GB; evaluation cap 30 GB. Do not change production on 56708 or the preview.

## Fresh evaluation of both players

Reserve seeds **79101** for 8,192 response-training deals and **79102** for
16,384 held-out deals. Neither stream has been used by the prior candidates.
Evaluation keeps the existing full-deal native payoff evaluator, independently
checked forward cash flows, and complete own-reach average bank. It does not use
the training cache to assign held-out outcomes. Compare CPU versus CUDA policies
and values on the first 256 response-training deals before drawing test deals.

Five BB root comparisons remain: a response selected by hand class on the
response-training stream, always fold, always call, always raise and always jam.
Minimum support remains 16 response-training deals per class. Use one final
look, with **alpha 0.025 across these five comparisons**.

Also predeclare three BTN comparisons at node 12, facing BB's root jam: a
class-based response selected from reach-weighted training payoffs, always fold,
and always call. The learned response retains baseline behavior below 16 raw
training observations or with zero summed jam reach; equal action values fold.
Hold every other decision fixed. Report paired gains per original spot entry,
including BB's jam reach, using **alpha 0.025 across these three comparisons**.
The two families together control within-trial error at at most 0.05 by the union
bound. This does not control selection across the wider research history.

The BTN script and selection rule are frozen before training and before any
fresh test data exists. It reads response-training outcomes and publishes its
chosen response before reading held-out outcomes. Reusing the same independently
drawn deal streams across these predeclared comparisons is allowed; independence
between the comparison families is not assumed. A zero jam-reach case reports
zero per-entry impact and no conditional calling frequency, rather than dividing
by zero or inventing evidence.

Training gets a full checkpoint/reservoir replay. Both evaluation families get
independent result readbacks. No intermediate significance stopping, hand patches
or feedback from these held-out outcomes into the candidate is allowed.

These remain restricted deviations, not an upper bound on either player's full
best-response gain. The context, betting menu and omitted earlier folded cards
still limit generalization. Better-looking ranges or an inconclusive interval
are not sufficient for deployment. Report action composition and both players'
results alongside the statistical uncertainty before choosing further work.
