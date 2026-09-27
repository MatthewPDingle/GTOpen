# CPU snapshot candidate: qualified locally, not deployed

Profiling the first committed 14531-row evaluation query found substantial
Python call overhead in `copy.deepcopy`. Its job is important: the shared query
must be isolated from caller mutation while all four model banks evaluate it.
The candidate preserves isolation using a finite JSON-native roundtrip. It
rejects non-JSON objects, non-finite numbers and document-changing conversions;
it is not a general-purpose replacement for Python object copying.

`native-query-snapshot-control-v1-result.json` compares the first four committed
32-deal query batches, with three alternating-order timing repeats. Every JSON
field and all six derived query arrays matched the deepcopy reference exactly.
Six unsupported inputs were rejected. Snapshot-to-caller isolation passed;
the separate `native-query-snapshot-isolation-review-v1.json` also verifies
caller-to-snapshot nested mutation, list append and top-level replacement for
all four real queries.

| Batch | Reference copy + preparation | Candidate copy + preparation |
| --- | ---: | ---: |
| First | 0.9725 s | 0.8570 s |
| Second | 1.2078 s | 0.9937 s |
| Third | 1.1380 s | 1.0234 s |
| Fourth | 1.2004 s | 1.1042 s |

These are per-batch medians. Sum of candidate medians / sum of reference
medians is **0.8804**, about 12% less time for this CPU stage. The benchmark ran
alongside the existing evaluation; contention and timing noise limit precision.
This is not an end-to-end throughput result and must not be combined naively
with the earlier 83% model-bank time share.

`crossed_complete_policy_batch_snapshot_v1.py` prepares a separate GPU integration
candidate using the same tensor types, shared-query class, bank arithmetic and
native cashflow evaluator. Nothing imports it into the running study. Before
use, qualify complete policies, own-action reach and per-deal cashflows on fixed
previously used deals; measure full wall time with 32- and 64-deal batches.
The CPU result alone does not qualify the CUDA integration, larger batches or
an interrupted/resumed scientific evaluation with a changed implementation.

No poker outcomes or partial gain significance were used to select this change.
The current fixed evaluation and production port 56708 were not modified.
