# The first response is the main remaining weakness

The frozen weighted-112 policy was diagnosed using the **already completed**
190-flop evaluation. This is a post-hoc explanation of that result, not another
independent confirmation, another trained policy, or a comparison against an
exported Wizard strategy. All 190 boards and all supported hands were retained.

## Where the error occurs

UTG's total remaining best-response gain is 0.284510 bb in this restricted game.
It decomposes sequentially as follows, with LJ's strategy held fixed:

| Change allowed to UTG | Additional gain (bb per study entry) |
|---|---:|
| Improve postflop decisions, keep preflop fixed | 0.000238 |
| Then improve later preflop decisions | 0.000852 |
| Then improve the initial response to the 3-bet | 0.283419 |

The last component is **99.62%** of UTG's total. Separately, changing only that
first decision while keeping all continuations fixed gains 0.283544 bb. These
are alternative decompositions and must not be added together. They locate
the problem at the root decision on this test panel. They do not establish why
Wizard differs, nor prove that every continuation is accurate in a richer game.

## Calling versus folding

The table uses the evaluated postflop best response, leaving later preflop
decisions fixed. Call-minus-fold is the gain from choosing call instead of fold
for that class against the frozen opponent. It is not a gain per randomly dealt
hand, and a best response is not a new joint equilibrium.

| Hand | Current call frequency | Call minus fold (bb) | Range after omitting any one test flop (bb) |
|---|---:|---:|---:|
| 66 | 3.83% | +0.898 | +0.611 to +0.983 |
| 76s | 0.73% | +2.318 | +1.725 to +2.411 |
| ATs | ~0% | +1.068 | +0.817 to +1.152 |
| AJs | 3.49% | +0.867 | +0.596 to +0.950 |
| AQs | 14.99% | +0.794 | +0.642 to +0.875 |
| KQs | 4.42% | -0.219 | -0.503 to -0.144 |

For the five positive examples, calling also beats both raising and jamming in
the class-average values under this continuation mode. The results support the
user's concern about missed calls for several named hands. KQs is an important
counterexample: these results do not support simply making every named hand call
more. Single-board omissions are a sensitivity check, not confidence intervals.

There are also overcalls: for example, 87s calls about 60.9% although calling
loses 0.660 bb relative to folding on this panel. The issue is the allocation of
calls among hands, not just total calling frequency.

## Incoming-range limitations matter too

98s has a positive call-minus-fold value of 2.134 bb, but its entry probability
is only **0.0000624%** in this evaluated prior. Its tiny displayed bar and almost
zero effect on the aggregate error reflect the inherited upstream range.
Similarly, 44's near-pure call strategy concerns only 0.002805% of entries here.
This study never relearned the opening and initial 3-betting ranges. A visually
strange action for a nearly absent hand must not be described as a large source
of practical loss, and matching Wizard requires matching those input ranges too.

## What this changes next

The earlier independent result showed a training gap near 0.005 bb but an unseen
panel gap near 0.332 bb across both players. This diagnostic now localizes most
of UTG's part to the first response, including several economically meaningful
calling hands. More iterations on the same training panel are therefore a lower
priority than better coverage and a controlled investigation of the continuation
values and input ranges. This does not isolate board selection as the sole cause.

Do not patch these individual hands or fit new policies to the inspected 190
boards. Preserve this evaluation for diagnosis, use broader independently chosen
training coverage, and reserve a fresh evaluation panel for any new policy.
Keep the BB-defense context-transfer work: it tests whether the method helps
the wider calling ranges the original application struggled with.

## Verification and scope

`hu_root_action_diagnostic_20260922.py` checked all 190 accepted weighted workers
against their recorded hashes, frozen preflop policies, iteration counts and
board identities. It reconstructed root action values from terminal CFVs,
cross-checked the recursive traversal with an explicit expansion of the 12-node
tree, recovered both published player gaps and EVs, and checked that the additive
decomposition reconstructs UTG's gap. Opponent action probabilities are already
included in terminal CFVs and are not multiplied a second time. Boards are
combined before selecting a best preflop action; there is no future-flop peek.

Class values use compatible opponent mass from the evaluator and preserve its
suit projection. Fold EV is -6 bb because the opening investment is included;
only differences between actions should be interpreted as additional value.
All class rows, action values, input hashes and omission ranges are retained in
`root-action-diagnostic-v1-result.json` and its registration. The scope remains
two live players, fixed incoming ranges, limited postflop sizes, omitted earlier
folded cards, and the existing selected-board evaluation population.

No solver was run, no policy changed, and production was not restarted.
