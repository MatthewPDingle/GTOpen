# Research paused — resume only when the user requests it

The user requested deployment of C23 + C24 and then a pause on 14 September
2026. That release is R05. Do not launch another experiment on an automatic
continuation. No overnight schedule is currently active or implied.

## Where to resume

Worktree: `T:/Dev/GTOpen/target/autoresearch/preflop-convergence-20260911`
Branch: `codex/preflop-large-refinement-20260912`
Dashboard: http://127.0.0.1:56709/ (read-only, can remain running while paused).
App: http://127.0.0.1:56708/ — normal GPU release with C23 and C24.
Check `raw/r05-deployment-verified.json` and current process identity before
assuming a PID or build is still current.

The experiment ledger, complete logs, frozen benchmarks, private saved fixtures,
source archives and rejected experiments are preserved. Read `R05_RESULTS.md`,
`C24_RESULTS.md`, `experiments.json`, then `program.md` before new work.
The historical large-game graph and C24 memory-limited graph use different
problems and controls. Their percentage gains are not additive.

## Suggested next bounded experiment (not started)

Explore coalescing CDF preparation for two adjacent four-sample batches, while
keeping each terminal sum and update in the original four-sample order. C24's
memory savings may make this possible. First prove bitwise equivalence and fit;
only then time it. This is an untested idea, not a promised speedup. Prior
rank-product sharing attempts C18/C22 regressed badly; do not repeat them.

Keep the existing 1024 samples, precision, models, quality checks and actions.
CPU optimization is out of scope. The original ~10x aspiration and the broader
convergence problem remain unresolved. C23/C24 are throughput improvements.

## Restart procedure

1. Get the user's requested overnight window/deadline. Do not revive the expired
   original 10-hour deadline or silently start a new 10-hour window.
2. Verify no solve/report is active on 56708, GPU ownership, free memory and the
   current checkout. Keep one guarded build/test/GPU workload at a time.
3. Set `control.json` to running, update the dashboard release status and remove
   the paused notice from `program.md` only after explicit resume authorization.
4. Register one candidate and caps before implementation. Use the pass-07
   `run07` live-work guard. Frozen prior executables and inputs remain available;
   never overwrite earlier raw results. Use a fresh experiment identifier.
5. Keep user solves protected, push retained/rejected evidence to GitHub, and
   pause scheduling again when the requested window finishes.

Both existing heartbeat automations were already PAUSED at handoff. Any new
overnight heartbeat must use the app automation tool and the new requested
window, with notifications only for meaningful results or required action.
