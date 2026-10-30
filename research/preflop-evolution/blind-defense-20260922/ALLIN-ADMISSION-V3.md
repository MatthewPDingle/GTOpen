# Correct the trainer's obsolete prerequisite before its first admission

The v2 study wrapper correctly verified the repaired hybrid workflow, but its
original child trainer independently required the failed hybrid evaluation v1.
The launch therefore stopped with FileNotFoundError before writing a training
registration, reserving the GPU, creating its store, generating a deal or fitting
a model. The v2 wrapper's registration, terminal status and failure log remain
preserved. This is a diagnosed launch repair, not an automatic training retry.

The new v2 trainer changes only its prerequisite from hybrid evaluation v1 to
v2, names the new training reviewer, and freezes this note. The training worker
is unchanged. The v2 reviewer changes only the trainer process name it must
reject as still running; all replay and integrity checks remain identical.
The v3 wrapper selects these two versioned entry points, records the failed
launch evidence and otherwise preserves its seven stages and complete-hybrid
admission helper.

Training and evaluation artifact prefixes remain v1 because no child training
artifact existed after the failed launch. The wrapper prefix becomes v3.
The original plan, cache, seeds, sample counts, fitting, numerical tolerances,
float32 evaluation decision, statistical families and resource guards remain
unchanged. See ALLIN-ADMISSION-V2.md for the numerical precision decision.

Entry point: `tools/research/hu_sampled_physical_allin_study_v3_20260923.py --run`.

Before this one launch, the source control verifies exact admission-only
changes, unchanged training worker syntax, the unchanged frozen pipeline,
completed hybrid prerequisites and the absence of child artifacts. No result
from the hybrid evaluation was used to retune the trial.
