# Independent-seed replication of root retention

Prepared after the complete first root-retention evaluation and its independent
readback, before drawing any replication deals. See ROOT-RETAINED-WIDER-FINDINGS.md.

## Question and limits

Does the same learning procedure produce comparable behavior with independent
training randomness? The first trial resisted the preceding model's frozen
challenger, but its new challenger had an inconclusive interval and unstable
class choices. One training seed cannot establish robust ranges.

This is one fixed-budget replication of the root-retention model, not a new
algorithm, a sweep for the best-looking chart, or a causal estimate of the
retention change across seeds. A matched old-algorithm replication would be
needed to isolate that treatment effect across independent runs.

## Fixed training design

- New store: `T:/GTOpen-research/root-retained-replication-v1`.
- Same BB versus BTN 2 bb open at 200 bb, same incoming ranges, 5% rake capped
  at 2 bb, same native tree and complete exact all-in cache.
- Same fresh uniform initialization; no previous checkpoint is loaded.
- Same 78 updates, each 8 batches of 64 fresh deals: 39,936 total.
- Same 262,144-row reservoirs per player, 302/64/64/4 networks, 512 fit steps
  per player/update, chunk 4,096, learning rate 0.003, float64 policy inference,
  and float32 fitting.
- Same unweighted cumulative BB root advantage retention, exact initial BB
  jam targets, and exact BTN response accumulation.
- New sampler seed 357301; action seed 357302; reservoir seeds 357303 and
  357304; fit seed base 357305. These were checked against the prior controller
  sources and top-level registered training configurations before this plan.
- Primary evaluation: all played generations 0 through 77, linear weights
  1 through 78 for both players. Exclude unplayed generation 78. Equal weights
  are descriptive only and cannot replace the primary choice.

The training implementation is unchanged. The new controller changes seeds,
artifact names, and storage admission/compression. Its independent reviewer
uses the unchanged complete-training reader with only its input prefix changed.
Previously passed numerical, checkpoint, reservoir, and raw-target controls
remain prerequisites. Source hashes are frozen at registration.

## Resources and stopping

Before launch, measure allocated file bytes across S:/GTOpen-research,
T:/GTOpen-research, and the repository research folder. Existing allocation
plus the full 40 GB new-store cap and 2 GB metadata reserve must fit within
800 GB. Require at least 80 GB free on T: at launch; retain 40 GB free during
execution. The new directory inherits transparent NTFS compression.

Both logical size and allocated file size are capped at 40 GB. Check allocation
at least once per minute, and require all completed files to be compressed.
Reserve 20 GB available host memory and 3 GB available GPU memory. Training
deadline is six hours. Only one research GPU job may own the shared lock.
Production activity stops research. Preserve evidence on the first failure;
there is no automatic retry, budget increase, or outcome-dependent stop.

After successful training, the continuation controller runs the complete
independent readback once, with the original two-hour reader deadline. It
reconstructs targets, played policies, all 39,936 BB root updates, checkpoint
state, reservoir contents, and random streams. It does not refit the model.

## Evaluation and decision

Report the complete exact endpoint evaluation and its independent readback,
including every predeclared averaging pairing, without selecting a favorable
checkpoint or seed. Compare the primary result with the first root-retention
trial and preceding exact-initial trial, retaining the restricted-endpoint
limitations. Exact endpoint gains do not establish calling-range accuracy.

A subsequent broader response test needs separate numerical/resource
admission, fresh prospectively registered training/test seeds, and the global
800 GB storage gate. The training continuation does not launch it automatically.
Do not reuse inspected holdout deals for tuning or claim equilibrium because
a tested gain's interval crosses zero. Report training-seed sensitivity and
hand-allocation instability even if the aggregate results look favorable.

This replication cannot validate other stack depths, positions, raise sizes,
folded-card effects, or multiway play. Production 56708 stays unchanged.
