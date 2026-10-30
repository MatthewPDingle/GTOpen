# Bounded exact-target learning diagnostic

Status: implementation plan, not an executed training registration. The exact
reference has passed. The next substantive result must be an actual fixed-budget
learning comparison, not another unbounded round of infrastructure checks.

## Data and question

Use the qualified uniform-opponent river call/fold reference. The purpose is to
test whether public numeric prices improve learned decisions and whether the
model transfers to untouched stack depths. This is neither a realistic opponent
range model nor a full-game equilibrium.

Construct 24 fitting, 8 validation and 8 final-test river boards from one fixed
new seed. Group by full-board suit isomorphism; all groups must be distinct and
exclude the twelve qualification-probe groups. Freeze the boards and split
before fitting. All 1,081 legal hero holdings per board have exact conditional
opponent counts. Each public state is a separate conditional decision.

Fit at 20/40/100/200/400 bb using the already qualified 476 legal two-action
states. No arbitrary price restriction or outcome-dependent state selection.
Keep 60/150 bb out of fitting and validation; generate/read their labels only
for the frozen final test. At test, report results separately for trained depths
on new boards and new depths on new boards. Public geometry checks at held-out
depths do not count as inspecting targets.

## Representation and policy

Compare the original 302 visible inputs with the 362-input representation that
adds actual public stack, pot, call-price and action information. Use two player
networks per arm, each with the established 64/64 hidden widths and four score
outputs. Only fold/call are legal in this reference. Preserve the registered
positive-score regret matching and nonpositive-score fallback; do not hide
imperfect predictions by replacing learned decisions with the exact oracle.

Create an explicit, separately versioned feature-only fitting adapter. It must
match native canonical cards, keys, actor/street/history fields and existing
visible/public inputs on retained native queries. Do not supply fictitious
empty own histories to the inference/strategy-average API. The diagnostic has
independent conditional decisions, so it needs no policy-bank reach averaging
or learned preflop lookup tables. Its model outputs must be labelled as this
diagnostic, not as a production-compatible preflop checkpoint.

Avoid storing millions of duplicated dense feature rows. Cache card features
and exact counts by board/holding, public descriptors by context/state, and
assemble indexed batches on the GPU. Keep physical-hand weights explicit;
canonical suit duplicates do not get deduplicated without retaining their mass.

## Fixed comparison

Use two fixed initialization/batch seeds and both input representations: four
fits total. Use Adam, batch size 4,096, and 8,192 updates per fit, subject to the
registered total wall-clock cap. Sample fitting contexts uniformly, then their
eligible states uniformly, then fitting boards and physical hero holdings
uniformly. Freeze the learning rate and initialization before execution; use
the same base-weight initial function for both representations, with new public
input weights initially zero, so a changed start does not confound the comparison.

Targets are fold advantage 0 and call-minus-fold advantage divided by starting
stack. Mean squared loss is over those two legal outputs, using the declared
context/state/board/holding weights. This normalization deliberately emphasizes
fraction-of-stack errors; report unscaled bb errors too. No resampled hidden
opponent or sampled showdown outcome is used as a target.

Evaluate the fixed validation boards at steps 0, 1,024, 4,096 and 8,192. Choose
the checkpoint with lowest context-balanced, stack-normalized decision regret,
breaking ties by earlier step. Do not tune on test boards or held-out depths.
Stop an incomplete run at its budget and report incomplete; never extend it
because results look promising. Preserve all intermediate registered checkpoints.

The final comparison reports both seeds, both players, each stack, calling-price
bands and hand-strength bands. Primary diagnostic quantities are mean and high
quantiles of exact decision regret, in bb and fractions of starting stack.
Also report squared value error and action mistakes outside a declared
near-indifference band. Constant fold/call and the analytic oracle are checks.

Before fitting, freeze numerical thresholds and the precise weighting/aggregation
implementation. A reasonable prospective gate is at least 20% lower mean
normalized regret for 362 inputs in both seeds, plus <=0.001 starting stacks of
mean regret in each held-out depth. Those thresholds are diagnostic engineering
targets, not a guarantee of real-game quality. Report adverse slices rather than
averaging them away. If the result fails, analyze training/validation limitations
without reusing the final test to select a replacement.

## Budget and subsequent decision

Target one bounded invocation, including one storage admission, feature-adapter
qualification, data preparation, four fits and the single final test. Reserve
at most 512 MB new evidence plus 128 MB overhead, one hour of elapsed execution,
combined research CUDA <=4 GB, and the existing RAM/free-disk/global-storage
limits. Use GPU indexing/batched inference and up to eight CPU workers for
independent board work where useful. Yield to production/heavy workloads while
allowing light desktop GPU use. Freeze exact budgets in the registration.

If this clean supervised target cannot be learned reliably within the budget,
work on representation/optimization before more broad self-play. If it passes,
the next scientific step is a restricted multi-decision poker reference with
independent best responses. Do not promote a model based only on this diagnostic.
