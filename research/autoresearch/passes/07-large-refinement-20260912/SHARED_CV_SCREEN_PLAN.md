# Shared-reference CV: registered small convergence screen

Run only after SHARED_CV_PLAN.md numerical/storage gates, old-CV compatibility,
native GPU equivalence and the default release suite pass. No live writes.
This screen compares convergence and complete cost, not just lower memory use.

Use the unchanged fresh 23,038-node six-learning-player fixture, calibrated fit,
canonical coupled_deck_v1, gamma15 averaging with horizon 1000 and native
counterfactual regret units. No normalization, pair estimator, exploration,
root changes, masks or locks. Use the same six exploration-diagnostic-paths.json
paths and per-hand gates as previous screens. At every 25 iterations evaluate
with all 1,024 particles. Require gap <=0.005 bb and 6/6 conditioned branch gates
on two consecutive checks. Limit 3,000 iterations; full cases have a 450-second
process cap, sampled cases 250 seconds. Independent final saved audit cap 60s.
Do not stop a quiet run before its cap, extend failed budgets, or relax gates.

First seed42, in order:
1. Native full-particle control (1,024).
2. Native sampled control (64).
3. Previous per-traverser reference CV, interval32, eager launches (64).
4. Shared reference CV, interval32, captured launches (64).
5. Shared reference CV, interval64, captured launches (64).

The old-CV arm establishes whether the representation/graph changes offset
reference overhead; it is not itself an admitted candidate. It need not have
the same learned trajectory as the shared-reference arm because their reference
snapshot timing differs. Numerical unbiasedness and full-particle cancellation
are tested separately. Complete times include first refresh, graphs, all quality
checks and saving. Keep all unsuccessful cases and independent saved-file audits.

Advance the faster qualified shared interval only if the full control qualifies,
shared complete time <= half the full control, and (if the plain64 control also
qualifies) shared time <= twice plain64 time. If neither shared interval passes,
stop the screen. No second seed or large run is admitted unchanged.

If the first seed passes, register/run the same full control, plain64 control and
selected interval for seed314159. The same accuracy and time gates must pass.
This would admit a separately registered large diagnostic, not qualify a large
speedup or deployment. Published timings must distinguish unqualified cases
from equal-quality comparisons. Input/executable/source hashes and complete
per-hand final audits must be independently verified.
