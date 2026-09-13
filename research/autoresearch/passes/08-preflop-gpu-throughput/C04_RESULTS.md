# C04: lossless CDF run compression - rejected

The candidate preserved numerical output, but failed the first large timing
screen. It has been removed from the active solver source. C01 remains retained.
The user's server on port 56708 was not changed.

## Mechanism

Learning-only CDF rows store changed prefix values plus six change-mask words.
Logical reads reconstruct the original prefix with popcounts. Dense accuracy
checks retain the original C01 writer and reader. The scan and terminal arithmetic,
1024 particles, and batch32 are unchanged. Added scratch: 298,046,976 bytes.

## Validation

- The first prefix test build failed on Rust unary-minus/cast precedence. Its
  log remains archived. The corrected v2 test passed.
- Every decoded logical prefix matched original bits for compact and ordinary
  layouts, dense/sparse/zero/one-hot/subnormal/varied inputs, permutations,
  offsets, partial batches, inactive branches and poisoned unused capacity.
  The test confirmed it exercised prefix changes across zero inputs due to
  scan rounding; encoding zero input support alone would be incorrect.
- Three original/C01/C04 adversarial solver tests passed, covering all 2..8
  opponent counts, forced/frozen policies, zero reach, recovery and graph replay.
- Six checkpoints and the final full-arena fingerprint matched on the large pair.

## First large pair

| Measurement | C01 control | C04 candidate | Candidate / control |
|---|---:|---:|---:|
| Complete run | 72.198 s | 141.575 s | 1.9609 |
| Warm iteration median | 3.693 s | 14.841 s | 4.0190 |
| Accuracy check median | 7.346 s | 7.461 s | 1.0156 |

The 96.1% complete-runtime regression fails the predeclared first-pair gate.
No additional timing pairs or full regression suite were justified. The learning
path's extra mask reads and decoding work are an apparent cost, not a measured
hardware-counter diagnosis. No speedup or convergence claim is made.

## Reproducibility

`check_c04.py` independently verifies the frozen source, input and executable
hashes, paired outputs, scratch size and rejection criterion. Prototype files
are under `artifacts/c04-rejected` with explicit original-path mapping in
`artifacts/c04-source-map.json`. The local frozen executable is
`target/c04-benchmark-frozen.exe`:

`ef1cb8ba71208dcdc60f8a65f8cf8fa3e36d261ae7882e69d205f73c9b78dbd0`

## Next investigation

Refresh eager CUDA phase measurements for the retained C01 path before choosing
another kernel change. The existing older profile predates C01; it cannot tell
us the current balance between CDF construction and terminal evaluation. Add
research-only markers, validate that profiling preserves results, and keep these
diagnostic timings separate from the graph's complete-run benchmark results.
