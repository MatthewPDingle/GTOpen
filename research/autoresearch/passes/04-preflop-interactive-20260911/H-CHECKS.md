# Research build479c065 checks

`preview-build-h.log` compiled server and ten research examples. `build-h-binaries.json` pins their hashes. `solver-tests-build-h.log` compiled all solver test targets with the GPU feature, then server tests; `test-h-binaries.json` pins all37 executables before subsequent source edits.

All37 test executables completed successfully from their Cargo package directories: **272passed,0failed,26ignored**. The ignored tests retain their existing manual/performance status; none were newly skipped to make this run pass. `suite-h-summary.json` records counts, executable hashes and raw log hashes. This includes native128 identity/roundtrip/pot/tie/partial-batch GPU checks, conditional baseline retention, full solver integrations, six postflop GPU and preflop GPU equivalence tests, and server preview checks.

The first direct invocation accidentally used the lab root as its working directory. Two preflop tests failed because their explicit relative fit-table paths require the package directory. Preserve that failure and the corrected full repeat; no test assertion or solver behavior changed to resolve it.

Scope ends at479c065. Detached snapshot locking introduced in8c37f18 is **not** covered by this test record and requires its own compiled focused/integration and API parity checks. Frontend publication checks also passed with `node tools/test_preflop_preview.mjs`; API/UI helper pure tests passed12/12 after the request-log deep-copy fix.
