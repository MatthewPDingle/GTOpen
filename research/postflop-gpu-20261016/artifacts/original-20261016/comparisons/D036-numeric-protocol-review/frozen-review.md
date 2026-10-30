# D036 frozen numerical and provenance review

PASS for the prospective source/protocol. This is not a runtime or performance result. The exact accepted full CUDA source is preserved, with only the fold reduction changed. The supplementary raw-total oracle contains mechanically extracted partial/reduction statements and remains distinct from the actual full up_fold comparison.

All observed GPU bits must match, including overflow-derived Inf/NaN outputs. The finite-domain flag adds CPU/finiteness checks without excusing GPU mismatches. Every device input is checked after each variant, all output gaps/guards are checked, active outputs must change from their stale guards, and changed nonzero outputs must exist. Verifier injections intentionally reject fabricated failures before CUDA and are not numerical cases.

Independently verified all sealed artifact/dependency/protected-source hashes, valid card lists in original opponent order, same-hand mappings, output ownership and bounds. Recomputed coverage: 1,120 raw pairs (1,040 also CPU finite-domain), 180 full pairs, 1,771,280 active full-output word pairs, 1,644,760 finite-domain words and 370 launches. There are 1,548 identical-hand matches and 1,615 unmatched own hands. All required lengths, both players, block 128 and fallback blocks 16/32/64/256, zero-count and zero-own cases are present.

The runtime matrix fixes all expected rows. Audit all 1,490 raw-result records, exact outputs/hashes, guards, nonfinite observations and provenance; preserve every failure. No compiler/GPU or solver edit was performed by this reviewer. No NaN-input/payload generalization, speedup or acceptance follows.
