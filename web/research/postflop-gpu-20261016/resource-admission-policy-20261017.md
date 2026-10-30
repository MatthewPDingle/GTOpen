# Prospective resource admission: allocated registers

Effective after D094 publication on 17 October 2026. The user's unchanged acceptance rule remains at least **1% complete-cycle improvement with no material tradeoffs**, exactness, fixed sampling and strict fixture nonregression. This clarifies a preliminary compiler/resource filter; it grants no performance or adoption decision.

For future independently scoped candidates, reported registers per thread may increase **only when the verified target-device allocation model proves that allocated registers per warp and block do not increase**. Keep the raw reported counts visible. Require the same fixed driver occupancy observations and no decrease in occupancy or maximum threads. Preserve the existing no-increase checks for local spill bytes and static/dynamic shared memory. Validate the declared ABI/caller changes and intended changed entry bodies; unchanged entries must remain exact. All actual host/global-device payload, capacity, behavior, compatibility, F32/save/resume/continuation and complete-cycle performance gates still apply.

If allocation granularity is not verified for the actual target device/compiler/runtime context, a nominal register increase cannot pass this exception. The checked helper currently supports compute12.0 with32thread warps and256register per-warp allocation units, pinned to D094's NVIDIA CUDA12.9.79 header and calibrated driver evidence. Other hardware requires its own verified evidence. Instrumentation, launch preferences and spill/shared/global costs cannot be waived by an allocation calculation.

The [NVIDIA occupancy guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#calculating-occupancy) distinguishes reported registers from rounded allocation. D094 compiled the official standalone CUDA occupancy header with live RTX5090 properties. Its20,480 rows cover10resource geometries, nominal counts38/40 and every1..1024thread count. All pairs have identical modeled allocated registers/shared memory, occupancy, feasibility and limiting factors. A separate integer replay passes30,780checks; all60 retained actual driver occupancy queries at64/128/256threads match. At128threads both counts allocate5,120registers per block in this model. Allocation counts are NVIDIA SDK model outputs, not hardware allocation-counter measurements or proof of runtime speed.

Seven helper tests cover all10retained geometries, quantum boundaries32->33and40->41, allocation reduction, spill/shared/occupancy/limit regressions, missing proof, malformed attributes and incomplete/misaligned driver observations. Crossing to the next allocation quantum is rejected even when sampled occupancy remains unchanged. The helper admits numerical controls only; it never accepts a candidate.

Historical protocols, samples and decisions remain frozen. E057 retains its rejection under its original no-nominal-register-increase rule; this audit does not reopen E057, E050 or any other closed hypothesis, nor permit variants or additional samples. Future protocols must freeze this policy and the helper/proof hashes before candidate execution. Performance thresholds, exactness, stopping/storage/workload settings, fixture guards, fresh16confirmation and broader/holdout/fresh-original qualification are unchanged.

- [D094 frozen audit protocol](evidence/D094-resource-materiality/protocol.json)
- [Allocation and driver-calibration report](evidence/D094-resource-materiality/report.json)
- [Helper tests](evidence/D094-resource-materiality/test-report.json)
- [Prospective admission helper](evidence/D094-resource-materiality/postflop_resource_admission.py)
- [Unchanged primary qualification policy](qualification-policy-20261017.md)

SDK header SHA256: a3445fd09846af0b16a9ab2b10b302522b72b0cd93e358a91bdd2dedd19bc8a2. Helper SHA256: 4ff9b4e57b6facb5d6b07a6c67b18695e524f7fd54879fbd6ac6b177892cc720. Audit report SHA256: 86f8062d84a2eba0d5387961abc337b2576072509e1f1d9c0627dce6fc2191f4. Root review/replay is not an external independent audit. No solver source or live executable changed; no new performance gain is claimed.
