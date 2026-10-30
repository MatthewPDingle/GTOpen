# E027 R2 fixed primary after a compile-only ownership repair

R1 Cargo stopped with E0382 before any native test or timing. The original source, scripts, authorization and failed-build logs remain unchanged and are pinned in preserved-r1-evidence.json. R2 precomputes the same two reach lengths before GpuPlan fields are partially moved. CUDA and the other four owned files are byte-identical to R1; test inventory remains 84 passed and 4 ignored.

The only executable-script changes are R2 design/protocol bindings, runs/E027-build-r2, build-primary-e027-r2 and the R2 plan path. Fresh E027 binary names and all seven run IDs remain unused. New root authorization and independent R2 review are required. The existing child cleanup, lock, live-server, disk, fresh-artifact, embedded-CUDA and 162-source checks remain unchanged.

Fixed order: V027-unit, B089/E027R1, E027R2/B090, B091/E027R3. All 18 complete non-timing results and 138 convergence records must match. The unchanged 2% aggregate and repeated material fixture regression gates apply to all samples; no exclusions, extensions or rescue. No timing sample has been replaced. Primary failure stops before broader, holdout or cumulative work.

All conditional old/new logical reach-row, padding, actual workspace/plan/budget/board-swap, original/F32/state/menu/resume/paging, wide-turn and fresh-original cumulative gates remain unchanged in protocol.json. No conditional harness is added. No arbitrary resource nonregression gate is introduced.

This package is prospective and has not executed. Preparation only reads/hashes files and parses Python source; it does not import execution helpers, invoke Cargo, run tests, launch CUDA or modify checkout/status.
