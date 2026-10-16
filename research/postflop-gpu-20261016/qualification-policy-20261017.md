# Current qualification policy: 1% with no tradeoffs

The user changed the minimum observed aggregate gain to **1%** on 17 October 2026 (Adelaide time). This supersedes the original 2% rule for prospective qualification. Historical outcomes and their original rules remain recorded unchanged.

- Measure the same complete-solve workloads at the same accuracy, stopping rules and storage settings. The aggregate remains the sum of per-fixture median wall times; compare unrounded values.
- Require exact full states, exploitability/EV bits, stopping iterations and convergence checkpoints. Complete the applicable broader correctness checks before adoption.
- Reject a fixture slowdown when its median is positive and a strict majority of paired runs are slower (minimum two). The old 3% allowance no longer applies.
- Establish that there is no material memory, capacity, behavior or compatibility cost. Source inspection alone cannot establish compiled-resource or captured-graph costs.
- An initial three-pair screen is preliminary. A candidate that advances must pass a separately frozen fresh 16-pair confirmation: aggregate gain at least 1%, at least 13 improving pairs, and positive paired, block and run-order medians. Retain all observations; do not add samples to rescue a result or pool historical measurements.
- Keep holdout and fresh-original cumulative qualification separate from the primary score. Do not add percentages from different candidates or claim universal speed/no-tradeoff guarantees from the registered workloads.

E037 adopted this policy before any native run. Its measured 0.9906835482% gain missed the cutoff; exactness passed and no fixture slowdown guard failed. Its implementation was restored to accepted E020. The earlier E007, E008, E032 and E036 hypotheses are being prepared for independent fresh confirmation on E020.

The original `program.md` and sealed build manifests remain historical provenance. The root decision, effective E037 policy, policy review, preserved timestamp-check failure and assessment-only repair are linked on the [live status page](http://127.0.0.1:43735/research/postflop-gpu-20261016/). No live executable deployment is included in qualification.
