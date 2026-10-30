# Exact-arithmetic check of the proposed sampling formula

The finite-domain formula in REACH-WEIGHTED-EVALUATION-DESIGN.md passed its first
mathematical control. This is not a poker sampler or a new accuracy result.

- 64 fixed-seed synthetic domains, eight contrasts each: 512 exact equalities
  between the original expectation and the reweighted expectation.
- 7,248 pointwise observation-bound checks, including highly skewed probability
  masses and large outcomes. No floating approximation was used.
- Zero-width positive-mass states contribute analytically. A fully deterministic
  case needs no draws; positive-width states with zero original mass stay unused.
- Seven invalid configurations/outcomes rejected, including a sampled outcome
  outside its declared bound. Outcomes are never clipped to make a check pass.
- Approximately 0.17 seconds; no GPU or new poker deals.

Evidence: bounded-pair-proposal-control-v1-result.json. Registration SHA256:
33f9c100106395acf58432c22d3daf3269a573fa20504854de1f4836c372e265.

The helper deliberately accepts exact rational inputs only. It does not qualify
floating-point normalization, numerical payoff bounds, categorical sampling,
native poker reaches, any suit/class reduction, or variance reduction on poker
data. Those remain the next implementation gates. Do not substitute it into a
registered historical evaluation.

The planning note's shared-mixture calculation used the completed continuation's
bank-identities.json, SHA256
4b9d3c61e2f0bc168367f3bdbc122429a827ea9b2f9b592355069b160f1c5539,
matching evaluation.bank_identities_sha256 in its completed result. The existing
bound helper returns common mass 632/1221 and changed mass 589/1221 for each seed
under weights 1..110. These metadata calculations do not change the old intervals.

Public stack/price descriptors and native geometry checks already exist. The
larger unresolved deliverable is a trained model that generalizes across contexts;
these evaluation controls are intended to make that work more informative, not
replace it.
