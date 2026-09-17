# Hold'em call-versus-fold audit

Read the frozen candidate heads-up 40bb, iteration-1500 save from N27. Examine
BB facing SB's 2.5bb open, and the immediate call continuation (path [2,1]):
BB out of position, 5bb pot, 37.5bb remaining, zero rake. Use this small existing
fixture rather than a new solve or a changed model. This is an accuracy audit,
not a new preflop convergence run or deployment candidate.

## Model and units

Evaluate the save with the unchanged N15 model through the validated N20
full-precision GPU interface. This experimental model is not deployed on 56708.
Check its call-minus-fold values against the independent Python implementation
within 0.00002bb. Folding loses the already posted 1bb in hand-start units;
calling costs another 1.5bb. Hence call advantage over fold = gross postflop
value minus 1.5bb. Use the same original calling and opening ranges for every
postflop reference. Preserve positive support with nine significant digits;
no support floor, range widening, model fitting, or selective hand deletion.
Also evaluate the interface's Balanced baseline on these exact same ranges.

## References and sample

Before generating labels, freeze 50 canonical flops: ten from each of five
pairing/suit strata, selected by a fixed SHA256 order from all 1,755 canonical
flops. Use iso_weight / inclusion_probability and hand-compatible pair mass.
The whole population is eligible. Some boards may overlap previous training
panels; these heads-up ranges and labels are new, but this is not a claim of
board-disjoint validation. No ranking or selection uses reference values.

Match the model's training abstraction: 50%-pot bets/donks, 100%-pot raises,
one raise per street, no extra jam, 85% all-in conversion, all turn and river
runouts. Use the existing hashed GPU reference executable, require both GPU
and independently transported CPU-policy gaps <=0.1% pot within 2,000 iterations.
Retain failed jobs and stop instead of treating them as valid references.
This finite tree and sampled flop average are not full-game Hold'em truth.

## Evaluation, fixed before labels

Report all 169 classes with coverage, model call advantage, reference call
advantage, and within-reference per-hand best-response gain. Highlight these
predeclared familiar hands: KQo, KJo, QJo, JTo, A5s, A9o, T9s, 98s, 76s, 22.
Do not infer well-measured values from the tiny nonzero support of near-pure
raises/folds. Flag BB call frequency below 0.0001 as sparse support, and
aggregate per-hand BR gains above 0.025bb as unsettled.

Compute direct board-averaged EV and an equity-control-variate estimate using
the unchanged cached preflop equity. Report both; cached-equity Monte Carlo
error is not included in board confidence intervals. Use 5,000 paired,
within-stratum bootstrap samples, seed 20260917, for exploratory 95% intervals.
These intervals are not simultaneous confidence guarantees across 169 hands.
Call a sign disagreement clear only when both intervals lie beyond +/-0.05bb
opposite a model advantage beyond +/-0.05bb, support is adequate, and the
reference hand passes the 0.025bb BR-gain screen. Otherwise mark it uncertain.

This tests call versus fold only; a profitable call may still be worse than a
3-bet. Postflop best responses evaluate the reference opponent policy, not an
independent best response against the entire saved preflop game. Do not turn
this local audit into a full-game exploitability claim or a matching-Wizard claim.

## Isolation and retention

Use offline executables and a new output directory. Check the live app before
each reference job; do not start a new one during a live solve. No POSTs, restart,
deployment, or save changes on port 56708. Preserve inputs, failures and output
hashes. Push the completed audit and report to GitHub, excluding binaries/saves.
