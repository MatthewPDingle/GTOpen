# Complete stratified-policy comparison

The training plan already fixes two 78-generation stratified candidates against
the two completed historical baselines, followed by 65,536 fresh physical deals
with seed 9278101. This document specifies implementation qualification; it does
not change the training budget, hypotheses, opponent pairs or evaluation seed.

The policy order is first baseline, first stratified, replication baseline,
replication stratified. Each bank includes played generations 0–77, weighted
1–78 and by the player's own action reach. Unplayed generation 78 is excluded.
All four banks must have full independent training readback before admission.

## Before fresh deals

The full-bank control reuses 64 previously inspected deals. It compares both
stratified banks with the separate CPU weighted-policy reference, and both
baseline banks with their CPU reference. Checks include all 265 catalog rows,
all 169 BB root classes, and complete native-query histories from two batches.
Probability and own-reach errors must remain below 1e-10. The shared accelerated
transport must equal the direct GPU calculation. Native cashflows must pass
the existing legal-action, conservation and bounded-payoff checks.

The control uses the newly qualified parallel archive worker. Three copied
batches produced archives identical to the prior serial implementation; a
malformed fourth copy produced a reported worker failure with all raw copies
preserved. The production probe admits a closed port or verified idle server,
rejects active work and fails closed on indeterminate activity.

The full-bank control then needs separate scalar archive readback, including
crossed-policy identities, chance inputs, cashflows, paired statistics and root
summaries. These checks do not independently recreate the native poker engine.
Passing them qualifies numerical execution, not poker strength.

## Fixed comparison

The registered primary descriptive measure remains entry-weighted cross-seed
BB root total variation. Eight paired payoff contrasts replace either player's
policy against both the old and new opponents, separately for each seed. Use
the existing bounded empirical-Bernstein simultaneous 95% intervals with
Bonferroni correction across eight contrasts and one final look. Do not stop
early or extend the sample because results look favorable or disappointing.

Batch evidence must be losslessly archived before raw scratch retirement.
Independent CPU compression may overlap GPU evaluation, with no more than four
archive workers. A resumable implementation must bind completed batches to the
same prospective chance stream and preserve failed attempts. Do not restart
the entire chance budget after an observation timeout or process interruption.

## Resources and interpretation

GPU evaluation waits for training to finish and for the exclusive research lock.
Admission checks competing CPU/GPU work; runtime checks production activity,
available RAM, VRAM and disk. Keep at least 24 GB available RAM, 3 GB free VRAM
and 40 GB free space on S during evaluation. Qualification is bounded to 100 MB
of new evidence. Project the full archive from the control before admitting it.

These are historical-baseline comparisons with matched settings and seed
identities, not identical training deals. Improvements in consistency alone
do not establish improved play. Any positive result still applies only to this
specific BB-versus-BTN game; it does not establish accuracy across other stacks,
positions, raise sizes or multiway pots. Production remains unchanged.
