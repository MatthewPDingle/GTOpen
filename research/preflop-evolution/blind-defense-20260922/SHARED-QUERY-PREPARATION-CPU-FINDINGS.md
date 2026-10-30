# Shared query preparation: CPU control

A separate CPU-only candidate prepares the common query arrays once for the
four complete model banks instead of rebuilding them for each bank. It passed
byte-for-byte comparison against the existing implementation on two previously
inspected 32-deal batches, containing 14,530 and 14,532 visible observations.
The live fresh evaluation and production application were unchanged.

Six arrays matched in shape, dtype and bytes: visible features, acting player,
legal-action mask, ancestor indices, ancestor actions and ancestor validity.
Returned candidate arrays are read-only. Model-dependent tables, network
inference, overrides, own-reach weights and model accumulation were outside
this control and have not been integrated with the candidate.

The reference was not a separately rewritten approximation: the control
extracted and executed the CPU preparation statements from the existing
`VisibleHybridCudaBank64.average` source. Both source identity and the extracted
AST were registered. Query archives were authenticated against the completed
control and independently decoded with compressed and original-byte checks.

| Operation across the two saved batches | First timing | Second timing |
| --- | ---: | ---: |
| Prepare separately for four banks | 2.688 s | 3.703 s |
| Prepare once and reuse | 1.031 s | 0.938 s |

Order was repeated/shared/shared/repeated. Combined preparation speedup was
3.25x, saving 2.211 seconds per two-batch pass, or approximately 1.106 seconds
per batch. These are short, cached-input CPU timings under concurrent study
load. Their variability is visible in the table. They do not prove an
end-to-end speedup, GPU agreement, or savings for larger or different trees.
No new poker evidence or fresh deals were generated.

## Remaining integration gate

After the fixed study releases the GPU, qualify an implementation that uploads
these common arrays once and shares them across the four bank predictions.
Keep the input batch immutable, validate each bank's context and geometry,
and continue preparing model-specific tables separately. Compare all policies,
own-action reach weights, native paired values and independent archive readback
against the current implementation on previously inspected deals. Measure full
batch time, memory and serialization/publication costs before adopting it.
Do not transfer this step-level speed ratio to overall runtime estimates.

## Evidence

- Candidate: `tools/research/shared_visible_query_arrays_v1.py`.
- Control: `tools/research/hu_shared_query_arrays_control_20260925.py`.
- Registration: `shared-visible-query-arrays-control-v1-registration.json`,
  SHA-256 `c3e4aec4ef3d112608973b66c83db3ae8d65f26a5aa109c7edc39e287a3a0859`.
- Passed result: `shared-visible-query-arrays-control-v1-result.json`,
  SHA-256 `df21bece8f49db6ba465fb4440830353214bb132e8d4466bcdd610bc62e87840`.
- Source result: `later-action-recovered-evaluation-control-v1-result.json`.

All registered source files were rehashed after the control and checked again
before documenting this result. The candidate remains unintegrated.
