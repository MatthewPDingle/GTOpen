# C13: faster terminal evaluation, rejected for startup regression

The bounded 32-bit element-index rewrite is numerically exact and improves
large-game complete work. This implementation is nevertheless **rejected**:
the small fixture's 3.67% median complete-time regression exceeds the registered
3% limit. The limit was not relaxed, and extra runs were not used to seek a pass.

| Metric, median of three paired ratios | Large vs C09 | Small vs C09 |
| --- | ---: | ---: |
| Complete work | 6.30% less time | 3.67% more time |
| Warm iteration | 7.88% less time | 5.84% less time |
| Accuracy check | 6.89% less time | 6.61% less time |

Large complete ratios were 0.93838, 0.93339 and 0.93700. Small complete ratios
were 1.01991, 1.04039 and 1.03669. All twelve runs matched the archived C09
checkpoints and complete arena fingerprints. The order alternated by pair.

The small game's median initialization grew from 0.291 s to 0.368 s, while
its median complete time grew from 0.999 s to 1.034 s. The prototype first
constructs retained modules, then compiles/loads replacement terminal modules.
That extra initialization is included in the result; it cannot be excluded
merely because subsequent kernels are faster. Large median initialization was
1.612 s vs 1.775 s and complete time was 56.892 s vs 53.323 s.

The mechanism uses 32-bit **float-element indices**, with 64-bit byte pointers.
Activation refuses an empty CDF or one larger than `u32::MAX` elements. No float
values, samples, ordering or global allocations change. Terminal register use
falls from 54 to 40, shared storage from 84 to 44 bytes; local storage stays zero.
The reference source-builder extraction produces PTX identical to archived C09.

Qualification includes 48 GPU address witnesses checked against wide host
arithmetic, including byte offsets above 4 GiB and up to 17,179,868,836;
420 partial-batch cases per variant, 169 hands each and 2-8 opponents;
zero/recovery, zero own/live/folded reach, all terminal and prefix bits;
full arenas, frozen/locked seats, captured graphs, stop and activation guards.
Both frozen-save allocation plans match C09 exactly. Two bounds/helper tests,
six expanded cohort tests and four exact-reuse tests passed. Full default/native
regressions were not rerun after the measured retention gate failed.

`check_c13.py` independently verifies source archives, compiler/input/executable
hashes, unchanged memory, reference PTX, every paired checkpoint/fingerprint and
the rejection gate. See `raw/c13-verified.json`. All tested candidate source is
preserved under `artifacts/c13-rejected`; working runtime source was restored to
C09 plus the previously qualified R01 research selection path. 56708 is unchanged.

Next: [C14](C14_PROTOCOL.md) constructs the narrowed modules directly so this
promising terminal improvement does not require duplicate startup compilation.
It must pass a fresh complete-work campaign. No C13 gain is counted in the
retained progress graph or claimed as improved time to full convergence.
