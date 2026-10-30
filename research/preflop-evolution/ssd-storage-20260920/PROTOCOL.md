# SSD-backed continuation storage study

Authorized after the user returned on 20 September and offered S: for research. This is a new daytime study, not an extension of the previous overnight deadline. Production 56708 and saved sessions remain untouched. Stop only research work if production starts solving or reporting.

## Stage 1: exact disk state

Extend the six-game, 720-pass explicit GPU reference comparison with disk-only parked strategy arrays under a new dedicated S:/GTOpen-research directory. Keep board metadata in RAM and share the seven large mutable GPU buffers. Release unused per-game pinned staging in candidates. Disk records contain a version, entry identity, generation, iteration, array lengths and a checksum; use a new temporary file, flush it, then rename before retiring the previous generation. A failed write must not discard the last committed record. Reject corrupt, truncated, wrong-entry or stale records before using them.

Every pass must exactly match all four resident reference arrays and returned values, including abrupt and zero incoming ranges, changed visitation order, and raw storage fallback. Reload each committed record for round-trip verification. Record bytes and time for state writes/reads, total runtime and resource samples. Compare to the previous RAM-only result descriptively, not as a controlled speed benchmark. Buffered file reads may hit the Windows cache: these timings do not establish sustained SSD bandwidth.

Compile at most two jobs. GPU test bounded to ten minutes, retain 20 GB free host RAM and 3 GB free VRAM; check production status throughout. Register hashes before execution and preserve failures. A pass qualifies only these storage fixtures, not production or the full forest.

## Stage 2: physical I/O feasibility

Use dedicated ordinary scratch files on S:, never raw disks, existing files or system settings. Run a bounded sequential write/read experiment with Windows unbuffered I/O and write-through so a RAM cache cannot masquerade as SSD performance. Use aligned buffers, verify deterministic payload content, record transferred bytes and timings separately. Cap scratch allocation at 32 GiB and total writes at 64 GiB for this initial experiment; preserve ample free disk space. Stop on production activity or low resources. Explicitly distinguish this bounded workload from drive-wide sustained performance or a solver benchmark.

## Stage 3: connected research integration

If the first two gates pass, integrate bounded RAM caching plus SSD parked states into the isolated connected continuation harness. Account for metadata, pinned staging, full restoration buffers and cached arrays. Validate checkpoints and values against an existing small complete reference before increasing board coverage. Select the larger run only from measured RAM/VRAM/I/O costs. Keep reserved validation cases separate, retain algorithm and action-tree fidelity, and record precision, board coverage and convergence limits. Do not deploy the prototype into the user's app.
