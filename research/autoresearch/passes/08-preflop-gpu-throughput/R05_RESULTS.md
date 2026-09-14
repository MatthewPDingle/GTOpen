# R05: C23 + C24 deployed, research paused

The normal GPU app now selects C23's static boundary tables for the retained
shared path and C24's static tables for compatible ordinary fallback games.
Failed private allocations rebuild the previous safe engine. Native batch size,
1024 samples, solver arithmetic and poker behavior are unchanged.

This is integration of existing results, not another speed experiment. C23
reduced the historical large case by 13.95% relative to R03. C24 reduced the
memory-limited ordinary case by 24.94%; the controls differ and cannot be added.

## Qualification

- Four automatic-selection tests, including actual allocation failures and
  leak-free recovery; four ordinary-path and ten shared-path numerical tests.
- 20 native GPU, 181 default solver and 20 server tests passed.
- Compiled C23/C24 GPU kernels match the retained versions byte-for-byte.
- The 5.7M-node native batch-four game matched all six reference checkpoints
  and all 1,928,235,582 saved regret/strategy entries (fingerprint
  `40005fb7a8048755`). GPU allocations are 18,525,962,768 bytes.
- The normal release server also matched this fingerprint after a save/reload
  continuation. Both smaller shared-path games passed real stop/reload/replay
  checks; all ten solves selected C23. Isolated port 56710 was closed afterward.
- The initial integration compile failed on a missing qualified map type; it
  was fixed and the successful checks were rerun. Failed logs remain preserved.

Release binary: `target/r05-server-frozen.exe`
SHA256: `b0f68de9d162d6dea1a30027075ae41443e34fa74f8ade328ca2cccc58ed8260`
The release and deployment receipts are in `raw/r05-*-verified.json`.

## Live deployment and pause

Port 56708 was updated after backing up both idle sessions and checking the old
process. Preflop iteration 53 and postflop iteration 210 were restored. Root
results, locks, model library and report library matched the pre-deployment
snapshots. Rollback binary and full backups remain under
`target/deployments/r05-20260914-live`.

No further experiments are running. Dashboard 56709 remains available. See
`RESUME.md` for an explicit overnight restart procedure and an untested next idea.
