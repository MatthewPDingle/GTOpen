# Compiler cache cleanup

To recover T: headroom, 2,755 old `.rlib` and `.rmeta` files were removed from
inactive nested `release/deps` build directories. These are rebuildable compiler
cache files. The current main build, executables, saved games and research
archives were excluded. No compiler process was active when the inventory and
deletion were checked.

Each absolute file path was verified within `T:\Dev\GTOpen\target`, and its
type, parent directory and size were rechecked before deletion. The inventory
excluded links, files changed in the preceding day, and direct inputs to the
active registrations. All inputs in both matched-trial registrations and the
supervisor registration retained their content hashes after cleanup.

Measured T: free space increased from 44.949 GB to 48.866 GB, approximately
3.917 GB recovered. Later builds may need to regenerate these caches. The
separate proposal to losslessly compress 36 older benchmark save files has not
been executed; it remains awaiting approval.

Evidence: `disposable-compiler-cache-inventory-v1.json` records the exact files,
sizes, modification times and file identities. The completed operation is in
`disposable-compiler-cache-cleanup-v1-result.json`. The inventory is intentionally
preserved as a pre-action record with `executed: false`; the separate cleanup
result records the completed deletion count and measured free space.
