# Anchored legal-pair interface

Research only. The ordinary app on 56708 and the frozen predictor stay unchanged.

## Protocol fixed before outcomes

1. Check exact legal class-pair probabilities by enumerating physical holdings.
   Check every selected action value against an independent Python oracle in
   deterministic two-, three- and eight-player test trees. Include folds,
   all-ins, learned continuations and already-folded seats' sunk costs.
2. At the first heads-up node, anchor a normalized legal-pair prior from the
   two arriving ranges. Keep that same normalizer through all descendants.
   Convert conditional hand values to counterfactual values with compatible
   opponent mass, including investments. Previously folded players' costs
   receive the same joint terminal probability. No common balancing offset.
3. Compare original Balanced, pair-interface Balanced, and pair-interface
   frozen candidate on the same fresh saved SB 0.5 zero-rake straddle config.
   Inspect 50 then 250 iterations, extend to 500/1,000 if useful and valid.
   Require finite normalized policies and total EV within 0.0002 bb of zero.
   Record GPU wall time; do not accept a performance regression for deployment
   merely because accounting passes. Target <=25% overhead for this screen.
4. Extract the resulting blind-call ranges and compare their conditional
   continuation predictions to new postflop references. Preserve both favorable
   and unfavorable hands. Accounting alone is not a poker-accuracy result.

The fresh reference screen uses two BB-call branches from candidate iteration
250, four previously unused flops from each of five texture strata (20 per
branch), and the same frozen half-pot postflop menu. Both GPU and independent
CPU best-response checks must meet 0.1% pot. The prospective accuracy screen
requires at least 15% lower weighted conditional-value error than original
Balanced in each branch. Report stratified bootstrap uncertainty and hand-level
regressions. These new ranges share a source scenario family with training;
this is a policy-shift stress test, not independent scenario generalization.
Also report equally weighted errors for the fixed 16 probe hands on both sides;
an average weighted improvement can conceal errors in rare but important hands.

## Meaning and limits

The two-player root's chance prior is exact for suit-symmetric hand classes.
Equities remain the existing Monte Carlo table. Larger games deliberately
reset the two-player joint distribution when only two players remain. They do
not model the cards held by previously folded players, nor correct all earlier
multiplayer decisions. This is an approximation, not exact eight-player dealing.

The anchor is computed from each current downward pass, not each descendant
terminal. Re-normalizing at each terminal would distort fold/call branch
probabilities. The learned model still depends on arriving ranges; reported
best-response gaps freeze those predictions and chance anchors. They are not
full-game exploitability guarantees. Small fixed-policy oracle checks establish
the interface implementation, not convergence of range-dependent learning.

Experimental saves retain ordinary Balanced metadata and must not be opened
in the live app. All inference/solve hooks require `preflop-research`.
