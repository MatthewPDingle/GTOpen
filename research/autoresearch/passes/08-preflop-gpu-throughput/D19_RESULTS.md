# D19: static rank-boundary storage admits a GPU prototype

The proposed CDF layout needs **60.29% less declared CDF storage** and **65.77%
fewer logical float stores** across the fixed sample table. Every prefix read
by the evaluator has an exact direct address in the compact layout. This is
an address/storage proof, not a GPU numerical test or speed measurement.

| Fixture | Original CDF bytes | Compact CDF bytes | Final declared total |
| --- | ---: | ---: | ---: |
| Small | 218,035,200 | 86,572,800 | 183,875,876 |
| Large | 13,984,825,600 | 5,552,798,400 | 11,747,680,568 |

The layout adds 1,392,644 bytes of static maps and keeps other buffers, caches
and cohort groups unchanged. The maximum row span for any up-to32-sample window
is 2,160 floats, at start237, versus the original 5,440. Across all samples,
59,590 prefixes are needed rather than 174,080. Both read indices fit u32.

The independent checker walks rank groups in original sorted-hand order,
reconstructs all maps separately, verifies 173,056 hand boundary pairs and
32,272 sample windows, and checks row addressing and both allocation plans.
The guarded host census completed in 1.063 seconds without solver or GPU work.

This differs from C04: selection is fixed by sampled rank boundaries, with
direct group and group+1 reads. It needs no value-dependent masks, run detection
or popcount decoding. Original scan rounding must still be retained exactly;
no assumption that unused neighboring prefix values are numerically identical
is made. The writer gains mapping reads/predicates; the reader gains sample
offset reads. Those costs could still outweigh the reduced storage/traffic.

Large simultaneous old/new CDF allocation would reach 26,000,941,624 bytes
including the existing reserve and exceeds the 23,000 MB budget. A prototype
must use fresh private construction, releasing its old buffer before allocating
the new one and publishing no engine on failure. Final large memory plus reserve
is 12,016,116,024 bytes. No live engine may change layout.

Next is a separately registered C23 GPU writer/reader prototype. It must compare
every required prefix and complete terminal result, including rounding-sensitive
inputs, partial batches, aliases and zero recovery; then whole solver and memory
checks precede complete-work timing. No speed gain, convergence qualification
or deployment is established here. R03 and56708 remain unchanged.

Evidence: `D19_PROTOCOL.md`, `d19_static_cdf.py`, `check_d19.py`,
`raw/d19-static-cdf.json`, `raw/d19-static-cdf-maps.json.gz`,
`raw/d19-verified.json`.

The turn first revisited complete opponent-tuple reuse. D01 already reported
only2.84% large current and0.319% average weighted duplicates; no repeated
inventory or prototype was run for that rejected mechanism.
