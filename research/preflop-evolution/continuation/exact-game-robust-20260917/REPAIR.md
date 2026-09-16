# Numerically validated LP backend

Both earlier attempts completed the exact integration screen successfully but
stopped before fitting any surrogate: default HiGHS exceeded1e-8 primal/dual gap
on a training range (8.7603e-8); tighter tolerances alone also exceeded it on
another range (1.4129e-8). Both failed attempts and their source freezes remain.

A numerical-only probe regenerated the fixed512 training and128 test contexts
per contribution context using HiGHS interior point, no presolve, feasibility
tolerances1e-10 and interior-point tolerance1e-12. All2560 primal/dual solves
passed the unchanged1e-8 gap check. No model was fitted, prediction error scored,
or model parameter changed during that probe. This does not isolate which LP
option accounts for the numerical improvement.

Re-run the full registered experiment with this explicit backend. LP solvers
can select different equilibria, so all solving arms are rerun; do not splice
old strategies into the new result. Record the source, numerical options and
prior freezes. Keep all original game, model, seed, count and acceptance gates.
