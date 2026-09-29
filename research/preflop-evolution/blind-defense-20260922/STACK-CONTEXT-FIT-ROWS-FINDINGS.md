# Context-bound training rows: five CPU integration tests passed

`stack_context_fit_rows_v1.py` now prepares weighted training observations
for both the 362-input control and 387-input candidate. Each observation
retains its exact game identity, public betting history, acting player,
private cards, legal action menu and native public prices.

Identical numeric observation keys in different games remain separate.
Targets use advantage in bb divided by starting stack. Each context's loss
is normalized by its own source-weighted legal-action count before applying
explicit mixture weights. Thus deeper pots and differing retained sample
counts cannot silently determine a game's influence on the fit. The bridge
preserves the existing weighted visit reservoir; it does not resample it.

Five CPU tests passed in 2.912 seconds (3.427 seconds command wall time):

- Native-input equality across both representations, both players, all four
  streets and all five fitting depths.
- Grouped objective plus retained within-observation variance equals an
  independently computed weighted sum over individual visits.
- Duplicating one context's entire retained sample leaves its contribution
  and grouped targets unchanged.
- Wrong actors, context sets, keys, action menus, illegal targets and invalid
  mixture weights are rejected.
- The 60/150bb held-out contexts cannot enter fitting.

Targets in these tests are synthetic. Native observation fixtures are reused
for feature correctness, not as new poker evidence. The fit encoder does not
invent missing own-action history: reservoirs did not retain ancestor query
indices, so played-policy reach evaluation remains a distinct interface.

Remaining work: integrate the objective with the CUDA fitter, preserve a
complete cycle of all contexts in restartable checkpoints, connect the
native training/evaluation workers, and qualify one real complete cycle.
Only then register a matched learning comparison. This bridge alone neither
trains a strategy nor improves the live preflop model.
