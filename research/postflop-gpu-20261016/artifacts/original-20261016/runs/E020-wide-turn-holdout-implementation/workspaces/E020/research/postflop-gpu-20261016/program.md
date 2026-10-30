# Postflop GPU autoresearch — 16 October 2026

User-authorized goal: improve GTOpen postflop GPU solve speed without accuracy loss, and keep a live status page updated. The preflop model menu was simplified first. This is a new experiment series; old research inputs and closed results remain untouched.

## Locations

- Application and status page: `X:\Dev\GTOpen`; port 43735.
- Experimental source: `X:\Dev\GTOpen-gpu-research-20261016`, branch `autoresearch/postflop-gpu-20261016`.
- Starting source: `a1704976c9100a54a626bcfa069bfc7d7e984209`.
- Build artifacts and raw measurements: `S:\GTOpen-research\postflop-gpu-20261016`.
- Dashboard: `http://127.0.0.1:43735/research/postflop-gpu-20261016/`.

The research worktree is explicitly for controlled GPU experiments. It is separate from `GTOpen-fix`, which contains the older hero/adaptive-default changes. No production server restart is needed for the dashboard or menu edits.

## Fixed evaluation

The primary score is the sum of median complete-cycle wall times across the registered rainbow, two-tone and river fixtures. Each fixture uses `bench_spot.json` with the same board/rake overrides as the existing postflop benchmark. CPU storage is compressed; GPU arithmetic remains f32. Target is 0.3% of starting pot, checked every 20 iterations with a 400-iteration ceiling. No range, menu, rake, algorithm, precision, stopping threshold or check-cadence change is a speed optimization.

Complete cycle begins before tree construction and CPU arena allocation and ends after the converged GPU state is synchronized back to CPU. Record construction, GPU initialization, solving including checks, readback, iterations, exploitability bits and complete arena fingerprints separately. Cargo compilation and correctness hashing are outside the measured cycle. Runtime NVRTC compilation and CUDA JIT are included in GPU initialization: the fixed suite order puts the cold compiler cost on the rainbow fixture, while later fixtures may reuse in-process compiler caches. Small flushed stage logging is included in wall time. This measures fresh native solves in a fixed-order suite, not browser/HTTP latency or disk saving. Report those boundaries explicitly.

Freeze the benchmark source and workload hashes before recording the baseline. A necessary evaluator correction invalidates earlier comparisons and starts a new baseline version; never silently edit the score. Retain raw logs and rejected/invalid runs.

## Loop

1. Confirm the RTX 5090 identity, free VRAM, disk reserve, and live-server state. Serialize all GPU jobs. Never replace the user's active session to run a benchmark.
2. Establish repeated baseline results and exact fingerprints on this hardware; prior RTX 3090 timings are historical only.
3. Profile to choose one bounded implementation hypothesis. Change only the postflop GPU implementation or its necessary host plumbing.
4. Compile, run a correctness screen, and time the same fixtures. Preserve failed attempts. Reject crashes, numerical changes, threshold failures or changes that only make a component faster while the full cycle regresses.
5. For promising candidates, alternate baseline and candidate binaries for at least three repetitions each. Compare paired complete-cycle times and spread; do not promote a gain indistinguishable from noise. Target a reproducible aggregate reduction of at least 2%, with no repeatable material fixture regression (>3%). These are qualification rules, not permission to ignore smaller real effects in the ledger.
6. Require exact baseline/candidate arena fingerprints and exploitability bits at identical stopping iterations. Run the existing postflop saved-state/action-menu/resume controls, GPU library and CPU/GPU tests before accepting a candidate. Broaden checks only as required by the changed code.
7. Keep a validated improvement in the research branch; discard only that candidate's own implementation edits on rejection. Record rationale and next hypothesis. Do not overwrite other work or sealed evidence.
8. Update `status.json` after each stage and run. The dashboard must distinguish pending, rejected, validated and deployed changes. No nonzero accepted gain appears before repeat measurements and correctness qualification.
9. Continue from the strongest validated candidate. Do not stop merely because one change passes or an arbitrary round count is reached. Stop/pause when the user directs it or report a concrete blocker honestly.

Deployment is a separate recorded step after qualification: integrate the reviewed change into the main checkout, run required checks, preserve sessions and only then rebuild/restart if applying it to the live app. Do not claim a research gain is already active in the live binary.

## Initial hypotheses

Fresh profiling takes precedence. A candidate to investigate is separate launch sizing for independent per-hand action/chance kernels, keeping fold/showdown reductions at their original 128-thread shape. Common-action specialization, graph reuse, compact arenas and pinned transfers already exist. Do not blindly repeat rejected card-run showdown loops or parallel compressed upload decoding from the prior pass.

## Setup record

The first worktree creation encountered Windows path-length errors and Git removed the failed checkout. The retry with repository-local long-path support succeeded. No performance measurement came from the failed setup.

The process follows Karpathy's fixed-evaluator, one-hypothesis, measure, keep/discard and log approach, adapted to fixed-quality numerical solver optimization: https://github.com/karpathy/autoresearch.
