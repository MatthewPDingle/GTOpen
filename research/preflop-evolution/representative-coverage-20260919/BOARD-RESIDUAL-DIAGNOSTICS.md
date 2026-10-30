# Per-board numerical residual diagnostics

Registered before any reserved strategic outcomes, 19 September 2026.
This is descriptive reporting; the frozen overnight solve, manifests,
iteration targets and aggregate 0.01 bb gates remain unchanged.

The aggregate postflop residual is the correct convergence statistic for
the sampled entering game, but it need not certify every individual flop.
Report each local residual and its contribution using chance weight times
the board's legal private-pair normalizer, divided by the panel normalizer.
These contributions must reconstruct the aggregate residual for each player.
Plain chance weights alone are insufficient because card removal changes
the entering private-card distribution.

`transfer_board_diagnostics.py` first runs the existing complete-panel and
source-policy audit. It then reports the largest local residual, the count
and entering mass of boards above 0.01 bb, and every board's weighted
contribution. The local 0.01 reference is not an additional pass/fail gate.
Do not selectively extend workers or remove boards based on these results.
This does not provide per-hand error bounds, confidence intervals, or a
full-deck accuracy certificate.

## Controls passed

Completed development workers with deliberately unequal 1:3 chance weights
give aggregate residual 0.0013922120 bb and maximum local residual
0.0014201266 bb. Contributions reconstruct the aggregate; reversing worker
input order leaves the report unchanged.

A synthetic panel with a 0.1% entering-weight board at 1 bb residual and a
zero-residual remainder has an aggregate of only 0.001 bb. The diagnostic
correctly exposes the 1 bb local residual and its 0.1% mass. This is a
constructed control, not an observed problem in the poker results. NaN and
materially negative local residuals are rejected. See
`board-residual-controls.json` for evidence and source/data hashes.

## Use after a complete source/panel result

Run the helper with SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER... .
Workers may be JSON or gzip. It refuses existing output paths and audits
all expected boards before producing JSON and Markdown. Apply to both
source policies and both reserved panels; retain all rows. Do not treat an
incomplete panel as a passing result. No extra solve or GPU access is needed.
