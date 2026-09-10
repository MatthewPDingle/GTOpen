# CPU minimum exact quadrature proposal

Proposal only: no production edits, compilation, hardware benchmark, or server interaction.

`combined.patch` includes the implementation and reference tests. Alternatively apply `cpu-quadrature.patch`, then `tests.patch`. Complete proposed source (with tests) is `multiway.rs`. Source SHA256 is recorded in `baseline-sha256.json`; `build_proposal.py` regenerates the files from the main checkout snapshot plus the `tests.rs` insertion. Read-only patch applicability passed using `git apply --check --ignore-space-change`.

## Scope and arithmetic

The public `CoupledDeck::equities` dispatches once per call to a const-generic inner loop, selecting the smallest Gauss-Legendre rule that integrates a polynomial of degree equal to the opponent count:

| Opponents | Points |
|---|---:|
| 0-1 | 1 |
| 2-3 | 2 |
| 4-5 | 3 |
| 6-7 | 4 |
| 8 | 5 |

The tie-share integrand is a product of one linear factor `less + t * equal` per opponent. Q-point Gauss integrates degree <=2Q-1. This is an algebraically equivalent integration rule, retaining all 1,024 deterministic particles, the same generated rank tables, the same CDF construction, and f64 intermediate/accumulator precision. It does not change model version, legal actions, sampling, or the latent game. The two-, three-, and four-point constants match the decimal constants already used by CUDA, represented as f64 on CPU. One point at 0.5 is sufficient for the public zero/one-opponent cases, although production multiway leaves have at least two opponents.

This is NOT bitwise-preserving. Fewer weighted terms and different abscissae change floating-point rounding. The existing five-point rule also uses rounded constants; mathematical exactness of Gauss quadrature does not mean exact real arithmetic on the machine. At eight opponents the five-point constants and operation structure are retained, but do not promise compiler-independent identical bits without measuring them.

Quadrature-product arithmetic falls by 60% for the common two-/three-opponent cases, 40% for four/five opponents, and 20% for six/seven. These are operation-count reductions in that part of the loop, not runtime speedup claims. CDF construction and particle/hand traversal costs remain.

## Proposed tests

The tests retain a test-only copy of the exact old five-point method body rather than using the new generic helper as its own reference. Every opponent count from zero through eight compares all169 hero outputs under:

- Dense asymmetric distributions with exact dyadic normalization.
- Sparse three-hand asymmetric distributions.
- All opponents concentrated on the same hand class, with analytic 1/(n+1) share for that hero class.
- Synthetic all-tied rank tables, checking the analytic tied share for every hero hand.
- Synthetic grouped-rank tables containing both strict wins/losses and tied groups, with mixed sparse/dense opponents.

Tests retain all1,024 particles and use 2e-12 absolute equity tolerance against the original. They have not been executed. The existing pot-conservation/rake and CPU/GPU parity tests remain necessary after integration.

## Acceptance gates

1. Run the added reference tests, existing multiway pot-conservation/rake tests, and GPU equivalence tests. Treat reference mismatch as a correctness failure, not an invitation to silently relax tolerance.
2. Measure CPU terminal evaluation and fixed-iteration throughput separately on frozen 3/6/8/9-seat fixtures. The new helper may help small live pots within a large table even when total table seats are high.
3. Compare time-to-the-same-gap target, total iterations, final gaps/EVs, and representative strategies against the original. Near-zero regrets can turn tiny rounding differences into different branch choices; fixed-iteration runtime alone cannot establish solver performance improvement.
4. Keep the user GPU solve untouched. This proposal modifies only CPU preflop quadrature; it is not expected to materially speed a GPU iteration by itself. It can matter for CPU fallback, audits, and CPU-side work that explicitly calls this evaluator.
