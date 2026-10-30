# Bounded memory transport for river training targets

Prepared before execution, 2026-09-28. The continuous weighted ingestion v2
passed 54 river rows, with actual overflow for both players. V1 remains a
failed coverage attempt; do not overwrite it or count it as a pass.

The new native example hu_river_two_stage_stream_v1 preserves the complete
history/selected-tree export logic. It accepts one context-path argument and
up to 64 KiB request JSON on stdin; it returns the same <=64 MB JSON on stdout.
Diagnostics use stderr. No native intermediate file is created or deleted.
New river_training_overlay_targets_stream_v1 retains compact requests, output
hashes, model-dependent probability arrays and target evidence, and holds the
large native output only in memory. No other target calculation changes.

Replay all eight completed weighted-ingestion v2 cases, using exactly their
original valid source generation, source slices, current models, native fixture
identities and K=64 seeds. Validate every streamed native output hash/length
against its immutable file-mode counterpart; also compare query structure via
the decoded data and all retained policy arrays/target rows. Overlay bindings
must remain identical; generator evidence changes explicitly to name the new
transport and executable. No truncated or partial outputs are accepted.

Run the 11 original malformed native request controls through stdin and also
empty input, oversized input and wrong argument count. They must exit nonzero
without stdout. Retain concise rejection evidence. Compare old conditional
folder bytes against complete new conditional evidence bytes. This is a storage
and exact-replay control; do not claim training speed or range quality from it.

Maximum 180 seconds, 8 MB retained new evidence, one CPU process at a time,
24 GB free RAM and idle production. Native query/node/output bounds and a
16 GB coordinator memory guard remain. No GPU, fitting, push, deployment or
historical deletion. Inputs are registered/rechecked; failures are retained.
The overall research cap stays 800 GB, with large admission requiring a fresh
inventory. Follow with a matched training experiment using bounded artifacts.
