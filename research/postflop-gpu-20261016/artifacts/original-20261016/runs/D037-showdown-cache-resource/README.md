# D037 showdown-cache compiler/resource probe

Prepared only. No compilation, CUDA context, kernel launch or solver execution occurred during preparation. Root alone executes after independent review and ownership of the serialized build/GPU slot. This probe has **zero kernel launches**, no numerical corpus and no timing/speed acceptance.

The local baseline CUDA is exact accepted E015. The candidate is byte-identical to the separately reviewed `runs/D037-showdown-cache-design/candidate/kernels.cu`; its copied host mod.rs changes only both dynamic shared expressions8→16. The probe compiles both complete CUDA sources under compute_120 and all other default NVRTC options, then loads only up_show for resource queries in the same RTX5090 context. It uses the pinned existing cudarc/serde_json rlibs. CUDA result calls use explicit unwraps, as in D031, so they do not rely on the optional cudarc std::error::Error feature that caused D036R2's pre-GPU build failure. A panic/error is a failed retained attempt.

For each source, query registers, local bytes/thread, static shared bytes, kernel max threads/block and theoretical occupancy at128 threads for these seven shapes:

| Shape | nh_o | max valid opponent hands | Baseline dynamic bytes | Candidate dynamic bytes | Provenance |
|---|---:|---:|---:|---:|---|
| Rainbow P0 |319|314|3788|6300|Observed accepted D033 graph metadata; independent all-runout census agrees|
| Rainbow P1 |257|252|3044|5060|Observed accepted D033 graph metadata; independent all-runout census agrees|
| River P0 |280|280|3360|5600|Frozen final-board hands; game.rs excludes only extra cards, which are absent|
| River P1 |233|233|2796|4660|Frozen final-board hands; game.rs excludes only extra cards, which are absent|
| Full-hand upper bound |1326|1326|15912|26520|Conservative capacity bound, not an actual river fixture|
| Empty sorted opponent |319|0|1276|1276|Synthetic resource edge; not numerically executed|
| Single sorted opponent |319|1|1284|1292|Synthetic asymmetric resource edge; not numerically executed|

The host reservation is `4*nh_o+8*m_max` before, `4*nh_o+16*m_max` after. Device default/opt-in per-block shared limits, shared bytes/SM and max threads/block are queried once. Static shared storage is included when reporting default-limit fit. No dynamic-shared opt-in attribute is set, and theoretical occupancy is not an executed launch. Exact two-tone per-plan maximum metadata was not available here; do not claim its fixture-specific occupancy was queried. The conservative1326 bound addresses only capacity feasibility.

Run the one-shot prepared attempt only after review:

```powershell
& 'C:\Program Files\Python312\python.exe' -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D037-showdown-cache-resource\run.py' --execute
```

The runner verifies sealed local inputs, accepted checkout hashes and exact rlibs outside/inside `gpu-run.lock`, before launch and afterward. It refuses active live solves, requires50GiB S: reserve plus1GiB output reservation, and keeps pre/post telemetry only. Fixed limits are600 seconds per rustc/native stage, with file-backed stdout/stderr and a10-second dashboard heartbeat preserving accepted/deployment fields. Failure, timeout, interruption, status-write error or drift triggers child cleanup and retained failure evidence; `execution-started.json` prevents retry/overwrite in this directory.

Expected `D037_RESOURCE` markers: one device row,14 resource rows in baseline/candidate then table order, and one completion row. The runner verifies dimensions, exact source FNV/length, counts and zero launches. Full/entry PTX, static opcode counts, other-entry byte equality, source/rlib/DLL/binary hashes, commands and logs remain evidence. Resource differences can motivate or reject a later native experiment; they do not prove numerical equivalence or any complete-cycle benefit. Existing frozen primary and broader correctness controls remain required if a candidate proceeds.

The candidate and design were independently reviewed before this probe preparation. All files are outside the checkout; no frozen evaluator, accepted implementation, server or live session was modified.
