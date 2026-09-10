# Q5 regression: bounded source review

The reported repeatable eight-opponent terminal slowdown is credible. I have
not compiled, profiled hardware, or inspected generated assembly in this review.
The exact cause remains unproven.

## What the source supports

The clean `423f58a` specialization performs the same 1024 particles, 169 hero
classes, eight opponent CDFs and five quadrature products as `9880326` when
there are eight opponents. The arithmetic still traverses opponents and
quadrature points in the same order. There is no newly introduced inner-loop
algorithmic work that explains a sustained approximately 5% loss.

Dispatch happens once per equity call. A branch or helper call alone is not a
plausible explanation for roughly 0.1 ms added to a roughly 2.5 ms kernel.
It can nevertheless change compilation of the large hot body. Release uses
ThinLTO and one codegen unit; the benchmark has opaque black-box inputs.
Moving a large public body to specialized private functions can change
inlining, bounds-check elimination, vectorization/unrolling, register spills,
stack layout or loop alignment. These are hypotheses, not measured findings.

The attempted constants-local specialization removes runtime-array arguments,
which weakens the theory that passing point/weight arrays is the main cause.
The known-eight product bound did not help. A private `#[inline(never)]`
original-body copy still changes the public call graph and does not recreate
the original caller context or promise identical machine code. Its source
comment promising the original machine-code shape is therefore too strong.

## One remaining minimal experiment

`from-current.patch` replaces the current CPU experiment with clean423 plus
one change: retain the original five-point loop directly in public `equities`.
Lower opponent counts early-return through the clean423 generic helpers.
`from-clean423.patch` isolates only that one experiment if clean423 is restored
first. Use one patch, not both. The full candidate is `multiway.rs`.

This retains the original hot body's owning function and direct constants,
while preserving lower-rule savings. It may still compile differently because
the guard changes optimization context; there is no guaranteed performance
benefit. It is worth at most one bounded trial, not another chain of layout
tweaks. Existing 0..8 dense/sparse/tie reference tests remain included unchanged.

Compare interleaved original, clean423 and this candidate with the frozen CPU
terminal benchmark. Require all eight-opponent equity bits to match the
original and no loss of the smaller-rule gains. Then use a nine-seat CPU
solver fixture with meaningful 9-live terminal exposure at the same gap target.
Nine players is essential: eight opponents means nine live players, so the
user's eight-seat fixture never exercises this branch.

## Retention recommendation

Prefer clean423 over the failed constants/known-bound/private-copy variants.
It is the simplest implementation with measured whole-solver benefits.
The isolated eight-opponent result alone does not establish that a whole
nine-seat solve regresses: most nodes have fewer than nine live players and
benefit from the smaller rules. Measure the fraction of solver runtime affected
through a whole nine-seat same-gap test rather than counting terminal nodes.

If that whole nine-seat control improves (or remains within the accepted
noise threshold), keep clean423 and explicitly record the approximately 5%
worst-case all-nine-live terminal tradeoff. If whole nine-seat solving materially
regresses, do not claim an across-the-board performance win. Either retain the
old rule for that configuration or defer acceptance pending an assembly-guided
fix, weighing the complexity of a configuration-specific dispatch against the
measured user workload.

If the public-body trial fails, stop source-shape guessing. A next investigation
would compare disassembly of the retained original and candidate executables:
hot-loop SIMD width, scalar tail, bounds-check branches, stack spills, function
and loop alignment. Evidence from those differences should choose any further
experiment. Do not introduce unsafe indexing, fast math, reduced samples,
approximate reciprocals or altered f64 accumulation to chase this edge case.
