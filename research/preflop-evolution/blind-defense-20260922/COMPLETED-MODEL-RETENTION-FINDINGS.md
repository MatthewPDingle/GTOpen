# Lossless model retention for the matched showdown study

The live four-arm experiment and its independent readback remain in progress.
These controls address storage and reproducibility, not poker strength. No fresh
evaluation deals have been sampled, and no production changes were made.

## Why this work is needed

`showdown-training-storage-projection-v1.json` records the first baseline arm at
38 updates. Its batch archives project to about 2.65 GB across 312 updates. If
every arm had the baseline's four model families, model JSON would add about
1.47 GB. Corrected arms have three families, so that second estimate is
conservative. Reservoir snapshots, restored final reservoirs and working scratch
also consume space. This is a risk to the existing 4.25 GB output cap, not proof
that the cap will be exceeded. The cap and the 800 GB global ceiling are unchanged.

The supported retention path archives only immutable objects from the newly owned
matched-training directory, after the selected arm finishes all 78 updates and
passes its full independent audit. Each original byte remains recoverable. Older
research originals are outside this path and remain untouched.

## Tests completed

* `archived-checkpoint-objects-control-v1-result.json`: copied 24 objects from the
  completed corrected integration control. The 7,441,152 original bytes occupy
  834,616 archive bytes. All original bytes were recovered exactly, model
  generations 0, 1 and 2 validated, and the real two-update checkpoint restored.
  Wrong hashes, path traversal and conflicting raw/archive files were rejected.
* `compact-showdown-bank-control-v2-result.json`: the real audited eight-update
  baseline bank still matches its saved played initial policies over 265
  observations, with maximum probability error 2.22e-16. Archived corrected
  control documents match their original validated documents exactly. Changed
  generations and relabelling corrected models as baseline were rejected.
* `completed-object-retention-control-v1-result.json`: the actual retention
  implementation recovered from an injected interruption after retiring one raw
  duplicate. It rejected changed completion evidence and a changed surviving
  original before further retirement. Resume and repeated completed cleanup were
  successful, and every archived object matched its source. Only new copies were
  modified; this was a CPU-only control.
* `showdown-evaluation-preflight-v2-result.json`: both evaluation modes and live-arm
  retention refused to start while the verified training worker owned the lock.
  No training files or lock bytes changed. The independent scalar evaluation
  reader still verified an existing 32-deal, 14,528-observation archived batch.

The compression ratio above describes a small control. It is not a guaranteed
full-arm ratio, and a full archived 78-generation bank has not yet been tested.

## Concurrency decision

Do not retire even a completed arm while the original training worker is active.
Its storage guard enumerates the whole output tree; concurrent deletion could
race a file-size read. The wrapper checks both locks and live Python processes,
then requires terminal training status and completed-arm/audit evidence. It never
stops training. If a resource guard ends training early, preserve that result and
recover from a verified checkpoint under a separately documented continuation;
do not silently raise limits or relabel the partial run as complete.

`retain_completed_showdown_arm_20260926.py ARM` is the gated entry point. Its
durable intent binds source/audit hashes before any retirement. Incomplete
compression artifacts are preserved and refused. A fully published archive can
resume interrupted retirement; every remaining original is checked first. The
wrapper checks the complete bank again through the archived reader afterwards.
This wrapper has passed live-worker refusal, not a completed live-arm execution.

## Evaluation handoff

Use `hu_showdown_complete_evaluation_v2_20260926.py --control` only after all four
78-update arms and their full audits finish. V2 uses the archive-aware bank loader
and adds the new retention/loader controls to admission. The associated scalar
reader is `hu_showdown_complete_evaluation_review_v2_20260926.py`.

Evaluation output prefixes now end in `v2`. The prospective design is unchanged:
64 reused control deals, then 65,536 fresh common deals with seed 9267201, all 78
played generations with weights 1–78, eight paired payoff comparisons, one final
look and the original simultaneous uncertainty method. No v1 fresh evaluation
was launched or inspected. V1 sources and their preflight evidence are preserved.
Full-bank CPU/GPU control, actual storage admission, fresh evaluation and final
independent analysis are still required.
