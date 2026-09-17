# Call versus 3-bet: fixed-policy Hold'em audit

Use the same frozen 40bb heads-up candidate save, BB facing SB's 2.5bb open,
as the completed call/fold audit. Compare calling with raising to 7.5bb.
Keep every preflop strategy fixed, including SB's folds, calls, 4-bets to
22.5bb and jams, and BB's later responses. Do not optimize a best response
or fit a new model. Export the entire small tree read-only and verify its
independent action-value backup against the previously frozen native GPU
outputs for both candidate and Balanced, within 0.00002bb counterfactual EV.

## Reference labels

Reuse all 50 call-pot references without changing them. Generate the same
50 boards for each additional non-all-in leaf: a called 3-bet (15bb pot,
32.5bb behind) and a called 4-bet (45bb pot, 17.5bb behind). This is 100 new
reference solves. Preserve the saved leaf ranges, including tiny positive
support; use the same nine-significant-digit serialization as the first audit.

Keep the previous finite postflop menu: 50%-pot bets/donks, 100%-pot raises,
one raise per street, no extra jam, 85% all-in conversion, zero rake, and
all turn/river runouts. Require both GPU and transported full-enumeration
CPU-policy gaps <=0.1% pot within 2,000 iterations. Stop and retain failures.
Fold payoffs are exact. All-in equity uses the same cached approximate
equity in both comparisons; it is not newly enumerated physical-deal truth.

The frozen predictor applies only to SPR 1 through 20. The called 4-bet
has SPR below one and therefore uses the existing Balanced fallback in
the model comparison. Report this distinction, rather than attributing
the entire 3-bet branch to the learned model.

## Aggregation and uncertainty

At each leaf, estimate gross BB postflop EV with canonical multiplicity /
inclusion probability and compatible hand-pair mass. Compute both direct
and equity-control-variate estimates, as in the call audit. Propagate those
values through the whole preflop subtree with exact class-compatible chance,
the frozen opponent's action frequencies, and BB's frozen subsequent choices.
Deduct investments exactly once. Normalize values to BB's compatible opener
range at the decision. The final comparison is 3-bet minus call; positive
favors raising. Also report both actions relative to folding and a contribution
breakdown for opponent folds, called 3-bets, 4-bet responses and jam responses.

Use 5,000 paired within-stratum bootstrap resamples, seed 20260918. The same
board indices must be drawn for all three leaf contexts, preserving sampling
covariance. Cached-equity error is not included in the exploratory 95% intervals.
They are not simultaneous confidence guarantees across 169 classes.

Report every class and the same fixed familiar probes: KQo, KJo, QJo, JTo,
A5s, A9o, T9s, 98s, 76s, 22. Require saved BB call AND 3-bet frequencies
at least 0.0001 for a well-supported comparison. Propagate each reference
hand's nonnegative postflop best-response gain through the relevant branch;
require this gain <=0.025bb for EACH candidate action. This screen concerns
postflop reference quality, not a full-game exploitability certificate.

A clear sign disagreement requires a model 3-bet-minus-call value beyond
+/-0.05bb, both reference 95% intervals wholly beyond 0.05bb on the opposite
side, and both support/quality screens. Otherwise mark it uncertain or
unsupported. No probability floor, reweighting to make hands look realistic,
retuning, selective hand deletion, or change in these gates after labels.

## Scope and isolation

This evaluates two first actions with frozen later preflop policies and
separately solved postflop continuations. It is not a full-game best response,
a new equilibrium, proof of optimal mixing, or a Wizard comparison. A changed
3-bet strategy could change the opponent's best response; this audit does
not model that adaptation. All references use one finite postflop abstraction.
The boards are reused intentionally, not a fresh board-disjoint holdout.

Do not change, restart, load a save into, or deploy to port 56708. Check the
app is idle before starting each offline GPU reference. Freeze source,
models, caches, binaries, exports, and reused labels by hash before new
labels. Retain full results and independent tests; push the finished audit
to GitHub without executable binaries or saved games.
