# Connected-game diagnostic

After adding stabilizer tying, same-state operators and same-policy full
enumeration agree, and fixed-range 2,000-iteration games pass their aggregate
value/convergence gates. The abrupt-changing-range stress test still fails
its independent-trajectory value threshold. Do not hide or relabel that failure.

Next test the actual coupled preflop/postflop schedule using the frozen subtree
and existing development panels, never reserved boards. Create a separate
example executable, preserving the original unprojected executable and source.
Compare projected explicit chance and projected compact chance on:

1. The existing two-board suit-orbit manifest through 2,000 iterations.
2. If its gates pass, the existing ten-board AB manifest through 2,000 iterations.

Use the existing 50% bet/pot raise menu, exact investments and rake, entry
support cutoff, chance weights, alternating-player schedule and evaluations
at 1/20/100/500/2000. The only intended changes are internal symmetry tying
and, between new variants, chance representation/storage. Keep one GPU job
at a time and monitor production idleness.

Required evidence: independent private-pair normalizer/frequency/hand-summary
accounting, terminal probability error <1e-5, cashflow error <1e-4 bb,
nonnegative player deviation gains with 1e-5 rounding tolerance. At 2,000:
both total gains <0.01 bb, corresponding player EV difference <0.002 bb,
and root prior-weighted policy total variation <0.01. Report maximum supported
hand policy difference and differences against the original unprojected game.
These latter are sensitivity diagnostics, not a claim of unique strategies.

No production deployment or larger-board accuracy claim follows from this
diagnostic alone. If gates fail, retain the evidence and investigate before
scaling the candidate. Record source/input/executable hashes before launching.
