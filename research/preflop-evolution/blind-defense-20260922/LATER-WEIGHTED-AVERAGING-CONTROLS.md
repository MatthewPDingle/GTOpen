# Fresh averaging experiment: execution controls passed

23 September 2026. These checks admit the fixed fresh-bank experiment; they do
not establish that either average produces good poker ranges.

- Independent scalar arithmetic and CPU/CUDA comparisons passed for both fixed
  output schedules. The fixture includes 7,198 rows with earlier own actions.
  It detects the incorrect shortcut of averaging each node independently:
  that shortcut differs by as much as 0.599 in action probability on this fixture.
- Four fresh training updates completed in 194.6 seconds with 2,048 physical
  deals, unchanged full fitting budget, and the complete exact equity cache.
- The independent replay reproduced every deal, action random state, reservoir
  insertion and final saved reservoir, all generated preflop tables, and the
  complete played-bank progression. It checked 4,096 native reference traversals
  and restored the final checkpoint. Replay took 22.2 seconds. This replay does
  not rerun neural fitting or certify its strategic quality.
- Both output averages and all four player pairings ran through the complete
  exact endpoint evaluator. Independent scalar chip accounting reproduced the
  gains within 5.56e-16 bb; pair cashflow conservation error was at most 1.43e-14
  bb. Repeated CPU policy lookup agreed within 1.12e-16. No accuracy screening
  result is assigned to the four-update control.

The full experiment uses different, prospectively fixed seeds. Its 78 updates
and equal/linear weights are unchanged by control outcomes. Full training,
training replay, exact evaluation and independent exact review run sequentially
and stop on the first failed stage. The full study still cannot qualify a
general preflop model or deployment from these narrow endpoints alone.

See `LATER-WEIGHTED-AVERAGING-PLAN.md` and the `later-average-weight-control-v1`,
`later-average-fresh-control-v1`, and `later-average-exact-control-v1` JSON
registrations, results and reviews for reproducible evidence. Immutable large
training and policy artifacts remain under `S:/GTOpen-research/` with recorded
content hashes.
