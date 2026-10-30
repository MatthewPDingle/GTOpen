# Prospective comparison of the matched showdown-control trials

This protocol is written before drawing its evaluation stream. Training is still running. The evaluation code is a candidate until the full-bank control and its independent readback pass.

## Question and scope

Does the fixed, unbiased showdown-based correction used in BB root learning produce more reproducible ranges or better complete policies at the same training budget? Compare it with the otherwise matched postflop-action-integrated baseline.

The game remains the registered restricted BB-versus-BTN 200 bb context in `bb-context-candidate.json`. This does not test all positions, stack depths, full-size trees, multiway play, or agreement with a full GTO Wizard solution. Evaluation uses ordinary native game payoffs. The correction is a learning-target device and never an evaluation payoff adjustment.

## Frozen policies

Use all four registered training arms, in this order:

1. `9266201-baseline`
2. `9266201-corrected`
3. `9266301-baseline`
4. `9266301-corrected`

Every arm must complete all 78 updates and pass independent scalar training readback. Average all played generations 0–77 with the existing iteration weights 1–78 and own-action reach weighting. Exclude generation 78, which was fitted but never played. Do not select a checkpoint, seed, hand class, or opponent pairing based on the resulting ranges or payoffs.

Baseline models retain the existing validated inference representation. Corrected models retain their separate version-8 type and frozen coefficient identity.

## Implementation control before fresh sampling

Reuse the first 64 previously inspected deals from `action-integrated-replication-v1`, authenticated through its original metric and artifact hashes. Evaluate two batches of 32 with all four full banks. At every exported query in both batches, compare each bank's GPU probabilities with its CPU counterpart to tolerance 1e-10. Check all initial policies separately. The new corrected shared-query wrapper must pass here; passing a small old bank is insufficient.

Archive both batches with the qualified lossless columnar writer. Independently restore and check original byte identities, chance data, profile crossings, legal probabilities, payoff conservation, paired differences, initial-policy summaries, and interval arithmetic. No fresh held-out deals are used for this control. Do not use its poker outcomes to choose models or alter the fixed evaluation budget.

## Fresh evaluation

The fixed seed is **9267201**. Draw **65,536 common physical deals**, in batches of 32, from the unchanged `PhysicalDeals` full-deck entry distribution. Register model/evidence/source hashes and resource admission before the first draw. Preserve initial and final sampler states.

Within each training seed, evaluate all four pairings: baseline BB versus baseline BTN, baseline BB versus corrected BTN, corrected BB versus baseline BTN, and corrected BB versus corrected BTN. Both training seeds share the same evaluation deals. There are eight profiles and eight paired player-gain contrasts in total.

Use the existing native full-policy evaluator with its conditional preflop all-in estimator and sampled-board postflop outcomes. Evaluate every legal action under the complete frozen policies; do not force or filter root actions. Shared query preparation may change only computation reuse, not probabilities, action histories, transports, or payoffs.

## Analysis and interpretation

For each seed, report the corrected BB's gain against each fixed BTN policy and the corrected BTN's gain against each fixed BB policy. Report every contrast, including unfavorable ones. Units are big blinds per entry into this research game.

The payoff-difference bounds are plus/minus `2 * stack + dead_money`. Use the existing two-sided bounded empirical-Bernstein intervals with Bonferroni adjustment across all eight contrasts, family error probability 0.05, and **one final look at 65,536 deals**. Report ordinary standard errors alongside these conservative simultaneous intervals. No outcome-based early stopping, interim promotion, sample-size extension, or best-result selection is permitted within this run.

An interval entirely above zero supports a gain for that specific player replacement against that particular fixed opponent. An interval entirely below zero supports harm for that comparison. An interval spanning zero is inconclusive; it does not establish equivalence. A favorable result for one seed or one matchup is not a general preflop-accuracy claim. Previous comparisons suggest effects may be smaller than these intervals can resolve; that limitation will be reported rather than hidden by a narrower uncertainty calculation.

Also report entry-weighted total variation between the two baseline root policies and between the two corrected root policies, their difference, all per-class differences, and the number of classes with different most-frequent actions. This two-seed stability comparison is descriptive. Stability alone does not establish poker strength or equilibrium accuracy.

## Storage and execution gates

Control has a 60 MB output cap. Before fresh sampling, project archive storage from both full-bank control batches to 65,536 deals, add a 25% margin and 64 MB for active scratch and metadata, and refuse projections above 2.5 GB. Then remeasure allocated research storage and require the projection plus the existing 2 GB metadata reserve to fit the 800 GB global ceiling. A successful codec test is not storage admission. No legacy evidence may be deleted or recompressed to make this run fit.

Preserve the production app and honor the research lock, user-activity checks, host/GPU/disk reserves, and the registered time/output caps. The control time ceiling is four hours; the fresh evaluation ceiling is 24 hours. Resource interruption leaves an incomplete run and retained evidence, not a valid fixed-budget result. Resume or retention changes require a separately documented, deterministic procedure; do not silently restart a failed attempt.

After evaluation, the independent CPU reader reconstructs the chance stream and all eight paired statistics from exact restored evidence, without calling the evaluation accumulator. Native poker evaluation and neural fitting are not independently reimplemented by that reader. Production remains unchanged until broader scientific evidence justifies a separate deployment decision.
