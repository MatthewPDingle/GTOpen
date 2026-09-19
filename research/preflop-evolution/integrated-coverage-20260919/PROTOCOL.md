# Integrated board coverage and folded-card audit

Keep production56708 and the frozen saved game unchanged. All work is offline.
This follows the two-flop integrated continuation prototype, commit830810c0.

## Suit coverage

Close each selected board under all24 suit permutations. Before the public
board, entry ranges and all preflop policies are suit-symmetric. Average
continuation counterfactual values across every combo of each169-class hand
before updating preflop regrets. This is the orbit quotient, not an average
of separately solved preflop strategies. Postflop policies retain exact
combos and full turn/river card enumeration.

Check the projection algebra against explicit permutation enumeration,
including missing combos blocked by the board. Compare an orbit river test
with24 explicitly expanded relabelings at1/20/100 iterations. Numerical
ties may separate later trajectories; require root EV and gap agreement
within0.002bb at the first checkpoint and within0.02bb at100 iterations.
Reject material conservation, probability or normalization discrepancies.

## Board sample

Use the existing canonical-flop list. Form the five previously used strata:
paired/two-tone, paired/rainbow, unpaired/monotone, unpaired/two-tone and
unpaired/rainbow. Within each stratum order canonical boards by SHA256 of
`integrated-coverage-20260919-v1|` plus board string, without looking at action
values. Development panelA takes the first board per stratum, panelB the
second. Their union has10 representatives. Give a sampled board unnormalized
weight `isomorphism_count * stratum_size / sample_count_in_stratum`.
This approximates uniform physical flop chance; it does not eliminate
finite-panel error. Report exact prior distance against the full-deck prior.
Third/fourth boards per stratum are reserved and not solved during this run.

Use50% pot bets,100% pot raises, one raise per street and85% all-in conversion
on all runs compared for board sensitivity. Preserve both called branches,
actual investments/stacks,4% rake capped6, and preflop no-flop-no-drop.
Keep the prior1e-5 entry support cutoff with no branch trimming or probe floors.
Run20-iteration smoke, then500 and2,000 if accounting and memory gates pass.
Use a21GB planned GPU budget, leaving room for the live app and CUDA overhead.

## Folded cards

Independently draw physical eight-player deals conditional on the frozen
UTG/LJ entry propensities, and weight the other six hands by their actual
earlier fold policies. Compare paired estimates with and without those fold
weights. Measure hand-class prior shifts and effects on raw equity against
the entering LJ range. This audit is not a substitute for integrating the
full folded-card posterior through flop/turn/river transitions.

Use fixed seeds and independent batches; retain uncertainty estimates and
effective sample sizes. Do not silently insert marginal adjustments into the
factorized two-player continuation solver: folded-card likelihood generally
correlates both live hands and future boards.
