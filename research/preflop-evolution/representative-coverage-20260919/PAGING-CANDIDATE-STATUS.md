# Isolated own-average upload candidate

Research branch: `codex/paging-own-average-research`, based on
`04c36d327a0f5818c182126274f80468ecb79d98`.
Checkout: `T:/Dev/GTOpen-paging-research`.

The deferred patch is applied **only in this checkout**. The primary
research checkout, active 47-board reference executable, frozen queue and
production app on 56708 remain unchanged.

The switching test retains its original bitwise resident-versus-paged
checks across 160 board/player sweeps. It additionally asserts unchanged
opponent host arrays after every sweep and the exact predicted byte count,
40 times 2.5 times the total F32 arena size. These are qualification tests,
not evidence of a pass until they actually execute.

Compile-only preflights passed with two build jobs in the separate
`T:/Dev/GTOpen/target/paging-own-average-build` target directory. No GPU test
has run. The test executable compiled in 2m58s, followed by the connected
example in22.70s. Build output is retained in `paging-candidate-build.log`
and `paging-candidate-example-build.log`. Source and executable hashes are
in `paging-candidate-build-status.json`, explicitly compiled-not-executed.

Follow all gates in PAGING-TRANSFER-AUDIT.md before use: fresh idle/resource
and source-hash checks, switching parity, complete two-board 2,000-iteration
checkpoint parity and accounting, then uncontended timing. Do not merge or
deploy this candidate based on compilation or the static byte prediction.
Do not interrupt or extend the current overnight accuracy queue to test it.
