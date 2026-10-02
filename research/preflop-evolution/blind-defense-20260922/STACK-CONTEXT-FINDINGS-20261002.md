# Stack-depth preflop learning: findings, 2 October 2026

The comparison and independent analysis are complete. Adding 25 river hand-versus-board inputs **has not established a consistent improvement in preflop ranges**. The registered improvement criterion failed, and supported hand-level responses reveal substantial variation between independent runs. These experimental weights are not ready to replace GTOpen's production model.

## What was compared

Both models learn the existing heads-up tree from preflop through the river. The candidate has 387 inputs rather than the baseline's 362; the extra inputs describe the hand relative to the river board and are zero before the river. They can affect preflop decisions through learned continuation values and shared network weights. This is separate from the earlier restricted terminal-river Fold/Call diagnostic.

The entry is BB facing a BTN min-raise to 2bb, with SB folded, 0.5bb dead money, and 5% rake capped at 2bb. The inherited 200bb BTN opening range is held fixed at every stack depth. This study therefore does not establish correct openings at other depths, other positions, limped pots, multiway play, or agreement with GTO Wizard.

There are two independent training runs, A and B, each with a baseline and candidate bank. All 64 played models per bank are retained with the original generation weights; no checkpoint was chosen using the test results. Five fitting depths are 20, 40, 100, 200 and 400bb. The 60 and 150bb depths were withheld from fitting. Testing used 4,096 fresh physical deals per depth: **28,672 total**, eight crossed profiles at each depth, and 56 planned comparisons. Each payoff comparison replaces one player while holding its opponent fixed.

The preflop menu remains restricted: BB may fold, call to 2bb, 3-bet to 6bb or jam. BTN may call, 4-bet to 18bb or jam after a 3-bet. **BB facing that 18bb 4-bet has only Fold/Call: no 5-bet or shove.** At 20bb the 18bb action becomes a jam. Solving through every street does not mean every preflop raise sequence is available.

## Payoff evidence did not qualify an improvement

Of the 56 comparisons, **38 mean gains are positive and 18 are negative**. All 56 original stack-specific uncertainty intervals include zero. All eight equal-depth pooled intervals also include zero. Six pooled point estimates favor the candidate and two favor the baseline, but none establishes a gain under the original decision rule.

The rule required all eight pooled lower bounds above zero and no negative per-depth mean. We retained the original simultaneous bounded empirical-Bernstein intervals, family alpha 0.05, and one final look. We did not replace them with narrower exploratory intervals after seeing the results. Pooled means range from -0.0484% to +0.0974% of starting stack per entry, while their intervals extend roughly two percentage points in each direction. These are stack-normalized payoff units, **not changes in hand-frequency percentages or ordinary cash-game win rates**.

At both withheld depths, the BB replacement has positive point estimates in A and B, while the BTN replacement is positive in A and negative in B. At 200bb all eight point estimates are positive, but their primary intervals still include zero. The result is mixed and inconclusive; it proves neither improvement, equivalence nor harm.

The [complete numerical report](stack-context-final-report-v3.md) retains every comparison, pooled interval, paired-loss tail and payoff extreme. Its [figure](stack-context-final-report-v3.png) shows the original intervals. Fixed-opponent returns are not a best-response bound or an equilibrium certificate.

## The ranges are still unstable

The table gives BB's total flat-call frequency facing the initial BTN min-raise. Calling means adding **1bb**, to make a total of 2bb. Root own-history support is full for every hand, so these differences cannot be dismissed as unsupported downstream display values.

| Starting stack | A baseline | A candidate | B baseline | B candidate |
| --- | ---: | ---: | ---: | ---: |
| 20 | 38.36% | 36.39% | 41.84% | 38.33% |
| 40 | 36.08% | 40.25% | 43.64% | 43.44% |
| 60 (held out) | 54.01% | 40.38% | 44.35% | 40.37% |
| 100 | 34.40% | 34.01% | 29.40% | 30.80% |
| 150 (held out) | 49.61% | 32.37% | 45.13% | 38.18% |
| 200 | 45.83% | 33.48% | 38.51% | 50.33% |
| 400 | 34.77% | 40.38% | 27.05% | 21.15% |

The candidate calls less at 20, 60 and 150bb in both runs. At 200bb it calls substantially less in A but more in B; at 400bb the direction also differs between runs. More river inputs have not produced a stable, consistently broader calling range.

Individual hands at the **200bb root** show the same issue. These are flat-call frequencies; the remainder includes folds and raises, rather than automatically being folds.

| Hand | A baseline | A candidate | B baseline | B candidate |
| --- | ---: | ---: | ---: | ---: |
| KQo | 88.43% | 25.78% | 22.39% | 61.01% |
| JTs | 2.50% | 48.15% | 99.14% | 10.97% |
| ATs | 2.62% | 42.96% | 0.01% | 42.65% |

ATs gains more flat-calling in both runs, but KQo and JTs change very differently. A few attractive-looking cells do not establish better ranges. All 169 classes at all 136 exported decision nodes remain in the [full range summary](stack-context-final-range-summary-v1.json); no support cutoff or hand-selection filter was used to generate it.

## A stronger warning: supported premium-hand folds

At 400bb, after BB raises to 6bb and BTN raises to 18bb, AA's response differs dramatically:

| Bank | AA call frequency | AA own-history support / 2080 |
| --- | ---: | ---: |
| A baseline | 51.13% | 99.29% |
| A candidate | 99.99% | 99.06% |
| B baseline | 70.90% | 98.68% |
| B candidate | 8.84% | 87.58% |

Run B's candidate folds AA **91.16%** of the time here. AA has 87.58% own-history mixture support and 2.80% of this node's arriving range. The same branch's total entry reach is 3.16%. This is not an almost-never-arriving hand. Baseline A also folds AA frequently, so the concern predates the added features.

This is a serious learning/policy-quality diagnostic. The readback confirms that these are the frozen models' actual probabilities; it does not certify that the recommendations are sensible. We have not independently measured AA's Call-versus-Fold action values at this branch, so this analysis does not attribute the problem to a proven payoff bug or a specific training defect. The missing 5-bet option is a separate tree limitation and does not by itself explain these folds.

Some apparently crude downstream frequencies have a different explanation. At 200bb in B, 72o shows roughly 50% calling at this 4-bet response, but its own-history support is only about 0.0120%, and its share of the arriving range is below 0.001%. That cell is not a robust played-range recommendation. **Low-support artifacts and supported premium-hand errors must be diagnosed separately.** Own-history support is a model-mixture reach quantity, not an observed hand count, confidence interval or joint node reach.

## What verification established

The corrected independent audit finished successfully in approximately 2 hours 29 minutes. It reconstructed 256 training chance cycles, checked all 896 test archives, replayed 28 complete preflop catalogs against CPU references, checked the first and last 32-deal postflop batches at each depth, and independently checked all 56 comparisons. It did not replay every postflop policy row. It shares the native payoff oracle with the evaluator, so it is not an independent implementation of poker payoffs. Test deals are fresh full-deck draws, but training and test boards are not strictly disjoint.

The initial audit failed on recognizing four already-documented interruption recoveries. That failed evidence remains preserved. A separately qualified correction recognized only those exact authenticated recoveries, retained the original audit deadline and numerical rules, and completed successfully. Neither the scientific trial nor its test sample was retried. Verification establishes evidence consistency, which is distinct from good poker strategy.

## Recommended next work

1. Trace the supported AA continuation through native action values, training targets, branch reach and the final averaged policy. Check the value scale/sign, legal actions and learning update at this concrete branch before spending more days on another large run. These are proposed diagnostics, not completed tests or a proven cause.
2. Address avoidable CPU preparation work with equivalence checks. Source inspection shows that `stack_context_full_policy_v1.predict` validates and reconstructs fitted-context tables for each model/query. Authenticating and preparing immutable models once may reduce idle gaps; the benefit still needs profiling. The completed audit was deliberately a CPU reference check, so low GPU use during that phase was expected.
3. After the value/policy diagnosis, use a small, explicitly registered stability comparison before another expensive full comparison. Assess independent-run agreement and supported premium decisions as well as payoff evidence. A future tree with 5-bets and stack-appropriate entry ranges needs its own qualified comparison; those changes must not be retroactively credited to this one.

These findings narrow the next problem to learning/value reliability and range stability. They do not establish a dead end for learned preflop models. **Production on port 56708 has not been changed, and the broad goal of accurate flexible preflop ranges remains open.**
