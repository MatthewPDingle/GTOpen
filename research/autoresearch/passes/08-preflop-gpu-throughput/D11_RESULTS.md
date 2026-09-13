# D11: where the retained GPU version spends its time

The two main stages still dominate: probability-table construction and multiway
terminal evaluation. A useful next experiment should eliminate repeated work,
not merely reschedule it. This diagnosis adds no retained speed improvement.

| Fixture / operation | Eager GPU time | Probability tables | Multiway evaluation | Other work |
| --- | ---: | ---: | ---: | ---: |
| Small learning sweep | 45.7 ms | 47.2% | 45.7% | 7.1% |
| Small accuracy check | 56.4 ms | 37.8% | 56.7% | 5.5% |
| Large learning sweep | 2871 ms | 49.0% | 47.1% | 3.8% |
| Large accuracy check | 5028 ms | 39.5% | 59.0% | 1.5% |

Medians of four warm measurements; component medians can differ slightly from
the median combined share. These are eager CUDA-event timings, not graph replay
or end-to-end convergence measurements. Both saved fixtures match archived C14
at all six gap/EV checkpoints and in their complete arena fingerprints.

## Prospects for a large gain

Even making one major stage completely free would improve the large learning
sweep by only about 1.9-2.0x; for checks, about 1.65x (tables) or 2.44x
(evaluation). With other work fixed, a 10x improvement would require the two
stages together to get about 15.5x faster for learning and 11.5x for checks.
These Amdahl calculations identify priorities; they do not prove that such an
improvement is attainable or impossible. Convergence iteration count is separate.

## Logical work census

| Large starting snapshot | Learning | Accuracy check |
| --- | ---: | ---: |
| Positive terminal tasks across seats | 1,034,001 | 2,361,983 |
| Distinct distribution rows across retained groups | 862,854 | 1,655,762 |
| Source floating-point operations | 6.03 trillion | 12.88 trillion |
| Logical CDF gathers | 4.72 TB | 10.30 TB |
| Minimum logical CDF output | 601 GB | 1,153 GB |

Counts include all 1024 samples and 169 hand classes. FMA counts as two
operations; fmax and indexing/control/normalization/final value arithmetic are
separate or omitted. Two independent binary decoders agree and reconcile every
seat with the previously verified D10 witnesses. These describe immutable
starting snapshots; live learning distributions evolve.

Logical gathers are not DRAM traffic: caches can satisfy many reads. Minimum
CDF writes assume exact deduplication; the bounded classifier may fall back to
additional work. Neither table gives a measured hardware lower bound.

For scale only, NVIDIA's [GA102 reference whitepaper, Table 9](https://www.nvidia.com/content/PDF/nvidia-ampere-ga-102-gpu-architecture-whitepaper-v2.pdf)
lists 35.6 TFLOP/s FP32 and 936 GB/s for the reference RTX 3090. At those idealized
rates, the counted arithmetic alone corresponds to 0.17/0.36 seconds and CDF
output alone to 0.64/1.23 seconds. They omit other costs and cannot be added as
independent bottleneck timings. The local card reports a 2100 MHz maximum SM
clock and 420 W limit, unlike the reference design; no settings were changed.

## Verification and next step

The new retained-constructor tracing test passed across 4/7/9 players,
fixed/learning seats and batches 5/32. Both saved unprofiled/profiled pairs pass
exact comparisons, event-count checks and source/input/executable hash checks.
Only test code changed; no runtime regression suite was required. The qualified
R03 executable remains untouched and port 56708 is unchanged.

Next, inventory exact first-two-opponent product reuse across terminal branches.
A bounded cache could remove some repeated table gathers and arithmetic while
preserving operation order. It must earn a GPU prototype through a separately
registered feasibility gate; no useful reuse or speed benefit is assumed.

[Protocol](D11_PROTOCOL.md), [independent checker](check_d11.py),
[verified timings](raw/d11-verified.json), [work census](raw/d11-work-census.json),
[census implementation](d11_work_census.py), [guarded runner](run_d11.py).
