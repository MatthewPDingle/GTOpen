# Comparing GTOpen with six Wizard decisions

**Status: baseline running, 19 September 2026. No comparison result yet.**

This study uses the six situations and 48 hand probes captured in
[the Wizard benchmark](../wizard-benchmark-20260918/README.md). It runs a
separate GPU process on port 56710 and leaves the user's session on 56708 intact.

The question is whether GTOpen's different ranges cause meaningful decision
costs, or mostly choose different mixtures between nearly equal actions.
We compare action values as well as frequencies. These selected hands are a
diagnostic sample, not an estimate of the entire strategy's exploitability.

## What matches

Eight seats, 200 original-bb stacks, SB 0.5, BB 1, straddle 2, 4% rake with a
6bb cap, 6bb opens, and the six inspected response menus. The [tree audit](TREE-AUDIT.md)
records remaining differences, including cold calls, SB completion and later
position-dependent sizes. Wizard's no-flop-no-drop convention is unverified.

Including Wizard's five-bet jam requires a larger tree than the old three-raise
configuration: 2,890,211 nodes. This run uses the existing production executable,
Balanced heads-up continuation and coupled-deck-v1 multiway values. It does not
train a model or change the application.

## Fixed procedure

1. Run to an internal total BR gap below 0.005bb, at most 3,000 iterations.
2. Save the baseline and all six nodes.
3. Run 250 more iterations and measure whether the selected decisions change.
4. Score the 48 probes against Wizard's displayed action values.
5. Read GTOpen's own action values from the saved game and report the limitations.

`run.py` owns the isolated solve. `postprocess.py` waits for that specific
existing runner, then runs `finish.py`, `plot.py` and `report.py` once. It does
not start another solve. `postprocess-status.json` records readiness or failure.
The large `.gtop` checkpoints remain local under `saves/preflop/`; hashes and
compact evidence belong in this directory. `RESULTS.md` will contain generated
tables; this README will be updated after review.

The reserved 100bb Wizard cases remain unopened. This is a baseline measurement,
not a parameter search or a production deployment.
