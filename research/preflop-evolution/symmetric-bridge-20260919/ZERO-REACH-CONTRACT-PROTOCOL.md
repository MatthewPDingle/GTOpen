# Focused zero-reach update diagnostic

Registered 20 September 2026 after the coherent-range qualification failed. Preserve its five failed cases and all original thresholds. This diagnostic tests the inspected difference between CPU pruning and unpruned GPU average updates; it does not replace a failed gate or qualify suit compression.

Use the coherent test's rainbow board KsQh2d, identical supported hands, pot, stack, rake and no-raise 50% postflop menu. Both implementations use full F32 arrays without suit isomorphism. Warm the GPU reference for sixteen iterations with the same deterministic positive class-based reaches. Start both diagnostic cases from that identical saved state.

At player zero's iteration-17 sweep:

1. Zero opponent, positive own reach: require both returned value vectors to be exactly zero. Confirm the CPU's whole-state early return leaves all four arrays bitwise unchanged. Independently calculate the root average-sum update from the existing regrets, quadratic discount and own reach; require the GPU to follow it within 0.000002 raw-sum units and to change its root sums. Record the resulting normalized strategy difference without setting a required minimum.
2. Zero own reach, positive opponent: require both root average arrays to follow the same independently calculated discount-only rule within 0.000002 raw-sum units. Require CPU/GPU counterfactual values to agree within the original 0.002 bb per opposing-mass tolerance. Internal pruned nodes are not asserted identical in this focused control.

Print both cases before final assertion. A pass establishes the expected existing semantic difference; it is not evidence that one implementation is the desired final contract or that the smooth suit-compressed trajectory failures are resolved. Do not modify solver code in this experiment.

Test: `crates/solver/tests/continuation_zero_reach_contract.rs`. Compile and execute only after the current sequential transfer timing pair releases resources, to avoid adding compilation interference to that measurement. Use the existing research guard, check production idle, retain input/executable hashes and cap GPU execution at five minutes and the existing 09:00 Adelaide deadline. If the deadline leaves insufficient time, preserve the source and defer execution rather than extend the run.
