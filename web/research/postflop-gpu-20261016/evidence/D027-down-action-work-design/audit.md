# D027: omit inactive-actor down-action CTAs after reach reuse

**Recommendation:** preserve this bounded actor-filtered downward worklist design pending resolution of E016's acceptance gate. A uniform-level-only optimization is lower value on the flop fixtures. This is a source/census design from **experimental E016**, not an implementation or accepted performance result. No builds, GPU jobs, checkout changes or server mutations were performed. E015 remains the accepted baseline.

Before sealing, the fresh original-baseline comparison reported 12.0971% aggregate improvement but failed the river guard: median river regression 15.8921%, with all three paired regressions above 3% (7.4135%, 5.0065%, 15.9419%). This differs from the passing incremental E015 comparison below. E016 acceptance is held; root is investigating the cohort/initialization behavior. These measurements do not isolate a cause. Do not implement D027 until root resolves that decision.

The copied `source/mod.rs` is frozen E016, SHA256 `0ca68663e9eeaf168b6769b36bd266d59ddc0c0d4838641ce0dd350c40d2abed`. Seven current source inputs match E016's measured binary manifest. All three preserved D001 census configurations and tree counts exactly match E016's raw results, and the plan source is unchanged. No fresh compiled census was run. `manifest.json`, the copied census and `counts.json` retain identities and derivations.

## What remains redundant

E016 reduces hand-loop work by passing zero for the reused player's count, but `paired_sweep` still launches one down_action CTA for every action node at each level (`mod.rs:821–854`). For a node owned by that player, the wrapper still reads its node/action-count metadata, selects a specialization and enters a kernel body whose hand loop is empty. Those CTAs cannot write output.

`kernels.cu:47–91` chooses the actor's hand count. Both locked and unlocked stores are inside `i<nh_a`. No barrier, atomic, shared side effect or counter remains outside the loop. The proposed omission removes these inactive CTAs; it does not further reduce hand arithmetic relative to E016. Actor metadata is uniform across a CTA, but the count of removed CTAs must not be confused with bytes read, SM occupancy or elapsed time.

## Existing depth distribution and options

D001 contains 13 nonempty action levels for each flop. Only levels 0, 1 and 2 are single-actor: `[1,0]`, `[0,2]`, `[3,0]`. Every larger level is mixed. The river has seven nonempty levels, all single-actor. Full per-level counts are in `counts.json`.

The frozen harness checks every 20 iterations. E016 uses one full p0 sweep after invalidation, 19 player0-reuse p0 sweeps, and 20 player1-reuse p1 sweeps in each batch. Original scheduled down-action CTAs are `40*N`. Filtering omits `19*A0 + 20*A1`; this is 48.69% on the flops. Launch omission is possible only where the selected actor's span is empty.

| Fixture | Actor0 / actor1 nodes | Uniform-only omitted CTAs per 20 iterations | Actor-filtered omitted CTAs per 20 iterations | Down-action launches, old → filtered |
|---|---:|---:|---:|---:|
| rainbow | 274,801 / 248,732 | 116 | 10,195,859 | 520 → 462 |
| two-tone | 167,213 / 151,349 | 116 | 6,204,027 | 520 → 462 |
| river | 6 / 6 | 234 | 234 | 280 → 144 |

Uniform omission alone saves the same number of kernel launches, but leaves essentially all large-flop CTA scheduling unchanged. There is insufficient evidence that those few early-level launches alone could clear the 2% complete-cycle gate. This is a prioritization judgment, not a measured upper bound.

## Concrete bounded design

Preserve the existing `action_nodes`, `action_spans` and every up/evaluation use byte-for-byte. Build a separate downward node-ID list with two per-level spans: actor0 followed by actor1, preserving original order within each actor. The total additional list has **N IDs**, not two copies of N. Filtering IDs changes neither node IDs nor the offsets stored in per-node tables.

Use one plan-wide pointer choice to avoid mixing coordinate systems:

- If **any** nonempty level has both actors, allocate/upload the separate N-entry list once. All actor spans index that list, including small/uniform levels.
- If **every** nonempty level is single-actor, retain no additional device list. Each actor span uses the original aggregate start/count when owned by that actor, and count zero otherwise. Empty levels produce empty spans without indexing a first node. This avoids a new CUDA allocation/upload on the registered river fixture.

In training down dispatch, `DownReachReuse::None` selects the original aggregate list/span; `Player0` selects actor1's downward span; `Player1` selects actor0's downward span. Skip a zero-count selected span before building a launch. Use the selected count for both the kernel count and grid size, and the selected start with its matching pointer. Keep all real/zero hand arguments exactly as E016 currently supplies them. No change to copy_root, down_chance, up kernels, kernel names/source, profile bucket 1, compiler options or 128-thread blocks is required.

This adds no down-action launch: a mixed level still launches exactly once per sweep. It changes no upward ordering. It can remove launches for an empty actor span. The three E016 graph variants already encode the correct reuse mode, so no new graph variant or invalidation rule is needed.

## Allocation, initialization and admission cost

| Fixture | Additional device IDs | Extra device payload / temporary host ID payload | Retained host span payload |
|---|---:|---:|---:|
| rainbow | 523,533 | 2,094,132 bytes each | 224 bytes |
| two-tone | 318,562 | 1,274,248 bytes each | 224 bytes |
| river | 0 | 0 | 128 bytes |

These are payload sizes; Rust vector capacity, CUDA allocation bookkeeping and graph objects are separate. Allocate the host node vector with exact known capacity and avoid an additional N-entry temporary partition buffer. Building spans requires actor classification and stable filtering of the existing list; include this CPU work, the one mixed-plan device allocation/upload, and all graph setup in complete-cycle timing. All-uniform plans still pay small host classification/span cost.

`GpuPlan::staging_bytes` currently counts only reach/CFV arrays (`plan.rs:494–499`), while the constructor adds a fixed reserve. Do not silently hide the new per-node payload in that reserve. Account for the added list explicitly in both the full-F32 admission decision and the final required-byte check, with checked size arithmetic. Update exact budget boundary tests accordingly. Conditional absence must add exactly zero bytes.

Update `continuation_capacity.rs` estimated immutable device metadata (`29`), observed metadata (`45`), and retained host span payload (`74`). Include the optional list length, not original action count unconditionally. New per-solver immutable metadata must be allocated before any graph capture and retained for graph lifetime. It is not part of the seven mutable arena/reach/CFV buffers swapped by paging/storage. Continuation constructors would pay this extra immutable metadata on mixed plans even though their generic sweeps use the original aggregate path; capacity accounting must reflect that real cost.

## Exactness and lifecycle obligations

- Every filtered list must be the stable subset of the original level whose `node_player` matches the actor. Validate full/disjoint union, no duplicate/missing IDs, same depth, and original relative order within each actor. Include mixed, uniform, empty, single-node and arbitrary-action-menu cases.
- Every action child is at depth+1 (`plan.rs:154–165`), and current same-level CTAs already execute without an order guarantee. Active nodes write only their own actor reach. Distinct action edges use distinct reach owners (`plan.rs:412–426`); removing inactive nodes cannot remove an input of an active same-level node. Preserve the level order and unchanged chance dispatch after each action level.
- Locked nodes owned by the active actor remain selected and run the original lock math. Reused-actor locked nodes have no write at zero hand count and may be omitted. Keep full aggregate down after invalidation, evaluation and generic continuation; do not infer eligibility from player index.
- No E016 validity-state edit is needed. Evaluation always uses the original list; standalone continuation uses `None`; warm construction and lock updates choose E016's existing full-p0 variant as required. The optional list and spans remain immutable across graph replay and workspace swaps.
- `use_full_action_arenas` changes data offsets, not visited node membership; lists should remain node IDs and use the same updated node_data_off table. Isomorphic lists must contain exactly the existing representative nodes; no extra branches may be filtered on actor alone.
- Re-run raw device reach/learning equivalence against unfiltered full-sweep reference. Extend existing E016 lifecycle controls, adding proofs for mixed and all-uniform allocation branches, active/reused actor locks, both storage modes, compact/full plans, graphs/profiled/eval/standalone transitions, and capacity estimates versus observed payload. Confirm raw arrays before CPU compression and keep full immutable aggregate-list equality assertions. Do not compare uninitialized CFV scratch.

## Complete-cycle plausibility and prior counterevidence

E016's primary comparison reports **9762.0023 → 9360.5316 ms (4.1126%)** against E015, with exact full-state records. Rainbow/two-tone solve medians fell **4691.6807 → 4441.2760** and **2883.4139 → 2737.2679 ms**. Broader E016 qualification was still underway when this design began; this audit does not accept or deploy it.

The incremental screens support investigating repeated reach work further; they do not override E016's unresolved cumulative river regression. Removing roughly half the still-scheduled down-action CTAs is a plausible next bounded step, but the residual no-op cost is unmeasured. D020's old E004 host profiles rank down_action third and include per-launch waits; they are not an E016 device-time share. Do not multiply the CTA percentage by those spans to forecast a gain. Initialization cost, cache locality and retained metadata can erase any saving; the river remains a regression control even though its extra device allocation is avoided.

E005/E014 regrouped upward arities and added 12 training-up launches per flop iteration. Better register resources did not produce qualifying complete-cycle gains; E014 was 0.7888% slower. D027 differs materially: it removes semantically inactive CTAs, uses the existing kernel unchanged, adds no launch, and leaves the original upward array order unchanged. Those differences justify preserving the hypothesis, not acceptance. Preserve all failures and use the same frozen complete-cycle statistic, alternating cohorts, exact fingerprints/exploitability/iterations, 2% aggregate gate and repeated fixture-regression guard against the actual accepted baseline. If E016 is not retained, rebase the design and rederive the mode/work counts from E015; the current 48.69% estimate specifically assumes E016's two reuse modes and must not be transferred unchanged.

Independent source-only critique found no mathematical/dependency blocker and agreed with the all-uniform allocation avoidance, subject to pointer/span coordinate consistency and exact capacity accounting. The received critique is recorded in `independent-critique.md`; no runtime proof is claimed.
