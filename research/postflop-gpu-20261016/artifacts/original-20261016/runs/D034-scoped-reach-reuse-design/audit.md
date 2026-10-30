# D034: structurally scoped cross-iteration reach reuse

**Decision: NO-GO for implementation or timing now.** A general structural fallback is source-feasible. The available evidence does not justify choosing chance presence as a performance eligibility rule or predict preservation of E016's observed flop benefit. This is an independent hypothesis assessment, not a candidate, authorization, resurrection or additional timing extension of E016. D033 actual-device diagnostics are being pursued separately by the parent; their results were not available or assumed here.

E016 remains terminally rejected. Its original three cumulative pairs failed the river guard; the finite extension also failed the required pooled-nine river guard (+3.7093%, five of nine paired regressions >3%). The favorable new-six subset does not supersede that result. D028 retained all nine diagnostic runs and did not isolate the earlier discrepancy uniquely to E016 or E015. Its overlapping initialization ranges did not establish a graph-setup cause. Preserve all these records and their original dispositions.

## What source establishes

The archived E015/E016 mod.rs files and unchanged plan/kernel sources are copied under source/ and hash-identified in manifest.json. References below use those copies.

- E015-mod.rs:393–434 captures/instantiates two training graphs, full-p0 and within-pair-reuse1-p1, then replays them in order. E016-mod.rs:406–451 adds full-p0/reuse0-p0/reuse1-p1 variants and validity across complete ordinary pairs. The extra graph is captured from iterate, inside the registered solve stage, not the constructor/init stage.
- The numerical precondition is unchanged root0, regret0, locks, reach storage and tree metadata between the preceding p1 down and the next p0 down. It holds independently of whether the tree contains chance edges. E016's p1 up changes only player1 learning arrays. Chance presence is **not a correctness capability**; it can only be a possible cost classifier.
- E015-plan.rs:168–204 builds representative traversed chance edges; 243–300 flattens reached nodes and those edges into chance work lists. A topology predicate such as `!plan.chance_parents.is_empty()` represents actual selected-plan down-chance work. It is more faithful than board-string, fixture ID, node-count equality, or merely board-card count. It must be computed after the isomorphism choice and remain immutable with the solver's plan. It applies to arbitrary flop/turn plans, including future variants, without naming registered fixtures.
- Chance-bearing plans really have additional card-mask/chance reach work (E015-kernels.cu:124–140). E016's reuse0 mode skips player0 hand loops in copy_root/down_action/down_chance, but retains their CTA grids, metadata prologues and launch count. No source argument converts chance presence into elapsed-time savings.
- Prior structural counts show very different work scales: 70,623,857/43,140,954 avoidable actor0 hand visits per eligible registered flop iteration versus 1,398 for the registered river. These are post-observation counts from three fixtures, not a universal threshold, action-weighted operation count, bytes transferred or device time. The roughly 30% relative visit reductions across all three do not distinguish profitability.

## Feasible fallback shape, if independently justified later

A prospective policy could derive one immutable eligibility bit from the chosen plan. Keep E015's two existing graph slots and use an optional extra reuse0 graph **only for eligible plans**. Ineligible plans must enter the E015 ordinary/profiled dispatch: full-p0 plus reuse1-p1; never create, instantiate, launch or retain the third graph. Simply declining to replay the third graph after still capturing it would not preserve the intended fallback.

No additional kernel, device metadata buffer, CUDA allocation/upload, hand-count change or root copy is needed for eligibility. An optional host graph handle is sufficient. Warm construction must still start invalid; first nonzero-iteration capture cannot infer valid reaches. Locks must clear both common graphs and the optional one. Capture is not execution and never makes the cache valid.

This can preserve the E015 **numerical kernel sequence and two-graph topology** on terminal-street plans. It cannot guarantee identical compiled host instructions, struct layout, initialization timing or total runtime: a new dispatch branch/host state can affect generated code even when its additional GPU graph is absent. Do not call the river path cost-identical without measurements. Do not introduce a benchmark-sized threshold or discard the river from evaluation to obtain that claim.

A chance-bearing gate would be an explicitly narrower policy, not new reuse mathematics. The source can implement it, but the gate alone does not explain or fix E016's failure.

## Why the policy is currently unsupported

1. The only offered dividing line matches the observed success/failure partition of the three registered fixtures. It was proposed after the rejection; therefore those fixtures are development evidence for selecting the line, not independent validation of generalization. This does not make a structural policy inherently invalid, but it raises a real overfit burden.
2. A tiny turn/flop plan can contain chance edges while exposing little removable device work. A large terminal-street menu can expose substantial actor0 work without chance edges. Isomorphism, hand counts, action arity/locks, chance fanout, number of levels and retained iterations all change the balance. Chance presence is a weak, unvalidated cost proxy.
3. Reuse frequency depends on evaluation, lock/root updates and standalone sweeps. The frozen check_every20 behavior is not a production-wide guarantee. A constructor topology bit alone cannot know how many consecutive valid ordinary pairs will amortize an extra graph.
4. D028's river initialization differences are outside the newly added training-graph capture stage. They cannot justify saying that removing the third graph will remove the measured river regression. Source changes can influence other behavior, but no causal chain was demonstrated.
5. Favorable E016 flop solve spans remain useful evidence for the mechanism, not an accepted domain-wide result. A new wrapper must earn its own unchanged complete-cycle/fixture qualification. It must not reuse old E016 repetitions, favorably combine subsets, or seek another extension of its terminal cohort.

## Minimum evidence before choosing a candidate

First inspect D033's actual device interval evidence under its stated diagnostic boundaries. It may locate removable downward work; it does not by itself measure a gated implementation's speed, graph setup, host dispatch or generalization. Keep profiling overhead and normal captured execution distinct.

If that evidence supports further study, prospectively state a policy and a small independent design/validation matrix before any new performance screen. Include tiny and large chance-bearing plans, tiny and large terminal-street action plans, turn and flop roots, iso off/on and narrow/broad hand counts. Use plans not selected for favorable E016 timings. A cost hypothesis should relate removable work over consecutive eligible iterations to extra capture/instantiate/host costs; no coefficients, threshold or minimum iteration count are justified by the current source audit. Do not derive them from the frozen stopping iteration or tune a threshold until the registered river falls on the desired side. Any later timing/candidate requires separate parent authorization; this audit authorizes none.

If a later policy survives independent evidence, retain all three primary fixtures and unchanged aggregate and repeated-fixture guards, plus fresh original-baseline cumulative comparison and all prescribed exact controls. Old failed and diagnostic cohorts remain excluded from new acceptance statistics and remain fetchable with their original labels.

## Exactness/lifecycle obligations remain intact

Eligibility is not validity. Eligible plans still require every E016 invalidation rule: consume validity before fallible ordinary/profiled iteration work; set true only after the complete ordered pair queues; invalidate at exploitability entry even for cached eval-graph replay, direct eval_down, standalone p0/p1, continuation entry before root upload/validation, and lock update before waits/uploads. Successful readback does not mutate the state, but an asynchronous error must not be treated as safely recoverable cached training. The cache flag is not partial-iteration recovery.

For eligible and ineligible plans independently compare raw reach/learning bits against the unchanged full/E015 reference through first eager iteration, warm first capture, replay, mixed profile/graph calls, eager/cached evaluation, both actors' locks, root changes and standalone sweeps. Ineligible plans need an explicit check that no optional graph is captured or instantiated; graph-count inspection is warranted for this stated resource boundary, while numerical results prove state behavior. Keep real hand counts, upward work, arithmetic/order, 128-thread launches and storage/stop settings unchanged.

Continuation wrappers privately construct fresh solvers and use the full bridge rather than ordinary iterate. Preserve that ownership boundary and test actual changed-root, paging and stored-workspace paths; never infer cache validity merely because a wrapper alternates player indices. Full/compact/F32/compressed, generic menus and saved/resumed states still need immutable-reference validation. Existing E016 exactness is historical evidence, not proof of a new branch policy.

Independent peer critique (menu_change_review) agrees: chance-bearing work is real but does not quantify removable cost or amortization, correctness is independent of chance presence, and a tiny-turn/large-river counterexample defeats a universal cost gate. Peer recommendation is NO-GO now pending actual device/setup evidence and independent holdouts.

No production edit, build, GPU execution, test, timing, dashboard mutation or candidate implementation occurred. Only this additive source-only design artifact and source copies were created. E016's sealed evidence was neither changed nor reclassified.
