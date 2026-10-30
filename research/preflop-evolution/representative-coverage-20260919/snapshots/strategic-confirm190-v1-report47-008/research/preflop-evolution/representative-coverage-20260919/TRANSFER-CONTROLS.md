# Transfer-evaluator controls

Use only the existing development river `KhQd9d2c7s`, closed under all suits,
with the same entry ranges, investments, rake and 50% bet menu. Run four
synthetic deterministic preflop profiles for 100 postflop iterations each:
root always folds, calls, 4-bets, or jams; every later preflop node always
calls. These profiles are code-validation controls, not player models.

Required checks at every recorded checkpoint:

- Imported preflop probabilities remain bitwise unchanged at every node.
- Independent physical-pair normalizer, frequencies and hand summaries match.
- Terminal probability within 1e-5 of one; chip/rake conservation within
  1e-4 bb; nonnegative unrestricted and postflop gains within 1e-5 bb tolerance.
- Restricted postflop BR lies between average and unrestricted BR, and its
  gain matches an independently forward-propagated sum of reached
  continuation gains within 1e-5 bb.
- Always-fold has EVs exactly -6 and 9.5 bb within 1e-5, zero expected rake
  and zero postflop gain. Always-jam/call pays 6 bb rake and has zero postflop
  gain. Calling/4-betting exercises both postflop pot branches.

Then freeze the completed old-two-orbits 2,000-iteration policy and train
only its postflop continuations on that SAME two-board development panel
for 2,000 iterations. Require postflop residual below 0.01 bb, the same
independent accounting checks, and exact policy preservation. Report its
full preflop-plus-postflop deviation separately; do not use that as the
continuation convergence criterion.

These controls precede any reserved-board strategy evaluation. They do not
give permission to select/tune a strategy using the reserved results.
