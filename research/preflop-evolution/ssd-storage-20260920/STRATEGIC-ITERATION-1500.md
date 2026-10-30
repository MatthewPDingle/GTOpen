# Weighted continuation study: iteration 1,500

The third weighted segment completed, saved its checkpoint, and passed independent numerical and file-integrity checks. The registered queue has started the final weighted segment toward iteration 2,000. Production port 56708 was not changed.

## Convergence and policy movement

The within-training total gap fell from 0.823835 at iteration 100 to 0.057798 at 500, 0.017229 at 1,000, and 0.008408 at 1,500. Crossing 0.01 does not change the fixed 2,000-iteration endpoint or establish accuracy on unseen boards.

Under the common physical-combination prior, the root calling frequency moved from 6.344% at 1,000 to 6.119% at 1,500. The weighted per-combination total-variation distance between these policies is 0.314%. This measures policy movement, not EV loss or accuracy.

## Validation

- Finite values, normalized policies, qualified input manifest, expected storage transfers, and chip-plus-rake accounting passed.
- Restoring the 1,000-iteration checkpoint reproduced its final evaluation exactly.
- The completed snapshot contains 227 files totaling 61,718,677,775 bytes, with a completion marker and recorded file hashes.
- The resource guard completed successfully. Minimum free host memory was 22,981,857,280 bytes; minimum free GPU memory was 11,652,825,088 bytes.
- The result and completed segment review hashes are recorded in strategic-weighted112-progress-1500-v1-review.json.

## Next

Complete the weighted and equal-weight branches at their registered 2,000-iteration endpoints, freeze both policies, qualify the common evaluator, then compare them on the 95 reserved boards. The equal-weight and reserved comparisons have not yet run. No accuracy or production-readiness claim is made at this milestone.
