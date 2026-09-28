# Next research after native posterior64 controls

Updated 2026-09-28. Latest goal turn made progress: posterior64 estimation and
native two-stage timing controls completed. No live study process remains.
The full goal stays active. Read RIVER-POSTERIOR64-FINDINGS.md and the earlier
RIVER-LEARNED-BATCH-FINDINGS.md before implementing the next training step.

## Current evidence

- Earlier broader exact training improved two fresh local gates: prediction
  error -16.28%, Fold/Call cost -36.28%, with mixed subgroups/generalization gap.
  No full-preflop quality improvement has been established.
- Actual generation-77 policy pilot: 67 visited river records supported, exact
  sampled-pair agreement with the real native action trace; 68 other postflop
  rows and 12 preflop rows untouched. Exhaustive candidate processing stages
  cost ~20x baseline; not a complete training-time comparison.
- Shared native export: identical values, 1.2325x throughput in eight cases.
- Posterior64 retained control v2: exact posterior, unbiased conditional
  64-draw estimator and /64 covariance; 173,955 -> 106,131 prepared rows. All
  eight TRAIN cases, 67 targets, invalid-input/multiplicity checks passed.
  V1 failed before registration/computation on Windows manifest separators;
  preserve it, and use v2. The math module remains river_posterior64_v1.py.
- Native two-stage exporter hu_river_two_stage_v1: complete 990-pair histories,
  then complete trees for <=64 selected unique pairs. All native structural
  comparisons and 14 invalid controls passed. Exact sampled regret agreement.
  Paired full 29.272 s -> selected 11.578 s, 2.5282x throughput. All eight cases
  faster, one repeat each. No fit, live-model change or fresh quality test.

## Critical integration facts

The existing board pipeline calls weighted_training_workers_v1, then
weighted_later_action_ingest_v1 -> later_action_training_ingest_v1. It already
uses hu_sampled_action_trace_v2 to replace all positive postflop targets with
complete future-action expectations at the sampled private cards. That is the
baseline, not raw external sampling. A new callback result fed into the old
ingester alone would be overwritten.

Add a visited-river-only overlay AFTER the existing validated target derivation.
Keep its flop/turn rows, preflop exact initial targets and board-root overrides.
Do not propagate sample-visit-selected replacements into full-action ancestors
without an unbiased-selection proof. Source weights attach once at weighted
insertion/fitting, never inside a conditional target value.

## Next concrete work

Qualify actual weighted reservoir insertion, preserving visit count/order,
keys, metadata, weights and Algorithm-R RNG decisions. Reject incorrect
query/policy/trace/context/record bindings and illegal values before mutation.
The exact entry/posterior support is mandatory; unsupported targets must stay
explicit rather than receiving an invented distribution.

The earlier four pilot deals are reused unweighted TRAIN fixtures. Do not
fabricate stratified source weights for them. Create a valid complete source
generation with ClassStratifiedDeals (at least one draw per active class), then
take a bounded slice for the integration control with DealWeightGeneration.
Its contract requires the full generation metadata even for a short slice.
Use existing first_action_view for the ordinary bridge queries and validate
current model probabilities against board_training_policy_v1. Preserve
InitialTargets and all-in matrix/cache identities. The full private all-in
cache has 47,478 canonical pairs; the independent v2 review is the valid source.

After that, preregister small matched training from identical initial state and
use fresh full-policy evaluation. Cost must include the complete training path,
not just inference. Keep K=64 fixed for this candidate. The new code still costs
more than the original one-opponent method; test quality per elapsed time.

Before larger training, do not accumulate raw JSON exports for every row. Add
bounded in-memory/streaming transport with replayable input hashes and compact
retained evidence. Re-inventory global storage before admission. Last inventory
717.79 GB plus bounded later additions stays below 721 GB; limit remains 800 GB.

All executed sources/results stay immutable; version fixes. Spent final deals
are not tuning inputs. Broader stack/rake/sizing coverage remains an independent
requirement under STACK-CONTEXT-PLAN.md. No deployment, additional push,
historical deletion, Jev, Serena windows or other app popups.

Light desktop GPU sharing is authorized. Qualified GPU guard permits <65%
utilization with 4 GB own budget, 2 GB external headroom and 24 GB free RAM;
heavy workloads and production solves take priority. Last actual probe: 100%
GPU, so this turn used CPU only. Recheck current load before GPU work.
