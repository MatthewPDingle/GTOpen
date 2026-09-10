# Exact terminal equity reuse: design assessment

Proposal only. No active worktree edits, builds, benchmark execution, GPU work,
or server access were performed for this assessment. Source inspected:
`target/autoresearch/preflop-20260910/crates/solver/src/preflop/{gpu.rs,kernels.cu,mod.rs}`.

## Recommendation

**Defer the cache: measured eight-seat counts show no same-traverser reuse.**
The parent ran the optional source-key diagnostic after this design assessment;
its results confirm that exact grouping saves no learning-sweep terminal work
on that fixture. Frozen cross-traverser checks have some duplicate work, but
preserving per-batch arithmetic imposes a large storage cost. Do not deduplicate
by pot size, live mask, position or ranges that happen to look similar.

Existing eight-seat worklist instrumentation gives 602,914 multiway terminals,
2,362,251 live terminal/traverser tasks, and per-seat task counts:
249947, 262422, 275567, 288871, 301587, 312687, 343929, 327241.
The later `../../key-stats-eight.json` records 2,118,535 unique keys across the
frozen-check union. Every traverser separately has zero duplicates. Cross-seat
reuse could remove 243,716 tasks (10.317% of live terminal tasks), across158,508
duplicate groups, maximum multiplicity6. At batch32, retaining all exact batch
sums for these groups costs3,428,845,056 bytes (3.43GB), before maps/activity
and scatter work. That buys at most a fraction of average-check terminal work,
not iteration work or all check time. The parent therefore deferred reuse.

The diagnostic took304.01ms, with103,939,044 bytes of dominant temporary record
payload (103.94MB; not measured RSS). These measurements were produced by the
parent's scheduled run, not a hardware job by this proposal author.

## Safe mathematical key and lifetime

For terminal `t`, live traverser `p`, construct the ordered vector

```
[reach_src[t, q] for q = 0..np, q != p and live[t] contains q]
```

The vector length encodes opponent count; retain original ascending seat order.
Each source ID is global within this immutable tree, so it already identifies
its player. Store original source IDs, not compact CDF slots: compact slots are
different for each traverser. Hash collisions require full vector equality.
An empty or padded fixed-array key must include the length (source 0 is valid).

This key identifies the **unscaled 169-hand batch sum**, conditional on a fixed
reach snapshot, fixed particle table, fixed batch boundaries, and fixed direct
versus normalized CDF path. Pot, investment, folded-opponent reaches, hero reach
and terminal probability do not enter this sum. They still enter each original
terminal's counterfactual payoff/gating and cannot be reused as a whole value.

Clear/recompute after every down sweep. Learning sweeps update regrets between
players, so a matching source tuple from player p's sweep is not a valid cache
entry for player p+1. `queue_evaluation` does one `down(1, -1)` before all seats;
only within that check is cross-seat reuse valid. Invalidate on the next check,
including checks after solve iterations or profile changes. Static mappings
can live with the GPU object, but computed values cannot outlive the snapshot.

Do not sort opponent sources to increase hits: floating products currently
follow player order, and reordering changes bits. Do not merge distinct source
IDs merely because normalized reach vectors presently match: equality can stop
holding after learning, or even change between the direct and normalized path.

## Why same-seat hits may be absent

`reach_sources` gives every action edge a globally unique actor reach block
`np + child - 1`. Other players inherit their nearest preceding action source.
Consequently different action histories normally leave at least one different
live-opponent source. A later matching action label does not merge histories.

At two different leaves, consider their first diverging action. If its actor
is a retained live opponent, its final source must differ. If the actor is the
traverser or a subsequently folded seat, retaining the same live-opponent
sources requires all further actions to avoid those opponents. A genuine raise
reopens their action (`next_state_of`); the only continuing non-raise choice is
call/check (`legal_actions_of`). With equal stacks, an opponent already all-in
has reached the common maximum, leaving no legal larger raise. This strongly
restricts same-seat duplicates. Treat zero duplicates as a prediction to check,
not a measured invariant or a reason to remove the equality check.

Cross-seat duplicates have a simple possible construction: live players A/B
finish acting, then C calls and D folds in one leaf; C folds and D calls in
another. For hero C in the first and hero D in the second, the ordered opponent
sources can both be exactly [A_source, B_source]. Hero identity itself does not
change this model's all169-class conditional sum. This sharing is useful only
where reaches are frozen across the two traversers (average checks).

## Preserve the existing floating computation

Current terminal work computes, separately for each particle batch:

```
sum_b = pf_multiway_sum(... all particles in batch b ...)
increment_b = prob * pots[t] * sum_b / float(samples)
value = increment_0 - prob * invested[t,p]
value += increment_1; value += increment_2; ...
```

Caching final `equity = sum(all batches) / 1024`, then applying pot/probability
once, changes rounding and possibly CUDA contraction. It is mathematically
equivalent but violates the exact-arithmetic candidate boundary. Instead cache
the exact f32 `sum_b` before scaling, then execute the same original expression
and batch-add sequence for every member terminal. Keep source order, Gauss rule,
particle count, loop order, batch size, and normalization path unchanged. Do not
derive one terminal from another by a pot or probability ratio.

The prepare pass must mark a group active if **any** member terminal has positive
counterfactual probability; selecting the first representative's probability
is unsafe. Hero-zero reach does not imply zero counterfactual payoff. All-zero
groups can skip their sum but each member must still get its ordinary first-
batch zero write; stale cached sums must never be read when a group becomes
active again. Gate-disabled evaluation needs the full live set.

## Candidate designs and memory

1. **Same-seat, one-batch group sums.** Build per-seat groups with at least two
   members; singleton terminals keep the original path. Compute `sum_b` once per
   duplicate group and scatter its scaled payoff to members in each batch.
   Added scratch is `duplicate_groups_max * 169 * 4` bytes, plus membership/key
   metadata and activity flags. Two launches instead of one for duplicate work,
   and extra sum writes/reads. If no groups repeat, allocate nothing and use the
   existing kernel. Even a small positive hit rate may not cover overhead.

2. **Cross-seat evaluation cache of batch sums.** Preserve existing per-seat
   up/BR scheduling by caching every batch's unscaled sums for duplicate groups
   until their last traverser consumes them. At batch32 this costs
   `duplicate_groups * 32 * 169 * 4` bytes: 21,632 bytes/group, or 216.32 MB for
   10,000 groups. Batch1 costs 692,224 bytes/group. A last-use lifetime plan can
   reduce peak storage; eager production of all groups can increase it.
   This must not shrink the existing CDF batch or disable normalization/HU cache.

3. **Evaluation batch-major scheduling.** Compute each batch's global groups and
   scatter to persistent terminal values for every traverser before any up sweep.
   One-batch sums suffice, but terminal storage is then per-live-task instead of
   shared per terminal. The eight-seat task count above implies 1,596.88 MB for
   all task vectors (676 bytes/task), before group scratch/maps. Existing terminal
   vectors may offset part of that allocation. This is a broader storage/graph
   change and is not recommended as the next quick experiment.

For reference, storing one 169-float sum for every task of the largest eight-
seat traverser would be 232.50 MB. This is an upper bound without deduplication,
not a proposed mandatory allocation. All planning arithmetic must be checked.

Any cache should be optional performance-only: compare its extra bytes against
the already chosen compact/normalized CDF plan and optional HU cache. Enable only
if those choices and batch boundaries remain identical. Minimum-budget solves
must retain their existing exact path; never fall back to another payoff model.

## Count-only next step

The companion `counting-plan.md` specifies a read-only planning experiment.
Run it inside the existing build/planning stage when the parent next compiles,
not in a new GPU benchmark. Report both per-seat and frozen-evaluation union
counts; cross-seat counts alone would overstate learning-iteration savings.

Only proceed to implementation if measured **duplicate group multiplicity and
active-member coverage** justify the extra memory traffic and launches. Current
phase timings show the coupled terminal phase is material, but they establish
neither duplicate reuse nor a speedup for this design.

## Required verification if implemented

- Key tests: same ordered live-opponent sources match despite differing pot,
  investment, hero/folded reaches; reversed source order and distinct source IDs
  do not match. Both zero and nonzero valid source IDs must work.
- Compare group results with original terminal writes bit-for-bit for every
  hand; different pots/rake/investments/probabilities must share only `sum_b`.
- Representative probability zero while a later member is positive; all zero;
  positive-zero-positive with poisoned scratch; hero reach zero; folded-opponent
  zero; gate on/off; tied ranks. No approximate activity threshold.
- Batch32/7/1, direct minimum-memory path and normalized compact path, 3/6/9
  players, mixed forced/live profiles, folded traverser's ordinary values.
- Same-source IDs across successive learning/down calls with changed reaches:
  ensure invalidation, including eager and captured evaluation graph replay.
- Verify learning arena hash, all gaps/EVs, and full terminal snapshots exactly,
  not only action-frequency tolerances. Keep the existing CPU parity checks.
- Budget edge tests preserve batch, direct/normalized choice and HU cache;
  no-duplicate plan must use the old kernel without runtime overhead.
