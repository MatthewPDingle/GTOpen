# Complete-policy comparison: implementation preparation

Prepared while the first matched later-action training trial was running. No fresh evaluation deals were drawn, and no candidate effectiveness results have been inspected. Production and the GPU training worker were not changed.

## Frozen comparison semantics

Within each of the two matched training seed pairs, cross old/new BB with old/new BTN, giving four complete profiles. Evaluate all eight profiles on the same physical deals. Keep each selected player's entire strategy, including the root and later decisions. Do not force a different root action while retaining an unrelated continuation.

For each seed, report four paired gains: new BB versus old BB against each fixed BTN, and new BTN versus old BTN against each fixed BB. A positive number favors the player being replaced. Use each player's native payoff directly; do not assume that changing one player's policy negates the other's payoff when rake may vary. Eight contrasts are one inference family.

The planned primary intervals use the existing bounded empirical-Bernstein implementation with Bonferroni allocation over eight contrasts and one final look, for simultaneous two-sided 95% family coverage under its assumptions. Payoffs are bounded by minus the effective stack and stack plus dead money; each paired difference is therefore bounded by plus/minus twice the stack plus dead money. Frozen policies and independent common physical deals from the registered entry distribution are required. Sharing deals between profiles induces useful correlation and does not require independence between contrasts. Report paired standard errors alongside the conservative bounded intervals. These intervals do not upper-bound best-response gain or establish equilibrium quality.

The held-out sample count and seed remain those provisionally specified in `LATER-ACTION-MATCHED-STUDY-PLAN.md`; they must be confirmed in the final resource-admitted evaluation registration before sampling. No extending the test after viewing its outcome.

## Checks completed

Three synthetic test groups passed:

1. Exact actor-by-actor profile mixing across both seeds, including root rows; illegal probabilities are rejected and inputs remain unchanged.
2. Independent scalar reconstruction of all eight contrast signs and pairings, sample variances, standard errors and interval bounds.
3. Rejection of early looks, additional samples, invalid shapes, nonfinite values and out-of-bounds payoffs without partially updating statistics.

The CPU-only native fixture used one previously inspected physical deal, four artificial visible-only policies, 455 decision observations and eight full profiles. A separate scalar construction reproduced every transported probability. The native evaluator outputs and independently calculated paired contrasts matched exactly. This took 2.265 seconds and generated about 1.34 MB. It used no GPU and no new poker samples.

Registration: `crossed-complete-policy-control-v1-registration.json`, SHA-256 `7fdc51e205be15fb93d26eaef233ac1d284664a86b41bf649b89f5c47dff6791`. Result: `crossed-complete-policy-control-v1-result.json`.

## Remaining gates

Both full training histories still need completion and independent reconstruction. The evaluator still needs a trained complete-bank integration check, lossless archive/readback validation for the new summary format, and a fresh storage projection before the held-out study. The provisional 8 GB evaluation allowance is not evidence that all 65,536 deals will fit; measure representative archived batches first. No range-quality conclusion follows from these transport and arithmetic checks.
