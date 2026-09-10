# Independent quality gates for an interactive preflop preview

Baseline: `ff54279`. Proposed before reviewing a candidate's results. These tolerances are engineering acceptance choices for an explicitly approximate preview, not established poker-accuracy guarantees. No benchmark, solve, or new physical-deal simulation was run to prepare this proposal.

## Measure useful decisions, not just cheaper iterations

Report time from a fresh configured game to a usable preview, including tree construction, feature/table preparation, device initialization, iterations, preview checkpoint, and first requested node. Report cold and warm separately. The target is at least **10x lower time to a preview that passes the gates**, against baseline on identical config/hardware and a predeclared baseline stopping target. Keep terminal throughput and iteration speed as separate supporting metrics. A tenfold faster iteration that needs twentyfold more iterations has not met the goal. A changed smaller tree must be disclosed and paired with its own action-menu coverage assessment.

At fixed wall-clock budgets (suggested 1, 3, 10, and 30 seconds after initialization, plus full end-to-end timestamps), capture the strategy. Evaluate these frozen strategies offline with the unchanged 1,024-particle coupled model. Do not let expensive reference evaluation time masquerade as interactive latency, and do not exclude mandatory candidate initialization from end-to-end latency. If the baseline never reaches its declared target within the run cap, report the observed speed curve and a bound, not a fabricated time-to-quality ratio.

## Three distinct tests

### A. Hard correctness and workflow gates

These are mandatory even for a rough preview:

- Every action probability and terminal value is finite; each per-hand legal action distribution sums to one within 1e-5, with no probability below -1e-7. Illegal actions have zero weight. Zero opponent reach yields zero counterfactual value, not NaN.
- Multiway terminal shares conserve one net-of-rake pot under the **candidate's declared chance model**. Check randomized normalized seat distributions at 3..9 players, including sparse ranges, and direct all-tied rank particles with expected share 1/n. Suggested tolerance: 2e-5 absolute share on f32 paths, 1e-10 on f64. Do not impose conservation on hero-by-hero physical conditional equities averaged under an incompatible independent prior.
- At a fixed node and identical inputs, locked/static profile policies, sizing routing, frozen-seat strategy sums, point-lock precedence, hero profile exemption, and adaptive threshold transitions retain their existing meanings. Compare exact policy arrays where the path uses unchanged code; any documented numeric conversion uses the existing engine tolerance. Arriving ranges can change when upstream learning changes and should not be confused with a policy-routing failure.
- CPU/GPU implementations of the **same preview model** agree within the existing terminal tolerance; neither is required to match full coupled bitwise. Saves identify the preview payoff/model version. Never silently resume full-solve regrets against changed payoffs; a transition requires a fresh learning state or a separately validated warm-start design.
- Cancellation never publishes a canceled zero gap as convergence. Preview results are labeled approximate and distinguish their own stopping diagnostic from a full coupled reference check. Restoring an existing save retains its original model. No arbitrary range widening or forced KQo rule is acceptable.

### B. Terminal equity and local call decisions

Use the existing compatible-deal references in `research/multiway-equity-audit/`. This costs no new Monte Carlo work for historical regression cases. Evaluate candidate equities for the exact saved arriving ranges and six existing hand classes. Preserve per-combo weights when constructing class probabilities; a class is not one equally likely concrete hand.

**Core proposed preview gate:** across the non-premium historical synthetic cases, overall mean absolute physical-reference error <=3 percentage points; each case mean <=4 pp; worst hand <=7 pp. For the original and rebuilt BB cases, mean <=3 pp and each of their five checked hands <=5 pp. Report all errors, not just pass/fail. These are deliberately looser than the full coupled reference and do not imply precise hand frequencies.

**BB closing-call guard:** at pot 7 bb, call cost 1 bb, final pot 8 bb, and current-pot rake 0.4 bb, use `call-minus-fold = 7.6 * equity - 1`. KQo must remain positive for both saved original and rebuilt ranges. Original physical equity is 20.7976% (about +0.581 bb without the old positional multiplier); rebuilt is 23.3060% (about +0.771 bb). The break-even equity is 13.1579%. Also report AQo/KQs/76s/AA values. This is a showdown-continuation check, not proof that calling dominates every raise or future-betting line. Do not confuse the saved action's total `to=2` with its incremental cost of 1.

**Overlap stress gate:** `premium_4way` is a separate red-flag case, not averaged into the core score. The existing full coupled model has a 15.85 pp worst physical error, including AA 52.55% versus physical 68.40%, so treating full coupled as truth would hide the defect. For preview acceptance require no more than +2 pp additional worst error over the fixed full coupled baseline and no more than +1 pp additional mean error, and explicitly retain the narrow-overlap limitation. A candidate meeting only this relative gate is not physically validated for premium-overlap decisions. If the candidate cannot recognize/exclude this region, label the preview globally approximate; do not invent calibrated confidence from low sample variance.

Monte Carlo references have sampling uncertainty. If a gate is within two reported reference half-widths of its boundary, mark it inconclusive and spend any extra validation budget only on that reference. Historical intervals exclude model error. Fresh physical checks reject the entire incompatible opponent tuple, split ties, and retain accepted counts, attempts, and uncertainty; never repair collisions by sequentially resampling just the later player. Bound attempts and return unsupported when no valid deal exists (for example three players all restricted to AA).

### C. Frozen-policy quality under the full coupled evaluator

On small paired full trees, solve a full coupled reference to the predeclared target (suggested summed learning-seat gap <=0.005 bb/hand; limit 500 iterations, check every 10). Record not-converged if capped. At candidate checkpoints, evaluate candidate average strategies using full coupled payoffs, preserving the same fixed/adaptive/frozen/hero constraints and the same action tree.

Primary proposed preview acceptance: **excess summed learning-seat BR gap <=0.02 bb/hand** over the paired full reference, on every small-tree case. Report each seat as well. A tiny gap measured only in the cheap model is not a quality gate. If the full reference misses its convergence target, the result is comparison with that checkpoint only, and cannot certify the absolute preview target.

For a clear unilateral-policy metric, freeze opponents at the full reference and report each learning seat's EV loss when its reference strategy is replaced by the candidate strategy, using full coupled evaluation. Proposed mean loss <=0.01 bb/hand and worst seat <=0.03 bb/hand. Keep this distinct from simultaneous all-player replacement, which can redistribute EV and conceal mutually exploitable play. Adaptive BR respects fixed ordinary actions; fixed/frozen seats' unrestricted bleed is reported separately and excluded from learning convergence.

At selected reached nodes, evaluate every legal action's full-reference continuation against the same opponent policy. Report reach-weighted expected action loss and its tail. For hands with >=0.25% of the actor's arriving mass and a clearly inferior action costing >0.1 bb versus the best, candidate probability on such actions should be <=10%. Near ties are judged by EV loss, not forced frequency agreement. Show unconditional reach and conditional hand mass so a tiny off-path branch cannot dominate the aggregate or disappear from the stress report. Exact action-frequency similarity is a secondary descriptive metric, not a hard gate.

## Corpus and separation from fitting

`corpus.json` registers historical regression references and new independent range/tree cases. All historical audits have already been seen in prior work; call them regressions, not blind holdout. The original BB hand is a must-pass regression and may be used during development, but it cannot establish generalization alone.

Reserve the new asymmetric range cases and two tree configurations until a candidate family/sample count is fixed. Do not fit parameters or choose a lucky seed on their outputs. If a gate fails and the implementation is tuned against it, promote that case to development and record that the independent set has been consumed. A four-hour pass can deliver useful regression evidence without claiming a statistically representative population study.

Use the existing six-seat modeled fixture only for end-to-end timing and a few frozen checkpoints after small cases pass; it is about 2.5 GB and should not be the inner validation loop. The seven-seat resolved BB node contains final strategy/reaches but is **not** a complete native reference game. The rebuilt iteration-378 node, not the resolved iteration-578 node, matches the existing million-deal physical reference; do not compare different arriving ranges.

## Bounded order for this pass

1. Inspect/reuse historical physical references; run candidate terminal calculations and invariants first. Reject coarse methods recreating the product model's cheap-call collapse immediately.
2. Run three small trees covering all-solver, fixed/frozen, and adaptive semantics. Use synthetic policies specified in the manifest; they are controls, not claimed empirical players. Reuse existing checkpoint profile/lock tests for unchanged routing.
3. Freeze the candidate, evaluate the new asymmetric cases (initially against full coupled; physical Monte Carlo only for a bounded six hands x four cases at 100,000 accepted deals if remaining time permits).
4. Measure two representative large end-to-end workflows only after quality survives. Keep a predeclared total validation time cap; omit unrun claims instead of dropping failed cases.

The new physical cases are not prerequisites to report a limited experimental preview, but are required before claiming improved physical-deal accuracy beyond historical regressions. Heads-up calibrated continuation still has its existing embedded-rake and future-betting limitations. A faster multiway model does not validate those independently.
