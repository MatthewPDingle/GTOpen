# Wider root evaluation execution control

23 September 2026. The active 78-update candidate was not accessed. This used
the already completed four-update visible-feature control bank with generation
weights 1, 2, 3, 4, on CPU only. It is an execution check, not strategic evidence.

The complete path performed:

1. Two correctly conditioned training deals for each of all 169 BB classes:
   338 physical deals, in 22 batches including the final two-deal batch.
2. Conditional preflop all-in evaluation using the complete exact private-pair
   cache, with unlabelled visible inputs supplied to policy inference.
3. Exact-aware class response fitting, original-baseline preservation for sparse
   classes, and training-only split diagnostics. The minimum support of one is
   deliberately a fixture setting; it is not the proposed full evaluation's
   training requirement.
4. Publication and hashing of the frozen responder and physical residual bounds
   before construction of the test sampler.
5. A separate IID population test stream: 128 deals in eight batches. None of
   the class-balanced training observations enter its confidence calculation.
6. Exact fold/shove offsets plus sampled call/raise residuals for the fitted
   response and all four fixed-action alternatives. One final look and a .025
   family error allocation cover all five comparisons.

The control passed in 84.11 seconds, including 61.08 seconds evaluating its
training sample and 20.66 seconds evaluating its test sample. A separate readback
replayed both chance streams, verified all native artifact hashes, reconstructed
169 response choices with scalar sums, and rebuilt all residuals and five
intervals without using the fitter or interval implementation. Maximum scalar
discrepancy was 2.27e-13 bb; readback took 0.36 seconds.

The readback checked file publication ordering and initial test RNG state in
addition to distinct sample identities. It did not independently rerun native
payoffs or model inference; those remain covered by earlier component controls
and require candidate-specific CPU/CUDA comparisons before a full GPU run.

Every downstream policy remained frozen. The result is only about the initial
BB deviation, with the existing physical game and restricted menu. Its small
test intervals are intentionally not interpreted as evidence of range quality.
The fixture does not certify the planned larger resource budget or the complete
78-generation GPU path. Production and the running training study are unchanged.

Implementation: `wider_root_evaluation_v1.py`. Evidence:
`wider-root-evaluation-control-v1-{registration,result,independent-review}.json`,
with complete control artifacts under `S:/GTOpen-research/wider-root-evaluation-control-v1`.
