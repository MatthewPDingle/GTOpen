# Accumulated-opponent learning: rejected

Both candidates finished at the registered 3,000-iteration limit and failed
global and conditional quality. No large trial is admitted. This conclusion
uses fixed iteration counts and accuracy, independently of any interruption
in the agent's connection. Timings below are the executable's recorded complete
wall time, not conversation/connection duration; no candidate speedup is claimed.

| Seed | Mode | Iterations | Seconds | Final global gap bb | Conditional passes |
| --- | --- | ---: | ---: | ---: | ---: |
| 42 | Control | 1,300 | 17.966 | 0.003364 | 6 / 6 |
| 42 | Accumulated opponents | 3,000 | 55.395 | 1.778135 | 0 / 6 |
| 314159 | Accumulated opponents | 3,000 | 54.697 | 1.404599 | 0 / 6 |
| 314159 | Control | 825 | 11.839 | 0.003672 | 6 / 6 |

Every control checkpoint, per-hand audit, final age and saved-file hash exactly
reproduces its earlier normalized-pair-tail run. All four cases round-trip their
saved histories exactly, and separate saved-game audits reproduce every final
per-hand record. The independent checker recomputes all accuracy and stopping
gates from raw records. The new target is worse on this fixture; do not retune
its cap or move it to a large game on the basis of the numerical tests.

Two new numerical tests passed: raw/calibrated reach and one-sweep updates
against separate frozen-opponent reference engines, and eager/captured identity
with native final CPU/GPU evaluation and fixed-policy handling. Existing
normalized-regret, exploration and pair-control tests passed. The native GPU
integration suites passed (six postflop and thirteen preflop tests), as did
the default release solver suite. The option is explicit and research-only;
port 56708 and production behavior remain unchanged.

Evidence: `raw/average-opponents-screen-verified.json`, four result archives and
SHA envelopes, separate audits, and the `average-opponents-*-compat-v1`,
`average-opponents-numerical-v1`, and `average-opponents-default-suite-v1`
process logs and source/input hashes.
