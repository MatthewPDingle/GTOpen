# D043 independent resource review

**PASS_COMPILER_RESOURCE_PREREQUISITE_ONLY.** The single preserved execution contains five raw markers and exactly three resource rows, from the RTX 5090 / compute_120 and queried NVRTC 12.9. Rust compilation and the resource probe both terminated successfully, in order. No kernel launches or solver execution occurred.

| Entry | Registers/thread | Local bytes/thread | Static/dynamic shared bytes | Theoretical 128-thread blocks/SM |
|---|---:|---:|---:|---:|
| Original up_action, baseline module | 66 | 64 | 0 / 0 | 7 |
| Original up_action, candidate module | 66 | 64 | 0 / 0 | 7 |
| New up_action_opponent | 40 | 0 | 0 / 0 | 12 |

The **39.3939% register reduction**, zero local bytes, increased theoretical occupancy and 128-thread support pass the prospectively fixed resource prerequisite. Independently extracted PTX for all nine original entries is byte-identical across the two modules. This equality does not prove the new entry's runtime numerical behavior.

The candidate CUDA is exactly the accepted E020 source plus the sealed opponent-only helper/entry. It retains the original positive-zero accumulator and ordered child sum for specialized 2/3/4-action and generic paths. Prepared inputs, dependency libraries, command records, compiler/DLL inventory, native binary, raw logs and source/reference pins verify. All 162 current checkout identities match accepted E020, including restored arena.rs after D042. The audit passed on its first file-only execution.

The permitted next step is to **consider one separately authorized production candidate**. This probe contains no host actor partition or dispatch, no numerical validation and no performance measurement. Full splitting would add 20 training-up launches per paired flop iteration; planning, compilation, capture and river effects remain in complete-cycle scoring. E005/E014 and the older preflop grouped-opponent regressions remain counterevidence. Existing exactness and performance gates must decide adoption; no accuracy, speedup or deployment claim follows here.

Reviewer actions were file reads and additive evidence only. No build, native probe, solver run, GPU call or checkout edit was performed by the reviewer.
