# Source-inventory correction and native replay

Prepared before replay, 2026-09-28. The nine numerical control cases passed.
Readback found that the first runner inventoried tree/evaluator as directories,
but the actual dependencies are tree.rs and evaluator.rs. The original binary
was hashed before execution, and no source or binary has changed, but the
source inventory was incomplete. Do not edit the executed runner, first
registration or results to conceal the omission.

Record a separate complete inventory covering all solver src Rust files,
research_sampled helpers, native example, Cargo manifests/lock, unchanged
binary, original registered inputs and all exact old control inputs/outputs.
Then replay the same nine native requests using the same binary and require
byte-identical exports. Repeat all three malformed native requests and require
rejection without output. Verify every registered hash again after execution.
The original Python numerical tests need no change: their exact source and
inputs were registered, and the native bytes they consumed must be identical.

Limits: CPU only, one request at a time, 60 seconds per request, 180 seconds
total and 100 MB additional evidence. Reserve the full 64 MB native allowance
before every positive request. Preserve all original evidence. No GPU work,
training, application change, source mutation, archive deletion or deployment.

Passing this replay resolves source-manifest completeness for the qualification;
it does not retroactively make the first manifest complete or establish
self-play integration, convergence speed or accurate preflop ranges.
