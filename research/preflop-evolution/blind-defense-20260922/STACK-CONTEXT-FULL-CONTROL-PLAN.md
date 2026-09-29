# Full-context model integration control

This checks the new full model wrapper before training integration. It does not
train a strategy, select a scientific model, or revisit final-test poker labels.

Retained fixtures: both earlier played policy seeds at generations 0, 1 and 77;
complete own-history dependencies for the previously selected TRAIN observations.
Compare the new full-wrapper CPU and CUDA policies at both 362 and 387 inputs,
including the first-two-played-model reach-weighted average. Absolute tolerances
are 1e-10 for action probabilities and for accumulated own reach. TF32 is off;
inference widens the float32 weights to float64 as in the prior contracts.

Native multi-context fixtures: existing 20/40/60/100/150/200/400bb observations
and public ledgers. Five contexts own deliberately synthetic local accumulators,
with different BB root and BTN response sentinels. The 60/150bb contexts are
held out and own no learned local state. Native preflop catalogs are exported
only to validate complete class routing; no new hands are solved or labelled.
The control-only accumulator values and uniform class masses are not empirical
or strategic estimates, and their synthetic matrix identities cannot authorize
scientific training. Models and exact source identities are saved separately.

Check CPU/CUDA policies and averaged own reach in every context, content-hashed
model roundtrips, exact absence of local overrides in held-out contexts, and
changing one local root without changing any other context. Reject swapped or
missing context state, held-out local state and attempts to fit held-out queries.
Use nonzero relative-feature weights in the synthetic candidate so this is not
only a zero-extension check. All streets and legal native action menus remain.

Pin sources and retained inputs before execution. One invocation, at most ten
minutes, 512MB own CUDA allocation, 64MB new evidence plus16MB reserve. Maintain
the800GB allocated research cap,40GB free-disk floor and existing admission
policy: share light desktop use, yield active solves and heavier workloads.
Keep production56708 and all registered studies unchanged. Save failures; no
silent re-run of a started control. Completion still does not qualify the
weighted objective, multi-context trainer or resumable joint-cycle checkpoint.
