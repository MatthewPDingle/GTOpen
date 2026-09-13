# R03: normal-server integration qualified

The retained C01 + C07 + C09 + C14 GPU evaluator is available through
`PreflopGpu::new_throughput` in a normal `gpu` server build. The server selects
shared evaluation when it fits actual available memory; unsupported layouts or
allocation failures retain ordinary GPU evaluation and report the reason.
Unrelated research algorithms and the allocation fault hook remain excluded.
The configured numerical grouping, model, samples, precision, seeds, policies,
stopping criteria and save format are unchanged.

## Integration overhead found and fixed

Version 2 passed exact and saved-game checks, but failed the registered overhead
gate: small complete-work median was 8.60% slower than explicit C14. Large was
unchanged. The memory probe's CUDA context was dropped before construction,
repeating initialization. All failed measurements and source are preserved.

Version 3 holds the probe context through construction. Across the registered
three alternating pairs at each size, small complete-work median is +0.29% and
large -0.06%, both within the unchanged 3% limit. Every checkpoint and full arena
fingerprint matches C14. This is qualification, not another retained speed gain.

## Correctness and release evidence

- Version 2: all four construction modes at both saved-game sizes match through
  six sweeps, save/reload, and a seventh sweep. The saved files are byte-identical.
- Version 3 changes only the CUDA context lifetime. Both public-selected saved
  games still match those files and seventh-sweep results exactly.
- Actual partial CUDA allocation failures recover to the normal evaluator, free
  partial buffers and permit optimized retry, for both wide and narrow kernels.
- Retained PTX is byte-identical to C14. Expanded address/partial/cohort/reuse
  tests pass; version 3 repeats selection/recovery and numerical suites.
- Normal GPU regressions: 20 passed. Default solver regressions: 181 passed.
  Server tests: 20 passed, one manual benchmark ignored.
- Normal-feature server build succeeds. Isolated port 56710 loads both saved
  fixtures, solves six exact sweeps, saves identical files, reloads and continues
  exactly, stops during real work and deterministically replays the interrupted
  snapshot. Root publication matches the completed iteration. Postflop/report
  endpoints stay unchanged. The owned server is stopped afterward.

Independent audits: `check_r03_saved.py`, `check_r03_bench.py v2` (rejected),
`check_r03_bench.py v3`, `check_r03_v3_saved.py`, `check_r03_release.py`.
Raw logs, source maps/archives, input/executable hashes and individual timings
are retained. The final machine-readable result is `raw/r03-release-verified.json`.

Frozen server: `target/r03-v3-server-frozen.exe`.
SHA256: `5035a18f206e7364217e86154481faf2c139d6fdce43b936d630bbb64dc88c8e`.
Source was tested before this results commit; recorded source hashes and archived
files identify the exact build rather than assuming a later branch head.

## Rollout and remaining work

Ready for an eventual switch with `R03_SWITCH_PLAN.md`. Port 56708 was never
restarted or mutated during qualification. The live preflop session remained
stopped at iteration 16, postflop done at 210, and reports idle.

The retained sequence's paired large fixed-work ratios imply about 20.6% less
runtime versus the original baseline. This is workload-specific; it is not a
direct convergence-time measurement, fewer iterations, or the desired 10x gain.
The broader convergence research goal remains open. No model training is part
of this release.
