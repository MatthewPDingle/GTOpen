# Separate prediction diagnostic: design, not an admitted experiment

The active four-arm comparison must finish unchanged. This document prepares the outstanding prediction question without changing its registration, models, gates, data, or final policy evaluation. No new labels, fits, model selection, native jobs, or deployment are authorized or performed by this document. Exact numerical budgets and seeds still need registration before any diagnostic data is generated.

## What the current networks predict

`stack_context_training_checkpoint_v1.py` declares the target as `advantage_bb / context_starting_stack`. `stack_context_fit_rows_v1.py:prepare` groups source-weighted reservoir visits, normalizes each context's legal-action loss, and mixes the five contexts with fixed weights. Those visits come from different played generations. The final network is therefore trained to approximate a weighted mixture of training advantages. It does not estimate the action values of the final averaged policy.

Consequently, subtracting a final-policy action value from a saved raw network output would compare different quantities. Training loss also includes sampled-target noise and cannot establish decision quality on new boards or stack depths. The registered fresh complete-policy evaluation answers whether the resulting policies perform better; it does not turn the regret network into a calibrated value predictor.

## A common target for a useful diagnostic

Use a separate supervised comparison of the 362-input and 387-input representations, with fresh networks and identical fitting budgets. Both must receive exactly the same target labels and source weights. The current 387-input representation adds 25 relative-hand features on the river and zeros in those columns on earlier streets; it does not yet add corresponding flop/turn hand-strength features. Earlier-street effects would come through shared fitting and continuation behavior. Do not refit or reinterpret any of the four active study models.

Choose one common teacher before seeing the final evaluation: the complete A-baseline played bank, generations 0 through 63, with the already-declared generation weights and own-action reach. Exclude its unplayed generation64. The choice is fixed by identity, not by which arm wins. Freeze and authenticate the exact bank only after training finishes successfully. This teacher provides one defined policy to predict; it is not an optimal-poker oracle.

For actor i, legal action a, and the actor's visible information I, define the label as

    A_i(I,a) = Q_i^teacher(I,a) - sum_b teacher_i(b|I) Q_i^teacher(I,b).

Normalize by the context's starting stack. The same teacher, continuation, opponent posterior, and action-value convention must be used for every action in a row. A fixed-teacher advantage is now a common regression target for both representations. Differences between action advantages also equal differences between their action values. Absolute chip EV is still a different output and must not be claimed.

Implementation qualification must show that the native target generator conditions on the actual public action history and compatible hidden cards, preserves all legal actions, and does not expose an opponent's cards or future board cards to the inputs. Retain exact all-in terms wherever available. Any sampled continuation labels must identify their estimator, budget, pairing, and remaining sampling noise.

## Separation and evaluation requirements

Freeze a new source manifest and independent sampling streams. Do not use the main comparison's 4,096-deal evaluation samples for fitting, hyperparameter choice, or diagnostic model selection. Keep 20/40/100/200/400bb as fitting contexts and 60/150bb as held-out depths unless a separately declared question explicitly changes that scope.

For postflop generalization, split by canonical flop identity before generating labels, keeping every turn/river descendant of a flop on the same side. Merely separating complete five-card boards can leak the same flop into fitting and testing. Define the suit canonicalization, partition, stratification, and any resulting distribution weights before sampling. Preflop rows need a separately specified holdout unit; they have no flop feature, so a board-disjoint label split alone does not demonstrate generalization to unseen preflop hands.

Use both actors and all legal action menus. Register the full data budget, representation parameters, initialization pairing, training seeds, optimizer, stopping rule, and any validation-only model selection before data generation. No numerical choices should be selected using the main comparison's final gains or the diagnostic test labels.

Report legal-action weighted regression error in starting-stack units, by actor, street, and depth, with fixed context weights. Illegal action slots must contribute neither error nor denominator. Include a repeated-label subset to measure target noise separately from approximation error; its size and purpose must be fixed before labels are drawn.

For the decision comparison, freeze the conversion from predicted advantages to a policy in advance. Evaluate the two frozen policies on independent paired held-out targets or continuations. Their paired expected payoff difference under the common teacher is a meaningful decision metric. Do not take the maximum of noisy action labels and present the resulting gap as exact optimal-action regret. Confidence calculations must respect that multiple decision rows from one physical deal or board are dependent. Derive payoff/error bounds from the actual native ledger and any explicitly registered score clipping before choosing a bounded statistical procedure.

## What this would and would not establish

This diagnostic would test how well the input representations learn a common, clearly defined target and whether their prediction differences affect decisions. The active self-play comparison separately tests whether those representations improve the learned complete policy. Neither result alone proves agreement with GTO Wizard, equilibrium accuracy, multiway accuracy, generality across arbitrary preflop entry ranges, or readiness for production.

Before admission: qualify complete-bank teacher inference, native target semantics, feature/label separation, split reproducibility, source weighting, CPU/GPU agreement, and the resource envelope. The exact run protocol and source identities remain to be implemented and registered. Do not claim this outstanding diagnostic is complete merely because this design exists.
