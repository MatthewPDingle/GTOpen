# D18: separate rank-product pipeline admitted for GPU qualification

The registered resource and source-work gates pass. This is an admission to
test two kernels, not a measured speed improvement. Runtime code is unchanged.

| Fixture | Extra allocation | Planned total device bytes | Terminal tile | Extra launches per sweep/check |
| --- | ---: | ---: | ---: | ---: |
| Small | 285,546,496 B | 599,492,128 B | 7,098 | 192 |
| Large | 874,496,000 B | 21,052,811,124 B | 16,384 | 18,688 |

The large case uses 37 terminal tiles per existing 32-sample batch. Scratch
holds separate quadrature products, preserving each hand's original addition
order. The producer avoids C18's per-sample block barriers; the consumer reads
those products after a stream-ordered kernel boundary.

Large learning/check source arithmetic falls by 56.65%/56.27%. Including
scratch writes and reads, logical terminal traffic falls by 16.99%/16.15%.
Small reductions are 54.83%/54.70% arithmetic and 12.77%/12.41% traffic.
Probability-table construction is unchanged. These counts do not establish
native instruction savings, physical DRAM traffic, or elapsed time.

The guarded host census completed in 1.047 seconds. `check_d18.py` independently
reconstructs the rank partitions and D10 opponent histograms, using separate
binary decoders and expanded work sums. All resource and launch counts agree.
See `raw/d18-verified.json` and the immutable `D18_PROTOCOL.md`.

Next: separately register C22, qualify producer/consumer exactness, partial
tiles and sample batches, poisoned unused scratch, and zero/inactive recovery.
Only after full solver, allocation, graph and stop checks may complete-work
timings decide whether the added memory and launches pay off. No deployment
or convergence claim follows from D18.
