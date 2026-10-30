# Actual-policy river targets: integration and cost findings

2026-09-28. Both preregistered CPU experiments completed successfully. These
are target-generation and engineering controls, not new training or evidence
of improved preflop ranges. Production, saved games and deployed models were
unchanged. No GPU was used; the live probe found another workload at 100% GPU.

## The important baseline correction

The existing board training pipeline calls weighted_training_workers_v1, then
weighted_later_action_ingest_v1 and later_action_training_ingest_v1. That final
ingester already replaces **all positive postflop targets** with complete
future-action expectations at the sampled private cards, using the native
hu_sampled_action_trace_v2 output. It also preserves exact preflop overrides.

Consequently, comparing the candidate only with raw external sampling would
overstate its benefit. Passing callback-walker targets to the old ingestion
path would also let that path overwrite them. The remaining proposed benefit
is averaging over the opponent's private hand, conditional on the visible
state and actual action history, under one bound current policy.

The pilot therefore constructed replacements for **visited river rows only**.
It retained the existing full-action flop/turn rows and left preflop, exact
initial and board-root overrides untouched. It did not insert these selected
river values into ancestors of a full-action trace: that would need a separate
proof about selection by sampled visits. Prior single-target native transport
controls remain valid engineering evidence, but do not by themselves qualify
integration with this actual trainer.

## Learned-policy pilot

Artifacts: river-learned-batch-cost-v1-registration.json and
river-learned-batch-cost-v1-result.json; raw evidence in the matching directory.

- Four previously used TRAIN deals, evaluated under both last-played
  generation-77 policies: eight cases, 147 positive records.
- 67 visited river records, 66 distinct exports across cases; all supported.
  Each export enumerated all 990 compatible opponent pairs and all legal
  future river actions.
- Actual sampled-pair action values matched the current native training trace
  exactly. Maximum current-policy probability discrepancy was 8.89e-16;
  legal zero/nonzero support was identical.
- All 68 other postflop rows were unchanged. The 12 preflop rows and their
  separate overrides were not replaced. Source weights were not multiplied
  into values; they remain attached once at the original weighted ingestion.
- Conditional query sharing reduced 293,510 raw query rows to 173,955 rows.
- Measured baseline stages: 1.5125 s. Extra candidate stages: 28.7104 s.
  Combined stage ratio: **19.9819x**. This is not complete training time:
  independent qualification, some file handling, fitting, board-root work and
  publication are outside that ratio. One native export was reused across
  policy cases. The whole controlled experiment took 101.41 s.
- Retained raw evidence: approximately 189.87 MB.

Extra stage breakdown: Python union 7.70 s, query preparation 8.38 s, native
export wall time 5.77 s, conditional values/pair checks 6.08 s, inference 0.78 s.
More GPU utilization alone cannot address most of this measured cost.

## Shared native query export

Artifacts: river-shared-export-control-v1-registration.json and
river-shared-export-control-v1-result.json. New exporter:
hu_river_action_queries_batch_v1; new value reader: river_shared_values_v1.
Previously executed implementations were preserved.

The native batch shares visible queries across up to 32 target trees. The
reader validates the bound policy once for the batch. It changes neither the
trees nor the private-card expectations. The comparison used all eight pilot
cases, alternating old/new execution order and doing fresh native export work
on both sides. Qualification and evidence archival were timed separately.

| Measured stage | Old path | Shared path |
|---|---:|---:|
| Native export and JSON parsing | 10.673 s | 11.552 s |
| Python query union | 10.534 s | none |
| Query preparation | 7.993 s | 12.829 s |
| CPU network inference | 0.827 s | 0.781 s |
| Conditional values | 5.481 s | 3.647 s |
| Complete compared path | **35.508 s** | **28.810 s** |

The aggregate throughput gain is **1.2325x**, or **18.86% less elapsed time**.
All eight paired cases improved (1.028x to 1.310x), but this is one repeat per
case, not a stable hardware benchmark. Preparation was slower in the new path;
the cause was not isolated. Do not attribute it to a specific mechanism or
multiply this gain by prior preparation speedups.

Every compared native tree, observation, action menu, own-history link,
posterior, pair value, policy probability and resulting regret matched. Maximum
numeric difference was zero. Five malformed batch controls rejected without
creating output. Total experiment time: 101.80 s; approximately 330.17 MB of
raw evidence, within its 512 MB bound. No learning or production modification.

## Decision and next test

The shared format is correct and useful, but its gain does not make exhaustive
opponent averaging cheap enough to enable everywhere without a matched
time-to-quality test. Do not launch a large training run on a claim of free
variance reduction. Both experiments reused TRAIN material; no fresh held-out
policy improvement has been established.

The next bounded candidate should average **64 opponent hands sampled from
the exact current-policy posterior**, instead of expanding all 990 future
trees. Construct that posterior from all compatible pairs' entry weights and
actual opponent action-history probabilities, then normalize once. The first
stage needs only history queries; the second stage expands complete future
actions for the sampled pairs. Keep all hero action values on the same draws
and center with the same current strategy. Sampling with replacement from this
posterior gives an unbiased conditional sample mean; do not self-normalize a
sparse importance sample or divide by reach a second time.

First use retained full exports to qualify query closure, exact posterior
binding and estimator moments, and measure the two-stage query demand. Keep
K=64 fixed before seeing results. If worthwhile, implement bounded native
history/selected-pair transport and measure actual elapsed cost. A smaller
query count is not itself a speed result. Zero-support states must reject or
retain an explicitly recorded baseline, never invent a posterior.

Then qualify actual weighted reservoir insertion: identical visit order,
record identity, sampling RNG and source weights, changing only approved river
targets. Run a small matched training pilot and fresh full-policy evaluation
before any larger study. Local target accuracy alone is not the user's goal.
Full policy quality, convergence per elapsed time and later broader
stack/rake/sizing coverage remain the acceptance criteria.
