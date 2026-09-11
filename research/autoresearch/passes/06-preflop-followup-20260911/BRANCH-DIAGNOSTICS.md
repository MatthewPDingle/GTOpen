# Branch convergence diagnosis

Prepared while phase-A timed GPU trials run. The new diagnostic example and
unit-test extensions must build/pass only after those timings finish. They do
not modify the timed executable, any saved strategy or the live application.

Inspect six selected paths in pass-05 native six/eight-player saves, the large
64-sample save, the tighter six-player reference, and the modeled baseline.
At each hand, retain the raw regrets and strategy sums, current and average
action probabilities, and actual current/average prefix masses separately.

Hypotheses to distinguish before changing learning:

1. The current action is sensible but its historical average lags. Compare
   both action distributions against the same average-continuation Q values.
   This comparison is not a best response against current future play.
2. Opponents give the branch effectively zero current mass, despite positive
   mass in the published average. Old regret information may then dominate
   the displayed conditional policy. Report both prefix masses explicitly.
3. Positive regret or average-strategy sums fall below the existing 1e-12
   normalization threshold. Count the actual uniform fallbacks among material
   hand classes, rather than assuming floating-point underflow is the cause.

The direct-payoff unit fixture also distinguishes current 75% calls from its
25% average, checks tiny positive regrets trigger the known fallback, verifies
different current/average prefix masses, and checks inspection is immutable.

Once these observations are available, choose a bounded local-convergence
experiment. Preserve prefix ranges, action menus, all accounting, profiles and
locks. Any reset/reweighting must be explicit and recorded, and all added work
must be included in convergence time. Verify local and whole-game error after
the change; do not deploy a cosmetically cleaner range as a solver fix.
