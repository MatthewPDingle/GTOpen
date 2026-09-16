# Zero-probability hand completion: separate follow-up

Registered after the robust LP run failed its fixed5000-iteration integration
screen (NashConv0.007225), while the earlier backend passed(0.003875). No model
was fitted in either run. This is a new hypothesis test, not a numerical repair
or a replacement for those outcomes.

Keep the robust interior-point backend, miniature game, checkpoints, model and
all original gates. At each exact continuation, identify hands with exactly
zero own probability. Replace only those hands' actions by a best response to
the returned opponent equilibrium. Preserve every positive-probability hand's
strategy; no epsilon range or tiny-probability cutoff. Recompute conditional
hand values, including the hands not played at that continuation. Changes to
both players' zero-probability hands cannot change the equilibrium's expected
payoff on its input distribution; verify this assertion at every query.

The hypothesis is that arbitrary zero-probability behavior can make earlier
counterfactual action values depend on irrelevant LP tie choices. This differs
from N32's fallback for an entirely empty range. This test does not establish
that either issue causes the large Hold'em residual.

Log changed actions, largest conditional-value change and maximum on-distribution
payoff change. Independently test the completion against enumerated pure best
responses and unchanged positive-support actions before running. If this exact
arm passes the original0.005 full-game threshold, run the originally fixed
surrogate experiment. Positive Dirichlet training/test contexts are unchanged
by zero-probability completion. Retain raw and completed full-game measurements.
