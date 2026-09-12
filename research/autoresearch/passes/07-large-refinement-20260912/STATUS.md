# Qualification status

The first expanded read-only audit covered 27 preregistered branches:

| Snapshot after initial six-path refinement | Passed | Failed | Unreachable |
| --- | ---: | ---: | ---: |
| Full-sample baseline | 12 | 15 | 0 |
| Fast sampled baseline | 10 | 16 | 1 |

Failures include branches not touched by the original six-path refinement.
They must not be presented as covered just because the global gap is small.

Adaptive v1 stopped before modifying anything because a selected subtree
exceeded its 10,000-node admission limit. A subsequent read-only inventory
found sizes up to 24,192 nodes. V2 explicitly raises the research-only bound
to 50,000 nodes; the full game remains 1,567,754 nodes. V2 was then stopped
because the historical audit treated tiny positive joint reach as unreachable.
V3 uses a separately tested conditioned audit; the original audit remains
available. Six research tests passed, including equivalence of action values
on ordinary and tiny positive prefixes and rejection of a true zero prefix.
The registered adaptive procedure is running with a one-hour cap per input.

The target remains large-game conditional accuracy, followed by evaluation
of GPU variance reduction. No deployment is authorized by these partial
results. GPU CV v1 has been tested and rejected on measured speed and storage.
The live application and main checkout remain unchanged.
