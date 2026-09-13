# C03: no-tie product reuse rejected

Across three alternating pairs, complete large-game runtime improved **1.87%**,
below the predeclared 3% retention threshold. Warm iterations improved 3.80%
and checks 1.13%. Small complete runtime regressed 2.38%; its checks regressed
5.79%. The candidate was removed rather than kept for a small diagnostic gain.

| Large pair | Control | Candidate | Candidate/control |
| --- | ---: | ---: | ---: |
| 1 | 67.544 s | 66.283 s | 0.98133 |
| 2 | 66.413 s | 65.337 s | 0.98379 |
| 3 | 66.519 s | 65.160 s | 0.97956 |

All paired checkpoints and final arena fingerprints match across twelve runs.
Three adversarial GPU tests passed (all native/C01/C03 comparisons). Full
regression suites were not repeated because the timing gate failed and the
solver files were restored to retained C01.

`check_c03.py` independently verifies the numerical records, all input/source
hashes and the rejection rule using the explicitly archived prototype sources
and local executable. Artifacts: `artifacts/c03-rejected/`; source map:
`artifacts/c03-source-map.json`; output: `raw/c03-verified.json`.

This experiment preserved sample and weighted-addition order. It only computed
an identical opponent product once when all lanes in a warp had zero tie mass.
It does not justify dropping quadrature terms or changing floating-point order.
No deployment occurred. The live graph records C03 as rejected, even though it
was slightly faster on the large fixture.
