# Matched river pilot operational handoff

Updated 2026-09-28 21:31 Adelaide. Goal remains active; no range-quality claim.

Runner source is committed at 4ffc7421. Registration exists:
`river-matched-training-pilot-v1-registration.json` in this output directory.
Executed sources and registered inputs are now frozen. Fixes require a new
version and preserved failure evidence, not edits to registered code.

Live runner launched with `--run --wait`:

- Exec session: 34932.
- PID: 94808; process creation Unix time: 1790596846.2597828.
- Latest verified state: waiting_for_resources, GPU 100% occupied.
- Status: `river-matched-training-pilot-v1-status.json`.
- No training updates or fresh test deals have run at this checkpoint.

Poll the existing exec handle and status. Never start a duplicate merely because
an observation times out. Verify the process identity before any recovery.
If it actually terminates, read any interruption evidence and complete progress
markers before using `--run --resume --wait`. Preserve partial attempts.

Fresh storage inventory completed successfully: 718,622,677,422 allocated bytes
across the three research roots. With 10 GB reserved this is below 800 GB.
Runner performs another inventory at actual admission. Study cap 8 GB plus 2 GB
reserve; preserve historical data. No deployment or additional GitHub push.

User approved sharing with light desktop/video use. Admission permits below
65% external GPU utilization, 4 GB own CUDA cap and 2 GB external headroom;
active production solves and heavy workloads retain priority. Initial wait is
bounded to 12 hours; actual invocation is bounded to four hours. CPU generation
uses bounded pools of four workers with single-thread BLAS.

The pilot forks two complete 78-update source states into baseline/candidate
pairs, tests full update interruption/restart, runs two updates per arm, then
compares full played-policy averages on 1,024 fresh common deals. Qualification
cost is recorded separately. Unplayed model 80 is excluded. This is preliminary
one-context evidence; old bank/reservoir content dilutes the treatment. An
independent analysis, equal-time comparison and broader contexts remain needed.

Follow RIVER-MATCHED-TRAINING-PILOT-PLAN.md for the prospective design. Its
preparation-time statements that the runner is not yet written/registered are
superseded by this handoff; do not edit that now-registered plan.
