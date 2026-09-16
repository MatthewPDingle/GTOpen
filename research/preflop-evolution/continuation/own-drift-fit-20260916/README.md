# N30: penalize own-range mean drift, preserving range support

N22 penalized all hand-value changes, including legitimate responses to changed
opponent ranges. This separate training-only experiment targets a narrower
quantity: the original hand-mass-weighted mean value shift of the player whose
own range changed. It is a modeling regularizer, not a proven poker constraint
or guarantee of equilibrium consistency.

Use only the original26 training/development contexts and four whole-family
folds. Mix each player's range toward its own premium pairs, offsuit broadways
or suited connectors by0.001, retaining original relative weights inside the
target group. Never introduce a previously absent hand. Skip a group with zero
or complete original mass. Keep every nontrivial prescribed direction.

For each direction compute the standardized, pot-centered feature change,
averaged using the original affected player's compatible hand mass, divided by
actual range TV. Add its squared linear-predictor response to the fitting
objective. Average directions equally inside each case, then cases equally.
Refit the same two8-unit neural corrections with unchanged N15 settings and
0.75 shrink. No additional inference operations or larger network are introduced.

Reuse N22's frozen fitting/control/gate machinery with explicitly replaced
variant, penalty and response functions. Fixed strengths0,0.0001,0.001,0.01.
The zero-strength control must reproduce every N15 held-family error within1e-9.
Eligibility remains >=5% better than original linear control, mean and every
family within5% of N15, mean targeted response at most75% of control, and no
family targeted response worse. No threshold rounding, expansion or relaxation.

All N15/N20/N21 evaluation labels are excluded. Freeze helper, this protocol,
N22 dependency, input manifests, model controls and caches before fitting.
Two numerical checks validate support preservation and signed-response
cancellation. Use two CPU threads and one BLAS thread; no fitting during GPU
timing. N21 reference generation may continue. Require at least20minutes before
the fixed20:49:02UTC deadline. Passing this training screen would only nominate a
candidate; fresh value validation, GPU parity, timing and settling remain required.
No changes to production or any earlier frozen experiment.
