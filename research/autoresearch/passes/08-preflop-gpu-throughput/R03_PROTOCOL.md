# R03: production integration and isolated-server qualification

Planned next step. Keep 56708 read-only; do not deploy or restart it as part of
this qualification. C01+C07+C09+C14 are the retained runtime. R01 selection and
R02 partial-allocation recovery are qualified independently of the normal app.

Make only retained probability sharing, terminal unrolling, bounded offsets and
memory-aware selection available in a normal GPU server build. Keep unrelated
research algorithms behind preflop-research. Preserve the ordinary constructor as
a reference/fallback to avoid recursive fallback or changing existing callers
silently. The server should explicitly choose the retained path when its actual
planned buffers fit available GPU memory and explain selection/fallback in its
existing status. Do not expose research labels or add configuration burden.

Preserve the original configured budget for particle grouping and HU-cache
choices; the optional sharing limit is separate. No changes to model, samples,
float accumulation, policies, seeds, stopping criteria, stored formats or CPU
performance. Keep wide-index fallback available when the bounded CDF condition
is unsupported. Test builds may enable research comparisons; production must
not pull in experimental convergence algorithms or the fault-injection hook.

Verify generated retained kernel PTX against C14, all expanded numerical suites,
R02 failure recovery, native GPU and default solver regressions. Update the
saved-game continuation harness to exercise production selection and explicit
retained/reference/fallback paths on both immutable six/eight-player saves;
compare all checkpoints, full arena fingerprints, metadata and save/reload
continuation. Confirm small and large complete-work behavior with the established
benchmark; do not label production qualification as an additional speed gain.

Build a separate server executable with only its normal GPU feature. Start an
owned hidden instance on a verified unused local port, with isolated session/cache
outputs. Never load/build/save into the user's 56708 session. Verify API startup,
preflop saved-session loading, chosen GPU path, solve/stop/resume and persistence.
Check postflop/report endpoints without altering the user's active session.
Record the exact binary/source hashes and a concrete backup/restoration plan for
an eventual 56708 switch. Stop only the owned qualification instance afterward.

Use serial run07 guards for builds/tests/GPU work, no concurrent GPU benchmarks,
and per-workload bounded caps. Preserve failed versions and raw results. A
qualified isolated server is readiness evidence, not live deployment or proof
that the broader GPU convergence/order-of-magnitude objective is achieved.
