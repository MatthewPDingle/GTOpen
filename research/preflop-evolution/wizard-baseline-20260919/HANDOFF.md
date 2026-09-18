# Pending run and review

The solve was launched on 19 September 2026. It is intentionally separate from
production. Do not launch another copy of `run.py` while it is active.

- Study server: port 56710, initial PID 64936; verify executable and listener.
- Solve runner: Python PID 61920, `run.py` in this directory.
- Extraction helper: Python PID 62012, `postprocess.py 61920`, hidden window.
- Production: port 56708, initial PID 26496. No writes are authorized by this study.
- Completion heartbeat: `finish-gtopen-wizard-comparison`, every 15 minutes,
  attached to this task. Pause it once the reviewed results have been delivered.

The helper waits for the existing runner and executes `finish.py`, `plot.py`,
then `report.py`. Check `postprocess-status.json` and individual logs for errors.
If extraction fails after solving, fix the evidenced error and rerun the
postprocessor; it uses `production-preserved.json` to recognize completed solves
and reuses existing action-value files. Never overwrite a completed solve merely
to recover a report-generation problem.

Next review:

1. Confirm the initial convergence outcome and 250-iteration stability. Report
   any target miss and material remaining drift explicitly.
2. Review RESULTS.md, comparison-with-own-values.json, figures, incoming reach
   and later-menu-audit.json. Own EVs and Wizard EVs use different opponent
   ranges/policies; their difference alone does not identify a model defect.
3. Update README.md with the findings and the most useful bounded next experiment.
   Do not tune a model or open the reserved 100bb references during this baseline.
4. Verify production preservation, run the five baseline and seven reference
   Python tests, and push the reviewed artifacts to GitHub. Commit only this
   study's intended files, without logs, PIDs, binary saves or unrelated research.
5. Once saved results are safe, close only the verified idle study server on
   56710. Leave production running. Notify the user and pause the heartbeat.

The initial runner's full progress file is useful locally. For the final commit,
prefer a compact per-accuracy-check history rather than repeated status polls;
if compacting it, preserve every measured checkpoint and the final status so
the convergence plot remains reproducible.
