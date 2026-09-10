# Estimator cost and safe reuse

The added exact count performs canonical `forced_sigma` routing once per action
node and immediately drops each temporary vector. Time is proportional to all
materialized forced policy entries, while peak extra vector memory is one node
(`actions × 169 × 4` bytes). Contextual inference may populate its existing
bounded cache; that is already part of canonical routing.

Current server `pf_solve` constructs `PreflopGpu` directly. It does not call
`vram_estimate_mb` first. Therefore this estimator change adds no duplicate
forced-policy materialization to the current production solve startup. Public
estimator callers found in source are capacity/budget tests and research
diagnostics. Measure before introducing a persistent cache.

If a future flow needs estimate followed by construction, prefer an explicit
`PreparedPreflopGpu<'a>` that borrows `&'a PreflopSolver` and owns the host
materialization (`src`, `foff`, `forced`, value plan and reach/cache plans).
`prepare(&solver)` routes policies once, `plan.estimate_mb()` reads the prepared
sizes, and `plan.into_gpu(budget)` consumes the same buffers and ends the borrow.
This prevents the caller changing public config/profiles/hero/locks between
preparation and construction, avoids a second large forced buffer, and avoids
repeating topology work. The API must not accept a second solver argument that
could mismatch the plan. Keep the streaming standalone estimate for callers
that want an estimate without retaining a large host buffer.

Do not memoize merely by tree size, position count, iteration or profile name.
Identical-size trees can have different point locks, per-node adaptive rules or
model policies; many input fields are public and bypass setter-based revision
counters. Do not add a separate approximate routing predicate to compute the
size: precedence must stay shared with canonical policy materialization.

This is an API design recommendation, not a proposed performance claim or a
necessary change for the current benchmark run.
