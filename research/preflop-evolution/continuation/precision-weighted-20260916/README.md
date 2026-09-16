# N08: fixed precision weighting for expanded training data

Specified 16 September before N03 training completes. The historical sampling
diagnostic found much more variation in 20-board than 100-board labels. Test
whether giving them equal case weight harms the expanded fit. This changes
training weights only: the 104 features, targets, inference equation and ridge
penalty per effective case remain unchanged.

Use all 62 training cases, leave each source family out in full, and score only
the unchanged original 26 validation cases. Compare two fixed weights for each
case: sqrt(board_count/100) and board_count/100. The same-data control gives
every case weight one. Normalize the regression objective by summed case
weight and use penalty 0.1 divided by that same sum. This preserves the old
fit when all cases have 100 boards and makes splitting a case into identical
weighted copies algebraically neutral.

These weights are heuristics motivated by reference precision, not a claim
that samples are independent or their variances exactly follow 1/N. Board
identities are shared within source sets; case-specific variance also differs.
Do not add choices or tune weights after outcomes.

An eligible model must improve equal-family mean weighted hand-value MAE by
at least 5% relative to both the same-62-data unweighted control and N06's
original-26-data ridge control, with no family more than 5% worse than either.
Choose the lowest mean among eligible models. Freeze before a separately
specified, fresh-board evaluation disjoint from N03 and earlier test boards.
No held-out evaluation labels enter this screen. GPU oracle, runtime and
changed-policy checks remain necessary. Port 56708 is untouched.
