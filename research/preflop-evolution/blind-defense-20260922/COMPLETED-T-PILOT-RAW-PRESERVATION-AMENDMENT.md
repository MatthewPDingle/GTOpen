# Preserve two completed T: pilot evidence sets

This storage-only operation extends the earlier lossless preservation work to
`T:/GTOpen-research/root-retained-fresh-pilot-v1` and
`T:/GTOpen-research/exact-initial-fresh-pilot-v1`. Both have successful terminal
78-generation results. Verify their result/registration hashes, store paths,
generation sequence and absence of an active owner before admitting files.

The exact manifest is restricted to 3,744 initially uncompressed `queries.json`,
`policies.json` and `updates.json` files, totaling between 12 and 13 GB. Exclude
model/checkpoint objects and every direct input bound by the current evaluation
and deferred GPU-control registrations. Reject linked paths and anything outside
the two named owners. No original file may be deleted, moved or renamed.

First qualify six copies: the smallest and largest eligible file for each of
the three names, with at most 100 MB of copies. Test wrong-hash and outside-owner
rejection. A separate full-file reader must pass on these copies before originals
can be compressed. The live evaluation keeps its existing process and settings;
this operation neither uses CUDA nor starts a solve.

Use first-time NTFS compression, four CPU/I/O workers, at most 32 exact paths per
batch, a two-hour invocation limit and a five-minute batch limit. Require idle
production, at least 20 GB available RAM, 30 GB free on T:, and CPU below 50% at
admission. Recheck owner liveness before every compression batch. A dedicated
lock prevents duplicate preservation writers. Preserve batch journals for exact
verification on resume; interruption does not authorize deleting evidence.

Record and verify each file's logical SHA-256, length and modification time
before and after; separately reopen and rehash every final file. Report measured
allocation savings, not an assumed ratio. Historical disk-throughput numbers for
these files describe their former physical representation. All logical scientific
artifacts, model parameters, results and paths remain unchanged.

This amendment permits only the physical representation change in the admitted
manifest. It does not relax the 800 GB global research allocation ceiling or
admit the next full training study. Refresh the inventory and project that study
from measured full-budget generation sizes before launch.
