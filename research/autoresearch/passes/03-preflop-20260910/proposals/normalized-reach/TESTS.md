# Normalized-reach refresh test proposal

`tests.patch` is test-only, generated against the isolated source after normalized-reach integration (`8ac30e8`). It adds one internal GPU test, `coupled_normalized_reach_refreshes_nonunit_inputs_and_ungated_evaluation`. Read-only patch applicability passed. No compilation or GPU execution was performed.

The test retains the existing tiny-tree/private-helper style. It isolates one three-live-player terminal and runs seven ordered states at each particle batch size32/7/1:

1. Gated positive inputs with poisoned normalized storage.
2. Gated zero-opponent inputs, leaving an empty active mask.
3. Ungated positive inputs with poisoned normalized storage and the explicitly verified empty stale mask.
4. Ungated changed inputs without poisoning, so old finite normalized values must be refreshed.
5. Gated changed positive inputs with poisoning.
6. Ungated zero-opponent inputs.
7. Ungated restored positive inputs with poisoning.

Every state changes both hand support and total reach mass. Sparse raw weights are scaled[1,2,4], yielding non-unit exact dyadic masses and nontrivial division-by-seven results. Merely rescaling an unchanged hand distribution could conceal a stale normalized cache, so the support changes too.

For every currently needed positive-mass slot, every one of its169 normalized values is compared bit-for-bit against direct host f32 division using the actual GPU reach mass. This is a strong test of the proposal's unchanged division claim; investigate a failure rather than automatically weakening it. All169 terminal outputs also compare to the existing CPU terminal evaluator within2e-5, and zero-opponent outputs must be exactly zero. CDFs are poisoned with NaN and terminal values with a nonzero sentinel on every state.

The test is eager-kernel coverage. Existing iteration/graph replay suites remain necessary, because this fixture replaces device allocations between calls and does not capture a graph itself.
