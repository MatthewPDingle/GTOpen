# R04: normal-build integration of retained C23

Registered against retained research commit 2de2678 before editing runtime code.
Port 56708 remains R03. No deployment is part of this qualification.

Promote a fresh, privately owned retained engine to the exact C23 table layout.
Reuse the existing primary context and constructed engine. Keep original cohort,
alias, sample, precision, scan and terminal arithmetic, batches and policies.
Apply only with retained cohorts and supported narrow offsets. Keep the same
final allocation check and reserve. The old table is released before allocating
its replacement. Do not count final storage savings as expanded game capacity:
this integration initially still needs the original retained layout to fit.

On promotion error, drop the incomplete private engine and rebuild the retained
engine; existing normal-GPU fallback remains available if retained construction
fails. Expose whether static tables were selected and the reason for fallback.
No partially promoted object escapes, and saved game format is unchanged.
Keep fault injection and evidence-file output out of ordinary application builds.

Qualification: preserve C23 writer/terminal PTX and all numerical invariants;
exercise selected, ineligible and failed-promotion paths, including actual CUDA
allocation failure and a successful retained retry. Run the existing integrated
cohort tests (save/resume, stop replay, zero/recovery, full arenas) and native
production-selector tests. Freeze source/executable before paired overhead tests.
Compare normal selection with the retained C23 research constructor for three
alternating full-work pairs per fixture: at most 3% median integration overhead.
Recheck saved-fixture continuation, isolated-server save/load/stop replay, normal
GPU/default/server tests and build before recommending a switch. Do not deploy
or claim a convergence gain merely because integration compiles or tests pass.

One guarded workload at a time; no source edits during a live workload. Existing
300-second build/test and 180-second fixture caps apply. Archive failures and
restore only owned candidate edits if qualification fails.
