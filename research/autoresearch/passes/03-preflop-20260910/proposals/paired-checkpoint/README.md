# Paired CPU preflop checkpoints — proposal only

Status: copied source and patch prepared; `git apply --check --ignore-space-change combined.patch` passes against the source recorded in base.txt. No compilation, GPU jobs, benchmarks, live source changes, or server interaction performed.

## Files and scope

- `combined.patch`: production CPU evaluator plus focused test-only hooks and a new internal test module.
- `mod.rs`: complete proposed `crates/solver/src/preflop/mod.rs`.
- `checkpoint_tests.rs`: complete new internal test module.
- `implementation.rs`: standalone paired evaluator used by generator.
- `generate.py`: rebuilds proposal files from the read-only isolated checkout.

Only preflop CPU accuracy checkpoints change. Learning `traverse(mode=0)`, iteration order, GPU evaluation, postflop, solver controls, samples, precision and payoff identity remain unchanged. No server patch or new public API.

## What is shared, and what stays independent

For a given traverser, both original checkpoint traversals use the same forced-or-average strategy to propagate reaches. Mode 2/3 differs only in which own-node children may be pruned and how their values combine upward. A paired visit therefore evaluates a shared terminal once, then produces separate average and BR outputs.

Each child carries independent `br`/`avg` need bits. In unrestricted mode 2, own zero-average actions remain evaluated for BR (including frozen or point-locked seats), while average can skip them. In mode 3, an own node maximizes only when neither forced nor frozen; otherwise it weights by the same sigma as the original traversal. Other actors' zero-sigma branches may be skipped for both. A child missing one output represents the same positive-zero vector the old pass returned on that skip; reductions still visit every action in the original order.

Floating-point invariants:

- Same f32 reach multiplication, normalization, terminal calculation, and child order.
- Same f32 weighted/summed/max root arrays for each output; cloning terminal values is exact.
- The gap reduction preserves `(br[h] - avg[h]) as f64`, with subtraction in f32. Two independent f64 dot products would not be equivalent.
- Same 1,024 coupled particles, existing f64 quadrature, and terminal input distributions. No cache survives a checkpoint.
- The learning function is retained as the independent mode 1/2/3 reference oracle in tests.

## Cancellation audit

`crates/server/src/main.rs` installs an Arc stop flag for the preflop worker around lines 1199–1210 and clears it only in worker cleanup. After CPU/GPU checkpoint evaluation, the worker checks the flag before publishing gaps/EVs and before the target-gap test (around lines 1379–1404). A canceled checkpoint is already discarded and the previous published checkpoint survives. `/pf/evaluate` rejects a running solver, so normal read-only evaluation has no active worker stop flag.

Accordingly, a public `Option` result and server changes are unnecessary. The private paired evaluator uses `Option` to latch cancellation while unwinding; `gaps_and_evs()` retains its existing signature and pre-set-stop zero result. As before, zeros returned with stop set are not valid convergence evidence. Async partial numbers are deliberately not compatibility guarantees: the worker discards them. A late stop that arrives after the worker's existing publication check is an existing race, not widened by this proposal; this patch does not redesign worker synchronization.

Tests exercise pre-set and deterministically injected mid-traversal stop, private `None`, unchanged arenas, retained stop flag, and successful recovery. The publication-predicate assertion models the already-existing stop guard; it is not an end-to-end server test. Read-only source inspection above is the evidence that the worker uses that guard.

## Memory and performance expectation

The proposal avoids an all-terminal persistent value cache. Such a cache would cost 676 bytes per terminal per traverser, about 544.6 MB per traverser at 805,640 terminals (4.36 GB for eight), before allocation overhead. Instead values live only in the same recursive/Rayon reduction frontier as before.

Two vectors are retained for a shared child rather than one, so peak frontier payload may approach twice the old single-pass payload. Unneeded outputs allocate nothing. A shared terminal now has one exact 676-byte clone instead of a second terminal evaluation. Child need records are two booleans; each requested root/reduction remains a Vec of 169 f32 values. No fixed whole-tree allocation is introduced. Measure peak RSS as well as checkpoint latency: don't claim a memory win merely from avoiding a terminal cache.

The upper bound is near halving duplicated terminal work on dense/no-prune checkpoints, not a promised 2x total speedup. Sparse own-node average paths still require extra BR-only work, and storing/reducing two values increases frontier traffic. `forced_sigma`/average strategy is formed once per paired node. Use terminal call counts and measured timings to quantify the actual saving.

## Acceptance gates to run in the isolated checkout

1. `cargo test -p solver paired_checkpoint --lib` (plus the repository's normal feature selection). Tests compare every root f32 bit in both modes 2 and 3, requested together and individually; final f64 gap/EV bits; pristine, seeded sparse/dense and learned states; pruning on/off; one/four Rayon threads; 2/3/4 seats; legacy and coupled terminals; fixed/adaptive profiles, frozen seats, hero transitions, root/deeper point locks. The deterministic small HU equity table is a test fixture; coupled terminals retain production 1,024 particles.
2. The terminal-count test requires exactly half as many `terminal_value` calls as the old two-pass oracle when both passes visit the same dense tree. This is a semantic work-count assertion, not a timing assertion.
3. Run the full existing CPU preflop suite, especially adaptive_gap_respects_fixed_actions, frozen/profile/hero/point-lock regressions and calibrated/rake cases. No GPU test is needed to time this change, but normal mixed feature build coverage still matters.
4. Interleave frozen-input before/after CPU checkpoints. Compare full root bits, gaps/EVs, arena hashes, live-seat convergence decisions, checkpoint latency and peak RSS. Keep thread count and machine load fixed. Include 3/4/6/9-seat controls and the user's eight-seat tree if practical.
5. Measure complete solve-to-same-accuracy wall time, not only standalone checkpoint timing. Learning iterations must stay byte-identical; checkpoints must not change arenas. Reject if checkpoint frontier memory causes unacceptable RSS growth or full-solve regression.

No performance outcome is claimed until those gates run.
