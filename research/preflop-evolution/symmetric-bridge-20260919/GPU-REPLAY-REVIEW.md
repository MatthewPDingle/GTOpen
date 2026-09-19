# Identical-state GPU replay: 72 local samples passed

All registered sampled passes completed across three flop textures and both abrupt and smooth range sequences. Each explicit replay started with all four arrays bitwise identical to the materialized compact state. The largest returned-value difference was 0.000004164 bb per opposing mass, below the unchanged 0.002 tolerance. Post-update root probabilities and average/best-response evaluations through the common full CPU evaluator matched exactly in these samples. Zero-opponent returned values were exactly zero.

This removes the CPU training/pruning contract from the local comparison. It supports looking at accumulation across independently evolving GPU regret states rather than a large local value error in these sampled passes. It does **not** prove all updated regret arrays are identical: the average sums use the pre-update policy, so their agreement after a single pass does not guarantee the same future policy after slightly different regret updates.

The earlier five coherent-range failures and their thresholds remain unchanged. Neither local agreement nor successful small connected experiments clear the compact bridge for broader training. The next diagnostic will ask whether the independent trajectories converge toward similar outcomes after the supplied ranges stop changing, measuring each strategy's own deviation as well as their difference. This distinguishes persistent solution disagreement from transient sensitivity without replacing the old acceptance gates.

Evidence: `gpu-replay-review.json`, registered protocol, source/build/runtime hashes and build log; sibling `representative-coverage-20260919/gpu-replay-diagnostic*`. The test-module inclusion is under `cfg(test)`; no production behavior changed.
