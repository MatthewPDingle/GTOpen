# E016 independent primary review

**Qualifying, not accepted.** Primary score independently recomputes to **9762.0023 → 9360.5316 ms**, **4.1125856% improvement** (401.4707 ms). All three repeats are retained; every paired fixture full cycle improved and no repeated material regression guard failed.

All **18 complete non-timing fixture records** match exactly, including full state/root fingerprints, configuration, exploitability and stops. Raw stdout payloads equal the reports. Both binary/build-manifest identities, six logs/reports, archived candidate source, prebuild source identity, build/patch logs, source review and unit evidence were verified; 29 artifacts remained unchanged. The only build-manifest source difference is mod.rs; kernels, plan, arena, store and the frozen evaluator are unchanged.

The unit log confirms **84 passed, 4 ignored**, including both expanded raw-device lifecycle proofs. The continuation validation/changed-root test is feature-gated and **did not execute in this gpu-only unit run**. Broader/F32/feature controls remain separate; this audit does not declare acceptance.

## Measured components

Fixture medians (baseline → candidate, ms):

| Fixture | Full cycle | Solve plus checks | Init |
|---|---:|---:|---:|
| rainbow | 5715.3170 → 5476.9716 | 4691.6807 → 4441.2760 | 617.1697 → 613.1014 |
| two-tone | 3932.9422 → 3778.9070 | 2883.4139 → 2737.2679 | 402.4997 → 423.1602 |
| river | 113.7431 → 104.6530 | 17.4472 → 15.9344 | 95.2250 → 87.8324 |

Paired suite savings (baseline minus candidate; positive is faster):

| Pair | Gain | Build | Init | Solve | Readback | Full cycle |
|---|---:|---:|---:|---:|---:|---:|
| B041/E016 | 3.9703% | +29.8349 | -42.9709 | +398.0175 | +1.3657 | +386.2310 |
| B042/E016R2 | 4.4804% | +0.5543 | +45.3974 | +402.0298 | -9.2635 | +438.7249 |
| B043/E016R3 | 4.2861% | -42.8642 | +58.1289 | +393.0916 | +9.9962 | +418.4072 |

Solve time improved in **9/9** fixture pairs. Mean paired suite saving is **414.4544 ms**; measured solve spans contribute **397.7130 ms** (95.96% of that separate mean). Mean build/init/readback savings are -4.1583/+20.1851/+0.6995 ms. This locates observed phase changes without identifying their kernel-level cause.

These paired means do not replace the primary sum-of-fixture-medians score, and separate component medians do not add to it. Accuracy checks and new graph setup remain inside solve time. No statistical-significance or cold-start claim is made, and no percentage is combined with earlier cohorts. No production edit, build or GPU run was performed by this reviewer.
