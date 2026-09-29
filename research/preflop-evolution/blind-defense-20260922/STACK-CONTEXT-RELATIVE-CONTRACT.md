# Relative hand inputs in the native context-aware inference path

Keep the qualified 362-input context registry and policy unchanged. A separate
registry and policy type append the 25 river-relative features to make 387
inputs. The original 302 card/history inputs and 60 public stack/price inputs
remain in exactly the same order. Earlier streets get 25 zeros; their existing
phase inputs identify that the river-only information is unavailable.

The adapter consumes actual checked native observations and actual own-action
histories. It must not fabricate histories, expose opponent cards or use later
board cards. Exact context hashes continue to route local preflop tables and
prevent fitting on held-out contexts. Context hashes are not numeric inputs.

Model objects have a distinct policy type and registry representation. Old
362-input models are rejected by the new reader, and vice versa. An explicit
neutral extension function may copy an old model into the new format only when
the contexts and their fitting roles match exactly. The 25 new weights start
at zero. Keep the original 362-column multiplication separate, so the extension
does not change existing arithmetic before those weights are trained.

The existing stack-normalized target units, action legality, per-context table
overrides, and own-reach weighting of played model mixtures are retained.
This is still an inference/model-object contract, not a resumable training
checkpoint or a promotion of the pending relative-input learning experiment.

CPU control: use the already retained native queries at all seven registered
depths and the two existing synthetic model objects. No new poker deals or
strategic labels. Require exact original-input, neutral policy, table and
own-reach-average equality; verify river inputs against the diagnostic feature
assembler. A synthetic nonzero extension must affect river predictions while
leaving earlier streets unchanged. Verify object roundtrips, rejected old/new
formats, held-out fitting, invalid extension parameters, and hidden-data
invariance. CUDA inference remains unqualified until resources permit its own
comparison; do not infer GPU parity from these CPU results.

Use four CPU workers, one BLAS thread each, at most 15 minutes, 16 MB new storage
plus 16 MB reserve. Keep the 800 GB allocated research cap and existing
CPU/RAM/disk admission guards. Acquire the research lock. Preserve all prior
studies and the separately queued GPU trial. Production 56708 is unchanged.
