# Fresh global GPU restart v1: interim result

Sampled input finished 500 iterations in 318.891 process seconds. Its final
canonical global gap was 0.01135552 bb, above 0.005. Only 7 of 27 final conditional
path gates passed (compact refinement had passed 26). Thus this restart is
rejected as a consistency repair at the registered budget. A reduced global
gap is not success when conditional accuracy regresses this far.

The first 50-iteration global check was 1.550414 bb. Resetting all learning
histories with scale-one policy seeding disturbed a substantially better input
strategy; later iterations recovered only part of it. This is evidence against
this particular restart, not proof that all warm starts fail. The native-input
counterpart completed in 319.891 seconds with gap 0.00905214 bb and only 6/27
conditional paths passing. Both runs are rejected. Do not deploy or substitute
these outputs for the original solve.

Next investigation should preserve converged local policies while adapting
upstream decisions, followed by unrestricted full-game and conditional checks.
Freezing policies must never be used to hide their deviations from those checks.

Evidence: `raw/large-eight-sampled-reconcile-v1-{exit,result,broad}.json` and log.
