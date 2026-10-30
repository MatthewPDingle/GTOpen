# Matched river continuation: verified findings

Primary bounded intervals: 0 positive, 0 negative and 8 inconclusive fixed contrasts. All eight comparisons appear below.

This is an equal-update, single-context comparison of two training methods, each with two independent training seeds. It does not establish robust preflop accuracy, a best-response bound, or a production-ready model.

Each arm continued from boundary 80 to 110. The final evaluation used 16,384 fresh common physical deals and the complete played banks 0–109; fitted model 110 was excluded. The original two-update pilot is retained separately. No test-based stopping or selection of a favorable seed or seat was used.

## Playing-strength comparisons

Positive values favor replacing the named player with the candidate against the specified fixed opponent. Units are **bb per entry**, not bb/100 played hands. The primary intervals have the registered 5% family error allocation. The separate normal intervals are exploratory approximations: rare tails can invalidate nominal coverage, and neither analysis accounts for uncertainty across training seeds.

| Seed | Player replacement | Mean | Paired SE | Primary bounded interval | Exploratory normal interval |
| --- | --- | ---: | ---: | --- | --- |
| A | BB against baseline BTN | +0.018176 | 0.007919 | [-0.747426, +0.783779] | [-0.003477, +0.039830] |
| A | BB against candidate BTN | +0.017802 | 0.008100 | [-0.748453, +0.784056] | [-0.004348, +0.039951] |
| A | BTN against baseline BB | +0.016434 | 0.008838 | [-0.752473, +0.785340] | [-0.007733, +0.040600] |
| A | BTN against candidate BB | +0.016834 | 0.008911 | [-0.752336, +0.786003] | [-0.007533, +0.041200] |
| B | BB against baseline BTN | +0.007387 | 0.011536 | [-0.771218, +0.785993] | [-0.024156, +0.038931] |
| B | BB against candidate BTN | +0.005184 | 0.011573 | [-0.773555, +0.783923] | [-0.026461, +0.036830] |
| B | BTN against baseline BB | +0.041802 | 0.009659 | [-0.730058, +0.813661] | [+0.015389, +0.068214] |
| B | BTN against candidate BB | +0.044040 | 0.009943 | [-0.728837, +0.816917] | [+0.016854, +0.071227] |

Point estimates by seed are reported separately; matching signs alone do not prove improvement. The two comparisons for a seat share data and are not independent replications.

## Learning cost

These are the thirty new training-pipeline updates only. The timer includes pipeline startup, targets, fitting and checkpoint publication. It excludes the outer checkpoint restore/readback after each update, between-update cleanup, parent copying, admission, final evaluation and independent review. These sums are not total elapsed training or research time. Order, caching and other desktop activity can affect them. GPU wait is the separately recorded training-loop counter; do not subtract it to infer pure compute time. This is not an equal-time test.

| Seed / method | Updates | Training pipeline time (min) | Average pipeline seconds/update | Recorded GPU wait (s) |
| --- | ---: | ---: | ---: | ---: |
| A-baseline | 30 | 30.03 | 60.06 | 1.97 |
| A-river | 30 | 92.41 | 184.81 | 12.74 |
| B-baseline | 30 | 35.41 | 70.82 | 1.97 |
| B-river | 30 | 99.58 | 199.17 | 14.12 |

Seed A: candidate/baseline training-pipeline time ratio **3.077×**.

Seed B: candidate/baseline training-pipeline time ratio **2.812×**.

## Changes reaching preflop decisions

These describe differences between individual fitted models, not measured gains. Entry-weighted total variation summarizes the BB action mix; the BTN column is the largest action-probability difference for its exact first-shove response. The evaluated average contains all played models, not just the last model.

| Seed | Model | Evaluated? | BB weighted difference (%) | BTN maximum difference (percentage points) |
| --- | ---: | --- | ---: | ---: |
| A | 78 | yes | 0.0000 | 0.0000 |
| A | 79 | yes | 0.0000 | 0.0000 |
| A | 80 | yes | 1.2721 | 0.0000 |
| A | 81 | yes | 1.7206 | 0.0872 |
| A | 82 | yes | 1.8734 | 0.2123 |
| A | 90 | yes | 4.4210 | 1.3142 |
| A | 100 | yes | 5.4452 | 3.6511 |
| A | 109 | yes | 6.5598 | 14.3747 |
| A | 110 | no — unplayed | 6.1203 | 15.8010 |
| B | 78 | yes | 0.0000 | 0.0000 |
| B | 79 | yes | 0.0000 | 0.0000 |
| B | 80 | yes | 1.0186 | 0.0000 |
| B | 81 | yes | 2.4849 | 0.0023 |
| B | 82 | yes | 2.6916 | 0.0021 |
| B | 90 | yes | 6.3963 | 0.6824 |
| B | 100 | yes | 8.5411 | 1.5747 |
| B | 109 | yes | 10.0437 | 0.5342 |
| B | 110 | no — unplayed | 10.7535 | 0.5586 |

## Tail diagnostics and verification

A large contribution from a few deals makes the exploratory normal intervals less reassuring. These diagnostics do not certify normal coverage.

| Seed | Player replacement | Largest squared deviation (%) | Largest ten (%) | Third absolute standardized moment |
| --- | --- | ---: | ---: | ---: |
| A | BB against baseline BTN | 8.850 | 24.107 | 10.178 |
| A | BB against candidate BTN | 8.515 | 27.140 | 10.722 |
| A | BTN against baseline BB | 3.316 | 17.165 | 7.796 |
| A | BTN against candidate BB | 3.087 | 16.780 | 7.651 |
| B | BB against baseline BTN | 3.438 | 17.618 | 8.348 |
| B | BB against candidate BTN | 2.412 | 15.542 | 7.882 |
| B | BTN against baseline BB | 3.635 | 18.489 | 7.725 |
| B | BTN against candidate BB | 3.389 | 17.540 | 7.461 |

Independent readback covered 512 batches and 7,443,270 observations. Maximum scalar-statistic discrepancy: 1.47e-14. It also checked complete checkpoints, parent continuity, source deals, archive identities, policy crossings and cashflows. It reuses the qualified native engine; it is not a second poker engine or independent neural implementation.

Stored study allocation: 16.817 GB (45.042 GB logical).

## Decision still required

Assess consistency across both seeds and seats alongside computational cost. A favorable exploratory result can motivate confirmation and an equal-time comparison. Mixed directions, regressions or excessive cost argue against adopting this treatment. Additional stack, rake, sizing and multiway contexts remain necessary. No automatic promotion or deployment follows from this report.

## Authenticated evidence

- [river-matched-continuation-v1-registration.json](river-matched-continuation-v1-registration.json); SHA256 `6b4b4dec4d0580d3aed5b3c2a38361eb91a58ab5dee778d929b919408ebbf14a`.
- [river-matched-continuation-v1-result.json](river-matched-continuation-v1-result.json); SHA256 `e0a81a258b3189047c3cfee9581a0ef6496eacdddc686b2c4f15c32dea1eaf95`.
- [river-matched-continuation-v1-review-v1-registration.json](river-matched-continuation-v1-review-v1-registration.json); SHA256 `7dd1ed3bf53f83d71810d37b64065cd127fd01ee3fefedfe1497aa772fece75b`.
- [river-matched-continuation-v1-independent-review-v1.json](river-matched-continuation-v1-independent-review-v1.json); SHA256 `8676d3ae76e0c3d026fecc468b3052278dd8ff06a6816463a16049bc3bede5fb`.

See [the prospectively frozen plan](RIVER-MATCHED-CONTINUATION-PLAN.md).
