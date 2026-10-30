# Gradually reducing the learning rate did not qualify

The 16-fit fixed-data comparison is complete. **Neither tested cosine schedule
met the registered promotion criterion.** Do not replace the current fitter or
launch a longer self-play run with this schedule on the strength of this test.

This follows the [residual diagnosis](SAMPLED-NEURAL-RESIDUAL-DIAGNOSIS.md).
It tests one possible fitting change; it does not identify the cause of the
self-play fluctuations observed there.

## Matched comparison

Use the same frozen no-rake/seed-17 table-generated reservoirs as the previous
[exact-mean fitting control](SAMPLED-LARGE-FIT-CONTROLS.md): 262,144 retained
visits per player, 28 occupied observations per player, the same 28-64-64-3
network, raw-target RMS scaling, full retained-data gradient, legal-action mask,
Adam and fresh initializations 991 and 20260922.

At each of 512 and 2,048 training steps, compare constant learning rate 0.003
with a cosine decrease from 0.003 to 0.00001 over the entire fit. Both endpoints
are included; the learning rate is set before each optimizer step. The loss,
samples and initial weights match. All eight constant fits reproduce the
previous control's MSE and probability-L1 results within 1e-12.

Before running, promotion required the cosine candidate to weakly improve both
excess mean-fit MSE and visitation-weighted policy L1 in **all four**
player/initialization combinations at a given budget. This conservative
fixed-data criterion is not a test of poker strength. No rule was relaxed after
seeing the results.

## Results

| Steps | Player / initial seed | MSE, constant | MSE, cosine | Policy L1, constant | Policy L1, cosine |
|---|---|---:|---:|---:|---:|
| 512 | 0 / 991 | 6.52e-6 | 4.68e-4 | 0.000118 | 0.000397 |
| 512 | 0 / 20260922 | 1.07e-4 | 6.27e-4 | 0.000166 | 0.000611 |
| 512 | 1 / 991 | 1.81e-5 | 1.27e-4 | 0.436367 | 0.052177 |
| 512 | 1 / 20260922 | 1.05e-4 | 1.73e-4 | 0.045410 | 0.206360 |
| 2,048 | 0 / 991 | 2.83e-8 | 1.96e-10 | 0.000049 | 0.000000236 |
| 2,048 | 0 / 20260922 | 5.15e-6 | 1.21e-5 | 0.000151 | 0.000027 |
| 2,048 | 1 / 991 | 2.11e-8 | 6.88e-6 | 0.014028 | 0.045410 |
| 2,048 | 1 / 20260922 | 7.64e-6 | 3.97e-5 | 0.045410 | 0.045410 |

Lower is better for both measures. Policy L1 compares regret matching of the
network predictions with regret matching of the retained empirical means; it
is not exploitability and can change sharply when advantages are near zero.

The shorter cosine fits worsen MSE in every combination. The longer schedule
has one particularly accurate fit, but worsens MSE in the other three, and
worsens policy L1 for player 1 / seed 991. These results do not support choosing
the attractive individual fit as the next general-purpose method. Nor do they
rule out every possible schedule: this only tests the registered whole-fit
cosine decrease with the stated endpoints and budgets.

## Evidence and next action

`sampled-schedule-fit-cpu-v1-registration.json` freezes the source, dependencies,
prior gradient-control evidence and retained-data hashes before training.
`sampled-schedule-fit-cpu-v1-result.json` preserves every fitted observation's
target, prediction and resulting policy, all 16 fits, and both failed promotion
decisions. The source is
`tools/research/hu_sampled_schedule_fit_probe_20260922.py`.

This is an exploratory CPU fitting diagnostic on already inspected finite data,
not a CPU performance project, held-out generalization test, or a physical
poker policy. It uses two threads, no GPU, a five-minute ceiling, a 20 GB RAM
reserve, and a production-idle guard. No game, preview or production model was
changed. The independently registered long CPU/GPU comparisons continue with
their original fitting schedules and stopping rules.
