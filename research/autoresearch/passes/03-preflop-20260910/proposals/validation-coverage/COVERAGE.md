# Validation coverage snapshot

Read-only evidence audit; no tests rerun. Hashes/time are in snapshot.json. Convergence queue is active; refresh after it finishes. Evidence paths below are relative to this pass directory.

## Reference definitions

- **Literal deployed original:** baseline1b8fc3f, including omitted forced-policy allocation in planning. All-solver controls are comparable; modeled batch/cache choices can differ.
- **Corrected original:** original GPU kernels plus common forced-policy accounting correction. Modeled budget comparisons and convergence original aeea634 use this reference.
- **Compatible candidate:** optimized kernels retaining corrected-reference batch/cache grouping (b7e8583; convergence wrapper3d538d5). This does not establish literal-deployed modeled parity. Pending deployed-compatibility/minimal proposals require separate evidence.

## Matrix

| Area | Recorded coverage | Limit / remaining gate |
|---|---|---|
| GPU all-solver3/6/7/8 | gpu-parity.json: compatible-three/six/seven/eight match original complete arena fingerprints, iteration, gaps, EVs | Fresh3/6/7; eight resumes checkpoint74. Fixed iterations, not four converged solves. Rejected candidates also appear in this file: passing correctness does not imply retention. |
| Modeled fresh coupled | compatibility-budget-comparisons.json: exact arena hash/gaps/EVs at19/21/23GB, batches23/27/30 and matched HU-cache | Corrected reference only. modeled-comparisons.json's default B32 row is non-exact and superseded. Literal deployed modeled grouping pending. |
| Legacy/frozen modeled | modeled-comparisons.json: exact fresh-legacy and freeze-non-btn arenas/gaps/EVs | Frozen fixture uses legacy_product, iteration100, five frozen seats and BTN learning. Not a frozen-coupled performance test. Fresh coupled profiles retain adaptive responses, so all six learning masks are true. |
| Full arena/policy comparison | raw/saved-comparator-batch30-a.log:861,384 action nodes,311,892,711 effective entries bit-equal, all raw regret/strategy values exact, headers equal after lock-order canonicalization | Elementwise B30 six-iteration evidence; other runs primarily compare FNV64 fingerprints. Comparator is descriptive, not an automatic acceptance threshold. B32 previously differed28.2 percentage points locally despite tiny aggregate EV differences. |
| Native roundtrip | modeled-fixtures.json, fixture-validated logs, B30 comparator headers, convergence roundtrip_verified | Strict raw/typed config/profile and model/iteration/frozen checks. Modeled pair passed. Original eight save passed; candidate still running at snapshot. Initial rejected fixture was not accepted silently. |
| Same-target convergence | Modeled pair both80iterations to0.004bb, eight checkpoint matches and identical final fingerprint;45.0% less trajectory time | Corrected-reference B23/HU-cache only. Eight original missed0.005bb at iteration174 (gap0.13924); candidate incomplete. Preserve bounded miss; any extension separately predeclared. |
| CPU quadrature | cpu-comparisons.json: f64 numerical agreement, reference tolerance2e-12; measured root/gap/EV equality3/4/6/9 | Not general bitwise equity equality. Six20iterations not converged. Eight-opponent terminal microbenchmark regressed about5%. |
| CPU paired checkpoints | Exact recorded checkpoints/root/gap/EV3/4/6/9; seven focused tests include parallel cancellation, profiles/locks/frozen/hero; synthetic4/16thread frontier | Exact against preceding CPU candidate, not retroactive quadrature bitwise proof. Synthetic frontier arena checks do not cover every CPU solve. |
| Low-memory/accounting | forced-budget-boundary-a: real134/135MB direct/normalized one-particle pass. forced-budget-cuda-a: actual forced upload and insufficient-budget refusal legacy/coupled pass | Earlier revision evidence. Latest compatible-internal-a:12passed/2ignored, including explicit boundary ignored. New deployed-compatible minimal path still requires real CUDA gates. |

## Required before integration

1. Finish active convergence and preserve any nonconvergence. Pin final source/executable; rerun gates affected by later kernels/planners. Source proposals are not validated results.
2. Resolve literal-deployed versus corrected-reference modeled grouping explicitly. If preserving deployed grouping, verify preferred/minimal real allocation boundaries, forced payload refusal, every-O terminal parity and full native arenas at identical batch/cache. Do not preserve the old accounting bug.
3. Run final combined default CPU and preflop GPU suites, explicitly selecting ignored boundary tests. The174-test CPU manifest belongs to source5f55793, before later checkpoint/planner changes; it is not final combined coverage. Include save/profile/lock/hero/frozen/cancellation gates.
4. Keep23GB original modeled timing instability explicit. Do not claim a stable8x speedup or measured paging. Constructor allocation estimates are not whole-device VRAM; eager phase timings are not production graph timing.
5. Final rendering must mark the rejected B32 comparison superseded and label reference provenance. findings.md still includes historical pending statements; do not infer final state from those alone.

No blocker found in accepted corrected-reference numerical evidence. Final integration coverage remains incomplete while research continues.
