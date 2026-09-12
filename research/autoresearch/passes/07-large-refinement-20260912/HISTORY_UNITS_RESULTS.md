# Conditional/full-game update units: identity verified on small GPU fixtures

No new continuation entry point or deployment was introduced. Only research
tests were added; port 56708 remains untouched.

For four seats with nonuniform incoming ranges, the tested conversion is:

- Counterfactual values and regret increments for p multiply by the product
  of incoming masses for all q != p.
- Own-reach-weighted average increments multiply by incoming mass m_p.

The first test used dyadic masses. The second run broadened the same identity
to non-dyadic masses and signed regrets, in both raw and calibrated games.
The four final cases each covered a 526-node tree across 11 levels, **354,900
child action values** and **64,727 learning entries**. They included folded
seats, rake, investments, a frozen seat and a point lock. Values were compared
immediately before each parent level consumed its children, respecting GPU
scratch reuse. Other actors and fixed histories were unchanged.

| Incoming masses | Continuation | Max conditional value error (bb) | Max conditional regret increment error (bb) | Max average increment error |
|---|---|---:|---:|---:|
| .03125 / .125 / .5 / .25 | Raw | 0 | 0 | 0 |
| .03125 / .125 / .5 / .25 | Calibrated | 0 | 0 | 0 |
| .037 / .173 / .61 / .83 | Raw | 6.48e-7 | 1.88e-6 | 1.75e-6 |
| .037 / .173 / .61 / .83 | Calibrated | 8.47e-7 | 1.91e-6 | 1.75e-6 |

All were within the registered 0.0002-bb value/regret and 0.000002 average
increment tolerances. `check_history_units.py` independently checks the actual
f32 factors, coverage counts, tolerances and the counterexample below.

Scope limit: these tests use identical full-tree topology with unequal root
mass injected through a test-only device write to model reached-branch units.
They establish the scaling identity across descendants, not correctness of a
new subtree extractor, history-age conversion, global continuation or large
conditional solution. The public normalized-root admission checks still refuse
zero, nonfinite and unnormalized ranges. No CPU speed research was performed.

## Positive rescaling can change the implemented policy

Both native regret matching and average normalization fall back to uniform when
their positive/total history sum is <=1e-12. The counterexample starts with one
action carrying 1e-11 and the others zero, giving probability 1. Multiplication
by .001 reduces the sum to 1e-14; the resulting probability is 1/3. The test
confirmed this on the GPU for both current and average policies.

Therefore blindly multiplying compact histories by their full-game mass factors
cannot claim policy preservation. The original offline compact method already
declared ordinary global resume unsupported; this is not evidence of an
undisclosed production continuation bug.

Next test a research representation which leaves stored local histories intact
and carries explicit fixed unit factors for future full-game increments. That
avoids the immediate rescaling-induced policy change, but does not solve history
age/schedule compatibility or prove convergence. Full native global and all-27
conditional checks remain mandatory before deployment.
