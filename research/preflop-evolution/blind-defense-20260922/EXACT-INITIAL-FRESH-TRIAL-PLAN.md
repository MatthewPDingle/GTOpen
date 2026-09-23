# Fresh exact-initial training trial

This experiment addresses the noisy initial all-in targets identified in the
previous BB-versus-BTN study. It is research only. The previous broader test
found a profitable BB first-action change of 0.293 bb per entry into this spot;
therefore improving only the all-in diagnostics cannot qualify the ranges.

## Fixed comparison

- Same BB-versus-BTN 2 bb open context, 200 bb stacks, 5% rake capped at 2 bb,
  incoming ranges, legal actions, complete physical all-in cache and native
  traversal as the previous fresh 78-update pilot.
- Fresh uniform initialization, 78 complete updates, eight batches of 64 deals
  per update: 39,936 fresh deal draws. No reused fitted checkpoint.
- Same baseline chance/action/reservoir/fit seeds (121301 through 121305),
  262,144-entry reservoirs, 302/64/64/4 network, 512 fitting steps per player
  per update, batch size 4,096 and learning rate 0.003. Common seeds preserve
  chance draws; policy-dependent traversal and reservoir insertion streams
  need not remain paired.
- BB's initial shove action receives its exact conditional expectation over
  the opposing incoming range. Other root action estimates stay sampled;
  advantages are recentered after replacing that action value.
- BTN's first response to that shove uses a separately typed cumulative exact
  regret table, updated once per frozen played generation. Opponent reach
  enters once. No fictitious observations are added to the sampled reservoir.
- Current-policy inference uses float64 with widened stored float32 weights,
  matching the admitted evaluator. Fitting remains float32. This is a bundled
  change; results cannot isolate the effect of target correction alone.

The primary output is the complete played bank of generations 0 through 77,
weighted 1 through 78 for both players. Unplayed generation 78 is excluded.
Equal output weights are a diagnostic, not a second selection opportunity.

## Admission and stopping

The passed CPU/CUDA policy, training, restart and independent readback gates
are required. First run two complete updates with the full pilot batch/fit
settings and separate control seeds 350501 through 350505, then independently
reconstruct all targets, policies, reservoirs, RNG streams and checkpoints.
The pilot requires that full-size control to pass. The two-update control is
not a range-quality candidate.

Only one GPU research controller may run. Production on port 56708 remains
untouched; activity there stops research. Reserve 20 GB host memory, 3 GB GPU
memory and 40 GB disk. Each new T-drive store is capped at 40 GB, with 80 GB
free required at admission. Control time cap is 30 minutes, pilot cap six
hours. Fixed update count or a resource/activity/deadline failure ends the
attempt; no result-dependent stopping or automatic retry. Preserve failed
attempts and the last complete checkpoint.

## Evaluation and limits

After training, independently replay every raw batch and corrected target,
reconstruct all exact updates and reservoir/chance states, and verify the
complete bank. The reviewer does not refit networks or independently rerun
the native poker traversal; it reconciles recorded policies and payoffs with
their saved training state.

Use complete-population initial BB fold/shove and BTN fold/call deviation
gains as the first screen. Relative to the previous primary linear/linear
candidate (BB 0.0540214379086447 bb; BTN 0.0542449900877829 bb), both gains
must fall by at least 25% to justify a separately registered wider test.
Failure means analysis, not choosing a different checkpoint or output mix.

Any wider test must retain ordinary call/raise alternatives, freeze its
response-learning and independent population-test seeds/counts before use,
and use new test data rather than the already inspected 224332 stream.
Exact all-in success alone cannot establish full-game convergence, accurate
blind defense, other stack sizes, other positions, or a production upgrade.
