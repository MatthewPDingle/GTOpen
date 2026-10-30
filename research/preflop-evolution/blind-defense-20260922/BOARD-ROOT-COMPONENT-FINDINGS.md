# Preflop root-value decomposition

The board-first prototype now separates the registered BB root's action values
into exact preflop terms and board-dependent continuation terms. The controls
passed; training and production remain unchanged.

Fold remains exactly -1 bb. Initial shove retains its existing full-population
all-in matrix expectation. For a 3-bet, the following terms are also integrated
over the original private-hand population without board sampling: BTN folds;
BB folds to a 4-bet; and BTN shoves followed by BB's fold or call. The two
all-in endpoints have identical investments and economics, which is checked.

The variable terms are BB's flat-call postflop branch, BTN calling the 3-bet,
and BB calling BTN's 4-bet. Each retains the appropriate own-hand preflop
probability and opponent reach before postflop evaluation.

## Checks and results

- Native observations cover all 1,326 physical holdings at all five preflop
  decisions (6,630 rows). Their own-action ancestry is reconstructed and
  validated before using the existing weighted-policy inference function.
- The saved generation-77 policy is exactly constant across suits within each
  preflop class. This is verified rather than assumed for matrix integration.
- All exact components match an independent scalar class-pair reduction;
  maximum absolute error is 1.07e-14 bb.
- Board components use every supported holding on the tested board: 1,081 BB
  holdings and 566 BTN holdings. An explicit joint-pair forward traversal follows
  the preflop child pointers and then pays the postflop terminals from actual
  investments, independently of the compact component combination.
- All six cases pass: saved policy, BTN call, BTN 4-bet/BB call, BTN 4-bet/BB
  fold, BTN fold, and BTN jam. Maximum class-value error is 1.60e-13 bb.
- Preflop-only lines have exactly zero variable raise contribution. Both fold
  and initial shove have exactly zero board contribution in every case.

The control took 38.75 seconds on CPU, with no GPU use. This includes repeated
independent dense reference traversals and is not a trainer timing estimate.
Sources and input artifacts are hash-bound in
`board-root-components-control-v1-result.json`.

## Chance weighting

For a uniform public-board proposal, the contribution includes the ratio
`C(52,5) / C(48,5)`. Independently counting sorted flops with ordered turn and
river produces the same ratio: `C(52,3)*49*48 / (C(48,3)*45*44)`.

The numerator sums original private weights over compatible holdings. It is
divided by the **original** joint mass and original BB entry-class mass.
Renormalizing each board's surviving range would change the game and is not
done. Board-impossible holdings contribute zero on that draw, rather than
receiving an invented replacement hand.

## Interpretation and next gate

This is a one-board value identity plus exact private-population terms, not a
multi-board accuracy result. The earlier rational small-deck control supports
the change in integration order; neither control estimates the variance of the
real-poker estimator. The saved postflop network is also not the complete
78-policy behavioral average.

The next useful experiment is a fixed-policy, fixed-sample-count precision and
cost comparison across fresh boards and private-first deals. Freeze the model,
chance seeds, sample counts, comparisons and resource limits before running.
Report class-level and entry-weighted uncertainty as well as elapsed time.
The original private-first reference must keep its original chance law; a
board-conditioned private sampler would answer a different timing question.
Use exact preflop terms in both arms so the comparison measures the variable
continuation estimator rather than rewarding removal of avoidable all-in noise.

Do not promote this into training until that comparison establishes useful
precision per unit time. The current registered stratified study's final
evaluation remains the priority and is unaffected by this prototype.
