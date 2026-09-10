# Actual CUDA minimum-budget parity test proposal

`boundary-tests.patch` is test-only and applies after the optional-normalization fallback implementation. Patch applicability passed against the current isolated source. No compilation or GPU execution was performed.

The test is explicitly ignored in ordinary test runs because one-particle CUDA batches can be relatively slow. Run it deliberately with:

```text
cargo test --release -p solver --features gpu --lib coupled_minimum_budget_direct_and_normalized_paths_match -- --ignored --test-threads=1 --nocapture
```

It searches only CPU-constructed four-, five-, and six-seat bounded fixtures until it finds at least3,000 CDF slots and integer-MB budgets that select direct1 and normalized1 paths. Trees above250,000 nodes are rejected. The search does not allocate CUDA contexts. Budget calculations reproduce the actual planner, and budgets are selected to retain identical HU equity-cache mode so that unrelated cache selection cannot confound the comparison.

Each GPU engine is then constructed normally from a fresh identical solver with its selected budget, sequentially rather than simultaneously. Assertions verify that the actual constructor chose the expected normalization mode and exactly one particle per batch. Three learning iterations, each followed by a gap/EV check, exercise eager execution, learning graph capture/replay, and evaluation graph capture/replay. Complete regret/strategy arenas and gap/EV outputs are compared bit-for-bit between the two paths; large arena mismatches report the first differing index rather than dumping entire buffers.

After recording those results, captured graphs are destroyed before test input arrays are replaced. An isolated three-live-player terminal is tested on both paths with non-unit input masses through positive/gated -> zero-opponent/gated -> restored-positive/ungated states. The last state explicitly checks that the previous gated zero left an empty active mask. CDFs/values are poisoned and normalized storage is poisoned when present. Every hero hand is compared to the CPU terminal evaluator within2e-5, zero results are required exactly, and direct-versus-normalized terminal outputs are compared bit-for-bit.

The source is in `boundary_tests.rs`; `build_boundary_tests.py` regenerates the patch. The test deliberately fails rather than silently skipping if the bounded fixture family no longer exposes both real budget paths. If planner/layout changes such as compact slots are introduced, adjust the fixture's budget calculation to use that new actual layout before treating a failure as a kernel regression.
