# Independent 190-flop confirmation: weighting advantage replicated

All 570 accepted evaluations and the independent analysis are complete. The weighted 112-board policy again has the lowest summed best-response gain, and its advantage survives every single-board omission in this larger panel. This supports using it as the next research baseline. It does not establish production readiness or broad preflop accuracy.

## Main result

Three unchanged preflop policies were evaluated on the same 190 new flops, with 2,000 postflop iterations per policy per board. These boards were excluded from training and from the earlier 95-board test.

Full deviation gain is the sum of both players' gains from unilateral best responses in this restricted game. Lower is better. It is not a policy-versus-policy EV advantage, expected loss per played hand, or distance to GTO Wizard.

| Frozen training policy | Full deviation gain (bb) | Postflop residual (bb) | Player 0 gap | Player 1 gap |
|---|---:|---:|---:|---:|
| Weighted 112 boards | 0.331970 | 0.000465 | 0.284510 | 0.047460 |
| Equal-weight 112 boards | 0.411767 | 0.000568 | 0.325972 | 0.085794 |
| Earlier 47-board reference | 0.542750 | 0.000145 | 0.393924 | 0.148826 |

Weighted training's gap is **19.4% lower than equal weighting** (0.079797 bb difference), and **38.8% lower than the earlier reference** (0.210780 bb difference). Equal weighting is 24.1% below the earlier reference. All aggregate postflop residuals are comfortably below the registered 0.01 bb threshold, so unfinished postflop response solving is not the main explanation for these differences.

Weighted versus equal is the controlled comparison: identical training boards, executable, actions and iteration budget, with weights as the intended difference. Comparison with the earlier 47-board reference also changes training-update treatment. Its improvement cannot be attributed solely to more boards or better weighting.

## Stability and the previous test

A paired leave-one-board-out analysis recomputed the combined terminal counterfactual values and preflop best responses after omitting each of the 190 boards in turn. All sources omit the same board. This is a sensitivity check, not a confidence interval or a reason to remove an inconvenient board.

| Comparison (first minus second) | Full-panel difference (bb) | Range across 190 omissions (bb) | Omissions favoring first |
|---|---:|---:|---:|
| Weighted minus equal | -0.079797 | -0.096015 to -0.064858 | 190 / 190 |
| Weighted minus earlier reference | -0.210780 | -0.302858 to -0.149447 | 190 / 190 |
| Equal minus earlier reference | -0.130983 | -0.206843 to -0.077513 | 190 / 190 |

The earlier 95-board panel also favored weighted training, by 4.8% against equal weighting, but omitting a single board could reverse that ordering. The new result replicates the direction and is less sensitive to any single board. It does not imply a universal 19.4% gain.

The eligible populations differ: the original panel represents 15,320 physical flops; this disjoint confirmation panel represents 14,036 of 22,100 physical flops. Keep their results separate. Do not treat the absolute change from the old panel's 0.467 bb to this panel's 0.332 bb as further improvement in the policy: the policy did not change. Do not combine these samples with arbitrary equal weights.

## Remaining errors and the next useful step

The weighted policy's training gap was approximately 0.005 bb, while unseen-board full deviation is approximately 0.332 bb here. The result is better, but substantial generalization error remains. Most of the remaining gap is on player 0's side. Its largest hand-class contributions are 76s (0.044981 bb), 66 (0.032175), A9s (0.024816), ATs (0.022188), AJs (0.017057) and AKo (0.015212). Player 1's largest contributors are JJ and QQ. These contributions include later decisions and are not standalone hand EVs or instructions to change those ranges manually.

Use weighted-112 as the research baseline and test the same approach in a second representative preflop context, prioritizing a heads-up blind-defense continuation because blind calling was one of the user's original concerns. Freeze its incoming ranges, action tree, training panel and separate test panel before evaluating the new comparison. This checks whether the benefit transfers beyond the one three-bet response subtree studied here. Keep this 190-board panel reserved; do not fit hand-specific patches to it.

Broader training-board coverage remains a promising follow-up, but it must fit the actual RAM/VRAM budget without changing the scientific target. A controlled 47-board run under the new update method would separately establish how much of the old-reference improvement comes from that method. Additional iterations on the same already-converged 112 boards are a lower priority than context transfer and coverage.

## Validation and recovery provenance

- All 570 accepted workers completed exactly 2,000 iterations, preserved preflop policies exactly, and passed private-pair, probability and chip/rake accounting checks.
- Independent analysis checked 14,514 recorded input/evidence hashes. Reconstructed aggregate EVs, full gaps and postflop gaps match the evaluator within 1e-9 bb (observed maximum below 5e-15 bb). Hidden-flop values are combined before any preflop best-response maximization.
- The initial runner stopped after 176 accepted workers when a Windows socket error interrupted the production-idle guard for report47 on KcTd3h. Its output was excluded even though a result file existed. The failure, log, resource record, output and snapshots remain preserved.
- A separately documented and registered recovery verified and reused those 176 workers, then ran 394 workers under a new prefix, including one fresh attempt of the interrupted worker. That attempt passed. No further retries, omissions, model edits or iteration extensions occurred. Completion was within the original absolute twelve-hour deadline.
- Successful guarded worker time totaled 28,929.200 seconds (8.04 hours); the slowest accepted worker took 61.141 seconds. This excludes recovery downtime, the failed attempt and final analysis. Minimum observed free RAM was 97,999,298,560 bytes and free VRAM was 20,353,908,736 bytes.
- Compressed accepted worker outputs, reviews, logs, resource samples, manifests and identity records accompany the study. Raw accepted JSON and byte-exact duplicate source snapshots remain local; gzip outputs reproduce the raw bytes. The failed output is separately compressed and clearly excluded.
- The study remains a restricted two-live-player continuation with fixed incoming support, a limited postflop action menu, and omitted earlier folded cards. These results do not prove full-deck equilibrium, full multiway accuracy or agreement with Wizard.

Production port 56708 was not modified or restarted. Read-only completion checks found its preflop session still stopped at iteration 800, postflop idle, and reports inactive. No model was deployed.
