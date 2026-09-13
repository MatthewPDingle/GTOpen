# D10: bounded terminal tiles — feasibility screen rejected

Contiguous tiles share tables much better than C16's per-terminal rebuilds,
but none of the three registered sizes meets the 4 MiB storage gate for both
learning and accuracy checks. Do not implement this fixed-tile proposal unchanged.

## Large mature fixture

| Terminal positions per tile | Learning table work | Check table work | Max learning CDF | Max check CDF | Learning launches | Check launches |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | 1.117x | 1.041x | 3.22 MiB | 6.56 MiB | 1,545,792 | 1,414,592 |
| 512 | 1.047x | 1.015x | 9.79 MiB | 20.79 MiB | 443,840 | 367,392 |
| 2048 | 1.019x | 1.005x | 32.93 MiB | 68.07 MiB | 125,184 | 95,200 |

Table-work ratios compare the total distinct rows produced across tiles with
distinct rows in the retained per-seat learning or shared-cohort check plan.
Launch counts sum producer and consumer calls across all seats, all tiles and
32 sample batches (1024 samples total). Empty consumer work is omitted, so these
are optimistic counts for the proposed schedule. Launch counts are not timings.

At 128 terminal positions, learning meets the storage limit but checks need
6.56 MiB. Larger tiles reduce repeated table work and launches but require still
more storage. The small fixture also fails the check-storage gate: 5.94 MiB at
128 positions. All table-construction ratios passed their respective gates;
storage is the registered rejection reason. Do not retrospectively change the
budget or search smaller tiles to turn this result into an admission.

## Qualification and limits

- Synthetic identity and tile-boundary test passed: exact-bit distinctions,
  forced hash collisions, repeated identities, empty and partial tiles.
- Both saved extractions passed and left full regret/average-strategy arenas
  and iteration unchanged. Large snapshot: iteration 1050, 602,914 terminals.
- Independent Python set-union reconstruction matched every per-seat tile count
  and ordered terminal-key count, then computed shared-cohort totals from the
  verified C14 grouping. Source, executable, save and witness hashes checked.
- The initial build failed because a JSON macro needed an intermediate value;
  its source and failure log are preserved. The corrected build passed.

These are exact counts for two immutable snapshots, not measured GPU cache
hits, hardware stalls, launch latency or time to convergence. Learning states
evolve during a real sweep. The inventory does not claim a runtime speedup.
The only solver-source addition is a test-only research module; production
kernels and the frozen qualified R03 server remain unchanged. Port 56708 was
not modified. No runtime regression campaign is needed for this diagnostic.

## Next constraint

A future tiled design would need to address both its variable working-set size
and the very large number of launches. Merely reducing fixed tile size would
worsen scheduling overhead. Any such design needs a new bounded protocol and
measured scheduling evidence before a complete solver prototype.

[Protocol](D10_PROTOCOL.md), [independent results](raw/d10-verified.json),
[checker](check_d10.py), [guarded runner](run_d10.py). Compressed binary witnesses
and immutable source snapshots are included; the extraction never learns or
writes to the user's server.
