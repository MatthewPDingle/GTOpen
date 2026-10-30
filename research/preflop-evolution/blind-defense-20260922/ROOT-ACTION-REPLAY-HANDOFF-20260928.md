# Continue with the full saved root-action replay

The two-batch correctness control and the CPU worker benchmark are complete and
independently reviewed. No research process is left running from either job.
The full replay has **not** launched. The broad research goal remains active.

## Completed work

- Local commit `551a13736416ddbe27c340e030442fed8e25402e` contains the three
  root-action control/review sources and six corresponding evidence/plan files.
- Correctness: 64 existing deals, eight crossed profiles, four forced root
  actions; original native replays exactly equal. Maximum mixture error 1.42e-14
  bb; independent decimal error 2.19e-14. All later probabilities unchanged.
- Worker benchmark: identical 12-job sequence for each of 1/4/8/12 workers.
  Times 52.719/16.172/12.156/7.875 seconds. Every one of 48 jobs exactly matches
  the qualified native and compact outputs. Twelve workers selected by the
  registered rule (fewest workers within 5% of fastest), about 6.69x the serial
  throughput on this small repeated-input test. This is not solver performance.
- Benchmark registration SHA256:
  `3c1fd6884e660eb05fe8d16b1a437dddfc0b86970f30e4d9e8d8c9192234d42f`.
- Benchmark result SHA256:
  `e34f6c82983be35efdec7b7fc56adb11704b42dc24e6ffe133117e239d9ff491`.
- Qualified raw control store:
  `S:\GTOpen-research\board-root-action-control-v1` (about 152 MB).
- Reviewed worker store:
  `S:\GTOpen-research\board-root-action-workers-v1` (11.62 MB retained).
  Only its two verified newly created scratch inputs per job were retired.

## Next implementation

Follow `BOARD-ROOT-ACTION-REPLAY-PLAN.md` and
`BOARD-ROOT-ACTION-DECOMPOSITION-PLAN.md`. Implement a new versioned, bounded
replay/aggregation runner; do not edit these now-frozen qualified `.py` sources.
The original study result/checkpoint supplies all 2,048 archive routes. Reuse
`board_root_action_decomposition_v1` for authenticated restore, strict root-only
transformation and native invocation. `board_root_action_workers_v1` demonstrates
qualified 12-worker behavior and exact-path scratch retirement.

The benchmark deliberately did not rerun the original mixed native evaluation:
it used the saved values as the reference and recorded `original_native_rerun:
false`. Do not present the helper's zero replay-error field as evidence of a new
mixed-policy native replay when the same saved document is supplied twice.
Every full batch still needs a genuine saved-mixture versus forced-action check.

Keep all 65,536 original physical deals and all eight crossed profiles; retain
compact values, native output and hashes, with explicit batch completion and
restart validation. Qualify aggregation and recovery before the full launch.
Use deterministic batch order for summaries regardless of worker completion order.
Report counts, four action means and paired differences for all 169 classes;
missing coverage must be explicit. Never infer training support from evaluation
counts. Reused-sample action maximization is exploratory, not a validated best
response or exploitability bound. Original eight registered payoff tests remain
inconclusive and unchanged.

Proposed full replay budget: at most 4 GB additional allocated storage, twelve
CPU workers subject to competing workloads, two-hour deadline. Check fresh global
allocation across the three existing research roots against the user's 800 GB
limit, preserve old evidence, and respect existing research ownership locks and
active production solves. Keep port 56708 offline unless separately needed.

## User preference and publication

The user explicitly approved research sharing with light browser/video activity;
heavier workloads and active solves retain priority. `DESKTOP-RESOURCE-SHARING.md`
records this. No GPU is needed by the current diagnostic. The completed GPU
evaluation passed its original startup check; no claim has been made that its
frozen 10% threshold was changed. A future GPU admission change needs an explicit
new qualified implementation that reports real measurements.

Only commit `69b8f082b64a78fd36ac80e4af6e944943769553` was approved for the earlier
GitHub push and was already pushed. New work remains local; do not broaden that
push under the old approval. Keep this research separate from production accuracy
claims. Jev remains deferred, and no Serena UI should be opened.
