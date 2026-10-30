# D031 child-slot compiler/resource probe

Prepared only. This directory is outside the checkout. No rustc, cargo, CUDA call, kernel launch, numerical test or timing run was performed while preparing it.

The baseline is the exact retained E015 CUDA source (also E004), 22,624 bytes, SHA256 `8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0`, FNV64 `3f0594b037a1dda3`. Candidate changes only the four training-up nested child-ID/CFV-slot lookups and the corresponding parameter name/forwarding. Prefix/suffix, entrypoints, math, action/hand order, parent-slot writes and other kernels remain unchanged. `source-checks.json` records mechanical assertions; `candidate.patch` is reviewable.

After the parent releases the serialized build/GPU slot, run once:

```powershell
& 'C:\Program Files\Python312\python.exe' -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D031-child-slot-probe\run.py' --execute
```

The script verifies sealed inputs and exact existing rlib hashes, takes `gpu-run.lock`, refuses active live-server solves, compiles a standalone Rust probe, then compiles and loads both local CUDA sources in one RTX5090 context. It queries only `up_action` resources with 128 threads and zero dynamic shared, matching the current kernel launch. It never launches a kernel or uses current checkout kernels. No cargo target or frozen binary is overwritten. Parent serialization is also required against concurrent compilation; the GPU lock alone does not police unrelated builds.

It records compiler command/logs/version, NVRTC DLL hashes, telemetry, probe hash, full/entry PTX, resources, static opcode counts and unchanged-entry comparisons. Preparation and execution records are separate. `execution-started.json` prevents a second attempt. A failure is preserved; do not remove evidence to retry. Existing D021-compatible cudarc and serde_json rlibs are fixed in `prepared-manifest.json`; dependency drift intentionally refuses execution.

Interpretation: changed PTX loads/registers/spills/occupancy can motivate a later solver experiment, but cannot establish faster or exact solves. Common-arity child addressing is already partly hoisted outside hand loops. Static opcode sequences do not prove float operand order or numerical equivalence, and virtual PTX is not executed SASS. The probe creates no mapped host/device table and measures none of its initialization, memory-admission or lifecycle cost. Those costs and full/compact/F32/locks/resume/continuation exactness would be separate obligations for any authorized production candidate.
