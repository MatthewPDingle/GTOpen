# Matched equity-pricing comparison

The comparison is registered and its GPU stage has started. No accuracy outcome
is available yet. It is a restricted terminal river Fold/Call experiment against
a uniform legal opponent, not a range-conditioned preflop model.

## What changed

The earlier approach learns separate fold/call scores while also having to infer
the effect of the pot, call price and stack. The candidate learns visible-card
equity and uses the known cash-flow equation to calculate calling value. Fold
value is fixed at zero. This removes the problematic comparison between two
learned negative scores, but inaccurate equity can still produce bad decisions.

The candidate uses 16,513 parameters versus 58,504 in the existing two-player
387-input baseline. This compares complete modeling approaches, not equal-sized
networks. Its opponent is uniform by construction; applying it directly to an
opponent's betting-conditioned range would be invalid.

## Implementation qualification

- Seven CPU integration tests passed, including sample generation, checkpoint
  round trips, independent double-precision inference, complete detailed metric
  reconstruction, checkpoint selection, and a two-update synthetic paired fit.
- Six protocol tests passed: new board quotas and suit-equivalence separation,
  both accuracy gates, independent gate arithmetic, rejection of missing depths,
  and refusal to replace a registration or run with changed frozen inputs.
- A separately registered GPU integration check passed eight raw prediction
  comparisons and four complete metric comparisons. It also matched the old
  CUDA sampler's inputs, actors, targets and generator states exactly. Its
  calculations took 1.938 seconds; this is not a training performance estimate.
- Earlier candidate controls remain unchanged: eight CPU tests and twelve
  synthetic CPU/GPU cases. No qualification used actual new poker test labels.

The integration check is `stack-equity-priced-integration-control-v1`. Its result
pins the inputs and reports all numerical comparisons. Training uses float32;
validation and final inference widen saved float32 weights to float64 for both
models. Independent NumPy readback uses those same stored weights with separate
dense arithmetic. Original numerical tolerances remain unchanged.

## Frozen scientific comparison

Study prefix: `stack-equity-priced-learning-v1`.
Store: `S:\GTOpen-research\stack-equity-priced-learning-v1`.

- Reuse the 1,024 random-arm fitting boards from the prior balanced-board study.
  Their files and known-card reference counts remain immutable.
- Prepare 128 fresh validation boards, 128 fresh random test boards, and 64
  fresh structured stress boards. Exclude all historical groups carried in the
  prior registration plus all its fitting, validation, test and stress boards.
  Board seed: 9297600. Stress boards have separate equal-cell quotas and never
  replace the ordinary-board primary test.
- Fit seeds 9297601 and 9297602. Each seed runs both approaches with one shared
  batch object per update, the same two-action normalized value MSE, Adam at
  0.001, batch 4,096 and 8,192 updates. The existing context/state/card sampling
  distribution is preserved. Batch identities and generator states are recorded.
- Train at 20/40/100/200/400bb. Select each model by minimum equally weighted
  validation decision loss at checkpoints 0/1,024/4,096/8,192; ties choose the
  earliest checkpoint. Freeze all four selected identities before preparing
  final-test or stress labels.
- Primary result: on fresh ordinary boards at 60bb and 150bb, achieve at least
  20% lower mean normalized decision loss in **both seeds**, while keeping mean
  loss at **each depth** at or below 0.001 starting stacks. These depths are
  excluded from fitting and selection; they are not globally unseen research
  geometry.
- Preserve absolute errors, tails, actor/price/hand/board breakdowns and adverse
  outcomes. Independent CPU readback collects every numerical discrepancy within
  its budget and fails qualification if any required check fails. It does not
  stop at the first numeric discrepancy or retry failed inference.

The previous study's failed verification and failed primary comparison remain
failed. They are not repaired, retried, or replaced by this experiment.

## Execution and limits

CPU preparation finished successfully in 46.297 seconds with eight bounded
workers. Final-test and stress labels were not prepared. Registration SHA256:
`41b5b799b7fb6cae773bf3358313959a691bef1c2c46af0ad701c5b8d89d66c8`.
Preparation SHA256:
`e29378e93c26647d13e68e7f9058802195568bf875fe7af4a818039014ed2610`.

GPU session at launch: 5880, PID 28172, process creation time
1790690089.1683035. Verify its live handle/process and outputs; do not trust an
old PID or status file alone. A GPU attempt marker exists: never rerun `run`.

Main work is capped at one hour including preparation; independent readback at
30 minutes. The study allows 4 GB research VRAM with 2 GB external headroom,
256 MB new study files plus a 128 MB reserve, and the existing 800 GB global
allocated-file cap. Admission measured 740.28 GB allocated across the registered
research roots. Research shares light desktop use and yields to heavier work.

After successful main completion and lock release, execute the registered
`tools/research/stack_equity_priced_readback_v1.py` once, only if no readback
attempt or result exists. A result with `passed: false` is terminal failed
verification, even if its `complete` field is true. Preserve all failures.
Then analyze both seeds and both fresh-test gates in plain English.

No production code, server, GitHub push or deployment is part of this study.
Even a pass requires subsequent range-conditioned, multi-decision testing before
it could support better practical preflop ranges.
