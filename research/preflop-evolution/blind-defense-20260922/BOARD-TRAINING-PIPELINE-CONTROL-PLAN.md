# Complete board-root training pipeline control

This bounded qualification follows the CPU accumulator, typed checkpoint,
inference, native target and worker controls. It is not a range-quality trial.
Run it only after the current main evaluation and readback finish and the GPU
and production session are available. No current process is interrupted.

Use the existing qualified weighted GPU fitter: 512 stratified physical deals
per generation, subbatches of 32, two 8,192-visit reservoirs and eight optimizer
steps per fit. Board-root updates use four independent public draws per
generation, with their own prospective seed. Keep the existing physical
targets, exact BTN update, tables and original entry weights. The control
configuration and source hashes are recorded before execution.

The pipeline stages the full mutable state on a private copy. It launches four
single-thread CPU board workers alongside up to two physical-target workers
and GPU inference/fitting. It waits for complete ordered evidence before
updating the root and publishing the immutable checkpoint, and replaces the
caller's state only after that checkpoint and its metrics are written.

1. Initialize and save generation zero; complete generation one.
2. Deliberately stop generation two after physical target ingestion. Verify
   that the caller and restored prior checkpoint preserve all accumulators,
   reservoirs, played models and random streams.
3. Repeat with a stop after both fits and the new root update, before publication.
4. Complete generation two, then restore generation one and replay the update
   using four physical workers. Require identical model/checkpoint references,
   native subbatch artifacts, reservoirs, RNG states and played-bank order.
5. Compare CPU and GPU policies on native observations using the newly fitted
   model, with maximum probability discrepancy below 1e-10.

Bound the invocation to 1,800 seconds and 6 GB of evidence, leave at least
24 GB available RAM, 3 GB free VRAM and 40 GB free on S:, and stop if production
becomes busy. Record failures without automatically retrying or overwriting.
Do not change preselected seeds or select a favorable intermediate model.

Passing establishes mechanical integration only. Independent target/state
readback and interpretation of the current main study precede any registered
matched learning trial or claim of improved preflop ranges.
