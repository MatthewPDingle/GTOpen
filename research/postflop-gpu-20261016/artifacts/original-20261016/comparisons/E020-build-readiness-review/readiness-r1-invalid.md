# E020 holdout build readiness R1: blocked

The all-builds-ready record 122ce989d6ffcc6fa83a99b15943e4e89aeac3d04e7dde654f7a970e82894982 is preserved but cannot authorize native work. All listed file hashes match, yet both holdout arms have the same linked executable hash d9cc5d1168b89c1753690467d94e63997cc40fabc312332e8ae3db9356f0def9. Both binaries contain the complete E015 CUDA source and lack the intended E020 source. The workspace kernel and host-module bytes are correctly distinct.

Raw E020 Cargo output marks solver and postflop_wide_turn_holdout fresh=true, reusing the same shared-target rlib/test paths as E015. E015 compilation took59.813s; the candidate-labelled command took250ms. This establishes wrong-arm artifact reuse; the exact internal Cargo freshness mechanism was not instrumented. Build-time dependency hashes/source maps and successful exit do not override the immutable linked-executable evidence.

No holdout or resource native process ran; no timing sample was excluded or replaced. The primary E020 verdict is unaffected. Keep every R1 build/readiness artifact. A separately reviewed build-only repair must use distinct new per-arm target directories and verify expected embedded CUDA/opposite absence and distinct executable hashes before resealing readiness. Resource executable legitimately contains both variants. No evaluator, fixture, mathematical setting, sample count or score change is justified.

The seven broader-control binaries remain separately verified. Overall readiness is blocked pending corrected holdout binaries. This audit only read and hashed evidence and wrote additive review files; no compiler/GPU/test/source/status action.
