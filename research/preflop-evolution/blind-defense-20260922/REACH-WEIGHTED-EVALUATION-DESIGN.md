# Next accuracy-evaluation design: concentrate work without changing the question

Design only, prepared after the completed river continuation. No new estimator,
sampler or poker evaluation is implemented by this note. The old 16,384-deal
analysis and its registered intervals remain unchanged. Use a fresh prospective
evaluation for any new method; do not keep sampling until a preferred sign appears.

## Why another large ordinary sample is not the first step

The current crossed evaluator already replaces preflop all-in runouts with exact
private-pair equity from the qualified cache. It still samples physical hole
cards and postflop boards. Simply proposing conditional preflop all-in evaluation
again would repeat completed work.

The prior shared-policy-mixture bound remains useful but is not sufficient by
itself for this longer continuation. The saved 110-model banks share normalized
component mass 632/1221 under weights 1..110, in both A and B. Applying the existing
bound helper gives a 193.19778869778872 bb absolute paired-gain envelope, versus
the generic 400.5 bb. This is a metadata-derived prospective planning bound,
not a newly adopted interval or proof of a positive gain. Unlike the earlier
one-update pilot, almost half the mixture weight now belongs to changed models.
Any real application must reverify model content, context and inference, and
include a prospectively justified numerical allowance.

## Candidate to qualify

Use complete preflop reach probabilities to spend more board evaluations on
private-card pairs that can meaningfully affect the comparison. Correct the
sampling weights so the answer remains expected payoff per original BB entry.
Do not report it as payoff per flop, per continuation, or bb/100 all dealt hands.

For each legal physical private pair h, let p(h) be its probability under the
existing entry distribution, including blockers and the established support
cutoff. For contrast j, let X_j(h,b) be the same complete-policy gain evaluated
on a shared board b. Derive deterministic lower/upper bounds L_j(h), U_j(h)
before sampling boards. Define:

- c_j(h) = (L_j(h) + U_j(h))/2;
- b(h) = max_j (U_j(h) - L_j(h))/2;
- C_j = sum_h p(h) c_j(h), Z = sum_h p(h) b(h);
- q(h) = p(h) b(h)/Z on b(h)>0.

Sample h from q, then a legal board from the original conditional board law.
The observation Y_j = C_j + Z*(X_j-c_j(h))/b(h) has the original expected gain,
and lies in [C_j-Z, C_j+Z]. The expectation follows by substituting q into the
weighted sum; pairs with b=0 have X_j=c_j and contribute through C_j exactly.
If Z=0, all gains are deterministic and no board sampling is needed.

All eight contrasts share the same q, retaining common random numbers. The
proposal depends on frozen policies and exact pre-board bounds, not measured
test outcomes. No clipping, rejection of costly outcomes or range reshaping.

## Constructing useful bounds

For each complete profile, separate deterministic preflop terminal contribution
T(h) from postflop entry leaves l, with preflop reach r_l(h). Existing exact
private-pair all-in labels enter T. Each postflop conditional value has a safe
terminal-payoff interval [a_l,z_l] derived from the same chip ledger and rake.
For one new-minus-old contrast, a valid initial envelope is:

L = T_new-T_old + sum_l r_new,l*a_l - sum_l r_old,l*z_l;
U = T_new-T_old + sum_l r_new,l*z_l - sum_l r_old,l*a_l.

This simple envelope does not assume the old/new postflop decisions coincide.
Pairs rarely reaching postflop can have a much smaller width. Common-policy
cancellation can be investigated separately, but is not required for the initial
proof. Whether Z is small enough to save meaningful work must be measured from
frozen policies before committing to a new large evaluation.

## Implementation gates

1. Check unbiasedness and bounds by exhaustive finite-domain arithmetic tests,
   including zero-width support, skewed probabilities, overlapping contrasts,
   constant outcomes and rare large outcomes. Check sampler/weight roundtrips.
   These are mathematical fixtures, not poker evidence.
2. Export all legal preflop decision policies with correct own-action reach from
   the frozen complete banks. The present 265-row root/jam-response catalog is
   insufficient for later preflop decisions. Do not assume missing rows are
   class-constant or suit-invariant. Verify any symmetry reduction against the
   native observation keys and the actual policy implementation, or enumerate
   the needed physical cases directly. The 5950X and 128GB RAM can accommodate
   a bounded, parallel table-construction stage.
3. Independently reconstruct preflop reaches, all terminal contributions and
   postflop entry masses. On retained training fixtures, require their recombined
   values to reproduce the existing native complete-policy evaluator, including
   both seats, all raises, zero-reach branches, all-ins, rake and card blockers.
4. Audit exact entry normalization, candidate C/Z, support, legal board sampling,
   and numeric bounds. Use a justified conservative error allowance; do not
   derive one from the largest observed fixture error alone. Stop on failed
   bounds instead of clipping observations into the intended interval.
5. Freeze method, source/model hashes, number of new deals, seeds, time/storage
   budget and family error allocation before fresh evaluation. Retain primary
   bounded intervals plus paired descriptive errors and timing. One finite study
   with the original and candidate estimators on appropriate fixed fresh streams
   can compare precision per unit time. It cannot establish a best-response bound.

Do the cheap deterministic envelope calculation before another expensive policy
training run. If the envelope or cost is disappointing, preserve that finding
and use a simpler fixed stratified design; do not spend days polishing it.

## Connection to better ranges

A more precise evaluation would help decide whether the slower river treatment
is worthwhile under equal compute. It does not itself improve ranges. After that
decision, return to stack/context transfer: the 60-input public-economics prototype
and seven native stack-geometry fixtures already exist, but a shared trained
cross-context model and held-out-depth accuracy are still outstanding. The earlier
12-input fixed-200bb fit was mixed/negative; do not confuse it with a cross-depth
test. Broader positions, sizing menus and multiway play remain unvalidated.

## Existing sources reviewed

- RIVER-MATCHED-CONTINUATION-DECISION.md and PAIRED-MIXTURE-BOUND.md
- PUBLIC-ECONOMICS-FEATURES.md and BOARD-LATER-PUBLIC-STATE-FINDINGS.md
- crossed_complete_policy_batch_v1.py: conditional preflop all-in protocol
- sampled_physical_deals_v1.py: physical private-pair and board distribution
- board_training_policy_v1.py: complete own-history-weighted policy averaging
- sampled_physical_preflop_table_v1.py: exact-key tables and neural fallback
- preflop_allin_matrix_v1.py: explicitly restricted first-own-action scope

No production change, deployment, new push or historical evidence replacement.
