# Behavioral support improves conditional coverage; transition still required

The fixed-epsilon diagnostic admits further transition design. It does not
qualify a speedup or deployment. All three runs completed the registered 1000
iterations; inputs, output hashes and saved-file audits independently verify.
The live app on 56708 is unchanged.

## Results on the same six-player fixture

All cases use 1024 particles, seed 42, native counterfactual units, gamma15
averaging and the same 23,038-node fresh game. Diagnostics run every 50
iterations. Times include preparation, learning, diagnostics, serialization
and fresh saved-state evaluation, excluding compilation and the separate
per-hand saved audit.

| Total uniform mixture | Seconds | Unrestricted gap (bb) | Constrained gap (bb) | Conditional checks |
| --- | ---: | ---: | ---: | ---: |
| 0% (native control) | 67.580 | 0.00094021 | 0.00094021 | 2/6 |
| 1% | 93.692 | 0.07096132 | 0.00071248 | 4/6 |
| 5% | 93.215 | 1.01375947 | 0.00029900 | 6/6 |

Epsilon is the total uniform mixture across legal actions, not a per-action
floor. It applies to every learning node, including offered all-ins. The
positive-epsilon strategies therefore still contain costly forced actions.
Their small constrained gaps are not acceptable substitutes for unrestricted
accuracy. The 5% candidate passes all six conditional checks at both 950 and
1000 iterations, but fails the unrestricted gap target by a wide margin.

Both candidates satisfy the predeclared transition-design admission: more
conditional passes than the matched control and constrained gap <= 0.005 bb
at the fixed final checkpoint. This is evidence that consistent behavioral
support can improve the selected rare branches on this fixture. It does not
establish robustness across seeds, the large game, or an unrestricted finish.

## Numerical and regression evidence

- The independent host recursion enumerates virtual-action transition matrices,
  rather than repeating the GPU's algebraic shortcut. It compares 798,525 regret
  entries, all 169 hand classes, epsilon 0.01/0.05/0.2, repeated actions by the
  traverser, zero native support, forced nodes, frozen seats, actual own-reach
  averaging, root values and the constrained best response.
- Eager/captured learning is exactly equal over five iterations with 64 samples,
  for raw and calibrated continuation. Calibrated fixtures actually load the fit
  and contain 129 calibrated leaves. Epsilon-zero arenas and native full gaps
  exactly match the disabled implementation.
- Canonical evaluation is read-only and exactly matches a fresh native engine
  on the learned state. The constrained diagnostic does not apply epsilon twice
  to the saved average behavior. Frozen seats contribute zero constrained gap.
- Admission rejects invalid epsilon, incompatible modes and already active or
  evaluated engines. Cancellation before the first sweep preserves all arenas
  and iteration. No epsilon-changing API exists in this implementation.
- Three targeted tests pass (96.860 seconds including compilation, 4.88-second
  body); native GPU equivalence passes 6 postflop and 13 preflop tests (67.437
  seconds); the default release solver suite passes (135.860 seconds).
  Example build passes in 63.406 seconds. Library source hashes are unchanged
  between numerical validation and all learning runs.

`check_behavioral_fixed.py` independently verifies fixed checkpoints, both gap
aggregates, every conditional gate, source identity, saved audits and admission.
`raw/behavioral-fixed-verified.json` retains the full compact trajectory.

Next: test an explicitly labelled warm-start transition to native learning,
including a matched control for any average reset. Count the complete initial
and finishing work, and retain the original unrestricted global/per-hand gates.
