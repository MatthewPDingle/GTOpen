# Fixed-current-policy river pilot

Prepared before inference, 2026-09-28. The full native export/value controls
passed. This bounded pilot measures compatibility, conditional target noise
and computation cost under actual learned research strategies. It trains no
models and cannot establish preflop improvement or a faster complete solver.

## Frozen policies and fixtures

Use generation 77, the last played model pair, from each of the two audited
board-root research arms. Exact identities are already recorded in the
board-river-bounds-bank-v1 registration. Do not use the 78-model behavioral
average, the unplayed generation 78, or the projected/bounded policy variant.
Keep preflop tables, exact BTN and board-root overrides as part of each policy.
Use that same identified policy for history likelihoods and future decisions.

Retain the eight original-rake native-control cases. Add four old-training
deal-000 cases selected from public legal geometry before scoring: first
query per actor whose legal Bet uses all remaining chips, and first whose
legal Raise does so. Use the public catalog's action costs and remaining
stack to select, never payoffs or predictions. Register exact keys and hashes.
No validation/final data is opened or used. Do not remove unsupported cases.

## Checks and measurements

1. Independently validate new native exports and reconcile visible card/outcome
   identities against old checked training exports. Require the selected bet
   or raise to carry the native all-in flag. Include full original cases too.
2. Compare prepared persistent-parameter GPU inference with unchanged CPU
   single-model inference. Require maximum policy difference <=1e-10,
   identical legal support, and action-value agreement <=1e-7 bb where
   supported. No epsilon floors, clipping, alternate models or substitutions.
3. Retain probabilities and their hashes. Compute full conditional values with
   the qualified reader, preserving supported zero-own-reach states. Explicitly
   retain unsupported cases and distinguish own-path status from counterfactual
   opponent support.
4. Compute exact first/second moments of external sampling conditioned on each
   visible target: one opponent hand shared across the sampled subtree; updater
   branches expanded; independent opponent action draws on distinct branches.
   Separate variance from private hands and later action sampling. Center all
   action values with the same current-policy probabilities. Compare moments
   against independent exhaustive outcome enumeration for fixed pair indices
   0, 495, 989 under uniform and learned policies. No global importance weights
   or upstream visit probabilities are inferred from these conditional moments.
5. Time native export, CPU query preparation, GPU inference and full value
   propagation separately. Repeat preparation/inference/value timings three
   times in fixed case/policy order, preserving cold versus warm results.
   Time cached external samples separately using 2,048 deterministic posterior
   draws per supported case/policy; this excludes native queries and network
   inference and is only a lower bound for an integrated sampling pipeline.
6. Full exact conditional targets have zero conditional target variance by
   construction. Report this fact with their cost, not as an end-to-end speedup.
   No quality gate is created from these reused training positions. Correctness
   failure blocks integration; cost/support findings determine practical design.

## Bounds and evidence

Register source/binary/model/input hashes and case identities before learned
inference. Verify all hashes again afterward. Preserve failures and version
corrections. CPU references use one BLAS thread; one GPU owner with persistent
small parameters and batched query inference. Use the qualified light-desktop
guard: yield to active production solves, >=65% other GPU load or insufficient
headroom. Own allocator budget 4 GB, external headroom 2 GB, free RAM >=24 GB.

Maximum runtime 600 seconds, each native invocation <=60 seconds, at most
100 MB new evidence. The 800 GB allocated research cap remains in force.
No archive deletion, production change, model training, deployment or GitHub
push. Following work still requires a separate visit-preserving native walker,
updates/ancestor-value checks and fresh self-play/full-policy evaluation.
