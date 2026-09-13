# Next focus: smaller conditional repairs of a globally accurate policy

The tested global regret-minimizer changes have not resolved rare-branch
accuracy. Revisit the original fast sampled policy as the anchor instead of
extending failed algorithm budgets.

The archived eight-player native baseline reached global gap 0.0045870 at
1050 iterations, with 5090.43 seconds complete time. The archived gamma15,
64-sample seed42 policy reached gap 0.0039928 at the same age, with 592.50
seconds complete time. The latter included 145.30 seconds of global checks.
These are historical measurements from their recorded executables, not current
equal-quality speed claims. Both still need the complete conditional coverage.
Sources: pass05/raw/eight-native-a-result.json and
pass06/raw/followup-eight-gamma15-s64-42-result.json.

Full subtree refinement changed substantially more strategy than an individual
bad response requires. Root-only repair also failed and should not be repeated.
A new diagnostic can instead keep the root and unrelated policies fixed and
apply small value-directed changes at selected non-root decisions. Evaluate
the entire parent game after each candidate, so local improvements cannot hide
a worsened global gap. Do not add locks, mark failed branches unreachable, or
change the relevant-hand/action-loss thresholds.

Before execution, register a bounded policy-change rule, candidate step sizes,
selection objective, time cap, and exact preservation tests. Selection should
use action-value improvement under a full-game accuracy constraint, not choose
whichever isolated hand happens to flip the acceptance flag. Recompute all 27
original branch checks; add independent topology-selected diagnostic paths to
detect damage outside repaired decisions. Research saves remain nonresumable
unless regret/average history semantics are separately defined and tested.

Only after both accuracy requirements pass should repeated whole-run timing
and a less costly check cadence be tested. A shorter check schedule is not a
speedup if it stops at a worse policy. This is a design direction, not an
executed experiment, a new acceptance gate, or a deployment recommendation.
