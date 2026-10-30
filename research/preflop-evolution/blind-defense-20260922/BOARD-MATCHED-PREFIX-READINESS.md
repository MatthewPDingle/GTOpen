# Next board-root training run: prepared, not launched

The prospective two-seed, 78-generation study now has a bounded first-stage
runner, `tools/research/board_matched_prefix_v1.py`. Its default command only
checks preparation. `--run` requires the complete GPU pipeline control and its
independent trained-state readback, terminal upstream queues, idle production,
free research locks, sufficient RAM/VRAM and a new global storage inventory.
Those GPU control/readback results are still pending. No new training has run.

The first stage performs two generations per seed at the actual 512-fit-step,
262144-reservoir budget. Those generations count toward the fixed 78, rather
than being discarded pilots. Each arm then restores generation one and replays
generation two, checking identical saved models, checkpoint, random-generator
state, reservoirs and physical batch artifacts. Generation three is impossible
in this runner. Independent verification of the trained prefix and a measured
full-study storage budget must precede a separately prepared continuation.

## Hardware and storage

The existing pipeline overlaps four CPU board workers with two physical-target
workers and CUDA training. This is the qualified starting concurrency, not a
claim that six workers maximizes throughput. Use the full-budget stage timings
to locate waiting and qualify any faster worker/batch configuration on identical
inputs before using it in research. Preserve the current running evaluation.

Both prefixes and their restart replays share a hard admission allowance of
4 GB allocated storage, plus the standing 2 GB metadata/headroom reserve under
the global 800 GB research ceiling. This is a bounded prefix allowance, not an
estimate or admission of the complete study. Running guards use RAM, available
VRAM and free volume space; any other S: writes count conservatively against
the prefix's live growth allowance. Allocation scans occur at quiescent
generation boundaries, avoiding races with temporary native board trees.
Failed attempts remain available; explicit resume restores published complete
generation boundaries. There is no automatic retry or deployment.

## Checks completed

`board-matched-prefix-preparation-control-v1-result.json` reproduces all 2048
historical physical deals and 32 action-batch seeds from the first two
generations of both stratified controls. The only changed configuration fields
are the explicit policy type and board-root configuration. The pending-control
gate rejects execution before resource/CUDA admission. This verifies preparation,
not full-budget training correctness or playing strength.

`board-study-storage-control-v1-result.json` checks new-directory confinement,
inherited compression flags, byte equality and allocation accounting on S: and
T:. A separate readback reopens all four fixtures and verifies their hashes.
Windows initially reported 524288 allocated bytes per fixture directory; the
settled measurement is 81920 with the same 524288 logical bytes. Therefore
immediate allocation may equal logical size even when compression is inherited.
Admission must never pre-credit hoped-for compression savings. This fixture
ratio is not a prediction for training checkpoints.

Next: finish the fixed evaluation and its report, run the already queued GPU
pipeline control, independently read back its trained state, then admit and
audit this full-budget prefix. The generic prefix auditor and full-study
continuation remain to be prepared; do not bypass them.
