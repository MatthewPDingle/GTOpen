# Integrated preflop and postflop continuation

This study connects preflop decisions to actual adapting postflop play in
both the call and smaller 4-bet branches. Neither AA nor another retained hand
has a prescribed preflop action. The opponent's preflop responses adapt too.

**Research only. Nothing is deployed on 56708.** Earlier entry policies are
fixed. These are limited-board development games, not full-deck preflop
solutions or a GTO Wizard accuracy comparison.

## What changed

The previous 400-solve study changed AA's calling frequency while other
preflop rows were held fixed. Here one connected CFR process updates the
whole conditional preflop subtree and both postflop continuations. Values
come from the same iteration's changing ranges; there is no separately
fitted continuation-price correction.

The new research-only CPU/GPU interface accepts external root reaches and
returns counterfactual values. Root ranges are not normalized separately at
each leaf. A separate whole-game best response includes deviations on all
streets, so the reported gap is not restricted to preflop decisions.

## Validation

- 240 changing-range GPU sweeps matched the CPU reference from identical
  starting policies: maximum normalized value error 0.000012590468 bb.
  The test includes future-card chance, rake and blockers.
- All 6 existing postflop GPU tests and 15 preflop GPU tests passed.
- An additional 200-sweep test verified changing own-range weights, including
  zero arrival, against CPU strategy accumulation; maximum root-policy
  difference was 5.96e-8. Both new bridge tests passed.
- Independent Python enumeration covers all 1,326×1,326 private-combo pairs
  and reproduces the root chance normalizer, hand-class masses and action
  frequencies. Maximum observed root-frequency error is below 4e-9.
- An independent scalar traversal checks terminal probability and expected
  rake. Net player utilities plus rake equal the 3.5 bb dead money; observed
  errors are below 2e-7 bb in the completed engineering fixtures.
- Fresh extended runs reproduce their shorter runs' matching checkpoints.

At 2,000 iterations the river-panel test reached 0.00166237 bb combined
deviation gain; the turn-panel test reached 0.00321878 bb. See
[verification.json](verification.json) for final results of every run and
[convergence.png](convergence.png) for the comparison. These gaps measure
the stated small games, not accuracy against real poker or Wizard.

## Full-flop expansion

All-combo two-flop continuations need 25.68 GB in regret/strategy arrays alone,
before traversal buffers. The separate supported-range executable drops
only negligible **entry** weights below 1e-5 of each player's maximum.
It retains 322 UTG combos and 106 LJ combos before removing board collisions.
Removed entry probability is 0.0001620% / 0.0001285%. Arriving branches are
never trimmed and no probe hands are added.

The two full-flop fixtures are KhQd9d and 8c7c4h. They include every legal turn
and river and betting on all three streets. The four continuation allocations
total approximately 9.8 GB. Both called branches preserve the actual pot,
stack, positions, 4% rake and 6 bb cap. The menus offer 50%/75% bets and pot
raises, with one raise per street.

The 500-iteration full-flop run reached 0.0527029 bb combined deviation gain
in 82.4 s. At 2,000 iterations the gain fell to **0.00365808 bb**, in **258.8 s**.
AA mixed roughly **52.7% call / 47.3% smaller 4-bet**, with negligible jamming.
This is an engineering observation about the selected two-board game,
**not a recommended AA strategy**. The extended run reproduced all three
earlier checkpoints exactly. Its largest scalar conservation error was
1.82e-7 bb; expected rake was 1.21438 bb.

Independent joint-chance enumeration bounds the fixed-policy value effect
of entry trimming to about 0.00124 bb in the two-flop game. This does not
bound changes in equilibrium action probabilities. The limited board panel
has a much larger modeling effect: **16.63% total variation** between its
private-combo joint prior and the corresponding full-deck two-player prior.
This is a distribution distance, not an action-frequency error. Earlier
folded-card bunching remains absent. Neither limitation is fixed by solving
the two-board game to a smaller numerical gap.

## Next research gate

Expand the public-board sample without exceeding memory, and measure its
effect on both the private-card prior and action values. Preserve physical
card accounting, include folded-card sensitivity, and reserve independent
boards before making any accuracy claim. Do not deploy these two-board
ranges or tune the board selection to obtain preferred mixed strategies.

The original all-combo pilot and its freeze are preserved for replay. The
supported executable is a separately named derivation, frozen independently.
The JSON files contain checkpoints and complete preflop policies; postflop
arenas are not saved, so a repeat starts from the registered inputs.
