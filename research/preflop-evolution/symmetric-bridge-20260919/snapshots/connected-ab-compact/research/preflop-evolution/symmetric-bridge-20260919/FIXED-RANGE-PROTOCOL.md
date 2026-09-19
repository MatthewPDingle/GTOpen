# Converged fixed-range diagnostic

The projected tests pass same-state sweeps and same-policy evaluations, but
their independent 100-step trajectories under abruptly changing externally
supplied ranges still fail the 0.002 bb value gate. Public-runout transport
reduces that discrepancy but does not eliminate it. Keep that failure.

Next separate convergence from numerical path sensitivity. Run the existing
two-tone and monotone fixtures for 2,000 CFR+ iterations with constant,
class-dependent, nonuniform external ranges. Compare projected full chance
enumeration and projected compact chance. Save evaluations at 100, 500 and
2,000 iterations. No hand histories or reserved strategic cases are used.

Evaluate both players' full average-policy and best-response values, weighted
by the same exact compatible private-card prior. Also report maximum per-hand
value differences and root strategy drift. Require at the final checkpoint:
nonnegative gaps (rounding tolerance 1e-5), each game's combined deviation gain
<0.02 bb, and each player's aggregate EV difference <0.002 bb. Root policy
and per-hand differences remain diagnostics, not evidence of a unique Nash
strategy. Do not replace the earlier stress-test thresholds with these gates.

This experiment helps decide whether the discrepancy is persistent value
bias or numerical trajectory separation in a nonstationary stress test.
It does not by itself authorize deployment or prove larger-board accuracy.
