# Fresh trial: all-sample preflop root retention

24 September 2026. Prospective recipe; no result-dependent checkpoint selection.

## Hypothesis and fixed recipe

Preserving every corrected BB root advantage in a separate cumulative state
may reduce the training variability introduced by sharing a finite reservoir
with postflop observations. The diagnostic supporting this experiment is
recorded in ROOT-RETENTION-FINDINGS.md. It does not establish stronger play.

Use the same BB versus BTN 2 bb open context at 200 bb, incoming ranges,
5% rake capped at 2 bb, four root actions, native traversal and exact all-in
cache as the completed exact-initial pilot. Retain its exact BB jam targets,
exact BTN initial response updates, float64 inference and float32 fitting.

The only intended training change is a separate BB root accumulator: all
corrected root advantages, equal weight per sampled visit, sums and counts
by class. Apply its regret-matched policy after the existing base table and
before own-action reach averaging. Preserve the base reservoirs, postflop
network fitting and random stream rules. Do not introduce a hand-strength
prior, threshold, altered action menu or chosen chart.

Train from fresh uniform initialization for 78 updates of 8 x 64 deals
(39,936 deals). Retain 262,144 samples per player in the original reservoirs,
302/64/64/4 networks, 512 fit steps per player/update, chunk 4,096, learning
rate 0.003. Pilot seeds remain 121301 through 121305 for a matched training
comparison; policy-dependent traversal can diverge. These training samples
are not an independent quality holdout.

Primary output is the complete played bank 0 through 77 with weights 1
through 78 for both players. Unplayed generation 78 is excluded. Equal
averaging is diagnostic only, never a second selection opportunity.

## Admission, integrity and stopping

Require the accumulator replay control, native CPU and CUDA restart controls,
and CPU/CUDA single/bank policy parity with independent own-history products.
Then run two full-size updates with separate seeds 356501 through 356505.
Independently reconstruct raw corrected targets, policies, both accumulators,
reservoirs, random streams and checkpoints before admitting the pilot.

The model and checkpoint use an explicit version-5 envelope. Old registered
code and artifacts stay unchanged. Resume only from complete checkpoints;
do not resume a partial batch or silently rerun an existing store.

One research GPU owner at a time, with both existing shared-lock checks.
Production activity stops research. Reserve 20 GB host RAM, 3 GB GPU memory,
40 GB disk; require at least 80 GB free on T at admission. Each store is capped
at 40 GB. Control deadline 30 minutes; pilot deadline six hours. Stop at the
fixed budget or a resource/activity/deadline failure, never by observed quality.
Preserve failure records and the last completed checkpoint.

## Evaluation and interpretation

Independently reconstruct the complete pilot before quality evaluation.
Report exact restricted BB fold/jam and BTN initial fold/call gains against
the preceding exact-initial candidate (0.0137934944 and 0.0135399269 bb per
entry). These are diagnostics, not the central quality claim or a reason
to select a different checkpoint.

Subject to correctness and resource admission, evaluate the complete primary
bank on a separately registered fresh wider call/raise response test. Retain
the preceding frozen response as an alternative. Freeze response training
and evaluation seeds/counts before drawing them; do not reuse the inspected
354332 test stream. Wider evaluation storage must be admitted separately.
Do not claim a statistically reliable change from differences between two
separately trained responses' point estimates alone.

No production promotion is authorized by these controls or a restricted test.
This single fixed heads-up context does not validate other stacks, positions,
action menus or multiway play. Successful retention is one potential training
improvement toward that broader goal, not completion of it.
