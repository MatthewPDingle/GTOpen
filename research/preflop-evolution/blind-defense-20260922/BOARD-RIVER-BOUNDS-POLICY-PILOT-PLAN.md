# Fresh-deal pilot for the river-bounds policy correction

## Purpose and prerequisite

After complete-bank numerical qualification passes, test whether the river-only
correction changes the expected payoff of the actual complete policy. Reduced
prediction error is not enough. Keep both completed 78-model histories, their
entry distributions, preflop tables, generation weights, rake and action tree
fixed. This pilot neither trains a new equilibrium nor demonstrates improved
preflop ranges across games.

Require the full result and independent readback from
board-river-bounds-bank-v1 before running the pilot. Bind their hashes, every
source model and its scale, the exact correction implementation and the native
query/payoff executables. Preserve the existing reference evaluators.

## Fixed pilot design, before fresh sampling

- 4,096 new independent physical deals from the original context's entry
  distribution, using PhysicalDeals mode full_deck, seed 9289901, batches of 32.
  Do not reuse the prior 65,536 evaluation deals or reservoir data for payoffs.
- Four complete policies, ordered Run A original, Run A bounded, Run B original,
  Run B bounded. Each bounded policy corrects every eligible river decision
  before per-model regret matching and own-action-reach averaging.
- For each run, evaluate all four BB/BTN combinations on every common deal:
  original/original, original/bounded, bounded/original, bounded/bounded.
- Report all eight replacement gains: BB and BTN, each against the original
  and bounded opponent, separately for both training runs. Units are bb per
  entry to this restricted preflop subtree. Do not combine runs to conceal
  opposing effects.
- Use the existing full-action native evaluator with sampled public runouts
  and the independently qualified conditional preflop all-in values. Hidden
  all-in labels must never enter policy queries. Maintain cashflow, rake,
  legality and conservation checks.
- No forced root action, new opening-range assumption, smoothing change,
  projection-strength parameter, model refit or early stopping on outcomes.

One final statistical look at exactly 4,096 deals. Resource interruptions must
resume the identical sampler/statistics prefix. An incomplete prefix is an
interrupted pilot, not a positive or negative result. Monitor progress and
resource use without drawing conclusions from interim gains.

## Transport control before the pilot

Reuse the existing first 32-deal archive as a transport-only control. With the
new adapter disabled, all four crossings within a run must reproduce the
corresponding original board-root versus board-root native payoff and have
zero paired replacement gains within numerical tolerance. With it enabled,
confirm that the transported probabilities reproduce the qualified adapter,
the native evaluator accepts every profile and the existing accounting checks
pass. These already used control hands are not pilot evidence.

Register a concrete numerical tolerance and exact control source hashes before
execution. Keep cached query preparation separate from model-specific tables
and scales. Reuse the qualified probability calculations rather than replacing
them with another untested optimized kernel.

## Analysis and interpretation

For all eight contrasts report the paired sample mean, sample variance,
standard error and the existing simultaneous bounded empirical-Bernstein
intervals at 5% family error probability and one final look. Also show mean
plus/minus 1.96 standard errors as an explicitly approximate descriptive
interval, not a second acceptance gate or a distribution-free guarantee.
Preserve extreme observations and original denominators.

This is a pilot to measure effects, variance and runtime. It does not authorize
production adoption, even if point estimates are positive. If effects differ
by role or training run, preserve that outcome and investigate it; do not
select a favorable role, bank or subset and label the whole correction better.

Estimate a possible independent confirmation budget using the largest observed
paired standard deviation across contrasts: ceil((3*s/0.01)^2) deals would aim
for a three-standard-error planning half-width of 0.01 bb per entry. State
that this is an approximate precision/cost estimate, not a guaranteed sample
size or a replacement for the bounded intervals. Use measured complete-batch
wall time and retained bytes to estimate compute/storage cost. Register any
confirmation study separately with fresh chance and fixed policies; do not
extend this pilot until a preferred sign appears.

If the pilot is inconclusive at a practical confirmation budget, report that
honestly and prioritize the larger modeling problem. If promising and
economical, complete independent policy confirmation before considering a
separate training/coadaptation experiment. An inference-only river fix cannot
by itself produce newly solved preflop opening/calling ranges.

## Resource plan

Prepare common queries once, share GPU parameters for original and corrected
policies where possible, and use CPU workers for independent archive compression
and readback. Compare end-to-end throughput, not utilization percentage alone.
Share the GPU with light browser/video activity; yield to active production
solves and heavier workloads. Never start or alter the production server.

Retain shared locks, the global 800 GB allocated-storage ceiling, and immutable
source archives. Reserve at most 2 GB for the pilot including temporary files;
measure a known control batch before admission. Start with a two-hour invocation
limit and resumable checkpoints. If measured overhead cannot meet those limits,
revise the execution plan before drawing the fresh pilot prefix, preserving
the fixed scientific design and its stopping rule.
