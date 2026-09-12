# Large adaptive refinement: interim results

The sampled adaptive-v3 run finished successfully in 3165.984 seconds (52.8 minutes). This is a completed experiment, not an accepted optimization.

- The independent conditioned audit passed 26 of the registered 27 paths. Path `[3,0,0,0,0]` failed after downstream refinements despite passing earlier in the sequence.
- The full canonical 1024-particle global gap sums to 0.0295076524 bb, exceeding the registered 0.005 bb target. Seat 0 accounts for 0.0259157277 bb.
- All unrelated/fixed arenas were preserved exactly; native save/load roundtrip was exact. The parent has 1,567,754 nodes.
- Local iteration ages still do not support ordinary global resume.

These findings show why passing each branch immediately after editing it is insufficient. Later edits can invalidate an earlier branch check, and replacing downstream strategies can worsen incentives outside the edited subtrees. The global-gap increase is measured; attributing it to changed upstream incentives is a hypothesis requiring further investigation.

The native-baseline adaptive run is still pending. Compact GPU refinement is an unvalidated prototype. Faster execution of the same edits would not by itself solve the consistency problem. Keep both the final independent branch audit and the global acceptance gate; do not relax either to qualify this result. No production deployment is authorized by this experiment.

Evidence: `raw/large-eight-sampled-adaptive-v3-{exit,result,broad}.json` and corresponding logs.
