# R1 holdout source-review limitation and invalidated build identity

The earlier PASS_SOURCE_ONLY review missed a concrete Cargo cache-identity failure. Its runner used the same CARGO_TARGET_DIR for two copied workspaces whose package/test identities and preserved source modification times allowed the E020 build to reuse E015 artifacts. Correct workspace source hashes and a successful Cargo exit did not establish the linked candidate identity. This review error is acknowledged without altering the original judgment or evidence.

Raw E015 JSON reports solver and holdout fresh=false. Raw E020 JSON reports both fresh=true and points to the identical shared rlib and test executable paths under build-holdout-e020. The copied E015 and E020 holdout executables both hash to d9cc5d1168b89c1753690467d94e63997cc40fabc312332e8ae3db9356f0def9. E020 stderr says the release build finished in 0.11s. Root caught the blocker before any native resource/holdout launch.

R1 build/report.json's compilation pass and the premature all-builds-ready.json are insufficient and invalid for native qualification. They remain preserved as originally written. No native timing was measured, excluded, repeated or reclassified. The seven separate broader binaries are unaffected by this wrong-arm holdout cache issue.

The prospective correction is a separately sealed R2 holdout artifact: unused per-arm targets, artifact/source/manifest path validation, non-fresh solver/test compilation, direct embedded expected/opposite CUDA-source checks, and distinct holdout hashes before readiness. It preserves evaluator, fixture, numerical settings/order and gates. A new independent R2 source verdict and terminal build/readiness audit are still required; this record grants no execution or acceptance.
