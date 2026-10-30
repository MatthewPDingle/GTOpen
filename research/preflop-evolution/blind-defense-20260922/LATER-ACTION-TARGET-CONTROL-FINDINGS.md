# Later-action integration: implementation controls passed

The first diagnostic and postflop-only ingestion controls passed. This establishes that the proposed targets can be calculated and inserted without changing the sampled visit stream or existing preflop estimators. It does not establish better learned ranges.

## Conditional action values

Saved replication batches at updates 1, 26, and 78 retained exactly the original sampled roots and 10,912 traversal records. Their full integrated root values matched the established evaluator exactly. Exported advantages were independently reconstructed from the visible policy and conditional action values.

On a separate one-deal uniform-policy fixture, every legal action at every node was forced through the established evaluator: 455 nodes and 1,056 actions. Both players' root-value changes matched the conditional-value prediction. Minimum reach was approximately 0.00001808, so the test did not pass vacuously on zero-reach branches. Maximum root-delta error was 8.88e-16 bb; maximum error after dividing by reach was 2.73e-11 bb. The established evaluator also checked forward cashflow and conservation.

An independent scalar reader authenticated all evidence, reconstructed the released intervention transports exactly, replayed 10,993 records including the uniform fixture, and checked 4,566 derived targets. The reader did not rerun native poker traversal. Native diagnostic runtime was 7.36 seconds including its controller; independent readback took 3.22 seconds.

## Postflop-only training-data insertion

Version 2 of the native trace additionally binds its output to the exact policy transport. Its values and sampled output were identical to version 1 on all three saved batches.

The ingestion control covered 4,221 positive-tag postflop visits across flop, turn, and river. Of these, 2,153 target vectors differed materially from their sampled-action values. All 311 positive-tag preflop targets retained their previous derivation, including the population-integrated initial BB jam correction. The separate exact BTN and integrated BB root estimators are not replaced by pair-conditional trace values.

Small 97-row reservoirs deliberately forced repeated replacement. Across all three fixtures, keys, visible features, action counts, iteration labels, visit counts, and reservoir random-generator states matched the original insertion stream exactly. All retained preflop values were identical. A separate scalar reconstruction of the changed targets matched the resulting reservoirs within 1.43e-14 bb.

Seven malformed-trace cases were rejected before any actual reservoir mutation or random draw: old unbound format, missing policy identity, different policy, different batch, missing target, wrong physical deal, and a corrupted late target. This control took 16.38 seconds including its controller. No model was fitted in it.

## Next gate

A new version-7 model/checkpoint envelope explicitly identifies the postflop target estimator and captured-gradient fitter. A two-update CUDA integration control is being prepared/run separately. It must verify current-policy inference, full played-bank averaging, unchanged first-generation sampling, and exact checkpoint restart before any longer matched learning trial. This document does not report that later gate as passed.

The scientific hypothesis remains unproven: integrating future actions removes their conditional sampling noise at fixed cards, but leaves private-card and runout noise, limited representation, and action-tree approximation. Better training-fit losses or plausible-looking ranges alone will not qualify the change.

## Evidence

- `later-action-trace-control-v1-registration.json`, `-result.json`, `-status.json`, `.log`, and `-independent-review.json`.
- `later-action-ingest-control-v1-registration.json`, `-result.json`, `-status.json`, and `.log`.
- Native examples `hu_sampled_action_trace_v1.rs`, `hu_sampled_action_trace_v2.rs`, and shared `research_sampled/action_trace_v1.rs`.
- Python sources `hu_later_action_trace_review_20260925.py`, `later_action_training_ingest_v1.py`, and `hu_later_action_ingest_control_20260925.py`.

Production on port 56708 remains unchanged. The original evidence and model histories are preserved.
