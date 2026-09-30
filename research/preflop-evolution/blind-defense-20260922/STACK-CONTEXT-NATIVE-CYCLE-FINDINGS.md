# The complete stack-aware training cycle now works

The five-depth native integration check and its separate saved-evidence readback
both passed on 30 September 2026. This clears the implementation gate for a
matched learning comparison. It does **not** demonstrate more accurate preflop
ranges, justify installing these weights, or complete the broader project.

The control collected actual native observations, including their betting
histories, at 20, 40, 100, 200 and 400 BB. Each depth used 169 physical deals,
one complete sampled public board, and the existing 64-opponent-sample river
target method. Both player networks were then fitted against the same frozen
generation, followed by one complete joint-state publication. Collection included
both players, all four streets, and nodes with two, three and four legal actions.
The 60 and 150 BB geometries received no training state.

These controls use explicitly unsolved, broad incoming ranges. They qualify the
implementation and coverage; they are not measured opening ranges or a selected
scientific training population. Only one update with 16 optimizer steps per
player was performed. The model produced by that update has not played and is
correctly excluded from the evaluated historical policy bank.

## What passed

- The original caller state remained unchanged until a complete publication.
- Restoring the published checkpoint reproduced the complete-state fingerprint.
- Interruptions before model publication and before checkpoint publication left
  the original state intact. Re-publication from the retained collected state
  produced exactly the same checkpoint. This is not a test of repeating native
  collection after a crash.
- A deliberately changed river policy affected upstream preflop values. The
  maximum change was 2.510465 in the retained board calculation. This confirms
  that the stages are connected; it is not a playing-strength improvement.
- The separate readback reproduced physical sample order, action seeds,
  weighted target derivations, ordered reservoir arrays and random state, and
  both preflop accumulators across all five depths. It authenticated the source
  files, native outputs and complete checkpoints.

The readback ran in 43.58 seconds using four CPU workers. It reuses qualified
ingestion routines and retained native evidence. It is not a second poker engine
or an independent reconstruction of every posterior target and full-tree value.

## Cost and next steps

The complete invocation took about 13.9 minutes. The measured training pipeline
was 809.31 seconds, including approximately 801.13 seconds collecting the five
contexts. The two CUDA optimizer phases together took 0.219 seconds, excluding
feature preparation, graph capture and publication. Consequently, increasing
GPU utilization alone would not materially shorten this particular control.
Native river-target preparation is the main measured cost in the worker logs.

| Stack | Collection time | BB visits | BTN visits |
| --- | ---: | ---: | ---: |
| 20 BB | 103.00 s | 2,167 | 398 |
| 40 BB | 139.25 s | 2,627 | 587 |
| 100 BB | 177.64 s | 2,999 | 656 |
| 200 BB | 177.28 s | 3,051 | 619 |
| 400 BB | 203.95 s | 3,143 | 828 |

The retained store contains 5.711 GB of original bytes, occupying 1.416 GB with
NTFS compression. Peak reserved CUDA memory was 197 MB. These are control costs,
not forecasts for mature policies, larger samples, or a full comparison. The
preceding V3 attempt exceeded its underestimated 4 GB logical artifact limit;
its failure is retained unchanged. V4 prospectively reserved 8 GB and passed.

Next, prepare the complete played-policy evaluator and a storage-bounded matched
362-input versus 387-input comparison. Fix the actual entry populations, budgets,
fresh evaluation streams and acceptance rules before generating scientific
labels. Test held-out prediction, complete policy value and upstream decisions
separately. Keep both training seeds, all stack depths, adverse outcomes and rare
costly mistakes visible. Lossless archival can reuse the already qualified
archive format rather than retaining many gigabytes of duplicate raw JSON.

No production change, deployment or GitHub push was made.

## Evidence

- Main registration: `stack-context-native-cycle-control-v4-registration.json`,
  SHA256 `dc0145a4933f271a49579c9b4b5d4ac858bab9d9b24164942a2e24d18b749ba8`.
- Main result: `stack-context-native-cycle-control-v4-result.json`,
  SHA256 `6990d0e7a78622182e55b6aee5ca6f9c0f284951f75a4733c65427a9e15ce591`.
- Readback registration: `stack-context-native-cycle-readback-v1-registration.json`,
  SHA256 `0fbf0652f17139b9deb0f200ee6745f0be9b83dacee38f44d441dad33984fbd3`.
- Readback result: `stack-context-native-cycle-readback-v1-result.json`,
  SHA256 `c88b621f6a05ff399849824cc31f83f757102ef48bab66e1ecdda890c622fdda`.

The result's 829.44-second timestamp precedes final artifact hashing; the process
reported 835.63 seconds at completion. Neither includes the separate readback.
