# Shallow correction: useful component, failed overall feedback screen

The frozen correction works inside the native GPU solver and improves the
tested shallow postflop values after the preflop ranges change. It does **not**
yet demonstrate a dependable improvement in the earlier call-versus-3-bet
decision. Keep it research-only. Production on port 56708 was unchanged.

## What passed

- Python, native CPU probe and CUDA agreed on 126 numerical fixtures. The
  complete-tree tests, including eleven stack-boundary fixtures, also passed.
- Disabled, sparse and multiway guard cases retained baseline behavior.
- Both fresh 40bb heads-up preflop runs passed the predeclared strategy-stability
  screen between 1,500 and 3,000 iterations.
- All 150 fresh postflop solves passed both CPU and GPU accuracy checks.
- At the called-4-bet leaf, equity-adjusted hand-value error fell from 4.280bb
  to 2.622bb (38.7%). Direct error fell from 5.711bb to 4.218bb (26.1%).
  The paired 95% intervals for the reductions were positive: 1.443–1.718bb
  adjusted and 1.248–1.708bb direct. Absolute error remains material.

These compare models on the same new reaching ranges. They are not measurements
of the full-game value gained by replacing one preflop policy with another.

## What failed

The earlier BB call-versus-3-bet comparison was inconclusive:

| Reference estimator | Previous model error | Shallow correction error | Change |
|---|---:|---:|---:|
| Direct | 0.2140bb | 0.2199bb | 2.7% worse |
| Equity adjusted | 0.2133bb | 0.2053bb | 3.8% better |

The paired 95% intervals for error reduction both include zero:
[-0.0120, +0.0067]bb direct and [-0.0046, +0.0108]bb adjusted.
Only 41 classes, representing 25.8% of decision pair mass, qualified for this
comparison; 128 classes lacked support for both actions. Call-versus-fold
values were unchanged, as expected from the correction's scope.

The predeclared screen required nonregression in both estimators. The direct
call-versus-3-bet check failed. The threshold and sample were not changed after
seeing this result. A small, uncertain regression is neither proof that the
model is harmful nor sufficient evidence to deploy it.

## What changed in the ranges

The correction removed the old near-100% calls with A3o and A4o when facing a
4-bet in this fixture. This is a useful behavioral change, but the new ranges
almost never bring those hands to that postflop leaf. Their individual fresh
postflop references are unsettled, so their new value estimates are not validated.

At the earlier BB decision, total calling barely changed (40.50% to 40.40%).
Individual hands changed more than that aggregate suggests. The SB also shifted
from raising toward limping. None of these movements alone establishes better
real-poker ranges or agreement with GTO Wizard.

## Why the improvement did not carry back cleanly

The separate, post-evaluation branch diagnostic reconstructs the action error
to numerical precision. On qualified hands, the equity-adjusted mean absolute
contributions to call-versus-3-bet error were:

| Postflop branch | Absolute contribution |
|---|---:|
| Called open | 0.198bb |
| Called 3-bet | 0.302bb |
| Called 4-bet | 0.035bb |

These are **not additive percentages**. Their signs partly cancel, leaving a
total error of 0.205bb. Replacing a single branch with its sampled reference can
even increase the error of the difference between actions. This is descriptive
evidence of cancellation in this sample, not a new validated training method.

The next experiment should address the connected continuation values together
and measure their relative action values. Optimizing only one leaf's absolute
error is an incomplete objective.

## Performance and scope

Three paired timings measured a 14.2% per-iteration slowdown in the 40-node
heads-up fixture (1.874s versus 2.141s for 1,000 measured iterations). Setup was
excluded. This does not predict the slowdown of a large multiway game, nor
compare time to a validated full-game solution.

Only the 40bb heads-up game and one shallow SPR were tested with fresh labels.
Other stacks, rake, limped branches, multiway games and richer postflop menus
remain outside this accuracy evidence. Numerical boundary checks do not fill
those gaps. The correction below SPR 0.2 and its blend between 0.75 and 1 remain
modeling assumptions. No production defaults or server code were changed.

## Next research step

1. Keep this frozen candidate as a research comparison. Preserve this evaluation
   set as a completed test; if its labels inform training, use new range contexts
   and boards for the next independent test.
2. Build a small paired-context study spanning called opens, called 3-bets and
   called 4-bets. Include baseline, corrected and independently perturbed range
   families, so evaluation is not limited to one policy's surviving hands.
3. Fit a conservative correction to those connected contexts. Track both
   absolute leaf-value error and the backed-up call-versus-raise difference,
   preserving pot conservation and excluding unsettled references. Select on
   separate validation contexts, then freeze before the new test.
4. Re-solve only after the frozen model passes that test, and repeat fresh-range
   feedback. Optimize the GPU cost without changing predictions before any
   deployment proposal. Do not add samples merely to reverse today's failed gate.

See REPORT.md, evaluation.json and branch-diagnostic.json for complete numbers.
