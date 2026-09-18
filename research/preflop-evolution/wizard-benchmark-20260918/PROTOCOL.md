# External preflop benchmark, version 1

Use a small set of GTO Wizard decisions to test useful preflop accuracy before
starting another continuation-model experiment. This is a diagnostic reference,
not training data, an exact full-game specification, or proof of equilibrium.

## Split frozen before the next experiment

- Development: eight-seat, 200 original-bb stacks, 2bb UTG straddle;
  rake-free and NL25 (4%, cap 6bb) configurations. Existing September 15
  comparisons belong here too: they are already exposed development evidence.
- Reserved: 100bb version of the straddle game, at unopened BTN, BB facing
  UTG's open, and UTG responding to an in-position 3-bet. Do not inspect these
  answers until a candidate and its acceptance rule are frozen. These cases
  are reserved, not yet collected or verified available in the subscription.

## Record before comparing

Record stack in original bb, all forced posts and antes, rake and cap, no-flop
no-drop convention, position order, action history, legal raise-to amounts,
incoming range/reach, displayed action probabilities, and per-action EVs.
Wizard UTG/LJ correspond to GTOpen UTG1/MP when GTOpen labels the straddler UTG.
SB is 0.5bb, BB 1bb, straddle 2bb. Do not confuse a 200bb stack with 200 straddles.

The inspected 6bb-open tree uses 18bb IP, 24bb SB, 27bb BB and 30bb STR 3-bets.
Later raises and postflop abstractions still require auditing. Matching these
first actions alone does not establish an identical tree.

## Measures

1. Primary diagnostic: local action regret, max(Wizard action EV) minus the
   candidate's probability-weighted Wizard action EV for the same hand/node.
   This evaluates a single decision against Wizard's continuation; it is not
   the candidate strategy's exploitability or its own expected return.
2. Also report hand-level action-frequency differences and aggregate continue
   rates. Do not optimize visual mixing for its own sake.
3. Report elapsed solve time, hardware and convergence information separately.
4. Wizard EVs are displayed to 0.01bb. Treat a computed regret as uncertain by
   at least 0.01bb from rounding alone, in addition to unknown solve error.
   A displayed zero is not evidence of exact indifference.
5. Keep per-hand results and coverage. Eight selected probes are not a
   representative average of all dealt hands. Never fill missing EVs with zero.

All captures use rendered browser UI, including the widths of the displayed
per-combo action bars. Validate combo identity, sum of frequencies and suit
symmetry. Preserve provenance URLs and capture date. No hidden application API
or internal solver data is used.

## Current comparison gate

The live game on port 56708 is a different configuration (SB 0.4, rake 5% capped
at 4.1bb and uniform 3-bet multipliers). Do not score it against the current
NL25 Wizard reference as though the settings matched. Keep that session intact.
No model promotion or deployment is authorized by a favorable probe score.
