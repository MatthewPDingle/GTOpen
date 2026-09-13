# D04: pair sharing rejected at the work-reduction gate

The best disjoint pairing saves **21.02%** of large-game average-check CDF
rows, below the registered 25% threshold. No paired GPU dispatch was built.
This is a work inventory, not a measured speedup.

| Fixture | Separate C01 rows | Best paired rows | Fewer rows | Preplanned peak including reserve |
|---|---:|---:|---:|---:|
| Small, six players | 29,009 | 22,637 | 21.97% | 0.543 GB |
| Large, eight players | 2,419,357 | 1,910,787 | 21.02% | 18.216 GB |

Enumerated all 15 small and 105 large disjoint pairings. The best pairing in
both fixtures happens to be natural adjacent seats. Other large pairings save
20.06%-21.02%, so no untested lucky pair can rescue this mechanism.

The safe large plan uses 574,196 static union slots, a 12.495 GB CDF buffer at
unchanged batch32, and a complete extra 695.6 MB value buffer. It also counts
normalized vectors, classification, maps, worklists, probabilities and a
256 MiB reserve. Initial allocation must be planned in the constructor:
allocating replacements while keeping old buffers would peak at **26.929 GB**.
The current enable-after-construction pattern does not fit that replacement.

The actual ungated average-check path has 2,419,357 unique per-player rows;
the older gated D01 average inventory counted 2,419,347. This small difference
is expected: D04 deliberately counts every row that check-time C01 builds.
All 1,875,134 repeated source-block observations across players match bit for
bit. Regrets, strategy sums, average reaches/masses and iteration remain
unchanged. Identity/collision/signed-zero/1-9-seat pairing tests passed.
Small inventory took 1.06s; large took 50.97s including host enumeration.

Evidence is in `raw/d04-*-v1.json`, guarded run metadata/logs and
`raw/d04-verified.json`. `check_d04.py` checks archived source, frozen executable
and input hashes, pairing coverage/costs, all 46 device buffers and budgets.
The source snapshot is `artifacts/d04-inventory`; the executable is local
`target/d04-inventory-frozen.exe`. Diagnostic code has no production dispatch.

Next hypothesis: three/four-player groups. The global large union is only
692,628 unique distributions (760,578 static slots), so pair sharing does not
exhaust overlap. Larger groups require additional value buffers and their own
registered memory/work gate; this rejection must not be relabeled a success.
Port56708 remains unchanged.
