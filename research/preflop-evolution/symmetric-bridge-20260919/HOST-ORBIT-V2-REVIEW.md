# Exact host storage passes 24 small cases

Version 2 restored all four arrays bit for bit at every registered checkpoint and resumed with bitwise-identical returned values and arrays after two full GPU passes. This is a storage-only result: it retains the full explicit traversal rather than using the compact chance traversal whose changing-range qualification remains failed.

| Fixture texture | Full array bytes | Stored array bytes | Array saving |
|---|---:|---:|---:|
| KsQs2d, two-tone | 38,292,320 | 22,827,200 | 40.39% |
| KsQs2s, monotone | 38,292,320 | 10,815,200 | 71.76% |
| KsQh2d, rainbow | 38,988,544 | 38,988,544 | 0% |

These are small fixture ratios, not a weighted forecast for the study forest. Encoding and restoration timings are retained per checkpoint; they include local allocation but exclude a production paging implementation. The approach requires explicitly symmetry-tied state and compatible ranges. Arbitrary unprojected or asymmetric policies are not covered.

Version 1's failed run remains saved. Its first eight two-tone/monotone rows passed, then the first rainbow case hit a bad prototype assumption that visited blocks fill the planner's entire allocation. Non-isomorphic plans retain full offsets, including unreachable gaps. Version 2 stores/restores the entire raw array for that case; no bitwise criterion changed.

Larger-tree testing is the next gate. Even if those checks pass, repeated board switching, static metadata, temporary full arrays and complete forest peak memory must be measured before starting broader training. No deployment or live solve was changed.

Evidence: `host-orbit-v2-review.json`; both versions' protocols, sources, build/runtime hashes, status files and logs. Original failed guard exit: 101. Version 2 guard: success, 10.328 seconds.
