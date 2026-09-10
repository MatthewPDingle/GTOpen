# Literal constructor allocation results

Evidence: `../../raw/literal-allocation-totals-a.log` and `../../raw/literal-allocation-each-a.log`. These are parent-run, constructor-only controls of literal `1b8fc3f`, the six-seat fresh coupled fixture, and a 19,000 MB requested budget. Both chose 24-particle batches and 846,156 union CDF slots. No solver iterations, checkpoints, or saves occurred.

## What is accounted for

Both independent ledgers agree on all 42 device slices: **19,098,906,628 requested bytes**. The original planner reported **18,711,579,824 bytes**. The 387,326,804-byte difference consists of the known omitted 414,292,684-byte forced-policy allocation, offset by 26,965,880 bytes of net planner allowance. This is distinct from driver usage above actual requested payload.

| Measurement | Totals mode | Each mode |
|---|---:|---:|
| Device usage before constructor | 1,333,264,384 | 1,333,264,384 |
| Device usage added by constructor | 20,236,742,656 | 20,268,707,840 |
| Actual slice payload | 19,098,906,628 | 19,098,906,628 |
| Added device usage minus payload | **1,137,836,028** | **1,169,801,212** |
| Device usage after object drop | 1,333,264,384 | 1,333,264,384 |

Module loading adds 2,097,152 bytes in both runs; loading constructor functions adds zero further bytes. Dropping the constructed object returns the device measurement to its exact initial baseline in both runs.

## Where the large difference first appears

Each mode synchronizes after every allocation/copy/zero-initialization. Its decisive intervals are:

| Completed buffer | Requested buffer bytes | Device usage increase in this interval | Cumulative driver-minus-payload bytes |
|---|---:|---:|---:|
| `d_mw_cdf` | 13,809,265,920 | 13,790,871,552 | 15,564,776 |
| `d_forced` | 414,292,684 | 402,653,184 | 13,187,408 |
| `d_regrets` | 1,247,570,844 | 1,241,513,984 | 7,130,548 |
| `d_strat` | 1,247,570,844 | 1,275,068,416 | 34,628,120 |
| `d_reach_src` | 44,292,480 | 33,554,432 | 23,890,072 |
| **`d_reach`** | **1,247,574,900** | **2,374,316,032** | **1,150,631,204** |
| `d_val` | 846,255,332 | 880,197,632 | 1,169,809,324 |

The `d_reach` interval alone increases the residual by **1,126,741,132 bytes**. It calls `stream.alloc_zeros::<f32>(reach_blocks * NUM_CLASSES)`; the snapshot occurs after both allocation and initialization. Before that interval, residuals remain between roughly 2 MB and 35 MB despite the much larger CDF allocation. This localizes the large extra usage to the reach-buffer allocation/initialization interval in the synchronized run. It does not reveal an extra Rust-owned slice or a double-sized CDF request.

Small allocations often add zero measured device usage, followed by 33,554,432-byte (32 MiB) increments. Therefore a single allocation's driver increment need not equal its payload. The final each-mode result is 31,965,184 bytes above totals mode despite identical payload and planner geometry, so synchronization measurably affects this control or its device-global surroundings.

## Limits

- The synchronized run localizes an **interval**, not an internal CUDA mechanism. It does not separate allocation from zero-initialization, nor prove reservation, fragmentation, paging, residency, or a leak.
- The CDF already used `alloc_zeros` earlier. The result is not evidence of an unconditional first-memset cost.
- Free/total memory is device-global. These two runs alone do not exclude unrelated device activity, although the exact baseline restoration and localized repeat of a similarly sized residual strengthen the constructor association.
- The literal planner's forced-allocation omission is known and separate. These controls do not directly measure the corrected original's different batch geometry or the optimized constructor.
- No solver kernel ran, so this residual cannot be assigned to the solver kernel's executed local-memory usage from these logs.

The present evidence is sufficient to stop describing the residual as an unaccounted application buffer. Its cause remains unresolved, but its first large appearance is now localized. This closes the diagnostic scope for this pass; no allocator tuning or production behavior change follows from these logs.
