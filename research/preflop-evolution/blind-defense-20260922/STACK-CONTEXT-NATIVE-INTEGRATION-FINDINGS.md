# Native training integration: current evidence

The full joint training cycle has NOT passed yet. No new scientific learning
comparison has started and no better preflop ranges are claimed.

## Passed components

- The worker publication/identity/future suite passed three tests in 0.024s.
  It checks ordered reservoir insertion, rejects mismatched provenance, and
  distinguishes polling timeouts from a worker's terminal TimeoutError.
- Cached policy scoring passed all 14 CPU/CUDA/reference cases: two input
  representations across 20/40/60/100/150/200/400bb. Maximum discrepancy was
  2.220446049250313e-16. Separate saved-array and identity readback passed.
  These are routing/scoring controls, not poker-quality measurements.
- New native helper hu_sampled_allin_history_bridge_v1 exports actual own
  histories using the existing native policy-bank reconstruction. Its value
  traversal and conditional all-in arithmetic are unchanged.
- The history integration check passed for 13 retained physical deals at each
  of 20bb and 200bb: 1,920 and 5,911 observations, respectively; all four streets.
  It validated 5,499 and 21,762 ancestor edges. The full-policy scorer accepted
  both batches without relaxing its history checks.
- Removing only the added history field gives exactly the old query export,
  including ordering and features. Histories exactly match the established
  native bank exporter; this shares the same reconstruction routine, so is
  compatibility evidence rather than an independent poker-history algorithm.
- Key-dependent nonuniform fixed policies produced exactly identical old/new
  traversal results. All 52 updater traversals passed cashflow verification
  with zero discrepancy. No fitting occurred in this helper control.

## Preserved failures

1. stack-context-native-cycle-control-v1 stopped before native collection:
   progress logging used an immutable-file writer without replace=True.
   Its completed scoring-parity evidence was retained and reviewed.
2. stack-context-native-cycle-control-v2 corrected the logging and reused that
   evidence. It stopped before scoring the first native batch because the
   old all-in exporter omitted own_history. A concurrent full fixed-board
   worker finished and its raw tree/request/result were retained. No update,
   fitted network or completed joint cycle was published.
3. stack-context-history-bridge-check-v1 reached query/history agreement at
   20bb but stopped when its harness passed immutable-object bytes directly
   to the model validator. V2 parses the JSON, reuses those completed query
   exports, and passed both depths. The V1 failure and source remain intact.

The new helper is separate from all previously executed native helpers;
registered prior inputs were checked unchanged. Sources, registrations,
failures and results remain local. Production 56708 was not modified.

## Next milestone

Prepare a separately identified control using the qualified history helper.
Complete one joint update over the five fitting depths with 60/150bb held out,
then verify whole-cycle checkpoint restoration, interrupted-publication replay
and propagation of a changed river policy into the preflop value calculation.
Keep the original controls and gates unchanged. This remains an implementation
control with broad unsolved incoming ranges, not a scientific population or
an end-to-end preflop accuracy result. Only after it passes should a matched
learning comparison be registered.
