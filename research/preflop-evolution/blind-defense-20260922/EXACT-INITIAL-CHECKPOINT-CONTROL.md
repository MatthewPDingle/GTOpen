# Separate exact-response model and restart state

23 September 2026. The proposed exact-response policy now has a distinct
version-4 model and checkpoint envelope. It contains the existing sampled
table/network base and the separately typed exact BTN response state. Old
readers reject the envelope; they cannot silently drop its override.

The envelope checks context, native catalog, population matrix, configuration,
generation order and object hashes. Each model must contain exactly one exact
state update per completed generation. The checkpoint contains only played
generations in its averaging bank and keeps the next, unplayed model separate.
Its nested base checkpoint retains the existing reservoir reconstruction and
random-stream checks. Restoration also verifies that both layers describe the
same base models, in the same order.

The CPU-only control repacked a historical four-update base checkpoint with
synthetic exact-state fixtures. Those fixtures were not trained together with
the historical networks: this is explicitly a serialization/restart test.
All reservoir arrays, reservoir random streams, deal sampler and action random
stream matched after restoration. The next 64 draws from each relevant random
stream matched, as did the next exact state update. Generations 0-3 remained
the played bank; generation 4 remained the next model.

Nine cases were rejected: old checkpoint/model readers, missing configuration,
changed population-matrix identity, reordered bank, including the unplayed
model in the average, state-generation mismatch, changed object hash, and a
duplicate exact update after restoration. The control took about five seconds
and launched no GPU work.

Remaining work before a new training trial: connect the version-4 runtime to
single-model and CPU/CUDA averaged policy evaluation, integrate the BB root
shove target correction, use the actual frozen played policies for each exact
state update, and verify a small complete training/restart/replay run. No
current candidate, active evaluation or production behavior changed. This
control provides no additional poker-strength evidence.

Evidence: `exact-initial-checkpoint-control-v1-{registration,result}.json`.
