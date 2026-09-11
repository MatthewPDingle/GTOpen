# Selected-branch refinement: feasibility and smallest safe experiment

Recommendation: evaluate a **separate conditional CPU solve on an owned snapshot first**. The engine already has an arbitrary-node traversal and path-conditioned ranges. It does not have a supported rerooted solver, custom GPU root ranges, or native persistence for such a game. A production compact GPU subtree/UI overlay is beyond a small safe change in this four-hour loop. No implementation or hardware work was performed for this design.

## What is already available

Paths below are relative to the interactive research worktree; line numbers refer to the inspected source.

| Primitive | Location | Use/limitation |
|---|---|---|
| `walk(path)` | `crates/solver/src/preflop/mod.rs:2006` | Returns the selected node and all original seats' class masses under average/forced policies. It starts from class probabilities and multiplies the chosen historical actions. |
| `node_view(path)` | `mod.rs:2148` | Supplies readable action/history and unreachable/unlearned notes; use those to reject an unsupported conditioning path. |
| `traverse(node,p,reaches,mode,depth)` | `mod.rs:1730` | Existing CPU CFR/average/BR recursion can start at any descendant. Descendant-only writes already follow disjoint-tree ownership. Private method; a research-only wrapper in a child module can use it. |
| `traverse_checkpoint(...)` | `mod.rs:3555` | Existing paired local BR/average evaluator also accepts an arbitrary node and input ranges. Local per-seat dot products must use the normalized arriving range, not `class_prob`. |
| `forced_sigma(node)` / `seat_static` | `mod.rs:909`, `1899` | Preserves point-lock precedence, frozen averages, profile policy, adaptive thresholds and hero semantics. These must remain in force in the conditional game. |
| `terminal_value` | `mod.rs:1617` | Existing full coupled-deck multiway values, calibrated HU values, folded-player losses, rake and invested accounting can be reused unchanged. |
| Local conditional action-value audit | `preview_quality.rs:178` onward | Already extracts arriving ranges and divides out current opponent mass; can compare before/after action loss on fixed reference ranges. It is a one-action-deviation diagnostic, not a new local equilibrium solver. |

`current_strategy` and `average_strategy` use an absolute1e-12mass floor (`mod.rs:892,1567`). Global regret updates are also multiplied by the other seats' reaching mass. A rare branch can therefore contribute little to the global gap and receive weak numerical learning. Removing the probability of the history from the conditional game is reasonable; inventing positive support for an impossible history is not.

## Conditional game definition

1. Freeze the source published snapshot, model ID, full typed config, profiles, locks, source iteration and exact action path. Reject a path with an unlearned ancestor or a zero-total arriving range. Do not use epsilon pseudo-observations to create a range. Extremely tiny positive masses require an explicit diagnostic rather than silently treating the branch as measured.
2. Obtain each seat's raw class-mass row with `walk`. Normalize **each original seat's** row to unit sum, including folded seats. `terminal_value` multiplies masses for all other seats, even folded ones; retaining an unnormalized folded seat would accidentally retain the history-probability penalty. Folded seats keep their accounting and contribute a unit chance factor; their actual class distribution is not used as card-removal evidence by this independent-class engine.
3. Keep all original positions/posts/ante/stack, invested amounts, pot, live mask, aggressor, raise depth, ever-raised mask, action menus, buckets, realization weights and model payload. The remaining stack is already derived from original stack minus investment plus ante. **Do not treat current investments as new blinds or reset the pot**, and do not drop/reindex folded seats: profile routing, limper detection, position calibration and all-in accounting depend on the original seat/config context.
4. Optimize only learning actors with decisions inside the subtree. Preserve every forced policy and frozen average. Reset learnable descendants' regrets/strategy sums for a clean local run; keep a distinct local iteration counter and local discount schedule. Reusing old globally weighted sums and calling the run fresh would blend incompatible weights. A future warm start needs separately validated rescaling.
5. Evaluate a conditional gap in bb per occurrence of the selected history, using normalized arriving hand weights. Report each learning seat separately and the same configured model. A small global gap is not a local convergence certificate; a small conditional gap still does not validate the model against physical poker outcomes or imply multiplayer Nash guarantees.

For the research prototype, retain an owned full-tree snapshot in memory, but traverse/discount only the selected descendants. This avoids node/lock remapping and allows exact outside-subtree preservation checks. It saves traversal time but **not** the initial full-tree memory/load cost. The parent live solver is never modified. Full `try_iterate()` is unsuitable: it starts at node0 and discounts all arenas. Similarly, full `gaps_and_evs()` uses full prior weights.

## When an even cheaper answer is possible

If every opponent policy at every descendant is fixed (forced or frozen), the selected actor's best response is a backward dynamic calculation. Existing BR traversal computes values; a small research extension could retain maximizing action choices and directly construct a response policy. That is an exploit against fixed continuations, not a joint solve. Do not assume measured profiles are fixed: default `adaptive_from` deliberately releases opponents to learn at large raises. `set_hero` already rejects active adaptive opponents (`mod.rs:1352` onward). Switching those opponents to frozen just to obtain a fast answer would change the requested model and requires an explicit separate mode.

## GPU work required for a true compact conditional solve

The current GPU constructor plans the whole tree (`gpu.rs:131` ValuePlan; `reach_sources` around198; constructor around756). `pf_init_root` always writes `cprob[k %169]` for every player (`kernels.cu:58`). `down` reinitializes those priors every sweep (`gpu.rs:1154`). Root EV/gap dot products also use the unconditional class prior (`gpu.rs:1494` onward).

A correct compact engine would need:

- Copy descendants in parent-before-child order, remap child indices, action/arena offsets and point-lock node IDs, and preserve all original node/accounting/profile fields. `PNode` is not currently Clone. Original config alone cannot recreate the conditioned root: `BuildState` additionally tracks `needs`, last raise, all-in seats, limpers/callers and next actor (`mod.rs:258`). Copying existing descendants is safer than guessing those fields from a visible node.
- Explicit immutable per-seat root-range payload, separate from the global class-probability buffer; upload it on every GPU down sweep and use it in conditional per-seat gap/EV reductions.
- Initialize only the compact subtree arenas and frozen/forced policy blocks; replan HU/CDF caches and budgets. Fresh capture/graph ownership is required after extraction. Existing cached graph addresses cannot be repointed to a new tree.
- A new conditioned-root representation and explicit persistence schema; meaningful CPU/GPU tests must cover the same normalized range payload. This is not a query-only patch.

## Save/publication risks

Current native load rebuilds the **entire original tree from config**, then reads arenas (`save.rs:211` onward). Saving compact arenas with the original config would be invalid. Saving a modified full tree as if ordinary global iterations had advanced would also misrepresent its learning history.

Use an ephemeral branch result or a separate research artifact first: source native hash, publication iteration, full reference/fast model IDs, exact path/action descriptors, original and normalized arriving ranges plus hashes, profile/lock hashes, local iterations/gaps and policy vectors indexed by source node ID. Branch policies may be used only for navigation/export inside that frozen branch. Display “Refined for this history; prior ranges fixed at iterationX; full-reference conditional solve” (or the actual fast model). Preserve inherited range approximation provenance.

A later overlay must invalidate when the source snapshot/path/model/profile/lock changes. It must not silently overwrite parent arenas or claim parent/global convergence. The exported Setup spot must combine the frozen prefix reaches with refined descendant policies, with one coherent generation; the current ordinary `/export` route cannot do this automatically. Changing downstream play can make upstream strategy nonoptimal, so merging requires a separate full-game refinement design and remeasurement.

## Bounded experiment for this loop

Freeze at most three selected paths before outcomes: one common HU decision, one rare but positive-reach HU decision, and one small three-player decision. Include one all-solver case and one modeled/frozen case if already present in the small quality fixtures. First count descendants/terminal types with pure tree walking; cap each at500actionnodes/1000terminals and the complete CPU experiment at120seconds. Large multiway1024particle CPU subtrees may fail that budget; record refusal/timeout rather than expanding the scope.

On each owned snapshot, record the starting conditional gap/action-loss audit, source masses and range support. Run fresh local refinement for2/10/30/100iterations subject to the time cap, evaluating only planned checkpoints. Compare to continuing the same number of global iterations on the **small** fixture if an already scheduled reference provides that control; do not schedule a large extra global solve. Measure time to a predeclared conditional gap and fixed-reference action-loss reduction, including worst relevant hand tails. Never select paths after seeing the improvement.

Required pure/correctness gates before any useful-quality claim:

1. With no local updates, normalized local value equals the source subtree value divided by the source opponent mass, up to the existing CPU f32 rounding tolerance; all actions and terminal accounting remain identical.
2. Multiplying each input reach row by a positive constant before normalization leaves the resulting local game unchanged; zero rows reject. Own zero-support hands stay zero support.
3. Forced/frozen policies, original config and every arena element outside selected learnable descendant blocks remain exact. Point-lock precedence and adaptive-profile release are unchanged.
4. Local BR/gap reduction uses the correct normalized own range and excludes static/folded actors from the learning gap. Constant folded losses/rake accounting remain correct.
5. Local result can be discarded without changing the source native/header/arenas; no ordinary save/load path is repurposed.

Proceed to compact GPU extraction only if this small conditional experiment improves relevant rare-branch quality within a useful latency budget. For this loop, the existing early-publication API and explicit fast-model qualification are closer to a reviewable product change; targeted conditional refinement is a justified next experiment, not yet an implementation-ready feature.
