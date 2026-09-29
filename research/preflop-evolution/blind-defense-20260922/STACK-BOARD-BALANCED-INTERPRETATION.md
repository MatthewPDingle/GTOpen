# Interpretation and recommended next step

29 September 2026. Read alongside STACK-BOARD-BALANCED-TERMINAL-FINDINGS.md.
The main comparison finished; complete independent numerical qualification
FAILED. All percentages below describe retained GPU measurements, not a fully
verified replacement model.

The structured board mixture did teach the difficult, deliberately rare board
set much better: its mean error fell 83.35%/80.62% versus random training across
the two seeds. But natural-frequency test error rose 0.51%/38.99%. This is useful
evidence of a tradeoff, not the accuracy improvement we were seeking.

The ordinary-board regression is visible in the saved hand-group breakdown.
Pair, high-card and two-pair hands worsen in both seeds; pairs and two-pair hands
account for most of the large second-seed increase. Trips improve in both seeds.
These are hand categories, not board strata. The full JSON retains the separate
board-cell breakdown, including unsupported cells. The measurements are
consistent with spending training capacity on rare structures at a cost to
common cases; they do not by themselves prove that mechanism.

Explicit relative-hand inputs still look useful: within random training they
reduce the main-test normalized loss 27.27%/41.01% versus 362 inputs on the SAME
fresh boards and seeds. This is a secondary observation, not a substitute for
the failed primary treatment. The richer inputs add parameters, so this is not
an equal-capacity attribution. In both seeds, validation slightly or materially
favored structured 387-input training while the fresh main test favored random 387-input.
Model selection/generalization uncertainty therefore remains.

The random 387-input baseline is close to the average-loss target in this finite test:
at 60/150bb, 0.06150/0.14549bb in the first seed and 0.06890/0.15943bb in the second.
The respective limits are 0.060/0.150bb. Neither seed clears both absolute limits.
Large tail errors remain. Means near a target do not establish safe or accurate
decisions for every holding, let alone a full preflop solution.

## Verification issue

The first preserved CPU comparison differs from CUDA by one classified error
on each of two boards: 994 versus 995 errors among 75,652 eligible rows, and 908 versus
907 among 75,670. The differences move in opposite directions. Each rate changes
by about 0.00001322, slightly above the fixed 0.00001 tolerance. All other metrics
in this failing context pass their numerical limits; its overall mean cash-loss
difference is 8.43e-8bb. That does not qualify uncompleted comparisons.

Small numerical changes around the 50% predicted-call boundary are a plausible
explanation, but the saved failure does not include exact holdings/raw scores
needed to prove it. The earlier plan explicitly said these boundary failures
must remain failures. It has not been weakened, and the scientific attempt and
CPU verifier have not been retried.

## Recommended next action, not launched

Keep random board sampling and relative-hand inputs as the research baseline.
Do not repeat the long balanced-board run unchanged.

Prepare a small, separately registered diagnostic of the preserved 40bb failure
using its exact frozen checkpoint, cards, prices and CPU/GPU arithmetic paths.
It should record every disagreement's raw scores, call probability, hand/board
identity, reference call advantage and cash-loss change. Preserve the original
evaluation batch geometry: changing batch shape while diagnosing floating-point
differences could hide the cause. It can reuse retained labels and needs no new
training, optimizer changes or fresh scientific accuracy claim. Bound it before
launch and retain any mismatch/failure. This is a proposed explanatory
diagnostic, not a retry that could turn the original result into a pass.

Use that evidence to design any future numerical contract on separate controls,
then select a new accuracy hypothesis from the retained common-hand/tail errors.
Keep a fresh evaluation set for any later changed learning recipe. Do not tune
against this final test or confuse the rare-board gain with population accuracy.

The eventual preflop goal still needs realistic action-conditioned opponent
ranges and multiple betting decisions. This study isolates only terminal river
Fold/Call against a uniform legal opponent. No production change, GitHub push,
deployment, new scientific experiment or broad-goal completion is made here.
