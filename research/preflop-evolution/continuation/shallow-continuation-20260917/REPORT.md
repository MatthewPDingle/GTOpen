# Shallow 4-bet continuation: prospective test

Research only. Production port 56708 was not modified.

The correction passed the predeclared screen in all three held-out contexts.
Average equity-adjusted value error fell 45.5%, 52.1% and 61.7%, respectively.
The frozen-policy call/3-bet error fell 30.5%, with no change to call/fold.
This supports further integration testing, not deployment or a full-game accuracy claim.
See [interpretation and next steps](CONCLUSIONS.md) for remaining weaknesses.

## Held-out range results

| Context | Boards | Qualified mass | Balanced MAE (bb) | Candidate MAE (bb) | Screen |
|---|---:|---:|---:|---:|---|
| confirmation | 150 | 100.00% | 2.219 | 1.210 | pass |
| heldout-mixed | 30 | 100.00% | 2.906 | 1.392 | pass |
| heldout-premium | 30 | 100.00% | 3.402 | 1.304 | pass |

Errors use the equity control variate and legal-pair mass, with both players equally weighted. The confirmation combines 50 old certainty boards with 100 newly sampled complement boards. The separate synthetic held-out contexts use 30 boards each.

## Original suspect hands, saved-game shallow leaf

| Hand | Balanced (bb) | Fresh complement estimate (bb) | Combined estimate (95% interval, bb) | Candidate (bb) |
|---|---:|---:|---:|---:|
| A3o | 15.20 | 10.55 | 10.58 [9.53, 11.70] | 13.66 |
| A4o | 15.41 | 10.75 | 10.78 [9.73, 11.99] | 13.91 |
| 54s | 16.46 | 13.55 | 13.57 [12.62, 14.63] | 14.39 |
| A8o | 17.56 | 14.55 | 14.49 [13.29, 15.84] | 16.84 |
| A3s | 17.09 | 13.32 | 13.35 [12.39, 14.38] | 15.30 |
| A4s | 17.24 | 13.23 | 13.27 [12.36, 14.30] | 15.48 |
| A8s | 19.08 | 17.17 | 17.12 [16.01, 18.37] | 18.19 |
| 86o | 14.79 | 7.77 | 7.74 [7.05, 8.44] | 13.28 |

These are gross values conditional on reaching the 4-bet pot, not values of the original 3-bet. The original action comparison weights each leaf by the probability of reaching it.

**86o is not qualified at this shallow leaf:** its remaining best-response gain is
4.52bb. It is shown for transparency, not as evidence of model error. Its mass is
tiny, which is why the aggregate qualified percentages round to 100%. The other
seven displayed hands have gains of 0.024–0.032bb. The displayed intervals use the
equity control variate; the direct intervals remain wider for A8o and A8s.

## Frozen-policy action regression

| Model | Call/3-bet direct MAE (bb) | Call/3-bet corrected MAE (bb) |
|---|---:|---:|
| candidate | 0.334 | 0.298 |
| balanced | 0.282 | 0.230 |
| shallow_candidate | 0.264 | 0.207 |

Call/fold value change: 0 bb. Only the shallow leaf changes; the original call audit and all other leaves remain unchanged.

Overall predeclared held-out screen: **PASS**.

All results concern one finite, zero-rake heads-up postflop menu. Bootstrap intervals are per-hand descriptive intervals, not simultaneous guarantees. Saved-game action labels are reused, so action regression is not an independent new action experiment. A passing value screen would still require native integration, fresh equilibrium tests, boundary checks and speed measurements. A failing screen is not eligible for deployment.

## Verification

All 280 new references passed CPU and GPU gap checks (maximum 0.09982% pot). Independent scalar aggregation agreed within 3.2e-14 bb. Offline solver time: 9.1 minutes, excluding process startup.

![Held-out and action errors](comparison.png)

Reproduce: run `shallow_continuation_audit.py run`, then `shallow_continuation_fit.py`, `evaluate_shallow_continuation.py`, and `report_shallow_continuation.py` from `tools/research`. Training refuses to overwrite a frozen candidate; skip that step when replaying the existing candidate. Frozen source files, local binaries and saved-game inputs are identified in `manifest.json`.
