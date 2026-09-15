# GTOpen / GTO Wizard: five-hand action comparison

Measured 15 September 2026. GTOpen MP corresponds to Wizard LJ, facing the
first player's raise to 6 original bb in an eight-seat, 200bb straddle game.

## Findings

The disagreement is about which actions are valuable, not a restriction that
prevents GTOpen mixing. It is also not uniformly excessive tightness. GTOpen
continues more with 99 and 88, but less with A5s and 55. For QJs its total
continuing frequency is similar, but calls are almost entirely replaced by raises.

### Frequencies

Percentages, ordered fold / call / raise to 18. Jams are negligible in GTOpen
and displayed as zero in Wizard. Wizard frequencies are the displayed combo
readouts; equivalent suits showed the same values.

| Hand | GTOpen fold / call / raise | Wizard fold / call / raise |
|---|---:|---:|
| 99 | 0.0 / 0.9 / 99.1 | 18.8 / 57.8 / 23.4 |
| 88 | 0.1 / 99.9 / 0.0 | 38.2 / 42.6 / 19.2 |
| 55 | 100.0 / 0.0 / 0.0 | 93.0 / 7.0 / 0.0 |
| A5s | 100.0 / 0.0 / 0.0 | 0.0 / 24.1 / 75.9 |
| QJs | 62.9 / 0.0 / 37.1 | 63.9 / 24.3 / 11.8 |

Whole range: GTOpen 93.7144% fold, 2.4703% call, 3.8153% raise;
Wizard displays 92.1%, 3.3%, 4.6%. The fold difference is **1.61 percentage
points**, masking larger hand-level changes.

### Action EVs

Original bb relative to folding at this decision (fold = 0). GTOpen numbers
evaluate taking one action and then following saved average policies. Wizard
values were read in its EV view and round to two decimals: 0.00 does not imply
exact mathematical equality.

| Hand | GTOpen call | Wizard call | GTOpen raise18 | Wizard raise18 |
|---|---:|---:|---:|---:|
| 99 | +0.6960 | 0.00 | +0.8206 | 0.00 |
| 88 | +0.2897 | 0.00 | +0.1916 | 0.00 |
| 55 | -0.9199 | 0.00 | -1.9274 | -0.35 |
| A5s | -0.8306 | +0.04 | -0.2869 | +0.05 |
| QJs | -0.6881 | 0.00 | +0.000027 | 0.00 |

Control: GTOpen TT calls 47.21%, raises 52.79%. Its EVs are +1.7321 and
+1.7287bb, only 0.0034bb apart. Mixing exists when GTOpen values actions similarly.

For several hands, GTOpen's chosen action is also an action Wizard mixes.
That means a striking chart difference need not imply a large immediate
deviation loss against Wizard's opponents. A5s is the clearer exception:
Wizard always continues but the displayed advantage over folding is still only
0.04-0.05bb. These observations do not establish full-strategy exploitability.

### Check for poorly learned later decisions

An unused branch can have a poor saved continuation. A second read-only
evaluation optimizes all of MP's later preflop decisions, keeping every
opponent's saved policy fixed. This is a best response inside GTOpen's existing
terminal approximation, not a new postflop solve.

| Hand | Call with own later best response | Raise18 with own later best response |
|---|---:|---:|
| 99 | +0.7538 | +0.8221 |
| 88 | +0.2927 | +0.2226 |
| 55 | -0.5970 | -1.6279 |
| A5s | -0.5327 | -0.2848 |
| QJs | -0.5173 | +0.0005 |

Improving MP's later decisions reduces some losses but does not reverse the
key disagreements. More iterations to refine these same later choices alone
cannot make these calls profitable against the saved opponents in this model.
This does not rule out changes if all opponents are solved further together.

## What is and is not controlled

- GTOpen: saved iteration 550, total approximate BR gap 0.0044507bb/hand,
  Balanced realization, coupled_deck_v1 multiway approximation, no rake,
  eight seats, 200 original bb, 2bb UTG straddle, no limps, all seats Solver.
- Wizard: Cash / Straddle cEV / With cold calls 6bb, depth 200. Its first
  acting UTG corresponds to GTOpen UTG1; Wizard LJ corresponds to GTOpen MP.
- Current-node menus match: fold, call6, raise18, jam200. Position-dependent
  later raise sizes exist in GTOpen; every later Wizard branch was not audited.
- One remaining mismatch: SB is 0.4bb in GTOpen and 0.5bb in Wizard. Thus
  current pot is 9.4 versus 9.5bb. This should be corrected for controlled runs.
- Each engine's EVs are against its own upstream and downstream opponent
  strategies. These are **not** same-policy EV residuals. Differences cannot
  be attributed numerically to only one part of GTOpen's continuation model.
- Balanced conserves the modeled pot but uses hand-class realization priors;
  it does not solve future postflop bets. Multiway values also remain approximate.
  This makes continuation pricing a strong next investigation, not a proven
  sole cause established by this comparison.

## Recommended next experiment

First match the SB and audit the later size menus. Then hold incoming ranges
fixed for selected heads-up call and 3-bet continuations and compare Balanced
values with a weighted sample of actual GTOpen postflop solves. Separate
heads-up and multiway branches so errors do not get conflated. Measure errors
for pairs, suited aces and suited broadways before changing the value model.
Do not add cosmetic randomization or tune toward Wizard's aggregate fold rate.

## Reproduction and provenance

Wizard source (authenticated UI, manually read five hands):
[200bb straddle, raise6, LJ response](https://app.gtowizard.com/solutions?soltab=strategy&solution_type=gwiz&gmfs_solution_tab=ai_sols&gametype=SingleStraddleNoAnteGeneral_8mcEVR6&depth=200&gmff_depth=200&gmff_type=general&gmff_rake=cEV&gmff_opening_size=6bb&history_spot=1&preflop_actions=R6).
The five frequency and EV readouts above are transcribed from that UI.

GTOpen source: `saves/preflop/action-ev-comparison-20260915.gtop`, saved from
the idle live game on 56708. Full configuration and selected-hand output are
in `gtopen-readout.json`. Save and full temporary outputs remain local.

```powershell
cargo run --release -p solver --example preflop_action_evs -- saves/preflop/action-ev-comparison-20260915.gtop target/action-ev-comparison/gtopen.json 1
cargo run --release -p solver --example preflop_action_evs -- saves/preflop/action-ev-comparison-20260915.gtop target/action-ev-comparison/gtopen-br.json 1 br
```

The example loads a separate saved copy, evaluates without solving, and
asserts the strategy/regret arenas are unchanged. Evaluations took about six
seconds each on CPU. A closed-form heads-up regression checks EV units,
conditioning, fold offsets, both modes and arena immutability. No live model
or deployment was changed for this comparison.

Validation: full `cargo test --release -p solver` passed, including the new
diagnostic regression. GPU equivalence suites passed all 6 postflop and 15
preflop tests. The first GPU launch lacked the local NVRTC directory on PATH;
after adding `.cuda-nvrtc/nvidia/cuda_nvrtc/bin`, the suites passed.
