# Resume after the user's computer restart

## Completed stage

All 60 development references completed and passed their frozen accuracy checks.
The 72-choice screen completed with **no passing candidate**. The best mean
improved adjusted action error only 1.74%, worsened one family by 7.84%, and
failed the leaf-error guard. No model was promoted or deployed.

Read `development-expansion/REPORT.md`, `completion.json` and
`training-screen.json`. Frozen inputs and every new label were verified.
The completion heartbeat is being removed after the results are pushed and
reported; no batch or screen should be restarted. Later sections are historical.

Recommended next study: paired uncertainty audit and one preregistered independent
board-panel repeat to separate target noise from persistent representation error.
If stable errors remain, test explicit interactions between both complete ranges.
Keep this failed screen intact; do not add samples or alter its gates to pass it.

## Resumed after reboot

The user returned and authorized continuation. The existing production executable
was restarted hidden on port 56708 (initial PID 26496). The reference batch is
running again, initially Python PID 10076 / exec session 47939. Verify processes
by command line before relying on these IDs. The six restart checkpoints were
verified byte-for-byte and reused. Current progress is in development-expansion/status.json.

Heartbeat `finish-paired-preflop-research` checks every ten minutes, stays quiet
during ordinary progress, and continues through the frozen screen, reporting and
GitHub push. Delete it once this stage is finished. Do not start a duplicate batch.
Serena's user-level `web_dashboard_open_on_launch` was set to false at the user's
request; keep any helpers hidden and do not open Serena dashboards.

The remaining sections preserve the restart handoff and research scope.

The user interrupted ongoing research to restart Windows. Resume when they
reopen this Codex task and ask to continue. Do not assume app launch resumes it.

Production port 56708 must remain unchanged. Reopen the normal app if needed
using its existing launcher/configuration; do not deploy a research candidate.
Before GPU work, the reference runner requires the live app's status endpoints
to be reachable and idle. No live sessions are loaded or overwritten by research.

## Current state

- Previous completed study: shallow-native-20260917, Git commit d6602216.
  Shallow leaf error improved, but the earlier action-value screen failed.
- This new paired-context study fitted an 18-feature correction using two
  completed policy families as development data. All 12 choices failed to beat
  the unchanged baseline on leave-one-family-out action accuracy. A frozen
  candidate exists for provenance but was NOT advanced to prospective testing.
- Further diagnostic showed substantial same-family fitting capacity but weak
  transfer. Range54 features helped only one transfer direction.
- We then registered a separate DEVELOPMENT expansion: 60 reference solves
  spanning synthetic linear/polar policies, three connected postflop contexts,
  ten shared stratified boards. The batch is paused, not complete.
- Exact completed count/IDs/hashes are in
  `development-expansion/restart-checkpoint.json`; `status.json` says paused.
- The runner and its current reference child were explicitly stopped for reboot.
  A job without a finished JSON file will rerun. Finished JSONs must be validated
  and reused. Incomplete logs are not completed work.
- Nine tests passed: paired model (4), expanded model (4), metadata adapter (1).
- No production solver source or server binary changed. No automation was created.

## Resume commands

Repository: `T:\Dev\GTOpen`; Python: `C:\Program Files\Python312\python.exe`.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
& 'C:\Program Files\Python312\python.exe' tools/research/run_paired_expansion.py run
& 'C:\Program Files\Python312\python.exe' tools/research/run_paired_expansion.py screen
```

Run `screen` only after all 60 references succeed. Use this wrapper, not the
original expansion runner: it contains a frozen, tested adapter for a one-ULP
Python/Rust serialization discrepancy in `inclusion_probability`. It accepts
at most two ULP in that field alone; original labels and all quality gates are
preserved. `runner-freeze.json` documents the repair and checks source hashes.

The expanded screen is already implemented in `fit_paired_expansion.py` and its
implementation hash was frozen before training. It considers 72 choices across
compact18/range54 features, penalties, action weights and shrink factors. Four
policy families are held out in turn. Advance only if the frozen protocol's
5% improvement, per-family nonregression and leaf guards pass. Otherwise report
no candidate. Do not alter the grid or gates to manufacture a pass.

If a candidate is selected, freeze it separately and design/register its fresh
prospective test before running any labels. The unused original test evaluator
assumes the original compact18 candidate; it must NOT be used blindly for a
range54 replacement. Native integration, re-solving, performance testing and
deployment remain later stages, conditional on independent accuracy evidence.

Finish the current study with an honest findings report, preserve failed screens,
verify hashes, and push updates to GitHub. Use explicit paths when staging; many
unrelated historical untracked outputs exist. Working branch is master. Working
SSH override: `git -c core.sshCommand=C:/Windows/System32/OpenSSH/ssh.exe push origin master`.
