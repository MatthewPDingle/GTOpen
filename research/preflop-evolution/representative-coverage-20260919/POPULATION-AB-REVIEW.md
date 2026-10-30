# Ten-flop source: population supplement and reconstruction check

Recorded 20 September 2026, after all 59 additional AB-source workers and their three aggregate reviews completed. The corresponding 47-flop-source supplement is still running. No production change is justified by this interim review.

| Evaluation | Combined deviation gain (bb) | Rebuilt postflop residual (bb) |
|---|---:|---:|
| Original connected ten-flop training game | 0.004091560 | Not a reconstruction |
| Same ten training flops, rebuilt postflop | 0.005662568 | 0.001049447 |
| Independent 95-board complement sample | 2.733421356 | 0.000967534 |
| Complete 69 excluded canonical boards | 2.308129556 | 0.001013807 |
| Combined 164-board population mixture | 2.704458752 | 0.000969647 |

The matched training-panel reconstruction preserves the entering policy exactly, its private-card distribution to numerical precision, and both EVs within 0.000307 bb. This is evidence against a large reconstruction effect for this particular ten-flop source. The much larger deviation on the broader mixture points instead to transfer across boards, including the private-card reweighting induced by finite chance panels. It does not isolate those two effects or establish the result for the 47-flop source.

For the combined mixture, changing only OOP's entering action gains 1.769502 bb, compared with 1.774488 bb for its full deviation. Thus most of the measured OOP error is already visible at the entering decision. The largest board-local postflop residual is 0.00179046 bb; none exceeds the descriptive 0.01 bb reference. Low residuals are numerical checks, not proof of accurate off-path behavior or full-deck equilibrium.

The additional conditional-hand audit retains every supported hand, including those almost never played. Maximum panel-averaged postflop gains are 0.018686 / 0.005445 bb in the call branch and 0.021358 / 0.003627 bb in the called 4-bet branch (OOP / IP). Reapplying each hand's actual entering reach reconstructs the overall 0.000969647 bb residual. This does not reveal a large hidden conditional mean convergence error; these maxima are not bounds for individual boards or for changed opponent strategies. Evidence: `population164-ab-conditional-residuals.{json,md}`.

The 164-board mixture combines the registered 95-board systematic sample of the eligible complement with all 69 excluded canonical boards. It includes training boards and is not wholly independent validation. Its weights represent the complete physical-flop population through the registered sampling design, but the finite weighted game is neither exact full-deck enumeration nor an unbiased exploitability estimator. No confidence interval or head-to-head strength claim is made. The generic aggregate review field `kind: heldout` names the checker, not the scientific independence of these panels.

All new workers used 2,000 iterations. Aggregate checks preserved the frozen preflop policies and passed independent probability, normalization and chip-accounting checks. The matched-panel comparator additionally checked the original entering hand masses and action frequencies.

Evidence: `sourcepanel-ab-comparison.{json,md}`, `excluded69-ab-result{,-review}.json`, `population164-ab-result{,-review}.json`, `sourcepanel-ab-result{,-review}.json`, and `population164-ab-{board,decision}-diagnostics.{json,md}`. Per-worker manifests, status, resource logs and compressed numerical results are retained. `FULL-POPULATION-SUPPLEMENT.md` and its frozen manifests define the evaluation before these outcomes were available.

Next: finish the unchanged 47-flop-source supplement, compare its own matched-panel reconstruction, and review both sources together. Do not infer success from the ten-flop source's low training-game gap or tune the acceptance rules to these outcomes.
