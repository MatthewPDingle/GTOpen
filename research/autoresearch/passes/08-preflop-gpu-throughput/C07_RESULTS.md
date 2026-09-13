# C07 retained: bounded three-player check cohorts

C07 shares identical probability tables across at most three players during
accuracy checks. Unlike rejected C06, it caps its allocation plan at 20.5 GB
including reserve. Ordinary learning, all 1,024 samples, batch 32 and the
baseline HU cache stay unchanged. This is an opt-in research constructor;
the application on port 56708 has not been changed or restarted.

| Fixture / metric | Median candidate / C01 time | Interpretation |
| --- | ---: | --- |
| Large complete run | 0.923314 | 7.67% less time |
| Large warm iteration | 1.007120 | 0.71% more time |
| Large accuracy check | 0.865543 | 13.45% less time |
| Small complete run | 0.963683 | 3.63% less time |
| Small warm iteration | 1.003109 | 0.31% more time |
| Small accuracy check | 0.809030 | 19.10% less time |

Three alternating-order paired comparisons per fixture, six iterations each,
with two warmups and a full check each iteration. Large complete times were
66.668 / 61.633, 66.696 / 61.434 and 66.708 / 61.592 seconds (control / candidate).
All three improve in the same direction. Small complete runs last about one
second and are noisy: their paired ratios range from 0.9240 to 1.0144. They pass
the registered median regression threshold; do not treat their median as a
precise prediction for every small game.

Every checkpoint gap/EV and final full-arena fingerprint matches its paired
control. Four cohort tests cover terminal and prefix bits, full learning
arenas, roots, 3–9 players, batch 5/32, locks/frozen seats, zero mass/recovery,
capture/replay, stop/sync, no-multiway rejection and explicit error restoration.
Four existing exact-reuse tests, 19 native GPU tests and 181 default solver
tests also pass. No source changes occurred between numerical tests, timings
and regressions. CPU tests are correctness checks, not performance work.

The large constructor selects masks [161,70,24], exactly matching the static
preflight: groups [0,5,7], [1,2,6], [3,4]. It allocates 20,178,315,124 bytes,
with 20,446,750,580 bytes including the 256 MiB reserve. Allocation totals are
checked against all 46 ordinary device buffers plus the extra cohort buffers.
The selected grouping reduces observed check CDF rows by 31.56%. It uses about
7.13 GB more device memory than C01 on this fixture, so it needs a memory-aware
fallback before production adoption. Small groups are [0,1,2] and [3,4,5].

C06's much larger allocation slowed both learning and checks; C07 avoids that
large regression. This supports keeping memory headroom, but does not prove
paging caused C06's slowdown. Read-only nvidia-smi snapshots before/after each
run show context only, not residency during the run. No profiler was active.

The dashboard chains the paired C01 and C07 ratios, giving about 11.4% less
complete time relative to this pass's original baseline. That is a composition
of separate paired measurements, not a new direct baseline comparison. It is
fixed-work throughput, not a claim that the difficult conditional convergence
problem is solved or that the requested tenfold gain has been achieved.

Evidence: [protocol](C07_PROTOCOL.md), [static preflight](raw/c07-static-preflight.json),
[audited results](raw/c07-verified.json), [retention checker](check_c07_retention.py),
[guarded runner](run_c07.py), and [source map](artifacts/c07-source-map.json).
Frozen local executable: target/c07-benchmark-frozen.exe, SHA-256
df5505cff6ee1b6637e2aadef0f024450912fecbaa90357bfb7328df90237754.

Next, measure where the retained C07 evaluation spends its remaining time,
with diagnostic timers separate from timed benchmarks. Prioritize terminal
evaluation and reducing the shared-table memory cost; do not add larger groups
again without a new allocation mechanism. Full convergence qualification and
safe production integration remain separate work.
