# Larger exact-storage fixtures: passed

All 24 restoration and resumption observations passed bit-for-bit. Fixtures used the study's 56/19-class entering support, two boards, pots of 39.5 and 93.5 bb, two betting menus, and snapshots at iterations 1, 17 and 50. The largest full strategy arrays occupied 1.898 GB.

For AcQd9d, the larger menu's arrays shrank from 1.595 GB to 0.951 GB. The 5c2h2d fixture used the raw fallback and saved no space. At iteration 50, the largest compressed fixture took 0.439 seconds to encode and 0.615 seconds to restore. These are individual observations, not a throughput benchmark.

The test preserved both restored arrays and subsequent solver outputs exactly. It does not establish convergence, complete-forest capacity or production readiness. The guarded run completed in 51.266 seconds; five resource samples are not a precise peak-memory measurement.

Machine-readable evidence: [review](host-orbit-large-review.json), [registered protocol](HOST-ORBIT-LARGE-PROTOCOL.md), and [run status](../representative-coverage-20260919/host-orbit-large-diagnostic-status.json). Source and executable hashes were checked when the review was generated, before the subsequent test-module addition.
