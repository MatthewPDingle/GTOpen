# Equal-weight continuation study: iteration 1,500

The equal-weight branch completed its registered 1,000-to-1,500 segment, saved its checkpoint, and passed numerical, resource and file-integrity checks. The guarded recovery queue has launched the final segment toward the fixed 2,000-iteration endpoint. The weighted branch remains frozen at 2,000. Production port 56708 was not modified.

## Convergence and range stability

The equal-weight within-training total gap fell from 0.014996 at iteration 1,000 to 0.007494 at iteration 1,500. It is below the registered 0.01 bb threshold, but this is still an intermediate checkpoint. The fixed training budget remains 2,000 iterations for both branches.

Under the common physical-combination prior, the equal-weight root policy is 73.206% fold, 8.485% call, 11.520% 4-bet and 6.790% jam. Its prior-weighted per-combination total-variation distance from iteration 1,000 is 0.099%, down from 0.602% over the preceding 500 iterations.

At the same 1,500-iteration stage, the weighted branch calls 6.119% under that common prior, versus 8.485% for equal weighting. Their per-combination policy distance is 5.941%. Thus the two weighting choices still produce different policies while this branch's recent root-policy movement is small. This does not establish which policy is better. Training-panel gaps have different chance distributions, and policy distance is not EV loss. The registered unseen-board comparison remains necessary.

## Validation

- Expected equal-weight manifest, 112 boards, 224 storage entries, finite normalized policies, chip-plus-rake accounting and transfer accounting passed.
- Restored iteration-1,000 scientific outputs exactly match the previous segment. Evaluations occurred at 1,000 and 1,500, with 500 further training iterations.
- The complete snapshot contains 227 files totaling 61,718,677,796 bytes. The segment runner checked every snapshot file hash and preserved predecessor integrity.
- The guard exited successfully without error after 14,596.047 seconds. Minimum free host memory was 31,922,618,368 bytes and minimum free GPU memory was 12,267,290,624 bytes.
- Final chip-plus-rake conservation error was approximately 1.40e-7 bb.
- Result and review hashes are recorded in strategic-equal112-progress-1500-v1-review.json. The companion comparison report retains all source hashes and the common prior.

The earlier admission pause was resolved without changing any resource limit or scientific input. No reserved outcomes were examined. Finish the registered endpoint, freeze both final policies, qualify the evaluator, then evaluate the 95 unseen boards. These intermediate findings do not establish accuracy or production readiness.
