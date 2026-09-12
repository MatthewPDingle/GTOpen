# Pair correction passed the conditional decision-noise screen

All three immutable saved-state comparisons passed the preregistered screen.
The pair correction reduced the hand-mass-weighted sum of decision-regret
variances to 29.51–30.97% of the uncorrected result. This warrants a separate
learning experiment; it does not establish a convergence speedup.

| Saved source | Variance ratio | SB promotion score ratio | BB promotion score ratio |
| --- | --- | --- | --- |
| 64 samples, seed 42 | 0.3097 | 0.1328 | 0.5761 |
| 64 samples, seed 314159 | 0.2951 | 0.1451 | 0.5101 |
| Full particles, seed 42 | 0.3028 | 0.1067 | 0.5141 |

Promotion scores weight each relevant hand's probability that a strongly
inferior action outranks all acceptable actions in one sampled draw. Relevant
hand mass is at least 0.0025. These scores are not whole-game exploitability
or range-wide convergence probabilities. Worst relevant-hand promotion also
improved at both blind nodes in all three states, passing its separate gate.

Every source policy, current prefix mass, full-reference action value and
fixed constraint matched the archived uncorrected diagnostic exactly. The
independent verifier recomputed all action moments from all 1,024 offsets;
the enumeration mean passed the canonical-reference tolerance. No histories
or source saves changed. Raw results and SHA-256 envelopes remain available.

Three Rust conditional-sampling tests passed, including the new corrected
enumeration, source-preservation and actual nonzero-correction test. Two new
analytic Python tests verified that an exact correction passes, unchanged
noise fails, and a changed reference is rejected. The production build's
mode defaults are unchanged.

The earlier terminal-payoff screen and this decision-level screen answer
different questions. This result supports evaluating corrected regret updates
at the actual failing decisions; it does not overturn earlier failed timing
results for a different learning setup. `NORMALIZED_PAIR_QUALITY_PLAN.md`
registers the next combined-quality comparison separately.

Evidence: `raw/conditional-pair-screen-verified.json`, each
`raw/conditional-pair-s*-result.json.gz` and envelope, guard records, and
`check_conditional_pair.py`.
