# D066 fold-input positive-zero census

This package reuses D045's fresh GPU-only build and one ignored invocation, with D065's exact two pre-existing PTX file allowances. It runs no performance cohort. Source and frozen workload are under `source/` and `design/`; neither is changed by these scripts.

Root alone may activate the append-only mod declaration and new helper after independent review, then write `authorization.json`. Its schema follows D045: `candidate: D066`, booleans `E020_accepted`, `E020_server_qualification_pass`, `independent_source_review_pass`, `independent_script_review_pass`; `candidate_sources` maps the two repo-relative owned paths to `{path, sha256}` of their frozen candidate files; `prerequisites` has `E020_acceptance`, `E020_server_qualification`, `D066_source_review`, `D066_script_review` as `{path, sha256}`. `evidence_sha256` includes those four reports, this scripts-manifest and every immutable execution prerequisite. The actual authorization is intentionally outside this seal and requires a separate root execution decision.

Root commands, in order, each only after observing the preceding terminal success:

```powershell
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D066-fold-zero-census\build.py' <authorization-sha256>
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D066-fold-zero-census\run.py' <authorization-sha256>
& 'C:\Program Files\Python312\python.exe' 'S:\GTOpen-research\postflop-gpu-20261016\runs\D066-fold-zero-census\assess.py' <authorization-sha256>
```

The single run is `D066R1`, filter `gpu::fold_zero_census::fold_zero_reach_census`, expected summary 1 passed and 88 filtered. All three fixed fixtures are processed sequentially with two ordinary E020 solvers. Six snapshots precede evaluation at iterations20/final200/200/60. All23 convergence anchors and three complete final CPU state fingerprints must match immutable B065/E020C1 evidence.

The runner creates fresh `runs/D066-execution/census`, exposes it through `D066_CENSUS_DIR`, retains three mapping and twelve row-flag files and SHA256-pins them. The assessor checks all39 markers, byte/FNV/length bounds, recomputes every per-level and aggregate fold-CTA classification and separately counts finite selected payouts. Negative zero and overlapping row categories are preserved. Whole reach category counts include non-fold rows; they are not fold work fractions.

Raw reach and CPU arena payloads are compared natively but not retained. Only compact mapping/row flags permit independent file-level incidence recomputation. This diagnostic establishes no timing, all-iteration share, speedup, fast-path correctness or acceptance. There is no incidence threshold, retry, extension or outcome-selected sample. Any nonzero exit, cleanup error, partial/missing file or exactness failure is retained and fails qualification. Root performs exact temporary-source restoration after custody review, returning to162 accepted entries and preserving both pre-existing PTX files.
