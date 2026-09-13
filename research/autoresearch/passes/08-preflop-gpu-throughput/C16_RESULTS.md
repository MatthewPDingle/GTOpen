# C16: fused local probability tables — rejected

Building probability tables inside each terminal block preserved results but
increased complete large-game runtime by **44.08%** in the first paired screen.
The candidate was archived and removed. The retained runtime is restored to
02c0898; port 56708 and the qualified R03 server binary are unchanged.

| Measurement | Retained C14 | C16 | Change |
| --- | ---: | ---: | ---: |
| Complete large run | 53.2562453 s | 76.7312239 s | +44.08% |
| Warm iteration median | — | — | +32.28% |
| Warm accuracy-check median | — | — | +59.58% |

This is one complete large pair. The registered first-pair gate failed, so no
extended timing campaign or small-game timing was run. There is no speed or
convergence improvement to retain.

## Numerical qualification

- 672 local-prefix and terminal-value cases matched exactly, covering dense,
  sparse, zero and recovery inputs, 2–8 opponents, full and partial batches,
  sample offsets and guarded output buffers.
- Six expanded solver tests passed (one manual test ignored), including full
  arenas, learning and average-strategy evaluation, fixed players, capture,
  stop and synchronization. Both timed runs matched each other and the C14
  reference at every checkpoint, including full-arena fingerprints.
- Saved small/large allocation plans matched C14. The original global scratch
  allocation was deliberately retained for this first screen, although C16 did
  not read it. No allocation saving is claimed.
- The first kernel invocation selected zero tests because its exact filter was
  incomplete. It is preserved as a failed qualification attempt; the corrected
  invocation selected and passed the intended test.

The aggregate tradeoff was worse: avoiding global table traffic did not repay
per-terminal prefix construction and synchronization. Arithmetic, barriers,
shared-memory bank behavior and occupancy were not profiled separately, so
these measurements do not identify a specific hardware stall cause.

## Evidence

[Registered protocol](C16_PROTOCOL.md), [integration record](C16_INTEGRATION.md),
[independent verification](raw/c16-verified.json), [checker](check_c16.py), and
[runner](run_c16.py). Source versions and compiler output are archived alongside
raw logs, source/input hashes, timing records and GPU snapshots.

The independent checker verified runtime restoration and the unchanged frozen
R03 binary. No additional broad regression run was needed for this rejected,
removed runtime candidate. The production-qualified retained version remains
available for a separate switch to 56708.
