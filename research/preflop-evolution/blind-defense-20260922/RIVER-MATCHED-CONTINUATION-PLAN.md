# Longer matched river-target continuation

Freeze this plan before drawing the new evaluation stream. This is exploratory
research in the existing 200 bb BB-BTN context, not a production qualification.
The completed two-update pilot showed working propagation but no reliable edge.
Its published analysis and sources remain unchanged.

## Training and execution

Continue all four complete parent states from boundary 80 to 110: thirty more
updates per arm, thirty-two since their common boundary 78. Preserve both
independent training seeds, baseline and river method, all learning settings,
reservoirs, chance/action streams and the complete historical model banks.
The candidate still averages 64 opponent-hand draws for visited river targets.
Keep 512 training deals per update, 64 per physical subbatch and four board
workers. Run A-baseline, A-river, B-river, B-baseline in that fixed order.

Use eight physical workers for both methods only after the full-update control
passes exact state/artifact equality and its candidate four/eight runtime ratio
is at least 1.1. That control recorded 247.75 versus 169.765 seconds, a 31.5%
time reduction in one paired replay. This is not a general speed guarantee.
Reuse the already-qualified shared-query evaluator; do not adopt the unqualified
snapshot variant. Verify source registrations, readbacks and frozen hashes.

An invocation may run for eight hours, with verified checkpoint resume after a
terminal process exit. Preserve partial attempts and all original evidence.
Eight hours is an operational boundary, not a promise of study completion.
The store has a 60 GB logical cap plus 4 GB follow-up reserve; admission counts
that whole reservation against the existing 800 GB global allocated cap.
Existing generation evidence suggests roughly 37 GB of new generation files,
before model/reservoir objects and evaluation archives. Refuse unsafe admission.
Light desktop GPU use is allowed below the established 65% guard, with a 4 GB
own-CUDA limit and 2 GB external headroom. Active production solves take priority.

## Fixed evaluation and interpretation

Evaluate the full played banks 0 through 109 using own-history-weighted mixing;
exclude fitted but unplayed model 110. Use exactly 16,384 fresh common physical
deals with seed 9294101, checking existing registrations for a seed collision.
Use the existing eight fixed player-replacement contrasts across the two seeds,
one final analysis only, no test-based stopping or selected favorable subset.
Verify common new training deals and action seeds despite divergent policies.

Retain the primary two-sided bounded empirical Bernstein intervals with 5%
family error allocated across eight contrasts and one final look. Their generic
payoff bound is conservative: even at 16,384 deals, its additive radius is about
0.74 bb per entry. This run will often be unable to certify a small edge with
that bound. Report paired means, sample variances and standard errors as well.

Prospectively add a separately labeled exploratory normal approximation:
mean +/- z * SE, where z = Phi^-1(1 - 0.05/(2*8)). These nominal Bonferroni
intervals are conditional on the frozen banks and independent evaluation deals.
They are not a finite-sample guarantee and do not cover training-seed uncertainty.
Rare tails may undermine normal coverage. Independently recompute these values
from archived paired deals and report tail diagnostics (largest centered
observation's share of squared deviation, standardized third absolute moment,
and the ten largest squared deviations' share). Never substitute these intervals
for the primary ones or describe them as proof of robust preflop accuracy.

Require the CPU independent readback of checkpoints, all evaluation batches,
source-deal replay, lossless archive hashes, cashflow/policy crossings and scalar
statistics. Compare initial BB and exact BTN components at generations
78, 79, 80, 81, 82, 90, 100, 109 and 110, marking the last as unplayed. This
readback reuses the qualified native engine; it is not a second poker engine.

Report every seed/seat, full learning costs and storage use. Consistent favorable
exploratory estimates can justify a further confirmatory or equal-time study;
mixed estimates, regressions or excessive cost argue against this treatment.
Do not pool away disagreement. No deployment or accuracy promotion follows
automatically. Equal-time quality and additional stacks, rake, sizing and
multiway contexts remain necessary for the user's broader goal.
