# Fixed-budget board-coverage comparison

The first stack-price diagnostic fits its training boards accurately but fails
on new boards. The exploratory decomposition rules out action conversion as the
main validation bottleneck. Test whether broader board coverage helps before
changing architectures or launching more broad self-play.

This is a new prospective learning comparison, informed by the prior failure.
It does not change that experiment or reuse its final test as confirmation.

## Frozen choices

- Board seed 9296600; sample 544 distinct full-board suit-isomorphism groups.
  Exclude all 12 reference-probe and all 40 preceding learning groups.
- First 512 boards are fitting. The baseline uses their first 24; the candidate
  uses all 512. The next 16 are validation, the last 16 final test. Preserve turn
  and river order in model inputs. Keep all 1,081 physical hero holdings and exact
  legal uniform-opponent counts on each board.
- Both arms use the existing 362 visible/public inputs and the same two 64/64
  player heads, four outputs, legal fold/call loss and policy conversion.
  No feature changes, extra layers, auxiliary targets or analytic oracle policy.
- Fit at 20/40/100/200/400 bb. Exclude 60/150 bb from fitting and selection.
  Those two geometries were evaluated in the preceding experiment, so describe
  them as excluded training depths on fresh boards, not globally unseen depths.
- Seeds 9296601 and 9296602; run seed 1 as 24 then 512, seed 2 as 512 then 24.
  Use unchanged `stack_price_learning_fit_v1.py`: Adam 0.001, batch4096,
  8192 updates, validation at0/1024/4096/8192, float32 inference, TF32 off.
  Within a seed, both arms have identical initial weights and independent batch
  generators seeded identically. Card indices differ because the dataset sizes
  differ; contexts and public-state sampling remain matched.
- Choose lowest context-balanced normalized validation regret, tie earlier step.
  Freeze all four identities before preparing final-test labels. Evaluate selected
  models once on final boards at all seven depths. No outcome-based extension.
- Primary gate: the broader arm must select a noninitial checkpoint, reduce
  mean normalized regret across 60/150 by at least20% in BOTH seeds, and have
  mean regret <=0.001 starting stacks at EACH of those depths. Report every
  fitting-depth slice, seat, price band, made-hand category and tail metric too.
  Finite-grid engineering gate only, not a population interval or exploitability.

## Execution and evidence

Factor card/count and public-state data; assemble rows on GPU. Reuse the qualified
canonical/feature and exact-count implementations. Use at most eight hidden CPU
workers, each processing a batch of boards, to avoid re-importing Python/Torch
for every board. Keep all child processes in the owning Windows job.

Cap the entire run at3600 seconds, including one storage admission, preparation,
four fits and tests. New evidence<=256MB plus128MB reserve; combined research
CUDA<=4GB with2GB external headroom, RAM admission28GB/during24GB, S: free>=40GB,
global allocated research storage<=800GB. Light desktop/video GPU sharing is
allowed; active production solves and heavier workloads have priority.

Save preparation phase times, process accounting, feature/cache sizes, actual
CUDA peak and each fit duration. No app session changes, production deployment,
new GitHub push or historical evidence deletion. Interrupted attempts retain
their evidence and are not silently restarted.

If coverage substantially helps but misses the absolute gate, diagnose only
training/validation outcomes before selecting a next treatment. If the richer
coverage does not materially help, test a structured board representation or
learned showdown component with exact public accounting, rather than increasing
the same budget indefinitely. Neither result completes the broader preflop goal.
