# Unseen-flop comparison: modest improvement, still sensitive to board coverage

All 285 registered evaluations completed: three frozen preflop policies on the same 95 unseen flops, with 2,000 postflop iterations per worker. Every worker passed exact policy-import, probability and chip/rake accounting checks. The combined responses are well converged. The weighted 112-board policy scores best on this panel, but the advantage is sensitive to individual boards and does not justify a production replacement.

## Main result

Full deviation gain is the sum of the two players' gains from unilateral best responses in the restricted game. Lower is better. It is not a guaranteed loss per played hand, an EV advantage between policies, or distance to GTO Wizard.

| Frozen training policy | Full deviation gain (bb) | Postflop residual (bb) | Player 0 gap | Player 1 gap |
|---|---:|---:|---:|---:|
| Weighted 112 boards | 0.467221 | 0.000463 | 0.387628 | 0.079594 |
| Equal-weight 112 boards | 0.490776 | 0.000567 | 0.406112 | 0.084663 |
| Earlier 47-board reference | 0.580774 | 0.000144 | 0.456299 | 0.124475 |

The weighted policy's full gap is 0.023555 bb (4.8%) below equal weighting and 0.113553 bb (19.6%) below the old reference. Equal weighting is 15.5% below the old reference. Both new policies were trained with the same executable, boards, actions and iteration budget; weights were the intended difference. The old-reference comparison also changes the training-update treatment, so its improvement cannot be attributed solely to more flops.

The numerical response residuals are much smaller than the differences. However, board-sampling uncertainty remains substantial. The tiny training gaps, approximately 0.005 bb, did not carry over to this unseen sample: the full deviations remain approximately 0.47-0.58 bb. More iterations on the existing training boards are therefore not the first thing to try.

## Sensitivity analysis

After completing the pre-registered comparison, a paired leave-one-board-out analysis recomputed the combined counterfactual values and preflop best responses for every possible single-board omission. The same board was omitted for every source. This is a post-hoc sensitivity diagnostic, not a confidence interval or a reason to remove any board from the reported result.

- Weighted beats equal weighting in 91 of the 95 omission checks. Their gap difference ranges from -0.053957 to +0.008403 bb; positive values reverse the ordering.
- Weighted beats the old reference in 94 of 95 checks. That difference ranges from -0.259245 to +0.002105 bb.
- Equal weighting beats the old reference in 94 of 95 checks.

Thus even the apparent old-reference improvement is not immune to an individual board's influence. Keep all 95 boards and treat the ranking as a promising sample result requiring replication.

## What the ranges and errors show

Under the common physical-hand prior, calling is 5.865% for weighted-112, 8.465% for equal-112 and 0.055% for the old reference. The new policies recover meaningful calling, but the policy with more calls is not the best-scoring one on this panel. Calling frequency alone is not the objective.

Most remaining deviation is on player 0's side. For the weighted policy, the largest hand-class contributions are A4s (0.052573 bb), ATs (0.047568), 66 (0.033697), 22 (0.033005) and TT (0.031883). These are contributions to full deviation, including later decisions; they are not individual hand EVs or recommended range edits. Player 1's largest contributors are JJ and QQ. The companion JSON preserves every class contribution.

## Validation and provenance

- Both final preflop policies were frozen before any new reserved-board evaluation. All 95 boards were evaluated for all three sources without omission, retry or iteration extension.
- All 7,261 recorded input/evidence hashes were independently rechecked after completion. All 285 worker exits, policy imports, board identities and final iteration counts passed.
- A separate reconstruction from terminal counterfactual values reproduces aggregate EVs, full gaps and postflop residuals within 1e-9 bb. Values are combined across hidden flops before preflop maximization.
- Minimum free RAM was 100,949,110,784 bytes; minimum free VRAM was 21,014,511,616 bytes. Total guarded worker time was 14,128.577 seconds; the slowest worker took 53.125 seconds.
- Compressed per-worker results, reviews, logs, resource samples, manifests and hash records accompany the comparison. Full raw results and byte-exact per-worker source snapshots remain retained locally; compressed results reproduce the raw result bytes.
- The eligible population represents 15,320 of 22,100 physical flops. The game remains a restricted two-live-player continuation with fixed incoming support and omitted earlier folded cards. No full-deck, multiway or Wizard-equivalence claim is made.

## Next research step

Keep all three policies unchanged and run a larger, independently selected unseen panel before choosing a training direction. Register that sample and its common evaluation rules before evaluating it; exclude all training candidates and previously evaluated boards. Use the result to assess whether the modest weighting improvement replicates. This addresses the demonstrated sampling sensitivity more directly than extending training on the same 112 boards. The different update treatment of the old 47-board reference still requires a separate controlled ablation before making a pure coverage claim.

Production port 56708 remains unchanged. This comparison is evidence for continued research, not a production promotion.
