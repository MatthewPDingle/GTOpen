# Showdown study: coverage and remaining policy movement

The completed candidate still has sparse evidence per hand class and continued
late-training movement. The small improvement in cross-seed averages does not
mean individual policies have settled. This read-only diagnostic used all four
completed arms, all 78 updates and all 169 classes. It sampled no new deals,
trained no models and changed no production behavior.

| Arm | Class deals: min / median / max | Mean classes absent per update | Middle-to-last window TV | Mean policy step TV, last 26 updates |
| --- | ---: | ---: | ---: | ---: |
| First baseline | 91 / 178 / 405 | 18.88 | 12.14% | 1.84% |
| First corrected | 91 / 178 / 405 | 18.88 | 11.45% | 2.12% |
| Replication baseline | 82 / 185 / 420 | 19.04 | 16.37% | 2.36% |
| Replication corrected | 82 / 185 / 420 | 19.04 | 15.89% | 2.53% |

Typical classes receive 2.28 or 2.37 deals per update. Empty classes represent
6.30% or 6.45% of incoming hand mass per update. Matched baseline/corrected arms
have exactly the same class counts at every update, so the correction did not
change evidence coverage. Every class eventually received observations.

Windows contain played generations 0–25, 26–51 and 52–77, with the original
generation-plus-one weights normalized separately within each window. The
correction slightly lowers middle-to-last-window distance in both seeds, but
increases mean one-step movement late in training in both seeds. These descriptive
metrics do not demonstrate convergence or quantify poker mistakes: strategically
similar actions may switch, while apparently stable averages may conceal drift.

The final current policy differs from the complete played average by 12.08%
versus 10.77% in the first pair and 12.15% versus 15.19% in the replication pair.
Generation 78 is included only for this diagnostic; it remains excluded from
the evaluated played banks. No alternate checkpoint was selected.

## Verification and resources

The diagnostic authenticated completed training/audit identities, read immutable
checkpoint objects through their existing original/archive/continuation readers,
and verified generations and cumulative counts. It reconstructed all four played
root averages and matched the independently audited evaluation policies to
3.34e-16. Full per-update counts and per-class summaries are retained in
`showdown-root-trajectory-v1-result.json`.

Four CPU processes inspected the independent arms concurrently after checking
available CPU and RAM. A first attempt stopped before admission because the
production server was offline. This saved-file-only diagnostic now accepts a
confirmed closed port without starting the app; if the server is present it
still requires the existing idle-solve check. Existing GPU/training safeguards
were not changed. No new solve or GPU inference was needed.

## Implication

The study does not justify deploying the correction or another large identical
training run. Regular per-class coverage is worth a bounded sampling pilot,
but eliminating empty classes alone cannot be assumed to resolve within-class
runout noise or changing continuation policies. The pilot must preserve the
intended conditional card distribution, handle any sampling weights explicitly,
and report throughput and variance per unit of compute before expanding its
training budget. These are exploratory findings, not new confirmatory results.
