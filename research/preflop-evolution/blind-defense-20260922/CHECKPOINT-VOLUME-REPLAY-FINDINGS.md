# Fixed GPU update replay after checkpoint relocation

The saved pilot update reproduced its original checkpoint, all 80 native
calculation artifacts, fitted model results excluding timers, entire retained
reservoirs, accumulators, played bank, and next action/deal random streams after
restoring its preceding checkpoint on S:. No numerical tolerance was added.

The initial GPU control stopped at a stricter metadata-byte comparison. The
initial-policy document's `used_model` reference stored its keys as
`file, generation, sha256`, whereas the original in-memory reference had
`file, sha256, generation`. All decoded values, including all action
probabilities, were identical. Reordering only those three keys and using the
original JSON writer's terminating newline reproduces the original bytes.

The failed GPU control and its artifacts remain preserved. A CPU-only completion
reader checked the already-produced update rather than rerunning it. The first
reader attempt omitted the original writer's final newline in its byte proof;
that failed attempt is also preserved. Version 2 corrected the byte proof and
completed every remaining state and artifact comparison in 12.204 seconds.
The 106 files in the new compressed S: directory occupy 91,246,250 allocated
bytes (289,204,988 logical bytes).

This qualifies unchanged numerical continuation across volumes on the fixed
pilot. It does not establish better ranges or independently qualify the complete
live trial. The continuation must retain the old prefix, original 78 updates,
seeds, batch identities, and remaining original runtime. It still requires the
prefix audit and subsequent full split-history audit before evaluation.

Use `hu_later_action_volume_continuation_20260925_v2.py` for the continuation.
It differs from the earlier prepared runner only in selecting this completed
readback's registration, result, and status. The earlier runner remains unchanged
because the original GPU control froze it as an input.

Evidence: `checkpoint-volume-replay-control-v1-registration.json`, its failed
status and log, `checkpoint-volume-replay-review-v1-registration.json` and
failure record, and `checkpoint-volume-replay-review-v2-registration.json`,
result, and status. Passing reader registration SHA-256:
`73a38fec7f55e6998ff8c20e62201a77450517c94339d29629dd2c18c87c2132`.
