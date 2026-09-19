# Shared GPU workspace with exact parked storage: passed prototype checks

Six small games completed 720 board/player passes with no differing values against full resident reference solvers. Board visitation was reordered, incoming weights changed abruptly, and whole ranges became zero on selected iterations. Each pass checked returned values, all four strategy arrays and storage round trips bit-for-bit.

Parked strategy arrays occupied 113,239,360 bytes instead of 180,129,920 bytes. The shared GPU workspace occupied 82,000,724 bytes. The guarded run completed in 45.188 seconds. These figures exclude other allocations and are not a production performance comparison.

This prototype preserves the explicit GPU calculation and only removes exact suit-related duplicates while storing state between games. It does not qualify the separate compact chance-traversal implementation. All four arrays still transfer each pass.

Remaining integration work includes sharing or releasing unused per-game pinned staging buffers, accounting for static metadata and temporary restoration buffers, robust error recovery, and a complete forest capacity measurement. The prototype currently retains per-game staging allocations. No full 164-board training or production deployment is qualified by this test.

Evidence: [review](host-paging-review.json), [protocol](HOST-PAGING-PROTOCOL.md), [run status](../representative-coverage-20260919/host-paging-diagnostic-status.json). A hashed executable copy is retained locally under target/qualified-paging/host-paging-diagnostic.exe.
