# Nonuniform chance-weight controls

Completed CPU-only on the existing two-board development workers. No new
poker solve, held-out strategy access, frozen-helper change or deployment.

The unchanged transfer aggregator was exercised with board chance weights
1:3, then with both multiplied by95 and worker input order reversed. EVs,
deviation gains, postflop residuals, frequencies, rake and terminal mass
were identical. The exact source policy was preserved. Missing and duplicate
board sets were rejected.

The correct weights **after conditioning on legal private hands** were
18.1525% and81.8475%, rather than25% and75%. Independently weighting each
board's scalar EV by that legal-hand mass reproduced the aggregate within
1.78e-15 bb. Weighting EVs by chance fractions alone differed by0.158871 bb.
This is a development test demonstrating the conditioning requirement, not
a measured error in production or a full-deck accuracy result.

Maximizing after combining unseen flops also stayed below the deliberately
invalid per-board maximization upper bound for each player. Independent
physical-card and chip/rake audits passed; maximum cash conservation error
was3.56e-8 bb and relative normalizer error2.54e-10.

Evidence: `weighted-transfer-controls.json`; helper:
`tools/research/weighted_transfer_controls.py`. These checks support the
weighting mechanics described in [the proposed full-population supplement](FULL-POPULATION-SUPPLEMENT.md).
They do not authorize launching that supplement before the existing gates
or replacing the independent95 result.
