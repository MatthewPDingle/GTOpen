# C14: retain direct construction of narrowed kernels

C14 passes the registered retention gates. It keeps C13's bounded element-index
arithmetic and constructs the selected exact/cohort modules directly, avoiding
construction and replacement of two extra modules. The normal constructor and
R01 automatic selection still use their previous paths; this is opt-in research.

| Median of three paired ratios | Large vs C09 | Small vs C09 |
| --- | ---: | ---: |
| Complete work, including startup | 6.44% less time | 5.33% less time |
| Warm iteration | 7.95% less time | 6.14% less time |
| Accuracy check | 6.82% less time | 6.60% less time |

Large complete ratios: 0.94242, 0.93555, 0.93444. Small ratios: 0.90524,
0.99527, 0.94669. No extra repetitions were used to obtain a pass. Small median
initialization is 0.292 s control versus 0.283 s candidate (rounded); complete
work is 1.002 s versus 0.949 s. Large complete medians are 56.849 s versus
53.178 s. Ratios are computed per pair, not from those separate medians.

Every checkpoint and complete strategy/regret arena fingerprint in all twelve
runs matches archived C09 exactly. Allocation plans, buffers, batch and HU cache
are unchanged. Forty-eight device address witnesses preserve wide byte offsets;
420 partial-batch cases per variant cover 169 hands and 2-8 opponents. Expanded
terminal/prefix/full-arena comparisons include zero/recovery, frozen players,
point locks, captured graphs and stop. Two bounds/helper tests, six cohort tests,
four reuse tests, all 19 native GPU tests and 181 default solver tests pass.

Control PTX is identical to C09; candidate PTX is identical to C13. Terminal
registers fall from 54 to 40, shared bytes from 84 to 44, with zero local storage.
The complete CDF must fit u32 element indices; byte addressing remains 64-bit.
The guard runs after capacity planning and before enabling narrowed kernels.
The compiler cache distinguishes wide/narrow and rolled/unrolled variants.

`check_c14.py` independently audits source archives, all input/executable hashes,
compiler output, allocation equality, checkpoints, timings and regression counts.
The verified result is `raw/c14-verified.json`; exact tested sources are archived
under `artifacts/c14-tested` with `artifacts/c14-source-map.json`. Frozen executable
SHA256: `d5428c154a9dd86a988927df0e10b4567efbf6b92858637320f66c0b9008f852`.

The dashboard's chained retained paired ratios now imply 20.57% less complete
large fixed-work time than this pass's original baseline. This is not a direct
end-to-end convergence measurement or evidence of the requested order-of-magnitude
improvement. Four candidates are retained: C01, C07, C09 and C14. C13 remains
rejected in the historical graph. Port 56708 has not been changed.

Next: R02 partial-allocation recovery, then isolate retained modules from other
research features and qualify a separate server build with saved sessions before
production promotion. GPU convergence work remains open.
