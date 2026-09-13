# R03 deployed to port 56708

User authorized deployment on 14 September 2026. The qualified normal-feature
R03 version 3 binary now serves http://127.0.0.1:56708 from the existing
`T:\Dev\GTOpen` application data directory, preserving its launch environment.
The C23 compact-table experiment is not included.

- New listening PID at verification: 138828; old PID 99900 stopped.
- Executable: `target/r03-v3-server-frozen.exe` in the research checkout.
- SHA256: `5035a18f206e7364217e86154481faf2c139d6fdce43b936d630bbb64dc88c8e`.
- Preflop restored at iteration 16; postflop restored at iteration 210.
- Preflop configuration, seat profiles, hero/frozen flags, model, tree size and
  root strategy match. Postflop root data, tree/settings and locks match.
- Report and player-profile API inventories match. Report files and cache JSON
  hashes match. UI health and no-cache response were checked.
- Neither session was advanced for a smoke test. Restoring a save resets
  transient engine/progress/publication labels; saved strategy is preserved.

Both original snapshots and both executable copies remain in
`target/deployments/r03-20260914-live` in the research checkout, together with
before/after responses, hashes, launch settings and deployment logs. Those local
session backups are not published to GitHub. The snapshots also remain in the
normal save library under `before-r03-20260914-090756`.

Deployment helper: `deploy_r03.py`. Compact evidence receipt:
`raw/r03-deployment-verified.json`. Earlier release qualification records remain
unchanged as historical evidence. Rollback can restart the preserved old binary
with the captured environment and restore the original two snapshots, after
checking for any newer user work.

Expected benefit remains workload-specific: approximately 20.6% less large
fixed-work preflop runtime relative to the research baseline. This deployment
does not establish 10x acceleration or fewer iterations to convergence.
