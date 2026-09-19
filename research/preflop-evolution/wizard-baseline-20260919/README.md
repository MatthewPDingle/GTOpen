# Comparing GTOpen with six Wizard decisions

**Status: completed and reviewed, 19 September 2026. No model deployed.**

The baseline reached its internal target at 750 iterations (85.6 minutes),
then completed the planned 250-iteration stability check (18.5 minutes).
The final internal total BR gap is 0.002861bb. Both checkpoints are saved.

## What we learned

The differences are a mixture of nearly equivalent action choices and more
substantial disagreements. Matching every colored square is not a good target.

- UTG opens 13.99% in GTOpen versus 13.4% in Wizard. All eight selected opening
  probes have local decision costs below 0.001bb at Wizard's displayed precision,
  despite conspicuous differences in which small pairs and suited hands open.
- Calling is not universally too tight in this configuration. GTOpen calls
  7.48% from BB versus Wizard's 2.8%, and 22.51% from the closing straddler
  versus 13.3%. LJ, however, calls effectively 0% versus 1.5%.
- Seven of the 48 deliberately selected probes have local costs above 0.05bb.
  Five are UTG responding to LJ's 3-bet; the other two are QJs 3-betting from
  SB and BB (about 0.52bb and 0.35bb respectively).
- The largest discrepancy is AA facing the 3-bet: GTOpen jams about 64.5%,
  whereas Wizard uses the smaller 4-bet. Under Wizard's continuation, that
  mixture costs about 4.97bb at this decision. GTOpen's own values put the
  smaller 4-bet and jam almost level (40.120bb and 40.104bb). The two models
  disagree about the value of the alternatives, not just their display colors.
- In the same 3-bet response, GTOpen mostly folds 55 and 76s where Wizard calls;
  it almost always calls QJs where Wizard folds. A global wider/tighter
  adjustment cannot address both directions.

These costs substitute GTOpen's current mixture into Wizard's displayed
one-decision action values, then follow Wizard continuation. They are not
GTOpen's exploitability or an estimate of a player's win-rate loss. Values
rounded to 0.00bb do not establish exact equality. These selected hands are
not a representative sample of the whole range.

## Stability and what remains uncertain

Across the five opening/first-defense nodes, selected-hand strategy drift
during the extra iterations was below one percentage point of total variation.
The 3-bet response was less settled: 76s moved 7.94 points and A5s 7.47 points.
The 76s diagnostic cost fell from about 2.82bb to 2.08bb, so its exact final
mix should not be treated as stable. Its GTOpen call value is still negative
(-0.221bb) versus Wizard's positive displayed value (+0.55bb). A small global
gap does not guarantee a fully settled rare decision.

The 3-bet response is reached with different opening ranges: GTOpen opens
76s about 77.6% versus Wizard's 9.08%. Opponent strategies differ too. Own-value
differences therefore do not isolate continuation-model error. The extra
cold-call branches excluded by Wizard are used at 0.19%-0.89%, depending on
seat; they cannot be described as absent. Other differences are in TREE-AUDIT.md.

## Recommended next experiment

Audit one heads-up continuation after UTG calls LJ's 3-bet, using fixed,
identical incoming ranges, pot, stacks, rake and postflop action menus. Compare
GTOpen's cheap continuation estimates with explicit postflop solves over a
predeclared board sample, with uncertainty and hand-level readouts for 55,
76s, QJs and AA. This can test whether the approximation misprices these hands
without confusing that effect with different opponent ranges. It is a bounded
diagnostic, not a proposal to train another broad model or adjust frequencies
to match Wizard. Follow up AA's 4-bet-versus-jam choice by auditing the opponent
response separately; a call-only continuation test cannot explain it by itself.

Keep the existing saves for any separately authorized convergence extension.
Do not replace this completed baseline or inspect the reserved 100bb cases.

## Evidence and checks

See [RESULTS.md](RESULTS.md) for frequencies, hand-level costs, own action
values and plots; `comparison-with-own-values.json` contains the exact readouts.
All six inspected menus and all 48 probes passed the extraction checks.
Five baseline tests and seven reference-scoring tests passed. The production
session on 56708 was identical before and after the study. Saved-game hashes
are recorded in `save-provenance.json`; binary saves remain local.

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
compact evidence belong in this directory. Progress files retain each measured
checkpoint and the final status, rather than repeated status polls.

The reserved 100bb Wizard cases remain unopened. This is a baseline measurement,
not a parameter search or a production deployment.
