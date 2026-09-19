# Reserved-board transfer evaluation

Registered before producing any connected strategy result on the ten boards
in `integrated-coverage-20260919/reserved.json`, and before the 47-board
strategy run. Do not change those board identities, their weights, or the
entry-game configuration in response to strategic outcomes.

## Question

Does a preflop strategy learned with broader flop coverage remain useful on
flops excluded from that solve? A small numerical gap on the training panel
alone cannot answer this. Nor can prettier ranges or agreement with Wizard.

## Evaluation design

Freeze each source strategy before reading holdout action values: the already
completed ten-board AB policy and the eventual 47-board policy. Preserve the
source result hashes and exact iteration checkpoints. Use the same 50% bet /
pot raise menu, stacks, rake, entry support and all-suit averaging throughout.

For each source policy, keep EVERY preflop information-set strategy fixed,
not merely the root action percentages. Solve only the connected postflop
continuations on the unchanged reserved panel, using the private-hand reaches
induced by that source's complete preflop policy. Never independently
renormalize those reaches or teach a player the hidden folded cards.

Distinguish two evaluations:

1. **Postflop residual:** hold both preflop policies fixed while allowing each
   player a best response at postflop decisions. This is the numerical
   convergence criterion for the continuation solve.
2. **Full deviation gain:** allow a player to change both preflop and postflop
   decisions against the opponent's fixed evaluated strategy. This measures
   vulnerability of the transferred policy in this reserved finite game.
   It need not converge to zero because preflop is intentionally fixed.

Do not incorrectly stop based on full deviation gain or call a positive
transfer gap an implementation failure. Report each player's EV, both kinds
of gap, root frequencies under the holdout private-hand prior, and differences
between source policies. Source preflop arrays must remain bitwise unchanged.

Start with implementation controls on development boards: a river-only
constant-preflop game checked independently, then the old two-board game
using its own converged policy. The restricted postflop best-response value
must be no smaller than average value and no greater than unrestricted
best-response value (allow 1e-5 bb numerical tolerance). When every preflop
node has one positive-probability action, verify the restricted calculation
against a separately enumerated sum of reached continuation games.

Require the existing independent physical-pair frequency, terminal
probability and chip/rake conservation audits. Register iterations and a
postflop-residual threshold before the actual reserved solve after runtime
preflight; do not weaken that threshold upon observing holdout outcomes.

## Interpretation and limits

The reserved panel has only two boards per coarse stratum. It is a transfer
stress test, not a precise estimate of full-deck exploitability. Report that
sampling limitation even if transfer looks excellent. Neither a single low
gap nor a comparison favorable to the new policy authorizes deployment.
If the policy fails transfer, any subsequent tuning consumes these boards
as development data; draw and freeze a NEW independent evaluation panel
before claiming a new validation result. Do not repeatedly tune to this set.

Larger independent chance samples, bet-menu sensitivity, and the earlier
folded-card posterior remain distinct unresolved accuracy requirements.

## Additional validation sample, frozen before strategic evaluation

`VALIDATION95-PROTOCOL.md` adds a separate 95-board sample after a chance-only
coverage audit identified gaps in the original ten boards. Keep and report
both panels. The new sample excludes all training/development/original
reserved suit orbits and estimates the eligible complement, not the entire
flop population. Its board selection and weights are already frozen.

`STREAMED-TRANSFER-PROTOCOL.md` defines a faster implementation of this same
frozen-policy evaluation, contingent on deterministic and two-board parity
controls. Combine leaf CFVs across boards before any preflop maximization.

The postflop policies learned during evaluation are a constrained response
equilibrium for the frozen preflop policies. The full deviation gain is
against those particular evaluated continuations, including their off-path
choices; it is not an invariant score of a preflop range in isolation. Keep
this distinction when comparing source policies or interpreting transfer.
