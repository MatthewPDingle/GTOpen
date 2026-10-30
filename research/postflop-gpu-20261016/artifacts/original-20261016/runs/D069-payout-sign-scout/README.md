# D069 retained payout sign counts

All eligible planned CTAs in these retained snapshots have payout sign bits `011` in win/lose/tie order. None have all three negative sign bits. These are integer sign-pattern counts; the script does not evaluate a GPU zero-mass expression.

| Fixture | Historical iteration | Traverser | Eligible | All three negative | Other finite patterns |
|---|---:|---:|---:|---:|---:|
| rainbow | 20 | 0 | 8160 | 0 | 8160 |
| rainbow | 20 | 1 | 43361 | 0 | 43361 |
| rainbow | 200 | 0 | 52583 | 0 | 52583 |
| rainbow | 200 | 1 | 49181 | 0 | 49181 |
| two-tone | 20 | 0 | 3388 | 0 | 3388 |
| two-tone | 20 | 1 | 17369 | 0 | 17369 |
| two-tone | 200 | 0 | 44887 | 0 | 44887 |
| two-tone | 200 | 1 | 24798 | 0 | 24798 |
| river | 20 | 0 | 0 | 0 | 0 |
| river | 20 | 1 | 1 | 0 | 1 |
| river | 60 | 0 | 0 | 0 | 0 |
| river | 60 | 1 | 0 | 0 | 0 |

Every eligible count independently matches the sealed D067 result. Eligibility means historical opponent row flag zero and all three planned f32 payouts finite; negative sign includes negative zero. The complete eight-pattern distribution is retained in report.json.

The input catalogs, all three maps, all twelve row-flag files, D066/D067 audits and root preparation are hash-pinned. The script ran once as file-only Python analysis. No tree/plan reconstruction, solver, new census, compiler, native test or GPU execution occurred.

The counts do not establish actual computed result bits, barrier-removal correctness, dynamic frequency or timing gain. E036 remains closed; source feasibility and independent review are separate obligations.
