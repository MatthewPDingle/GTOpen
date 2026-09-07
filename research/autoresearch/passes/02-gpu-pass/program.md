# GTOpen autoresearch program

Pass 1: 2026-09-07, 00:38–03:38 UTC.
Pass 2: 2026-09-07, 03:57–06:57 UTC (three hours, user authorized).
Pass 2 focuses on preflop CUDA, postflop CUDA and GPU memory/transfers;
continue the cumulative metric graphs and archive each completed pass. Adapted from
https://github.com/karpathy/autoresearch and its program.md.

## Objective

Improve speed and efficiency without reducing accuracy. Work through all
six paths in paths.json, not just the current most promising path. Each
path has its own hypotheses, measurements, decisions and metric graphs.

## Loop

1. Inspect the last retained code and the path's results. Pick one falsifiable
   hypothesis. Record its ID, scope, expected effect and applicable controls.
2. Change only implementation files in the isolated research worktree:
   `target/autoresearch/workspace`, branch `codex/autoresearch-20260907`.
   The initial commit a43b09a includes the already-validated changes from
   the preceding conversation. Never reset or clean the main checkout.
3. Commit each candidate in the research worktree. Preserve its patch in
   this research directory. Benchmark one hardware workload at a time.
4. Fixed workload, input ranges, bet menus, precision, iteration/check
   budgets, caches and evaluation harness are the ground truth. Do not
   weaken assertions, change targets, omit expensive game branches, add
   fast-math, or change the model to manufacture an improvement.
5. Bound ordinary experiments to ten minutes. Log failed builds, crashes,
   inconclusive measurements and rejected ideas as well as retained gains.
6. Retain changes after relevant correctness tests and numerical checks.
   Seek repeatable >2% time gains, or >5% memory savings with no material
   time regression. Repeat marginal results and test important controls.
   Speed gains must survive timing noise and time-to-accuracy checks where
   learning trajectory changes. Prefer simple changes over complex near-ties.
7. If rejected, restore only this experiment's implementation in the
   research worktree. The ledger and plots keep the rejected trial.
8. Rebuild all graphs after every measurement/decision. Rotate paths;
   record why a path is stalled or exhausted rather than silently dropping it.
9. Copy a retained implementation into the main checkout only after checking
   that its pre-experiment file hash still matches. Preserve other user work.
10. Run the CPU and CUDA suites on combined retained changes before finishing.

## Reporting and persistence

`events.jsonl` is the append-only audit log; `results.json` and `results.tsv`
are derived views. Raw logs and patches retain the evidence. `progress.png`
summarizes paths; `graphs/` contains a chart for every measured optimization
metric. `index.html` groups charts and decisions by research path.

Continue the active run across context compaction by reading run.json,
paths.json, results.json and the latest log. Stop at the configured deadline
or when the user asks. Progress updates should report findings and decisions.
Do not replace a user's running solver session or start external services.

## Accuracy gates

- Existing solver CPU suite; existing postflop/preflop CUDA equivalence tests.
- Same inputs and immutable evaluation-harness hashes for A/B comparisons.
- Bitwise arena/EV/gap fingerprints where implementations are deterministic.
- Postflop atomic-reduction noise: compare fixed-state evaluation and final
  exploitability, not just exact fingerprints of independent trajectories.
- Save compatibility, lock semantics, hero/frozen seats, stopping and
  compressed/f32 storage must remain valid for affected changes.
