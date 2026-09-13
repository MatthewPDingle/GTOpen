# C10 rejected: factor-four terminal unrolling

The three large complete-run ratios versus retained C09 were 0.989984,
0.985317 and 0.967767. Median improvement **1.47%** falls below the registered
3% large retention threshold. Small median improvement was 4.91%, but the
large fixture is the primary gate. Do not retain factor four or automatically
advance to factor eight. C09 is restored byte for byte.

| Fixture | Control / candidate complete seconds, pairs 1-3 | Median ratio |
| --- | --- | --- |
| Large | 65.807 / 65.148; 65.817 / 64.851; 67.328 / 65.158 | 0.985317 |
| Small | 1.135 / 1.086; 1.160 / 1.100; 1.132 / 1.077 | 0.950897 |

Large warm-iteration/check median ratios are 0.985600/0.982076. The first
pair barely passed the initial <0.99 gate, which is why all three pairs were
completed. The third control was slower than the first two; the paired median
still fails the pre-registered rule. No extra repetitions were selected to
change that result. No retention-only native/default regression campaign ran.

## Exactness and allocation

Five expanded cohort tests passed (original/C01/C07/C09/C10, whole arenas,
roots, terminal/prefix bits, 3-9 players, batches 5/32, locks/frozen seats,
zero clearing/recovery, capture/replay and error handling). Four exact-reuse
tests passed. The dedicated helper test passed 756 cases per version across
2-8 opponents, counts 1/2/3/4/6/7/23/31/32 and offsets 0/1/37/992, including
zero recovery and all remainder classes. Each case compares 169 hand values.

All 12 benchmark runs match the retained C09 checkpoints and full final arena
fingerprints exactly. The large/small allocation plan and every global array
match C09 (large device arrays 20,178,315,124 bytes). No samples, arithmetic
order, precision, game model or bet tree changed.

## Actual runtime compiler evidence

An additional untimed constructor diagnostic saved the generated alias-aware
C01 and cohort PTX and queried their loaded function attributes. This improves
on C09's base-terminal-only resource inspection:

| Kernel / factor | Registers | Local bytes | Static shared bytes | PTX body bytes |
| --- | --- | --- | --- | --- |
| Exact reuse / 2 | 54 | 0 | 84 | 111786 |
| Exact reuse / 4 | 56 | 0 | 84 | 183859 |
| Cohort / 2 | 54 | 0 | 84 | 109914 |
| Cohort / 4 | 56 | 0 | 84 | 182013 |

Factor four increases code size substantially. There is no local-memory
allocation in these loaded kernels. Those facts do not separately establish
whether instruction-cache behavior, register use or loop overhead caused the
small timing difference. No unsupported bottleneck attribution is made.

`check_c10.py` validates source/executable/input hashes, all prerequisites,
run ordering, exact outputs, layouts, compiler records and the failed gate.
See `raw/c10-verified.json`, `artifacts/c10-source-map.json` and the rejected
source archive. Frozen executable SHA-256:
`ce47faa16d6dfc4373f5fe534c77f6d3271be772f13e02914d1367a147ce1b74`.

No live-app write, deployment or restart on port 56708 occurred. This is a
fixed-work GPU experiment, not full convergence validation. Retained cumulative
progress remains C01+C07+C09, about 15.1% less time by chained paired ratios.
