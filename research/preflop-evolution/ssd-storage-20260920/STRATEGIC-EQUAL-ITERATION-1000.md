# Equal-weight continuation study: iteration 1,000

The equal-weight branch completed its registered 500-to-1,000 segment, saved its checkpoint, and passed numerical, resource and file-integrity checks. Its restored iteration-500 scientific outputs exactly match the preceding segment. The weighted branch remains frozen at its registered 2,000-iteration endpoint. Production port 56708 was not modified.

## Convergence and policy comparison

The equal-weight within-training total gap fell from 0.051218 at iteration 500 to 0.014996 at iteration 1,000. This is an intermediate result above the registered 0.01 bb endpoint threshold. The planned 1,500 and 2,000 checkpoints remain unchanged.

Under the common physical-combination prior, the equal-weight root policy is 73.151% fold, 8.545% call, 11.502% 4-bet and 6.802% jam. Its prior-weighted per-combination total-variation distance from iteration 500 is 0.602%.

At the same 1,000-iteration stage, the weighted branch calls 6.344% under that common prior, versus 8.545% for equal weighting. Their per-combination policy distance is 5.905%. The weighting choice still changes the policy appreciably more than the equal branch changed over its last 500 iterations. This does not identify the more accurate policy: the training objectives have different chance distributions, and the unseen-board evaluation remains necessary. Policy distance is not EV loss.

## Validation

- Expected equal-weight manifest, 112 boards, 224 storage entries, finite normalized policies, chip-plus-rake accounting and transfer accounting passed.
- The segment resumed at 500, evaluated at 500 and 1,000, and reproduced the prior scientific evaluation exactly on restoration.
- The complete snapshot contains 227 files totaling 61,718,677,784 bytes. The segment runner checked every file hash and preserved predecessor integrity.
- The guard exited successfully without error after 15,674.469 seconds. Minimum free host memory was 22,130,593,792 bytes and minimum free GPU memory was 11,816,402,944 bytes.
- Final chip-plus-rake conservation error was approximately 1.23e-7 bb.
- Result and review hashes are recorded in strategic-equal112-progress-1000-v1-review.json. The companion comparison report retains all source hashes and the common prior.

## Admission pause and continuation

The original queue subsequently stopped before launching the next native solve because available host RAM was below the unchanged launch threshold of 96,302,143,764 bytes. This was not a failure of the completed checkpoint. No equal-1,500 artifacts or native process were created.

After reviewing the failure and all six completed stages, a separate recovery wrapper was launched to wait for the original resource reserve and idle production. It checks every 15 minutes, uses the unchanged segment runner, attempts each remaining segment once, and stops on any new failure. Original stopped-queue evidence is preserved. See STRATEGIC-RECOVERY-20260921.md. No resource threshold, model, board set, training endpoint or native code changed.

Both final policies must still be frozen, the common evaluator qualified, and the 95 unseen boards evaluated before making an accuracy claim. No reserved outcomes were examined for this milestone and no deployment is authorized by these results.
