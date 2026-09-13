# C09 retained: partial terminal sample-loop unrolling

Three alternating pairs on each frozen fixture passed the registered gate.
The explicit factor-two hint reduces large complete runtime by **4.21%** versus
C07 (median ratio 0.957908). Warm iterations take 4.64% less time and accuracy
checks take 3.92% less time. This is fixed-work throughput, not a demonstration
of faster convergence or the user's desired tenfold improvement.

| Fixture | Complete ratios, candidate/control | Median |
| --- | --- | --- |
| Large | 0.956957, 0.957908, 0.963388 | 0.957908 |
| Small | 1.017663, 1.059935, 0.981448 | 1.017663 |

Large complete pairs are 68.772/65.812, 68.700/65.808, and 68.652/66.139 seconds.
Small complete runs are only about 1.1 seconds and noisy: median 1.77% slower,
worst pair 5.99% slower. The registered small gate is median <=3% regression;
it passed. Small warm iterations/checks improve by 3.06%/3.55% respectively.
Initialization, all six sweeps and checks, synchronization and arena hashing
are included in complete time; the first two sweeps are excluded only from
warm phase medians.

## Change and compiler evidence

An opt-in `new_research_unrolled_cohorts` constructor compiles the C01/C07
terminal modules with `#pragma unroll 2` immediately before the original sample
loop. Each variant has its own cached PTX. The single sequential accumulator,
inner quadrature/opponent ordering, 1,024 samples, game model, batch sizes,
CDF layout and C07 group allocation are unchanged. The normal production
constructor remains unchanged. No shared staging from rejected C08 is present.

The compiler already generates factor-two loops for two and three opponents.
The hint changes the four-to-eight-opponent helper loops from single-step to
factor-two loops, with remainder handling visible in PTX. This is a real
compiler change rather than just a source annotation. Diagnostic base-terminal
registers change from 64 to 54; local memory remains zero, static shared memory
84 bytes. These attributes are from the base terminal in the diagnostic module,
not the actual alias-aware C01/C07 runtime functions, so they do not prove a
particular occupancy explanation for the measured speedup. Code grows: base
terminal PTX body 58,830 to 109,408 bytes; instruction-cache effects remain a risk.

## Verification

- Five expanded cohort tests: original, C01, C07 and C09 full arenas, roots,
  terminal bits and final prefix bits; player counts 3 through 9, locks/frozen
  seats, zero-mass clearing/recovery, batches 5/32, capture/replay and errors.
- Four exact-reuse tests pass.
- One dedicated helper test checks 420 cases per variant, each with 169 hands:
  2-8 opponents, sample counts 1/7/23/31/32, offsets 0/1/37/992, tied/untied
  cumulative probabilities and zero/recovery. Every output bit agrees.
- All 12 timed runs agree with retained C07 in every gap/EV checkpoint and
  final full-arena fingerprint.
- All 19 native GPU and 181 default solver regressions pass. Default tests
  are correctness checks; CPU performance remains out of scope.
- Small/large global allocations match C07 exactly. Large device arrays remain
  20,178,315,124 bytes (20,446,750,580 budget including reserve). The existing
  cohort memory constraint still applies.

`check_c09.py` independently verifies source/executable/input hashes, immutable
source archive, run ordering, finite outputs, exact checkpoints, allocations,
compiler emission, gates and regression counts. See `raw/c09-verified.json`.
Frozen executable SHA-256:
`a3a0cacbb764422cd101bf283fe1ea2c07d2f8b1313ec197191e697a51630703`.

This remains research-only. No live session, server restart or deployment to
port 56708 occurred. The dashboard's cumulative retained line chains paired
ratios; it is not a new direct comparison against the original pass baseline.
