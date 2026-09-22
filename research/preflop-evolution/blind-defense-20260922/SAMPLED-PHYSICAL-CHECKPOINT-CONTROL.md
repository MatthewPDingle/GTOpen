# Complete iteration-boundary research checkpoints

The CPU continuation control passed: after two tiny physical learning iterations,
the restored third iteration exactly reproduced uninterrupted execution. This
qualifies checkpoint mechanics for the registered research loop, not strategic
accuracy, CUDA training resume, or arbitrary incomplete-step recovery.

## Stored state

A checkpoint binds the original game-context hash and exact training configuration
to the physical deal sampler, action-sampling PCG64 state, both advantage
reservoirs (including replacement RNGs), completed iteration count, played model
bank and next model. Model files validate the 269–64–64–4 architecture, finite
parameters and positive advantage scales. Generation zero explicitly represents
the uniform initial policy.

After T completed iterations, the played bank contains generations 0 through
T-1, while generation T is the newly fitted model for the next iteration. The
unused next model must not enter the average strategy. Bank order and generation
identities are checked during both save and restore. The averaging rule remains
equal ordinary-CFR iteration weights with each model's own earlier reach; saving
the model bank does not replace that separately qualified averaging calculation.

Objects are immutable and addressed by content hash. A complete JSON manifest is
published only after its referenced models and reservoir objects exist. Restore
verifies every referenced object, refuses changed context/configuration, and
rejects paths outside the object directory. Temporary writes are confined to that
directory. Interrupted publication leaves unreferenced files rather than replacing
the previous checkpoint.

The caller must freeze state and save only at a completed iteration boundary.
Each model fit starts afresh from its registered seed, so there is no continuing
optimizer state between iterations. A stopped partial traversal or fit must be
discarded and restarted from the last completed checkpoint. This is not a promise
to resume in the middle of an optimizer step.

## Actual continuation test

The test uses eight fresh full-deck deals per iteration, a 257-visit reservoir
per player, and eight CPU fitting steps. These deliberately tiny settings exercise
state transitions, not useful poker learning. Both updater passes use the same
frozen model pair; each pass is checked against independent canonical policy
lookup by the Rust traversal reference.

After completing two iterations, the test saves and restores all state. It then
runs iteration three independently from the original state and the restored state.
The batch, query, policy and update files match byte for byte. Fitted model files,
all reservoir arrays and counters, all random-generator states, and the model bank
are identical. Sixty-four updater traversals were reference-checked in total.
The played bank contains generations 0, 1 and 2; fitted generation 3 remains unused.

Six negative cases are rejected: changed fitting settings, changed source context,
putting the unused model in the played bank, a misordered generation, mismatched
object hash and an escaped object path. Nineteen registered inputs were verified.
The control took 3.81 seconds, used no GPU and changed no production state.

Generated objects and per-step transcripts for this **disposable control** live
under `target/research-sampled/sampled-physical-checkpoint-v1/`; their hashes and
the checkpoint reference are retained in the result. A long research training run
must place its durable checkpoints outside the build/cleanup directory. The store
accepts an explicit directory for that purpose.

## Remaining work

The combined CUDA pipeline control is still queued behind the finite strategic
comparison. A substantive physical learning pilot needs those method results,
resource admission, a frozen training/evaluation plan, and durable storage. Exact
CPU continuation does not establish cross-device or cross-version equivalence;
configuration and runtime changes must be treated as a new experiment.

Evidence prefix: `sampled-physical-checkpoint-v1`.
