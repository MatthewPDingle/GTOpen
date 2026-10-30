# Repeated host parking with one shared GPU workspace

Registered after all small and larger exact-restoration fixtures passed. This is test-only end-to-end parking, not a production API or full 164-board integration.

Six small explicit symmetry-tied games: KsQs2d, KsQs2s, KsQh2d at pot/stack 39.5/80 and 93.5/155, using the same supported hands and no-raise 50% menus as the small storage tests. Retain one resident reference GPU per game. Candidate games retain their static GPU metadata, but share seven large mutable device buffers (both regrets, both averages, both reaches, CFVs). Candidate host strategy storage retains only canonical blocks, with the established raw fallback when no isomorphism is active. Restore one full candidate host state at a time; do not keep a full parked host copy per candidate board.

Run 60 iterations, both players, all six games: 720 passes. Alternate/reverse/rotate board visitation deterministically. Use the abrupt coherent reach schedule with entire zero reaches at 17, 34 and 51. Every pass must return bitwise-identical values to that game's resident reference, preserve all four resulting arrays bitwise, and survive another exact host park/restore. Synchronize before handing shared device buffers to another stream. Compare the full resulting arrays, not only traverser arrays, to catch cross-board contamination. Print every pass and a final summary; no tolerance or sampling substitutes for equality.

This test intentionally uploads/downloads all four arrays for maximal state verification; it does not combine the separate own-average upload optimization. No throughput claim. Recorded array/workspace sizes exclude static metadata and temporary full states. A pass advances the storage integration evidence only; bigger trees, full forest capacity, failures/cleanup and a connected-game comparison remain separate gates.

Source: `crates/solver/src/gpu/continuation_host_paging_tests.rs`, included only under `cfg(test)`. No production solver behavior changes. Compile with two workers, freeze input/executable hashes, production-idle and memory guards, ten-minute execution maximum capped at 09:00 Adelaide.
