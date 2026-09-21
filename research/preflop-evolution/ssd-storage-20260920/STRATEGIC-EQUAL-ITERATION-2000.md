# Both continuation policies have reached the fixed training endpoint

The equal-weight branch completed iteration 2,000, saved its checkpoint, and passed numerical, resource and file-integrity checks. The recovery queue completed all eight registered segments and froze both final policies before any new reserved-board outcomes were examined. Production port 56708 was not modified.

## Convergence and remaining strategic question

The equal-weight within-training total gap is 0.004634 bb; the weighted branch finished at 0.005085 bb. Both meet the registered 0.01 bb training threshold. These gaps concern different training distributions and do not establish which policy generalizes better.

Under the frozen common physical-combination prior, equal weighting produces 73.224% fold, 8.465% call, 11.527% 4-bet and 6.784% jam. Weighted flops produce 75.886% fold, 5.865% call, 12.443% 4-bet and 5.806% jam. Their per-combination policy distance is 6.022%, while the equal-weight policy moved only 0.031% during its final 500 iterations. The stable difference merits the registered unseen-board evaluation; more calling is not itself evidence of better play.

## Validation

- Expected equal-weight manifest, 112 boards, 224 storage entries, finite normalized policies, chip-plus-rake accounting and transfer accounting passed.
- Restored iteration-1,500 scientific outputs exactly match the prior segment. The segment evaluated iterations 1,500 and 2,000 and performed 500 further learning iterations.
- The checkpoint contains 227 files totaling 61,718,677,799 bytes. The unchanged segment runner verified every snapshot hash and predecessor integrity; the independent endpoint review checked the completed file set, size and completion marker.
- The guard exited successfully after 15,931.860 seconds. Minimum free host memory was 26,603,843,584 bytes; minimum free GPU memory was 11,520,704,512 bytes.
- Final chip-plus-rake conservation error was approximately 1.95e-8 bb.
- The final result hash, segment review hash and two-policy freeze hash are recorded in strategic-equal112-progress-2000-v1-review.json. The companion range comparison retains source hashes and the common prior.

## Next step

Requalify the frozen-policy evaluator on the registered development controls, then evaluate the weighted, equal-weight and old 47-board policies on the same 95 unseen boards. Keep postflop residual convergence separate from full deviation gain. These training results are not an accuracy claim, a multiway result or authorization to replace the production model.
