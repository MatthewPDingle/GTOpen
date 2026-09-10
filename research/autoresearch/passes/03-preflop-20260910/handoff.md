# Current state

Run active; fixed deadline is in run.json. User server 56708 is preserved.
Both sessions saved as `Before preflop autoresearch 20260910 2104`.
Preflop save is iteration 74 (status initially read 73 during stop completion).
Source baseline is 1b8fc3f. New isolated worktree created; cache copies made.
Do not use the old September 7 autoresearch worktree or historical runner.

## Measurements and candidates

Frozen harness commit c4501e3; input SHA256 values in run.json. `measure.py`
runs one already-built benchmark with a ten-minute cap and polls live server
56708 every three seconds; it kills only its own benchmark if user work starts.
`run_guarded.py` provides the same safety guard for built test executables.
`render.py` regenerates results.json and progress.png from events.jsonl.

Baseline eight-seat checkpoint74, six iterations: median9.788s, check11.700s.
192-thread terminal candidate9ea4164: median7.852s then7.829s on repeat,
checks8.935/8.910s. Arena hash1d7a03735896ad92, gaps and EVs identical.
Small3/six/fresh7 candidate controls recorded; baseline controls still needed.
128-thread candidate4b872ce: median8.438s; rejected in favor of192, exact output.
IMPORTANT: original Self::cfg uses64 threads for big grids,256 for tiny ones.
Early description claiming universal256 was corrected in the ledger.

Current worktree commit483c63a restores baseline launch for interleaved controls.
Build session42141 was started at21:21 local; poll to completion before running
the baseline executable. It builds example preflop_research_bench.

Next run baseline-eight-b (same checkpoint,6 iterations), baseline-six-a
(fixtures/six.json,6), baseline-seven-a (fixtures/seven.json,4), baseline-three-a
(fixtures/three.json,30). Use unique run IDs and absolute fixture paths with
measure.py. Each command runs from main T:/Dev/GTOpen and executes in worktree.
Compare matching fixture/iteration arena hashes and timing medians. Then restore
192 if controls support it, compile test executables with cargo --no-run, and
run preflop GPU plus internal coupled tests via run_guarded.py. Do not claim
192 retained until validation passes.

## Next substantive hypothesis

Agent preflop_kernel_review completed a proposal and focused tests in
proposals/active-slots. Read README.md and TESTS.md. Apply active-slots.patch
and tests.patch only to isolated worktree, preserving independently retained
thread launch choice. Proposed gating computes counterfactual probability once
per terminal/traverser, marks only needed CDF slots, skips unused CDF scans.
No sample count/precision changes. Correctness critical: never prune on own
reach; folded opponents still contribute; zero writes and stale masks handled.
Proposal is UNCOMPILED and UNTESTED; apply check only passed. Compare eight
checkpoint and fresh-seven (dense early reach) to catch marking overhead.
Probability-only ablation is useful if atomic marking loses performance.

Other paths: CDF cache memory layout/batching, average-evaluation reuse across
seats (do not reuse across alternating learning sweeps), CPU fallback,
save/load/display overhead. Reserve final window for combined tests and report.
No production implementation has changed and no server restarted.
