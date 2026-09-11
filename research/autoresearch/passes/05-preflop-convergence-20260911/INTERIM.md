# Feasibility checkpoint

2026-09-11. Production unchanged. Research branch only; no qualified release yet.

Six-player calibrated tree: 23,038 nodes, 100bb, opens 2.5bb, reraises 3x,
limps/all-in enabled. All players learn. Two consecutive canonical full-1024
gap checks <=0.005bb, every 25 iterations. Time below includes initialization
and full checks, up to the second passing check; save/readback and local audits
are separately recorded in raw evidence. This is not a claim of 10x or of
complete local convergence.

| Candidate | Iterations | Seconds to second passing check |
|---|---:|---:|
| Native, repeat A/B |350|24.23 / 24.20|
| HS15, full samples |300|21.62|
| HS30, full samples |325|23.39|
| Gamma15 only, full samples |275|19.30 approximately|
| Rotating 128, seeds 42/314159/90210 |350 / 375 / 350|5.53 / 6.03 / 5.55|
| Rotating 256, seed 42 |350|8.44|
| Rotating 64, seed 42 |350|4.19|
| HS15 + rotating 128, seed 42 |350|5.75|

The 128-sample results reproduce a roughly 4.0-4.4x global time-to-threshold
improvement; 64 is roughly 5.8x in one seed. The unconfigured and native-DCFR
research paths produced byte-identical small-control saves. Independent CPU
checks agree with sampled six-player GPU gaps to substantially less than 1e-6bb.

## Local quality remains unresolved

A separate 3,000-iteration native reference reached about 0.000254bb summed
gap, but did not reach its stricter 0.0001 target. Selected one-action-deviation
audits use that reference's arriving ranges and future play. They are not exact
physical-equity checks or full conditional best responses.

The baseline and all sampled candidates fail the <=10% probability-on-actions
losing >0.1bb gate on some relevant conditional hand classes in these paths:
SB after UTG opens and BTN calls; BB after UTG opens and BTN/SB call; BB facing
a limp. BB facing an open with everyone else folding passes. The native tight
reference itself still fails the first two paths. Therefore a global threshold
alone is insufficient evidence of usable answers throughout the tree.

Sampled candidates generally reduce weighted losses on the cold-call lines,
but not uniformly across every path/seed. Do not promote on global gap alone.

The reference's independent-range joint reaches explain why the global metric
underweights these lines: SB after open/BTN call is 0.0001190; BB after
open/BTN+SB calls is 0.00001017; BB facing an open after all folds is 0.09564;
BB after an initial limp and remaining folds is 0.001792. These are model
reach probabilities, not measured poker population frequencies. The cold-call
line can be important to an interactive user despite its tiny global weight.
For example, the ordinary stopped baseline gives JTs at the selected SB node
almost 100% probability on actions over 0.1bb worse than the best one-action
deviation followed by reference play. This is not just a cosmetic range difference.

## Verified and pending

Verified: three focused research tests (coverage/bounded discounts and immutable
self-policy quality), default-feature cargo check, research release builds,
native save roundtrip, read-only live guard, initial GitHub research push.
Pending: original 1,567,754-node eight-player case, adaptive measured-profile
fixture, larger-tree repeated seeds, full comparison and final recommendations.
No live app update, no production speedup claim, no goal completion.
