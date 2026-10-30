# E027 revision2: host ownership repair only

Preserve `runs/E027-design` and failed `runs/E027-build` unchanged. The first root build exited101 before producing candidate executables or running native tests/timings. Rust E0382 reported a whole-plan `reach_elements` borrow after the struct literal moved `plan.show_spans` (the same source error appeared for library and library-test compilation). Syntax-only preparation had not checked ownership.

This additive revision makes exactly one host repair: compute `[plan.reach_elements(0), plan.reach_elements(1)]` immediately before `Ok(GpuSolver { ... })`, before any plan field moves; use those two copied lengths in the existing reach allocations. No new allocations, CUDA calls, loops, arithmetic, error handling or tests are introduced. CUDA is byte-identical to R1, as are plan.rs, game.rs and continuation_capacity.rs. The full E020-to-R2 patch and minimal R1-to-R2 repair patch are both preserved.

The five-file eight-float physical reach-pitch hypothesis, unchanged logical layouts/ABI/FP/launches/E015 reuse, original units84/4, fixed primary protocol and all conditional logical-row raw/padding/workspace/budget/swap obligations remain exactly as registered in R1. This is a build repair, not a different performance variant or gate.

Preparation checks confirm exact full reversal to accepted E020, exact repair reversal to R1, all prior source and failed build hashes preserved, changed mod.rs syntax parsing and full-patch applicability. All162 checkout inputs were independently found restored to E020 at sealing; this agent did not alter production. No compiler, native test or GPU execution occurred during this repair. Rust typechecking remains root's next reviewed build step.

`manifest.json` pins the parent source manifest, failed build files, all five base/candidate snapshots, both patches and source checks. Never overwrite prior evidence.
