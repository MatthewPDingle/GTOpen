# Ancestor-only GPU repair: rejected on both large inputs

V1 failed the retained-arena invariant because the default discount kernel still
discounted frozen regrets. V2 restricted both learning and discounting to the 18
authorized ancestor decisions. The strengthened nonzero-history test passed.

Sampled-input v2 completed in 411.75 seconds. Retained/fixed arenas were unchanged
exactly and native roundtrip was exact. Nevertheless, unrestricted global gap
increased to 0.17479331 bb and only 4/27 conditional paths passed. Preserving
downstream policy bytes does not preserve their quality when upstream play
changes the incoming ranges. This experiment does not qualify for deployment.

Native-input v2 completed in 417.609 seconds. Retained/fixed arenas and native
roundtrip were exact, but unrestricted global gap was 0.04755879 bb and only
7/27 conditional paths passed. Both inputs fail the unchanged 0.005 bb global
gate and the requirement that all 27 conditional paths pass.

Next algorithmic work needs to
account for simultaneous upstream/downstream adaptation rather than treating
one side as fixed and assuming the other will remain valid. Do not suppress
these failures with a constrained best-response check or looser thresholds.

Evidence: `raw/large-eight-sampled-ancestors-v2-{exit,result,broad}.json`;
`raw/large-eight-native-ancestors-v2-{exit,result,broad}.json`;
`raw/large-eight-sampled-ancestors-v1.log`; `raw/ancestor-tests-v3.log`.
