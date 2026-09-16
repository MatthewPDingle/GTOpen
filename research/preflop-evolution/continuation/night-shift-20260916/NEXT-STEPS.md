# Next investigation: separate the predictor from the search interface

This is a proposed follow-up, not a completed experiment or a new deadline.
N35 failed its practical screen, N37 found larger deep-range differences, and
the unchanged N38 extension still missed its stopping target. These outcomes
support this controlled investigation before another large training run.

The strongest result so far is that the full predictor estimates continuation
hand values better on fresh boards, including wider flop menus. It still fails
the practical settling screen. More training examples, several smoothing
penalties, fixed pairwise values and the zero-own-range fallback have not
resolved both requirements. Charts looking stable is not sufficient evidence.

## First, establish a small end-to-end control

Build a deliberately small two-player game whose full tree can be solved and
whose continuation can also be queried independently. Specify the cards, exact
legal chance probabilities, action menu, stacks and payoff rules before solving.
Use explicit legal card combinations and zero rake initially. Keep precisely
the same game for both routes; a restricted-board or restricted-action game is
an integration test, not a full Hold'em or GTO Wizard benchmark.

Compare the full-tree solution with a preflop-only tree supplied continuation
values by a fresh direct solve of that same continuation game. At this stage,
do not substitute N15: its training game differs from the miniature game. This
tests whether the search interface behaves properly even when it receives very
accurate values. Independently compute best responses in the complete small
game, including actions below the cutoff, rather than relying only on the
current frozen-value gap. Report both metrics, strategy differences and elapsed
time to fixed error targets.

If the direct-continuation route itself fails to approach the full-tree result,
investigate its range conditioning, off-path values, averaging and update order
before changing the learned predictor. Preserve the full-tree control and do
not tune against its test results. If it behaves well, introduce a surrogate
trained for that exact small game with whole-context holdouts; this separates
approximation error from interface behavior. A fresh held-out comparison must
then test whether the surrogate changes actual full-game best-response error.

## Then return to the real preflop workload

Any resulting change needs new held-out range contexts and fresh boards, plus
the existing hand-group and physical-accounting checks. N21's wider-menu result
does not validate untested stacks, rake settings, multiplayer dealing or every
hand group. Preserve the original independent accuracy gates; no claim that
more mixed or wider charts are inherently more accurate.

Run matched repeated GPU timings and cold-start time to the same practical
target on several representative trees. Include setup, inference, memory,
iterations and total time. The N20 short per-iteration overhead passed, yet
N19's longer continuation took more time and did not reach its target. A single
warm-start blend comparison cannot replace this check.

Only a candidate that clears both fresh accuracy and practical performance
checks should become a separate app preview. Never load these research saves
into the current app: their stored Balanced metadata does not describe their
experimental continuation semantics. Production stays on its existing model
until an independently validated replacement is ready.
