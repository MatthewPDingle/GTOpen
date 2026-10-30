# Saved-data preparation profile

25 September 2026. CPU-only profiling used the completed replication's final
checkpoint and batch 78/00, selected before timing because the retained data
are at their largest. No training, new chance samples, new policy or production
change was performed. Global storage was freshly measured before each attempt;
new output was capped at 10 MB with a 600-second worker deadline, 20 GB host RAM
reserve and 40 GB T: free-volume floor.

The first profiling harness was rejected before processing: it supplied the
registration configuration to the checkpoint reader, omitting the recorded
device/NumPy/Torch metadata present in the completed result. The strict identity
check correctly refused it. V1 source, registration, failed status and log are
preserved. V2 uses the completed result configuration and verifies every
original registered configuration field still agrees. This was a harness
correction, not a change to the experimental checkpoint or registered sources.

V2 completed in 143.532 seconds. The profiled sections reported 181,334,812
function calls and these elapsed times:

| Section | Instrumented seconds |
| --- | ---: |
| Restore final checkpoint | 51.156 |
| Group BB retained rows | 0.360 |
| Build BB visible features (245,141 rows) | 55.453 |
| Group BTN retained rows | 0.140 |
| Build BTN visible features (121,251 rows) | 27.500 |
| Parse one native query batch | 0.094 |
| CPU base-policy inference, 29,046 observations | 6.750 |

Profiling adds overhead, especially to Python-heavy work. These numbers locate
hotspots; they must not be used as an uninstrumented baseline or extrapolated
into an end-to-end speedup claim.

## Concrete hotspots

1. Visible feature construction dominates the selected workload: 395,438 calls
   to `from_active_features`, including 14,235,768 calls to its small `one`
   decoder. Each decoder scans the feature set again. The visible-card rank and
   summary calculations also repeat across observations with identical visible
   cards but different betting histories. Grouping itself is comparatively cheap.
2. Checkpoint restoration repeatedly validates nested banks and models. The
   profile records 397 base-model validations, 786 preflop-table constructors,
   1,824 JSON decodes and 325 canonical JSON encodes across the nested restore
   and selected operations. Reservoir reconstruction also contributes. This
   warrants scoped caching of authenticated immutable objects and validation
   results, not removing validations or trusting mutable files indefinitely.

## First optimization to test

Implement a separately versioned feature builder which validates/decodes the
36 one-hot groups in bulk and reuses the unchanged visible-summary calculation
for identical visible card tuples. Compare all output bytes against the old
builder on both complete saved retained datasets and native observations.
Include malformed rows, invalid one-hot groups, missing/duplicate/future cards
and invalid public history. Preserve the original 302 inputs and action/history
features. Benchmark without cProfile, include allocation/setup cost, and retain
the ordinary scalar implementation as the reference.

Only after equivalence and timing checks should a new fitter/inference/audit
version consume the optimized builder. Existing registered modules and completed
artifacts stay unchanged. GPU batching and parallel audit work remain separate
subsequent candidates; this profile did not measure their speedup potential.

## Records

`saved-preparation-profile-v2-result.json` records the phase timings, row counts
and feature-byte hashes. `saved-preparation-profile-v2-cprofile.txt` contains the
top 45 cumulative-time functions. V1 and V2 each retain registration and terminal
status. V2 verifies its frozen source inputs after profiling, and checkpoint
restoration authenticates the stored objects.
