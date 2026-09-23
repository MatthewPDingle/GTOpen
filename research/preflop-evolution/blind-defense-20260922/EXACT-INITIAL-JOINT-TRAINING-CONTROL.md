# Joint training and restart control

The corrected BB targets and separate exact BTN response state now run together
through a small native/CPU training pipeline. This is an integration result,
not a better-ranges or performance result. No production change was made.

The control starts with uniform models, draws 32 new physical deals per update
in two batches, executes both native updater passes against the same frozen
played model, derives separate BB root learning targets, fits both visible-input
networks, and updates the exact BTN accumulator once. It publishes a complete
next model and checkpoint only after both fits and the exact update finish.
The sampled BTN records remain in the network's training reservoir; the exact
table overrides its initial response at runtime.

Two updates completed with four small fitting steps per player, followed by a
replay of update two from the saved update-one checkpoint. The control uses
257-row reservoirs to exercise replacement. It uses the existing native
conditional-all-in verifier and the complete all-in cache. It intentionally
runs on CPU with CUDA disabled so it does not compete with the live evaluation.
This is correctness work, not CPU preflop performance optimization.

## Results

- 64 fresh training deals plus 32 replayed deals; about 23 seconds total.
- Identical replayed native batches, queries, frozen policies, updates and
  derived-target audit artifacts.
- Identical final learned models, exact response state, played model bank,
  reservoir contents and chance/action/reservoir RNG states.
- Both saved checkpoints restore successfully. Sampled tables reconstruct
  from their corrected reservoirs.
- Independent scalar reconstruction of every exact BTN update agrees within
  2.14e-13 bb. Opponent shove reach enters once; sampled visits add no extra
  updates to the exact accumulator.

Older raw native queries omit own-action history. The training adapter adds an
empty history in memory only at the structurally first BB decision and initial
BTN shove response. Explicit nonempty histories there are rejected. Raw native
documents on disk stay unchanged, and later histories are not fabricated.

The next gates remain CUDA policy parity and actual CUDA training/restart,
followed by a registered fresh training comparison. The current broader
evaluation continues unchanged. This control cannot establish strength,
convergence, improved calling ranges, or transfer to other stacks/positions.

Evidence: `exact-initial-joint-cpu-control-v1-registration.json` and
`exact-initial-joint-cpu-control-v1-result.json`; the latter hashes all native,
model, checkpoint and replay artifacts under the registered T-drive store.
