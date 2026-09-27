# Weighted replay storage and fitting: numerical controls passed

The separately typed weighted reservoir and objective preserve source-deal
weights through retention, grouping and checkpoint recovery. These are numerical
components only; they remain disconnected from poker training and production.

## Results

- Algorithm R retained exactly the same visits and RNG state as the existing
  reservoir when every weight was one. The original grouped objective was also
  reproduced with unit weights.
- Saving after 60 synthetic visits, restoring, then continuing to 120 visits
  reproduced every retained array, weight and RNG state exactly, including
  reservoir replacement at capacity 37.
- Grouped weighted loss plus its residual-variance constant matched the direct
  ungrouped weighted loss with zero measured discrepancy. Maximum float64
  gradient discrepancy was 2.78e-17.
- Eleven negative controls rejected invalid or missing weight semantics,
  incompatible old/new checkpoint formats, changed context and damaged retained
  weights. Rejected insertions left both data and RNG state unchanged.
- A separate RTX 3090 control compared eight Adam steps with the same float32
  objective and initialization on CPU and GPU. Maximum parameter discrepancy
  was 4.95e-7, gradient discrepancy 3.36e-8, and loss discrepancy 8.95e-8. These
  were below the declared tolerances. This was a tiny synthetic numerical check,
  not a performance benchmark or a learned poker policy.

The fixture uses twelve previously inspected visible catalog observations with
explicitly synthetic action-menu lengths, signed targets and importance weights.
Those altered menus/targets are not presented as real poker observations.

## GPU admission detail

The first combined control recorded a GPU skip. Its imported CPU-only diagnostic
helper intentionally hid CUDA from that process, so this was not evidence that
the user's GPU was occupied. A first separate launch encountered the same import
effect and stopped before registration. The dedicated CUDA control now uses an
independent activity probe, checked available GPU memory/utilization and research
locks, acquired its own lock, and completed successfully. Existing registered
CPU results and source files were retained unchanged. No user process was stopped.

## What remains

These controls do not yet qualify a full weighted learner. Every later training
record must retain its correct source-deal weight. BB root updates need a new
weighted accumulator; preflop lookup means must use the same weights; complete
model checkpoints must identify the new semantics. Population-integrated exact
BTN updates must remain unweighted by sampled deals. The ordinary held-out
evaluation law remains unchanged.

The next gate is to validate those adapters on reused evidence, including
all-ones legacy equivalence and direct calculations. Only then should a bounded
GPU training pilot compare coverage, fitting behavior and compute cost. No
claim of better ranges, convergence, or poker strength follows from these tests.

Evidence: `weighted-learning-control-v1-{registration,result}.json` and
`weighted-learning-cuda-control-v1-{registration,result}.json`, with both tiny
fixture checkpoints retained. Production code was not changed.
