# Dedicated specialization coverage

Apply `tests.patch` separately from `implementation.patch`. It minimally expands
the existing `coupled_terminal_matches_cpu_across_particle_batches` test:

- Live seats3 through9 exercise every exact O2 through8 specialization.
- Every fixture uses particle batches32,7,1 (including a partial final batch).
- Every seat's169-class terminal values retain the existing CPU absolute-error
  assertion `< 2e-5`; no assertion is loosened. Model identity is asserted.
- Existing normalization of counterfactual reach masses remains. Configs remain
  tiny: the original three-seat tree, and fold/limp-only equal-stack trees for
  the other sizes, at most the existing766-node nine-seat fixture.

This is21 seat-count/batch cases,126 traverser vectors, and21,294 individual f32
payoffs per control/candidate run. CPU expectations are still computed by the
existing model method. The test does not solve a large tree or touch a session.
This expansion has not been compiled or run; actual runtime is unmeasured.

Optional `PREFLOP_MW_TERMINAL_BITS=1` emits those exact f32 bit patterns as21 JSON
records under `--nocapture`. Run **the same test patch** on the accepted dynamic
opponent-loop kernel first, save that output, then apply only the specialization
implementation and repeat. The companion comparator requires every expected
case and compares every bit, avoiding a tolerance-only or partial-case pass.
Do not compare batch1 to batch32: existing accumulation can differ across batch
boundaries. Compare control/candidate at identical seat count and batch size.

Example parent workflow when the GPU is scheduled:

```powershell
$env:PREFLOP_MW_TERMINAL_BITS='1'
cargo test --release -p solver --features gpu --lib coupled_terminal_matches_cpu_across_particle_batches -- --test-threads=1 --nocapture
# Save control output using the existing guarded logging workflow.
# Apply implementation.patch and repeat with candidate output.
python compare_terminal_bits.py CONTROL.log CANDIDATE.log
Remove-Item Env:PREFLOP_MW_TERMINAL_BITS
```

No embedded old kernel is necessary. This avoids another NVRTC module and lets
the control use the exact accepted production source/compiler options. Keep
the CDF geometry, thread width and all unrelated source settings identical.

These all-opponent tests supplement existing non-unit/stale/zero/tie/compact
coverage, mixed ruled/live parity, and exact full-arena fixture comparisons.
The selected all-live terminal exercises each count directly; other production
tree branches alone are not adequate proof that every new dispatch case ran.
