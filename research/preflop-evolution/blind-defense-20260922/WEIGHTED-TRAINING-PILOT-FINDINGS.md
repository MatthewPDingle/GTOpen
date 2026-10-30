# Complete weighted trainer: implementation pilot passed

The class-stratified trainer completed two full 512-deal generations on the
RTX 3090 on 27 September 2026. Restoring generation one's checkpoint and replaying
generation two reproduced the native artifacts, retained arrays and weights,
reservoir RNG, sampler/action RNG, learned model and final checkpoint exactly.
All 169 BB starting-hand classes were covered in each generation.

This qualifies the complete implementation for a bounded research comparison.
It does not establish better ranges, faster convergence or profitable play. The
pilot used only eight optimizer steps per player per generation, not a trained
policy suitable for deployment. Production and the original trainer were unchanged.

## Numerical checks

- Maximum current-model CPU/CUDA policy difference: 1.1262e-14.
- Maximum played-bank average policy difference (CPU/CUDA and scalar oracle):
  3.3307e-16; own-action reach difference: 4.4409e-16.
- Averaging used native own-history queries, applied all weighted table and root
  overrides before calculating own-action reach, and included only generations
  0 and 1. The final, unplayed generation 2 was excluded.
- Both populations received exactly two root/exact BTN updates. BB root sample
  count was 1024; actual learning visits were 33,740 BB and 4,009 BTN. The BB
  reservoir retained 8192 visits, exercising replacement and weighted fitting.
- Changed training configuration, use of the old model reader and insertion of
  an unplayed model into the average were rejected.

The new model/checkpoint stores weighted state directly in a distinct policy
format. It does not strip weights to create an old-format nested checkpoint.
Restore checks the complete ordered played bank, accumulated root sample budget,
sampler generation/draw counts, reservoir boundaries, and exact reconstruction of
current preflop tables from retained weighted targets.

## Time and hardware

Published generation times were 49.61 and 51.45 seconds. The second generation
spent 19.44 seconds in ingestion, 11.30 seconds in root integration, 8.39 seconds
in inference and 0.47 seconds fitting. The full control, including restart replay,
CPU/GPU comparisons, native history queries and artifact hashing, took 167.17
seconds. CUDA was admitted only after checking available resources and the app;
the owned research lock was released on exit.

Published evidence occupies 903,721,294 logical bytes. The separate one-generation
development smoke occupies another 303,341,336 bytes. These are bounded retained
controls; no long training study or model deployment was started.

The main immediate throughput opportunity is independent CPU subbatch work,
with deterministic ordered insertion retained. See
`WEIGHTED-TRAINING-THROUGHPUT-PLAN.md`. A GPU utilization graph alone would obscure
that most of this pilot's time was spent preparing and validating its inputs.

## Reproducible evidence

- Registration: `weighted-training-pilot-v1-registration.json`
- Result: `weighted-training-pilot-v1-result.json`
- Native evidence, metrics, models and checkpoints:
  `T:/GTOpen-research/weighted-training-pilot-v1/`
- Final checkpoint SHA-256:
  `6fecce5e836d87dbc53f45a7b4d2cc0f96256dcce19c4d9bed4d1e448e03cb91`

Next: benchmark equivalent CPU parallelism, then use the faster validated path
for the matched baseline versus stratified comparison and independent evaluation.
