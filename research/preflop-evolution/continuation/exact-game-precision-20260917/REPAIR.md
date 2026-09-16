# LP numerical precision repair

The original registered run completed both full-tree and exact-cutoff arms.
Both passed their fixed0.005-chip full-game NashConv screen at5000 iterations.
During generation of the training ranges, a continuation LP had primal/dual
gap8.760261538398595e-8, failing the required1e-8 check. SciPy HiGHS defaults
allow feasibility error larger than this experiment's required accuracy.

Preserve the original source, freeze and completed outputs. A separate adapter
sets primal/dual feasibility and interior-point optimality tolerances to1e-10.
Re-run all arms in a separate directory. No game, acceptance threshold, model,
seed, iteration count or training split changes. No model was fitted and no
prediction test was scored in the original attempt. Record this adapter and
the earlier completed results in the new input freeze before execution.

This is an LP numerical-precision repair, not permission to relax the accuracy
gate. The original implementation remains hash-verifiable.
