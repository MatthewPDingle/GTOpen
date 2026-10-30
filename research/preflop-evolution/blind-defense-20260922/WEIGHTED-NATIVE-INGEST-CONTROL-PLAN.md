# Weighted native visit ingestion

Generate 512 class-stratified physical deals and process the first 32 with the
existing native query, traversal-verification and version-2 action-trace binaries.
Use a uniform frozen policy and the existing complete physical all-in cache and
population matrix. Keep the original exact initial and conditional postflop
target derivations unchanged; attach weights only after all validation succeeds.

Compare both players' weighted reservoirs against an independent oracle that
uses each native trace target's explicit deal index. Capacity 97 forces Algorithm
R replacement. Require exact retained weights, visible rows, visit counts and RNG
states; original unweighted ingestion must retain exactly the same target values.
The independent target arithmetic tolerance is 1e-10. Cover both players and
preflop, flop, turn and river. Reject moved deals, wrong offsets, unweighted stores
and corrupted late targets without changing any weighted reservoir or its RNG.

This is a single-process CPU control with a 180-second cap, 64MiB output cap,
20GB free RAM requirement and below-70% CPU load at admission. It does not train
a model, acquire the GPU, restart the application or interfere with user solves.
Record binary/source/input hashes before the published run. Full model and
checkpoint versioning plus an end-to-end training pilot remain outstanding.
