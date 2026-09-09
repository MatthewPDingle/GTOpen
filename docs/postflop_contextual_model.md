# Contextual postflop betting

The Ignition NL10 regular pool now carries separate heads-up betting evidence
for flop donks, stabs after the initiative holder checks, turn/river leads,
and probes after a checked-through street. Each cell is specific to street
and preflop pot type (limped, single-raised, or 3-bet+).

This replaces the use of the pool's 25.25% combined no-initiative statistic
for those decisions. It does not change c-bet, fold-to-bet, or raise-facing-bet
modeling. Those remain broad HUD targets and need their own later refinement.

## What the history supports

The same 34,466 validated hands give 131 bets in 911 heads-up 3-bet+ flop
donk opportunities (14.38%), versus 193 in 420 flop stab opportunities
(45.95%). These are different decisions. They also pool boards, stack sizes,
positions and bet sizes; some bets are shoves. Neither number is a measured
33%-pot betting frequency on KQ9.

The collector, opportunity definitions and retrospective evaluation are in
[the evidence study](../research/ignition-postflop-contexts/README.md).
That evaluation supports separating contexts. It does not validate the final
solver adjustment, hand allocation, or profitability. Observations within
hands and sessions are correlated.

## Conservative adjustment

At a matching no-initiative decision:

1. Read each hand's underlying solved strategy and the range arriving there.
2. With fewer than 50 matching opportunities, preserve that strategy exactly.
   Missing pot type, unknown action history, or a missing cell also preserves
   the baseline. Never substitute the old combined donk/stab statistic.
3. Otherwise move the node's aggregate bet target toward the observed rate
   with weight `n / (n + 200)`.
4. Bound the adjustment: each hand's bet-to-check odds can change by at most
   a factor of four in either direction. Clamp the target to what that bound
   can achieve, then use one common odds multiplier across hands.

The minimum count, 200-opportunity shrinkage constant and fourfold bound are
explicit conservative modeling assumptions, not fitted confidence levels.
For example, a hand betting 0.01% cannot be inflated into a 25% bettor by this
adjustment. Exactly zero/one probabilities remain fixed. Relative betting
propensities and each hand's proportions across available bet sizes remain
intact, including any existing all-in share. The `min`/`max` size preference
still applies to the other, legacy profile targets.

No new hand-strength ranking or observed postflop hand policy is claimed.
The selected hands and size shares remain inferred from the original solve.
Manual node locks take precedence. Reapplying a profile starts from the
underlying strategy arena, not from the previously installed locks.

The Browse readback distinguishes observed frequency, bounded target and
achieved frequency, and shows sample count/source at the root when the
modeled player acts there. It remains a root readback while navigating.
Reports store the same evidence and use the same lock method. Pot type is
carried from Preflop export through Setup/Browse and report requests.

## Compatibility and activation

`PostflopStats.contextual_betting` is optional. Old custom profiles retain
their explicitly configured broad targets. Only the source-verified Ignition
NL10 regular pool is upgraded in the candidate library. Other sites/stakes
and edited models are not silently assigned these observations. Model edits
preserve the new evidence; its obsolete pooled donk/stab input is read-only.

The migration tool defaults to a dry run and can write a separate library
copy. It checks provenance and original postflop settings, preserves all
other fields and refuses in-place/live-library writes. Saved player profiles
do not retain enough provenance for automatic replacement. After activation,
reselect the updated pool for relevant seats, then transfer the preflop spot
again so its pot type accompanies the new profile. Existing painted/custom
ranges should be preserved separately.

This change is prepared in a separate checkout while reports run. Do not
replace the live binary, web files, model library, or sessions during those
jobs. Completed reports and their saved profile snapshots remain historical
results; generating a new report with the new profile is an explicit step.

## Verification

Parser fixtures cover opportunity eligibility, initiative, checks, limped
pots, hero exclusion and all-in handling. Migration tests cover provenance,
custom-model preservation and output safety. Solver tests cover all four
contexts, missing/sparse context, normalization, exact zero/one preservation,
bet-size shares, bounded amplification and manual-lock precedence. Server
and JavaScript tests check metadata transport and model editing.

No GPU workload or request to the active report server is required for these
checks. GPU-feature compilation can prepare the desktop executable without
launching it; GPU runtime tests must wait until the user's reports finish.
