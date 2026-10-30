# Root-action verification queued after the existing replay

Recorded 2026-09-28 around 12:06 Adelaide. This is a historical handoff;
verify identities, status files and new output before calling a process live.

- Replay PID 51220, creation time 1790561572.256763, remains the existing
  `board_root_action_replay_v1.py --run` process. Last observed committed
  prefix: 52,224 / 65,536 deals. Do not restart it.
- Pipeline PID 64544, creation time 1790562892.5529237, runs
  `board_root_action_review_pipeline_v1.py --run` hidden. It waits for that
  exact replay process to finish, requires its completed result, then starts
  the qualified full readback and all-class report in order, once only.
- Pipeline registration SHA-256:
  `8ab25f7042451240fa335526db3b6b8a1e09993ac3bdae339481d62a622fb453`.
- Status: `board-root-action-review-pipeline-v1-status.json`.
- Controller logs: `board-root-action-review-pipeline-v1-controller.log` and
  matching `.stderr.log`. Stage logs replace `controller` with `readback` or
  `interpretation`. No automatic retry occurs after failure.
- The pipeline preserves the replay's original deadline. Full review has its
  own one-hour calculation bound and waits only for original replay completion,
  not an extended or restarted scientific sample.

The reader passed its separate 64-deal control in 9.625 seconds. Source and
control evidence were committed locally as
`3f52cb8a1462d9a1e809ae315f00a7b39240e906`. Report and pipeline sources were
committed as `2f37535b8424ee2af638b85519b238bff8e2b37c`. Committed bytes were
verified against disk. None of these commits has been pushed under the older,
specific approval for 69b8f082.

Expected completed outputs:

1. `board-root-action-replay-v1-replay.json` (replay finished, review required).
2. `board-root-action-replay-readback-v1-result.json` (independent saved-input
   reconstruction and arithmetic pass; not independent poker-engine evidence).
3. `BOARD-ROOT-ACTION-VALUE-FINDINGS.md`, `board-root-action-all-classes-v1.json`
   and `.csv` (descriptive full sample, all 169 classes, all eight profiles).

Next: inspect the finished report, check its numeric conclusions against the
retained summary, and decide the next targeted research step. Sample-selected
root maxima are exploratory and upward-biased; no accuracy qualification or
fresh exploitability bound follows. Different runs also use different opponent
and continuation policies. Do not mark the broad research goal complete.

If interrupted, inspect the exact terminal process state and error logs first.
Preserve registration and partial evidence. Do not edit already-run versioned
research source or blindly retry a failed stage.

The user approved sharing GPU resources with light browser/video work. Active
solves and heavy workloads retain priority. This replay and review are CPU-only;
no GPU work, production change, Jev integration or new training was launched.
The original GPU startup guard remains unchanged, as documented separately in
`DESKTOP-RESOURCE-SHARING.md`.
