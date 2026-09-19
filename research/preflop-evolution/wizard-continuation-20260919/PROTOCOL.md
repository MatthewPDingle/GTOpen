# Fixed-range continuation audit

Registered before reference outcomes, 19 September 2026. Development diagnostic;
no model training, production changes, or reserved Wizard cases.

Use the saved 1000-iteration Wizard-baseline game. Follow UTG raise6, LJ raise18,
all intervening folds, UTG call. Compare Balanced against explicit heads-up
postflop solutions using the same exported weights, pot, remaining stacks and
4% rake capped at 6 original bb. UTG is OOP. Preserve source saves and hashes.

Normalize each range by its maximum weight; discard weights below 0.005 only
if the removed combination mass is below 0.5%. Add OOP diagnostic hands at a
minimum weight of 0.001: AA, A5s, KQo, QJs, 99, 88, 55, 76s. Report removed and
added mass and compare the original versus altered Balanced prices. These are
explicit small range perturbations, not the untouched original ranges.

Freeze 40 canonical flops, eight per pairedness/suit stratum, using seeded hash
ordering. Use each board with separate 50% and 75% pot bet menus; both players
may lead, one 100%-pot raise per street, no extra jam button, normal stack caps
and 85% jam conversion. Enumerate turn and river within those restricted trees.
This is not Wizard's postflop abstraction. Run the first four boards per stratum
before the remaining four, but do not select boards based on results.

Reference target: both GPU and transported full-enumeration CPU exploitability
at most 0.05% pot, maximum 2000 iterations per job. Record both players' per-hand
best-response gains; an OOP probe above 0.05bb is flagged as underresolved even
if the global target passes. Best-response gain is a diagnostic, not a rigorous
bound on value error. Do not discard failed jobs or claim a complete estimate
from partial results. Later precision refinements require separate manifests.

Primary estimator: ratio of summed hand values weighted by compatible pair
mass, suit multiplicity and inverse board inclusion probability. Show a
secondary equity-control estimate, using the existing Monte Carlo preflop
equity cache with compatible-card weighting; it is not an exact control mean.
Use 5000 board bootstraps within strata, paired across menus. Intervals describe
board sampling conditional on ranges and menus, not all modeling uncertainty.
Report future rake separately: unlike Balanced, explicit solves can charge
rake on matched future betting. Check means conserve the pot net expected rake.

Check the user's preflop, postflop and report status before each offline GPU
job; defer if busy. Never mutate port 56708. Preserve all checkpoints and report
honest partial progress if the user returns. Keep Jev deferred.
