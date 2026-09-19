# What the coverage measurements imply for the next prototype

The current connected game remains a reference experiment, not a replacement
for the interactive Preflop Lab. A small numerical deviation gain certifies
only the announced board panel and betting menu. Increasing iteration count
does not add missing boards or folded-card information.

## First, validate a lossless memory saving

The ten-board plan needs 17.558 GB for the current GPU staging and full action
arenas, excluding CUDA context overhead. The existing future-card suit-orbit
planner estimates 12.209 GB when only reachable representative action blocks
are retained: a 30.5% reduction. These are allocation estimates, not measured
runtime or an already validated external-reach implementation.

There is a specific correctness condition. The general continuation bridge
currently disables future-card suit folding because arbitrary external ranges
can break suit symmetry. The new preflop orbit game has class-symmetric root
policies, so its arriving ranges preserve permutations that fix each flop.
A future restricted bridge can verify this property for both players on
every call, then use the corresponding compressed plan. It must reject or
fall back for asymmetric inputs, and must preserve any lock constraints.

Test the change against the current uncompressed executable with identical
external ranges and initial policies. Check counterfactual values, average
strategy accumulation, whole-game best responses and cashflow. Test a range
that deliberately violates symmetry to confirm the guard refuses it. Also
verify the GPU constructor actually uses compact arenas: an unrestricted
budget currently makes F32 storage prefer full arenas.

## Then, process more boards without changing the game silently

Compression alone does not make hundreds of full postflop trees fit. The
chance-only audit's typical joint hand-class prior distortion is about 4.2%
at ten boards and 1.0% at 160 boards. This does not establish the number needed
for strategy accuracy, but it rules out treating ten boards as comprehensive.

Private-card prior distortion is also an incomplete quality metric. The
ten-board panel gives 77 no flop-set opportunity and gives 99 one about 43%
of the time. Full-deck rates, conditional on the fixed opposing range, are
around 12%. The maximum error across pocket pairs is 31.4 percentage points.
The existing report subsets have much smaller maximum errors on this specific
check: 4.28 points for 47 flops, 2.90 for 95, and 3.24 for 184. More boards do
not guarantee monotonic improvement in every feature. The CLI output was
checked against the source's systematic sampling calculation and the frozen
canonical list. No postflop strategies for these subsets were solved here.

The next panel should cover every rank and check actual hand-making
opportunities against the full deck before expensive solving. The existing
47-flop subset is a reasonable feasibility starting point, subject to a new
protocol preserving independent validation cases. Passing pocket-pair and
private-prior checks would still not prove that all continuation values are
accurate; draws, broadway connectivity and interactions with both ranges also
matter. The current prescribed ten-board run remains intact for comparison.

A larger reference implementation should investigate transferring groups of
board states between host memory and the GPU while retaining one common
preflop policy. A correctness reference is available: reproduce the current
resident ten-board game's iteration schedule and outputs before scaling.
Preserve each board's postflop regrets and averages; restarting postflop games
or averaging independent preflop solutions would change the experiment.
Measure host memory and transfer time before committing to a large overnight
run. Rebuilding or transferring every board every iteration could dominate
runtime, so this is a feasibility gate rather than a speed promise.

If full reference solves remain too expensive for interactive use, they can
still supply better training and validation cases for a continuation model.
Any such model must predict values under changing ranges and actual decisions,
not just fit average postflop values for a fixed starting range. The previous
failed range-transfer and AA-feedback studies remain part of that validation.

## Keep folded-card integration separate and explicit

The 34-million-deal audit confirms that the earlier folds alter both live
hands and board probabilities. Do not apply a single offset to every hand,
or give the solver the hidden folded cards as if players could see them.
The connected-game extension must average over hidden folded-card possibilities
while sharing strategies at information sets that players cannot distinguish.
The completed physical-deal audit supplies an independent correctness check.

No step above justifies deploying a new range model yet. The reserved board
panel and untouched Wizard validation cases remain available for a later,
separately registered accuracy check.
