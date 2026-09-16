# N26: separate own-range value drift from opponent response

Read-only diagnostic, not fitting or a deployment gate. Use the unchanged N15
predictor and 24 original training contexts, with no reference labels or test
outcomes. Reuse the established legal-pair context builder and compare candidate,
linear base, Balanced and raw-equity values.

For each player, mix their normalized range toward premium pairs, offsuit
broadways or suited connectors by 0.001, 0.0001 and 0.00001. Hold the other
player's range fixed. Record both players' signed and absolute value changes,
weighted by the original compatible hand mass, per unit of actual range TV.
The signed own-player component measures whether the same original hand mix
receives a systematic value shift when only its own input distribution changes.
Different step sizes distinguish a persistent local response from finite-step
effects. All 432 prescribed changes are retained; no favorable subset selection.

Own-range dependence can be legitimate in postflop games. This diagnostic does
not establish exact value error, exploitability, a convergence theorem, or the
cause of N19's gap. In particular, predicted game values can be nonsmooth and
the original distributions include zero-weight hands. The fixed pairwise/raw
controls should have no own-range hand-value dependence; that provides an
arithmetic check, not a theory-based acceptance threshold for the neural model.

Freeze this protocol, helper and all model/context inputs before evaluation.
Run only after N24 isolated timing ends. N21 reference generation may coexist
with this bounded single-BLAS-thread diagnostic. Stop before the night-shift
deadline. No change to model weights, production files or existing gates.
