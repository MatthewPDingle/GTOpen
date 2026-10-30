# Complete context-policy routing: implementation control passed

The full context-aware policy now passes the bounded CPU/CUDA integration
control. The original run is terminal and must not be repeated. This is a
software-integration result, not evidence that a newly trained strategy is
better at poker.

The run checked 16 retained-policy CPU/CUDA comparisons across two earlier
training seeds, generations 0, 1 and 77, both input representations, and the
first two played-model averages. It also checked 14 combinations of seven
stack depths and the two input representations. Those multi-context fixtures
use native observations but synthetic network and local correction states.

The 20/40/100/200/400bb fitting contexts retain their own weighted preflop
tables, exact BTN responses and BB root corrections. The 60/150bb held-out
contexts receive shared-network predictions without learned local state.
Changing one local root affected only that context. Twelve rejection controls
covered swapped/missing state and forbidden held-out fitting/local state.
The model objects also round-tripped through content-addressed storage.

The run completed in 58.297 seconds. Peak reserved CUDA memory was 58,720,256
bytes. Its retained store is about 7.96 MB logical and 4.89 MB allocated.
The largest recorded retained-policy probability difference was about
9.1e-14, below the fixed 1e-10 tolerance.

The separate reporting-only readback rehashed all registered inputs and saved
artifacts and recomputed differences from all 14 saved multi-context array
sets. It also checked normalization, legal-action padding, finite/nonnegative
probabilities and own-reach values, fitting/held-out state ownership, and
the recorded control counts. It passed without another inference or fit.

Limits of that audit are explicit: raw single-context retained-policy arrays
were not saved, so their recorded scalar errors were checked rather than
independently replayed. Context-isolation and rejection executions were not
rerun. No training checkpoint, complete training cycle, learned multi-context
accuracy, preflop improvement, or production deployment is qualified here.

Evidence: `stack-context-full-control-v1-registration.json`, `-attempt.json`,
`-result.json`, `-readback-attempt.json`, and `-readback.json`. Array artifacts
remain in `S:\GTOpen-research\stack-context-full-control-v1`.
