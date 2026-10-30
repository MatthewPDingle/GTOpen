# E016: carry valid player0 reaches between ordinary iterations

Source frozen for root's compilation and qualification. No compilation, GPU execution, timing, commit, server/API write or deployment was performed by the builder. No runtime correctness or speed claim is established by this artifact.

The sole checkout edit is `crates/solver/src/gpu/mod.rs`, based on accepted E015 (`e868cfbb125002216f25046af2d88b22a697b2fd`). The design and independent proof critique are sealed in `../D025-next-hypothesis/`. Before/after source, patch, exact hashes and 18 mechanical checks are preserved here. Candidate SHA256: `0ca68663e9eeaf168b6769b36bd266d59ddc0c0d4838641ce0dd350c40d2abed`.

Production behavior follows D025: an explicit `DownReachReuse` enum and host validity flag select full p0 or reused-player0 p0, followed by E015's reused-player1 p1. The three captured graph variants retain two graph launches per iteration. The flag is consumed before fallible iteration work and enabled only after a complete ordered pair queues successfully. Construction, evaluation entry/replay, direct evaluation-down, generic standalone sweeps, continuation entry before validation/uploads, and lock updates disable reuse. It does not provide recovery from partially applied CUDA learning updates. Successful readback still leaves device state and validity unchanged.

There are no kernel, plan, Store, evaluator, workload, device buffer, precision, stop rule or graph math changes. The original test-only full-down oracle is byte unchanged. All upward dispatch, evaluation-up and readback code are byte unchanged; constructor changes only initialize the new bool. Ten protected source/config files were checked against HEAD.

Run `LIB.exe gpu::tests::paired_reach_reuse_ --nocapture --test-threads=1` serially. With `gpu`, two nonignored tests cover:

- Eight DCFR/CFR+ × F32/compressed × full/compact cases against full-sweep reference iterations, comparing all device regret, strategy, reach and root-weight bits. Eager, captured and replayed training, eager/captured/replayed evaluation invalidation, mixed profiled/ordinary dispatch, direct evaluation-down, standalone p0/p1 followed by training, both-actor lock updates/recapture, and warm CPU reconstruction are exercised.
- Independent before/after raw player1 and player0 reach invariants, using the preserved original full-down dispatch. Changed root weights and poisoned reach storage check isolated generic p1 full refresh. Uninitialized CFV scratch is excluded.

With `gpu,preflop-research`, a third nonignored test verifies invalid player/iteration/length requests disable validity without modifying device state, then compares valid changed-root p0/p1 bridge calls and their following paired iteration to full-sweep reference state. It also compares the valid returned root CFVs. No CUDA fault injection is used.

Limits: syntax-only rustfmt parsing and whitespace/source checks passed; tests are not executed by this builder. Warm reconstruction is not a disk save/load test. Actual paging/storage wrappers, larger menus and frozen F32/state/menu/resume controls remain root's qualification work. All timing must include additional graph setup cost and use E015 as the incremental baseline. The preserved profile/work-count reasoning does not predict an accepted gain.
