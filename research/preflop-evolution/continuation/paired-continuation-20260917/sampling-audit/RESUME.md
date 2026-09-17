# Sampling audit: resume and completion

The user authorized this uncertainty audit and one independent repeat. Port 56708
must remain unchanged, and all processes must stay hidden. No Serena dashboard.

1. Read status.json, manifest.json and runner.log. Check whether the existing
   paired_sampling_audit.py process is alive before launching another.
2. Existing-data audit is complete. `linear` was selected by the frozen rule.
   Do not rerun audit/prepare or change fixed-controls.json. The 72-choice screen
   remains failed; no model can be deployed by this study.
3. Resume with Python 3.12, OPENBLAS_NUM_THREADS=1, repository cwd, command
   `tools/research/paired_sampling_audit.py run`. This validates hashes, skips
   already complete labels, and waits for idle production before new GPU jobs.
   Launch hidden. The runner sets the NVRTC DLL path for its child executable.
4. The runner validates all 150 labels, writes evaluation.json and REPORT.md,
   then sets status stage to complete. A failure writes its reason to status.
5. At completion review report and direct/adjusted results; verify frozen inputs
   and qualification coverage. Do not automatically add labels or train models.
   Record conclusions in plain English. Add a useful comparison plot if helpful.
6. Commit only this study and its scripts/tests; do not include unrelated outputs.
   Push master using the Windows OpenSSH override if the default SSH fails.
   Verify remote HEAD. Tell the user the outcome and recommended next step.
7. Remove the completion heartbeat once finished. Notify only completion, failure
   or a decision needed; stay quiet during ordinary progress.

Three focused tests cover paired-board cancellation, pair-mass ratio weighting,
missing support and stratified resampling. The real-data audit also checks unit
resampling recovers all original target estimates. Source hashes freeze at
manifest registration. Preserve originals if a genuine bug requires an amendment.
