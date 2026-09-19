# Why a rebuilt continuation can change earlier incentives

This exact mathematical control isolates a possible mechanism. It is not a
model of poker and does not diagnose the measured GTOpen transfer discrepancy.
No empirical protocol, numerical gate or production code changes.

A player privately receives A or B, each with probability one half. They can
fold for zero or enter. After entry, the opponent chooses X or Y without seeing
the private type. With A, either choice pays zero. With B, X pays the entering
player +1 and Y pays -1. The opponent receives the opposite payoff.

Start with A entering and B folding, while the opponent chooses Y. Nobody can
improve by deviating, so the full game is at equilibrium. Now freeze that
entering range and solve only what happens after entry. The opponent only
encounters A, so X and Y both give zero. Replacing Y with X is therefore a
perfectly converged local solution. But B now wants to enter, gaining +1 when
it occurs: a full-game deviation gain of 0.5 before the private type is dealt.

| Entering probability for B | Original full gap | Rebuilt conditional post gap | Rebuilt full gap |
|---|---:|---:|---:|
| 0 | 0 | 0 | 0.5 |
| 0.000001 | 0.0000005 | 0.000001999998 | 0.5000005 |

The second case uses tiny positive entry instead of zero. Its rebuilt
continuation is only approximately optimal, with the small residual shown;
do not call it an exact local equilibrium. Small positive probabilities and
small conditional residuals still do not bound the earlier deviation tightly.
Both players' best responses respect the opponent's inability to observe A/B.

The reproduction enumerates pure best responses using exact fractions. Its
first development assertion omitted the opponent's additional epsilon/2
contribution to the full-gap expression; exhaustive evaluation exposed that
arithmetic mistake. The corrected full-gap formula is (1 + epsilon)/2, and
both exact cases now pass. This was a development correction to the toy's
expected value, not a changed poker experiment or acceptance threshold.

Implication: first measure reconstruction on the original poker training
boards. If it changes the combined game materially, preserve or constrain
continuation values, or continue joint training, before crediting every
transfer difference to flop coverage. This example proves possibility only;
the upcoming matched-panel results must supply the actual diagnosis.

Evidence: reconstruction-toy-control.json. Reproduction:
tools/research/reconstruction_toy_control.py. See RESOLVING-INTERPRETATION.md
for related primary research and the limits of zero-sum guarantees for our
raked poker experiment.
