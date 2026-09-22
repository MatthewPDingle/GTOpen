# Hybrid evaluation recovery status

The original float32 evaluation failed its numerical gate before generating
held-out deals. The complete float64 control and independent readback passed.
The separately registered evaluation v2 has completed on the same candidate,
and its independent 1,536-batch audit passed. The original failed files remain
preserved. The [completed findings](SAMPLED-PHYSICAL-HYBRID-FINDINGS.md) do not
establish improved range accuracy; the candidate is not promoted.

## Correction to the frozen admission note

The [frozen repair plan](HYBRID-NUMERICAL-REPAIR.md) describes the discrepant
river alternatives as call and fold. That action-label wording is incorrect;
the numerical diagnosis uses action indices and its arithmetic is unaffected.
The actual alternatives are **bet and check**: the observation's public history
decodes to `[2, 3, 2, 5, 2, 2, 5, 1]`. Token 5 deals the river, and the sole
following token 1 is OOP's check. The sampled state implementation therefore
gives IP check as action 0 and its one bet size as action 1. Generation 6's CPU
float32 inference selected bet, while CUDA float32 selected check. Float64
reference arithmetic selects check.

This is a postflop numerical ambiguity, not evidence of a preflop fold/call
mistake or a reason to widen a preflop hand manually. The recorded 0.038989
averaged-policy difference, reconstructed scores and passed precision controls
remain valid. The immutable plan is retained with this explicit correction so
the active evaluation's registered hashes do not change.

Sources: `sampled-physical-hybrid-numerics-v1-result.json`, the observation-key
decoder in `crates/solver/examples/research_sampled/observation_v1.rs`, and the
action ordering/transitions in `crates/solver/examples/research_sampled/state.rs`.
