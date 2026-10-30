# D067 planned-showdown incidence

This package minimally reuses D066's fresh build, serialized single ignored test and file assessment. The selected test executes accepted `Spot` and `GpuPlan` construction on the CPU only. It creates no Solver, learning arenas, CUDA context, kernel, iteration or exploitability check. The binary is built with the GPU feature solely to place the ignored test beside the private accepted planner; unchanged existing GPU tests are filtered out.

Root alone may activate the append-only `mod.rs` declaration and new `planned_show_incidence.rs` after independent source/script review, then write `authorization.json`. Required fields: `candidate: D067`; booleans `E020_accepted`, `E020_server_qualification_pass`, `independent_source_review_pass`, `independent_script_review_pass`; `candidate_sources` maps the two owned repo-relative paths to frozen `{path, sha256}`. `prerequisites` contains `{path, sha256}` for `E020_acceptance`, `E020_server_qualification`, `D067_feasibility_review`, `D066_terminal_review`, `D067_source_review`, and `D067_script_review`. `evidence_sha256` includes those reports and this scripts-manifest. The authorization is outside the seal and requires a separate root runtime decision.

Root commands, each only after observing the preceding terminal success:

```powershell
& 'C:\Program Files\Python312\python.exe' -I -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D067-planned-show-incidence\build.py' <authorization-sha256>
& 'C:\Program Files\Python312\python.exe' -I -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D067-planned-show-incidence\run.py' <authorization-sha256>
& 'C:\Program Files\Python312\python.exe' -I -B 'S:\GTOpen-research\postflop-gpu-20261016\runs\D067-planned-show-incidence\assess.py' <authorization-sha256>
```

One invocation, `D067R1`, runs `gpu::planned_show_incidence::planned_show_incidence_mapping`: expected 1 passed, 88 filtered. It constructs the three original configurations sequentially, requiring 16 GiB available host RAM before each Spot. Each full retained fold map must match byte-for-byte, with EOF and exact historical dimensions/spans, before that fixture's new planned-show file is emitted. The assessor requires all three checks and the final complete marker before any flag join. Partial outputs are retained and cannot qualify.

`D067_CENSUS_DIR` points to the immutable D066 census; `D067_MAPPING_DIR` points to fresh `runs/D067-execution/mapping`. All 15 historical file hashes are pinned and checked before/after the one process. The three new files have 36-byte records: node, slot0, slot1, river slot, win/lose/tie f32 bits, and both sorted-hand counts. The assessor validates bounds, spans and codec, then joins each planned CTA once per traverser using opponent `1-p`. It reports whole-row exact-positive-zero incidence, independent overlapping flag categories, finite-three-payout eligibility and empty sorted-list categories separately.

The source/schema and historical configs are immutable. `num_slots` and show/tie metadata are newly reconstructed host-planned fields, not historical device readbacks. D066's six snapshots, 23 checkpoints and three final full-state checks are historical inputs, not tests rerun here. Incidence does not prove shortcut correctness, all-iteration frequency, latency or savings. No performance cohort, incidence threshold, retry, extension or acceptance is allowed. Existing runner process times serve custody only.

The inherited live-idle check, lock, disk reserve, timeout and owned-child cleanup remain. Exactly two pre-existing PTX fixture files are permitted only with their frozen hashes and sizes; no directory exemption or deletion. Root restores the temporary two-file test wiring after custody, returning to 162 accepted sources. Draft preparation is preserved in `draft-r1/`; no draft was executed.
