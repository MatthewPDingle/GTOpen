# Weighted continuation study: iteration 2,000

The weighted branch reached its registered endpoint, saved its checkpoint, and passed numerical and file-integrity checks. The equal-weight branch has started its first segment toward iteration 500. Production port 56708 was not changed.

## Convergence and policy movement

The within-training total gap fell from 0.057798 at iteration 500 to 0.017229 at 1,000, 0.008408 at 1,500, and 0.005085 at 2,000. The final result meets the registered 0.01 bb within-panel threshold. This establishes convergence to that tolerance in the restricted training game, not accuracy on unseen boards or agreement with GTO Wizard.

Under the common physical-combination prior, root calling moved from 6.119% at 1,500 to 5.865% at 2,000. Root folds are 75.886%, 4-bets 12.443%, and jams 5.806%. The prior-weighted per-combination total-variation distance from 1,500 to 2,000 is 0.302%. This measures policy movement, not EV loss or strategic quality. These common-prior frequencies differ slightly from the native training-panel frequencies retained in the result.

## Validation

- Finite values, normalized policies, qualified input manifest, expected storage transfers, and chip-plus-rake accounting passed.
- Restoring the 1,500-iteration checkpoint reproduced its final evaluation exactly.
- The completed snapshot contains 227 files totaling 61,718,677,787 bytes, with a completion marker and recorded file hashes. The predecessor snapshot also passed its unchanged-file checks.
- The resource guard exited successfully with no error after 14,204.703 seconds. Minimum free host memory was 23,916,994,560 bytes; minimum free GPU memory was 11,760,828,416 bytes.
- The final evaluation's chip-plus-rake conservation error was approximately 3.23e-9 bb.
- Result and completed segment review hashes are recorded in strategic-weighted112-progress-2000-v1-review.json. The companion JSON and Markdown comparison retain all four training checkpoints under the same physical prior.

## Next

Complete the equal-weight branch at its registered 2,000-iteration endpoint, freeze both final policies, qualify the common evaluator, then compare the weighted, equal-weight, and existing 47-board policies on the 95 reserved boards. No reserved outcomes have been examined for this milestone. No accuracy or production-readiness claim is made, and neither branch is extended or selected because of its displayed ranges.
