# N25: fixed pairwise continuation values

Training-only screen of a structurally different value model. N20 improves
held-out continuation values but its equal-work frozen-value gap is larger.
Neither that result nor local sensitivity proves the reason. This experiment
tests whether a fixed hand-versus-hand payoff can retain useful accuracy while
removing dependence on a player's own range from that player's per-hand value.
The existing approximate heads-up-entry card accounting remains a separate
issue, tested by N24. No convergence guarantee is claimed for the whole game.

Use only the original 24 training contexts and the two development contexts.
Exclude an entire source family in each fold. Never fit to N15/N20/N21 test
labels. The prediction is cached compatible-card equity plus a correction from
a fixed OOP-versus-IP hand matrix. IP uses the negative transpose correction,
so compatible-pair weighted gross values sum to one pot without range-dependent
centering. Prediction for a hand depends on the opponent's distribution and
SPR, not on its own range. This is less expressive than a true postflop solution;
that tradeoff must survive the accuracy gate rather than be assumed acceptable.

Eleven fixed hand features: bias, pair, suited, high rank, low rank, high rank
squared, low rank squared, rank gap, ace, connected, and both ranks ten or above.
Their 121 ordered OOP/IP products have three SPR bases: 1, min(SPR/8,1), and
log(1+SPR)/log(21). Total 363 coefficients. Scale columns by training-weighted
RMS without subtracting means, preserving paired zero-sum structure. Weighted
ridge strengths are fixed at 0.01, 0.1, 1, divided by training-context count.
No neural residual, clipping, per-hand free parameters or adaptive grid search.

Eligibility requires all of:

- Mean family error at least 5% below the original 104-feature linear control.
- Mean and every family error no more than 5% above N15's recorded training CV.
- Compatible-pair pot conservation and direct pair-matrix arithmetic checks.

Reproduce the original linear control on exactly the same folds before claiming
eligibility. Select lowest mean error among eligible fixed strengths. If none
qualifies, stop this model family without new labels or GPU implementation.
If eligible, freeze a model trained on all 26 contexts; fresh evaluation and
independent GPU correctness, runtime and strategy-stability checks still remain.
Do not use N21 results as prospective validation if any of those labels existed
before this candidate was frozen. No automatic production deployment.

Prepare during N19 but do not run fitting while its isolated timing is active.
CPU fitting may run during N21 reference generation. Require at least 20 minutes
remaining before the fixed 2026-09-16 20:49:02 UTC deadline to start. Single BLAS
thread; verify absence of active GPU timing controllers before fitting.
