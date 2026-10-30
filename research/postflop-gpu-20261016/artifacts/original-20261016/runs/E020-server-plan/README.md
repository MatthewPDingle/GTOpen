# E020 isolated server build and smoke plan

Preparation only: no command in this plan was executed. Root may build now that all cumulative measurements are terminal. Native unit/smoke execution follows E020 acceptance and confirmation that other GPU work is idle. These checks establish server integration only; they cannot change performance qualification.

## References and source identity

Reuse the successful `runs/E015-server-build.py` build/artifact-selection flow and `runs/E015-server-smoke/run_smoke.py` API sequence; exact reference paths/hashes are in reference-pins.json. Do not run those historical scripts unchanged: they select E015 binaries/main checkout, reuse an old target, and lack the new provenance/cleanup requirements below. All prior evidence remains immutable.

Build from X:\Dev\GTOpen-gpu-research-20261016, never the main/live checkout. source-pins.json fixes the current E020162-file solver benchmark map plus six explicit server Cargo/source files (168 total). Those six server files match E015's successful native unit inventory exactly. The only E020 solver production deltas remain the reviewed CUDA integer cache and two show_shared sizes. `python -B verify_sources.py` is an optional read-only pre/post check; it does not build or invoke native code.

## Build-only operation

commands.json supplies exact argument arrays. Under the existing GPU lock, verify all source/reference pins, at least54GiB free on S (50GiB reserve plus4GiB output allowance), all timing cohorts terminal, and no concurrent compile. Require S:\GTOpen-research\postflop-gpu-20261016\build-server-e020 previously absent, create it empty, and set CARGO_TARGET_DIR only to that path, RAYON_NUM_THREADS=16. Reject inherited compiler/profile/wrapper overrides listed in commands.json. Preserve rustc/cargo versions, source commit and dirty state, explicit environment absence, and complete stdout/stderr/Cargo JSON.

Run cargo build --release --locked -p server --features gpu --bin gto-server --message-format=json, then cargo test --release --locked -p server --features gpu --bin gto-server --no-run --message-format=json. Both are compile-only. Each child is hidden/file-logged, bounded1800s, with best-effort10s heartbeat and owned-child cleanup inside the lock on signal, exception or timeout. No failure triggers an equivalent live-server operation.

Require terminal exit0 and build-finished success, exactly one gto-server compiler artifact for each intended profile, paths under the fresh S target and correct server manifest/source paths. The first fresh-target solver and server must be fresh=false; reusing the SAME E020 solver during the second unit build is legitimate, but the unit executable itself must be fresh=false. Verify all168 source pins before/after both jobs. Freeze-copy to new S binaries/E020-gto-server.exe and E020-server-tests.exe, each with an adjacent manifest pinning source, Cargo artifact, dependencies, commands, logs, toolchain, binary SHA and exact CUDA embedding. Refuse existing destinations.

For BOTH executables, require the full exact E020 CUDA source bytes (SHA075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b) present and the full E015 CUDA bytes (SHA8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0) absent. Successful Cargo exit and source hashes alone are insufficient, as the preserved invalid holdout R1 demonstrated. No copying into a live/launcher target, no production source edit and no main checkout integration is part of this build.

## Inventory and unit check

The frozen unit executable --list --format terse must list exactly the21 names in unit-inventory.json before tests execute. Inventory listing executes no test; root may do it after build. After acceptance and GPU-idle preflight, run the unit command serially with NVRTC PATH and retain raw output. Require exit0 and exact summary20passed/0failed/1ignored/0measured/0filtered. The ignored test must be report_adaptation_benchmark; do not enable it. The ordinary report_gpu_continuation_uses_additional_budget_and_keeps_locks test uses CUDA, so the unit suite is GPU work and must own the GPU lock. Preserve its results separately from solver performance and all broader qualification.

## Isolated smoke after acceptance

Reuse the prior smoke's tiny river request and100-iteration solve exactly; copied spot-request.json/solve-request.json are byte-identical to E015. Root should make a new derivative outside checkout that changes only evidence paths/frozen E020 binary, plus explicit binary/manifest/source/acceptance pins and robust cleanup. The historical API helper already refuses POST to any base other than the test base. There is no need for an expanded test harness.

Under the GPU lock, verify immutable acceptance evidence and that unit/build work is terminal and GPU idle. Verify43736 is free; if occupied, stop the smoke attempt, never terminate its occupant or select another live server. Record GET-only live status before/after. Launch only the frozen S E020-gto-server.exe hidden, cwd research checkout, PORT43736/SOLVER_GPU1/SOLVER_COMPRESS1/RAYON16 and pinned NVRTC PATH. Save owned PID and launch hashes; verify that exact owned PID and executable own43736 before any POST.

Wait up to60s for GET /api/status idle/tree=null. POST the copied tiny river spot, then copied solve request (100iters,target0,check100,dcfr). Poll only the isolated status with120s solve bound; require done,iteration100,gpu=true,no error/gpu_note,finite outputs. POST /api/node at root and action0 check-child; require finite EV/EQ, two players, valid action dimensions, all strategy values in[0,1] tolerance and per-hand sum error<1e-5. No save/load/report/scenario mutation. All mutating requests stay on127.0.0.1:43736.

Finally drain/terminate only the owned test child, wait, and if needed use a bounded kill of that same verified child. Cleanup must occur even on failed readiness, request, assertions or signals, while the GPU lock remains held. Verify its PID exited and43736 released, source/binary hashes unchanged and live GET state unchanged. Preserve every failure; do not reinterpret an incomplete smoke as pass. No timed server-smoke speed claim.

## Explicit live restriction

The prior automatic-approval block on live replacement/restart remains binding. Never replace/restart the live process/server identified as37268/43735 or its executable, and never retry the equivalent action through another tool, launcher, shell, service or path. This plan permits only isolated S build outputs and a separately owned43736 process. A successful isolated smoke does not clear the live block or authorize deployment.
