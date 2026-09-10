# Focused active-slot regression test proposal

Apply `tests.patch` after `active-slots.patch`. The tests patch only adds a test inside the existing `gpu.rs` internal `#[cfg(test)] mod tests`. `tests.rs` is the insertion source; `build_tests_patch.py` regenerates the patch. Both patches passed a combined read-only `git apply --check --ignore-space-change` against the original checkout.

The single parameterized test, `coupled_active_slots_preserve_counterfactual_zero_reach_and_reset_masks`, runs eight sequential cases at each of three particle batch sizes (32, 7 and 1). It uses a tiny four-seat no-raise tree and chooses a three-live-player terminal, giving both live and folded opponents. It keeps only that terminal in the GPU's multiway term list while retaining the production slot/source mapping, so the complete expected active mask is deterministic and can be asserted directly.

Coverage:

- Zero own reach: counterfactual values stay nontrivial and match CPU for every hand.
- Zero live opponent reach: every target value is exactly zero.
- Zero folded opponent reach: every target value is exactly zero even though that seat is not eligible to win the pot.
- Positive -> zero -> positive transitions with traverser changes: no stale active flags or prepared probabilities may survive.
- Values prefilled with a nonzero sentinel: catches missing first-batch zero writes.
- CDF scratch prefilled with NaN: catches consumption of a CDF slot that was not produced.
- Exact whole active-mask and prepared-probability assertions: catches unnecessary retained marks even if they happen to give correct output.

Synthetic reach vectors are asymmetric, sparse, and use dyadic weights summing to exactly one. This avoids different reduction summation rounding obscuring the tested counterfactual logic. Nonzero outputs use the existing CPU terminal comparison tolerance of 2e-5; zero outputs and prepared probabilities are checked exactly.

The test uses actual existing internal helpers: `PreflopGpu::new`, `f_reach_mass`, `terminals`, `PreflopSolver::terminal_value`, and device upload/download methods already used by `coupled_terminal_matches_cpu_across_particle_batches`. Private fields are accessible from this child test module. The added proposal fields `d_mw_active` and `d_mw_prob` are used only after applying the implementation proposal.

No compilation or GPU execution was performed. This is eager-kernel coverage; do not claim it validates graph replay by itself. Existing iterative GPU equivalence checks should still exercise the capture/replay path after integration.
