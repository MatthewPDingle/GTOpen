# A confirmed CPU/GPU update-rule difference

The focused diagnostic passed both registered cases on 20 September 2026. Compilation took 12.203 seconds; the guarded test completed in 2.203 seconds. Source, protocol, executable and log hashes are retained. No solver-core code was changed.

With positive own reach and zero opponent reach, both implementations return exactly zero counterfactual values. The CPU leaves all four strategy/regret arrays unchanged because its traversal returns immediately. The GPU still updates its own average-strategy sums from its current policy and own reach, matching the independently calculated formula within 1.20e-7 raw units. The resulting maximum root probability difference was 0.0585356355—exactly the immediate difference seen in the earlier abrupt rainbow case.

With zero own reach and positive opponent reach, both root average arrays follow the same discount-only formula exactly. Their normalized root strategies match, and returned values differ by at most 0.00000703 bb per opposing mass, below the unchanged 0.002 tolerance.

This explains a specific CPU-replay failure when an entire opponent range vanishes. It does not establish which averaging contract should be chosen for every application. In a changing continuation game, the treatment of unreachable intervals needs to be deliberate and consistent; merely making one test pass is insufficient.

The separate smooth-range compact/full trajectory failures remain unresolved. Those positive-reach cases cannot be explained by this whole-opponent-zero event. The earlier coherent qualification still has five failures out of six and remains failed. The compact bridge is **not cleared for larger training**. The completed board-coverage study used consistent full-arena GPU training; its fixed-policy CPU accounting checks do not rely on matching this CPU training update rule.

Next isolate one GPU update from identical expanded state, comparing the compact bridge with the explicit GPU reference. This removes the CPU pruning mismatch from that comparison and separates an immediate update error from differences that accumulate during independent training. Keep the original failed gates intact.

Evidence: `zero-reach-contract-review.json`, `zero-reach-{build-freeze,build-status,runtime-freeze}.json`, `zero-reach-build.log`; sibling `representative-coverage-20260919/zero-reach-contract-diagnostic-*` and its log. Test: `crates/solver/tests/continuation_zero_reach_contract.rs`.
