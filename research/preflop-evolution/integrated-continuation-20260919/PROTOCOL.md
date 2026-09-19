# Connected continuation experiment

## Purpose

Replace the two fixed postflop leaves in the saved UTG/LJ conditional game
with live CFR continuations. Every represented private hand can change its
preflop action. Both players also adapt in both postflop branches. AA is not
locked or assigned a special floor.

## Engineering gate before poker conclusions

The first run is a small **river-panel game**, not a realistic preflop solution.
Preflop actions occur before the board is revealed, then a complete board is
revealed and the players can bet. This makes an inexpensive, fully specified
integration test. It omits flop/turn betting and restricts the public boards.
Its ranges must not be described as full-deck ranges or compared to Wizard.

Use KhQd9d2c7s and 8c7c4hJs2d, initially 500 iterations. All 1,326 private
combos are represented; entry weights come from the frozen conditional subtree.
The announcement of this two-board panel changes the private-card prior.
Define joint chance as uniform panel weight times the two entry weights times
physical card compatibility, with ONE normalization at the root. Never
renormalize arriving ranges separately at continuation leaves. Earlier folded
cards remain omitted and must be addressed before a realistic validation claim.

Root actions remain fold, call18, raise45, jam200. Facing raise45, LJ may fold,
call45 or jam200; UTG may fold/call that jam. Both called branches use 50% and
75% bets and pot raises, one raise per street, 85% all-in conversion. Preserve
pot39.5/stack182 and pot93.5/stack155, 4% rake capped at6, preflop no-flop-no-drop.
UTG is OOP. Postflop net values gain1.75bb to restore original investments.

## Checks

- External-root GPU sweeps must match CPU counterfactual values from identical
  starting arenas while reaches change; include a turn fixture with future
  card chance, rake and blockers. CPU is a correctness oracle only.
- Whole-game best responses must include continuation deviations, not merely
  preflop deviations against frozen continuation prices.
- Report both players' deviation gains; do not infer convergence from iterations.
- Verify full-game probability/rake accounting independently of best responses.
- Checkpoint at20,100,500; extend only after the connection passes checks.
- Keep all work offline; no live-server mutations, no saved-game writes.

Passing this gate supports expansion to turn/flop panels; it is not deployment
approval or evidence that the full poker accuracy problem has been solved.
