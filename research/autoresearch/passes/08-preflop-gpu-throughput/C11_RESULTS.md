# C11 rejected: terminal L1-cache preference

The first large complete run went from **65.736 to 76.776 seconds** versus
retained C09: ratio **1.167944**, or **16.79% slower**. Warm iteration ratio
1.139980 and accuracy-check ratio 1.216000 also regressed. The initial <0.99
admission screen failed, so no additional timed pairs or retention-only
native/default regression campaign was run. C11 source is archived and removed;
current solver files match retained C09 byte for byte.

## Mechanism and qualification

A fresh research constructor set `CU_FUNC_CACHE_PREFER_L1` on the exact-reuse
and cohort terminal functions once, before graph capture. No other functions,
context-wide preferences, shared-memory carveout, math, samples, unroll factor,
CDF layout or global allocation changed. Configuration after warmup was refused.

Five expanded cohort tests passed: original/C01/C07/C09/C11 full arenas, roots,
terminal and prefix bits; 3-9 players, batches 5/32, locked/frozen seats,
zero clearing/recovery, graph capture/replay and error handling. Four C01 tests,
one direct helper test (420 cases per variant, 169 hands each), and the actual
kernel/cache diagnostic passed. Both timed runs match retained C09 in every
checkpoint and final complete-arena fingerprint.

The driver accepted the cache preference. Actual exact-reuse and cohort PTX
are byte-identical to the factor-two kernel artifacts recorded by C10. Loaded
resources are unchanged: 54 registers, zero local bytes, 84 static shared bytes.
The small and large layout audits also match C09 exactly; large device arrays
remain 20,178,315,124 bytes. No source-level arithmetic change explains the
slowdown.

A successful cache-preference call does not prove the actual hardware partition
or hit rate. NVIDIA also documents possible synchronization when launching
kernels with different preferences. Neither effect was isolated in this test;
do not attribute the slowdown to one of them without further evidence.
[CUDA Driver API, cuFuncSetCacheConfig](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__EXEC.html).

`check_c11.py` independently checks source/input/executable hashes, prerequisites,
layouts, exact checkpoint/fingerprint equality, compiler identity and rejection.
See `raw/c11-verified.json` and `artifacts/c11-source-map.json`. Frozen executable
SHA-256: `1eac8950bba28f323e1be7bc45ca90aec513d5f3fb3fc7764b472b2747b263f3`.

This remains fixed-work GPU research; no convergence improvement or deployment
is claimed. Port 56708 was not changed or restarted. C01+C07+C09 remain retained,
about 15.1% cumulative less time by chained paired comparisons.
