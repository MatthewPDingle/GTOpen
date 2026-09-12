# Large adaptive refinement: interim results

The sampled adaptive-v3 run finished successfully in 3165.984 seconds (52.8 minutes). This is a completed experiment, not an accepted optimization.

- The independent conditioned audit passed 26 of the registered 27 paths. Path `[3,0,0,0,0]` failed after downstream refinements despite passing earlier in the sequence.
- The full canonical 1024-particle global gap sums to 0.0295076524 bb, exceeding the registered 0.005 bb target. Seat 0 accounts for 0.0259157277 bb.
- All unrelated/fixed arenas were preserved exactly; native save/load roundtrip was exact. The parent has 1,567,754 nodes.
- Local iteration ages still do not support ordinary global resume.

These findings show why passing each branch immediately after editing it is insufficient. Later edits can invalidate an earlier branch check, and replacing downstream strategies can worsen incentives outside the edited subtrees. The global-gap increase is measured; attributing it to changed upstream incentives is a hypothesis requiring further investigation.

The native-baseline adaptive run was stopped after 1080.438 seconds following the user's instruction to stop focusing on CPU preflop performance. PID 111136 was verified as the owned research executable before termination. Its nonzero exit is an intentional cancellation, not a numerical failure or a timeout. No final native result exists, and it will not be restarted as a performance prerequisite. Compact GPU refinement is an unvalidated prototype. Faster execution of the same edits would not by itself solve the consistency problem. Keep both the final independent branch audit and the global acceptance gate; do not relax either to qualify this result. No production deployment is authorized by this experiment.

Evidence: `raw/large-eight-sampled-adaptive-v3-{exit,result,broad}.json` and corresponding logs.

## Follow-up design constraints

[Brown and Sandholm, Safe and Nested Subgame Solving (2017)](https://papers.nips.cc/paper_files/paper/2017/file/7fe1f8abaad094e0b5cb1b01d712f708-Paper.pdf) explains that an imperfect-information subgame's strategy can depend on alternatives outside that subgame. Its formal setup is two-player zero-sum. Do not transfer its safety guarantee directly to this eight-player, raked, approximate-payoff model.

For this implementation, investigate upstream incentives explicitly: compare per-seat full-game gaps before and after the same refinement, and inspect the affected ancestors under the updated continuation. Repeating independent local solves is not enough to assert consistency. A future reconciliation experiment must define valid regret/averaging ages, revisit changed incoming ranges, and pass both the unchanged global target and final conditional tests. Preserve the current local-only outputs as offline research artifacts. Compact GPU tests can establish execution equivalence and cost even if this strategy-replacement design remains rejected.
