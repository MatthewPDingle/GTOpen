# Equal-weight continuation study: iteration 500

The equal-weight branch completed its first registered segment, saved its checkpoint, and passed numerical and file-integrity checks. The queue has started the segment toward iteration 1,000. The weighted branch remains frozen at its registered 2,000-iteration endpoint. Production port 56708 was not changed.

## Convergence and policy comparison

The equal-weight within-training total gap fell from 0.819357 at iteration 100 to 0.051218 at iteration 500. This is an intermediate result above the registered 0.01 bb endpoint threshold. The planned 1,000, 1,500, and 2,000 checkpoints remain unchanged.

Under the common physical-combination prior, the equal-weight root policy at 500 is 72.797% fold, 8.957% call, 11.417% 4-bet, and 6.829% jam. Its prior-weighted per-combination total-variation distance from iteration 100 is 6.564%.

At the same 500-iteration training stage, the weighted branch calls 6.638% under that common prior, versus 8.957% for the equal-weight branch. Their per-combination policy distance is 6.129%. This establishes that the weighting choice changes the learned policy in this restricted setup. It does not identify the more accurate policy: both are intermediate, and the training-panel gaps have different chance distributions. The untouched reserved-board evaluation remains necessary.

These common-prior frequencies differ from the native training-panel frequencies retained in the result. Policy distance is not EV loss or an accuracy score.

## Validation

- Finite values, normalized policies, the expected equal-weight manifest, 112 boards, 224 storage entries, expected GPU transfers, and chip-plus-rake accounting passed.
- This is a fresh branch from iteration zero, with evaluations at iterations 1, 20, 100, and 500; there is no predecessor restore to compare.
- The saved snapshot contains 227 files totaling 61,718,677,577 bytes. The runner verified its file hashes and completion marker before proceeding.
- The resource guard exited successfully with no error after 14,100.718 seconds. Minimum free host memory was 22,077,812,736 bytes; minimum free GPU memory was 11,871,977,472 bytes.
- The final evaluation's chip-plus-rake conservation error was approximately 1.36e-8 bb.
- The result and completed segment-review hashes are recorded in strategic-equal112-progress-500-v1-review.json. The companion comparison JSON retains source hashes and the common prior.

## Next

Continue the equal-weight branch to its registered 2,000-iteration endpoint. Freeze both final policies, qualify the common evaluator, then compare weighted, equal-weight, and existing 47-board policies on the 95 reserved boards. No reserved outcomes were examined for this milestone. No accuracy or production-readiness claim is made.
