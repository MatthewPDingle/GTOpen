# Initial all-in target arithmetic check

23 September 2026. This is a preparation check, not a new trained candidate.
The running equal-versus-linear averaging experiment remains unchanged.

The proposed corrections preserve expected initial decision targets in the
fixed BB-versus-BTN game. Complete enumeration of 47,478 canonical compatible
private pairs, including both BTN responses, passed for all 16 cross-pairings
of two old policies and two synthetic extremes. No active candidate was read.

- Maximum BB conditional expectation discrepancy: 5.49e-14 bb.
- Maximum BTN conditional expectation discrepancy: 3.79e-13 bb.
- Maximum own-policy-weighted regret mean: 3.82e-14 bb.
- Exported BB helper versus direct payoff recentering: 1.43e-14 bb.
- Zero reached shove mass and invalid probabilities/payoffs are rejected.
- Runtime: 3.08 seconds; no GPU or production modification.

The BTN expectation is conditional on both its cards and BB shoving. Shove
reach weights visitation, rather than multiplying the conditional targets a
second time. BB replaces its sampled shove payoff and recenters all four
regret coordinates. These are expectation identities; individual-deal returns
are intentionally different.

Two synthetic, correlated call/raise payoff stress cases explicitly demonstrate
that every regret coordinate need not become less noisy. For the old visible
policy paired against itself, one case increased the call-coordinate variance
from 230.99 to 264.30 while reducing the shove coordinate from 1198.01 to 75.53.
These artificial call/raise values are not estimates of actual training
variance and cannot justify a speed or strength claim.

The check uses independently calculated outcome-wise physical-pair payouts
against the already separately audited exact matrices. This control has not
received a separate full audit of its own. Native record transport, use of
current played policies, untouched ordinary call/raise records, random-number
preservation, and actual training variance remain to be checked before any
separately registered training attempt. No current trainer imports the helper.

Priority remains completion and analysis of the active averaging experiment,
then meaningful evaluation of the wider calling/raising behavior. This narrow
all-in preparation does not qualify preflop ranges generally or justify a
deployment.
