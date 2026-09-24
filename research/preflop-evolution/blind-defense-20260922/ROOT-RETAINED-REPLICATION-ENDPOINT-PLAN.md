# Independent-seed endpoint evaluation

Prepared while the second training seed is running, before examining its
endpoint gains. The training plan and registration remain unchanged.

## Fixed comparison

After all 78 replication updates and the complete training audit pass, evaluate
the entire played bank (generations 0 through 77, excluding generation 78).
Report all four equal/linear averaging pairings. Linear/linear remains primary;
do not choose a pairing or checkpoint based on its outcome.

Use the unchanged complete private-card population and all-in runout cache:
47,478 canonical private-card cases representing 776,650 physical pairs.
No new sampled deals are needed for these endpoint calculations.

The BB test can reallocate only its existing fold/jam probability. Its call,
non-all-in raise and later decisions remain fixed. The BTN test changes only
its response to the initial jam. These are restricted profitable deviations,
not full exploitability or evidence that the calling ranges are accurate.

The comparison baseline in this evaluation is the **first root-retention
training seed**, not the older algorithm. Also report the older exact-initial
results in the eventual findings for context, clearly labeled. A difference
between these two root-retention runs is training-seed variation; it does not
isolate the causal effect of root retention.

## Verification and resources

The evaluator and scalar reader retain the previously checked numerical
implementation. Changes are input/output names, comparison baseline and the
storage admission checks. Validate the complete diff before execution.

Check all inherited input hashes, the completed training audit and the first
seed's endpoint review. Compare CPU and CUDA outputs for all 265 initial
observations in both averaging schedules. Independently reconstruct all four
pairings using outcome-wise chip accounting, including conservation and every
hand class. A passing test confirms this restricted calculation, not an
independent implementation of all poker traversal or model inference.

Before execution, measure allocated bytes across all three research roots.
Require current allocation plus a 10 MB endpoint output allowance and 2 GB
metadata reserve to fit within 800 GB. The new output directory inherits NTFS
compression. Verify its logical size, allocation and compression attributes.
Keep 40 GB free on T:, 20 GB available RAM and 3 GB available GPU memory.
Each evaluator/reader retains its 20-minute deadline. Preserve failures; do
not automatically retry, increase budgets, or choose an alternative model.

Production activity and the existing GPU-exclusive locks remain authoritative.
Do not run this evaluation concurrently with training or its audit. The
training continuation schedules only the audit; it does not start this test.
There is no deployment and no automatic broader response evaluation.
