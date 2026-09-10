# Paired CPU checkpoint: concrete design and test plan

Proposal only. This is intentionally not bundled into either allocation patch.
No implementation/source changes, compilation or benchmarks performed here.

## Current exact reference

`gaps_and_evs` parallelizes players, then calls existing `traverse` twice for
each player: `br_mode = if constrained_br(p) {3} else {2}`, and mode1 average.
Mode1/2/3 all select the same forced/average sigma and never mutate regrets or
strategy sums. Their downward reach vectors are the same for any node that
both visit. A terminal's calculation has no mode argument and excludes the
traverser's own reach from its counterfactual mass. Therefore it can be shared
between these two outputs for a fixed node/player.

Retain the old two-call body as a `#[cfg(test)]` reference helper; do not replace
the reference with another paired computation. Use its exact result as oracle.

## Suggested method boundary

Add a dedicated read-only method rather than changing learning traversal:

```text
traverse_checkpoint(node, p, reaches, br_mode, needs, depth) -> EvalPair
needs = {best_response: bool, average: bool}
EvalPair = {br: Vec<f32>, avg: Vec<f32>}
```

Initially retain the current Vec result shape to isolate evaluation reuse from
an unrelated stack/arena rewrite. A later allocation change can be separate.
Root requests both results. Missing outputs contain positive-zero169 vectors,
exactly matching existing pruned-child return vectors.

At a terminal, call `terminal_value` once if either output is needed, and copy
the169 f32 values only if both outputs are needed. Never prune on own reach.
At an action node, obtain forced status, frozen status and owned sigma exactly
as current evaluation modes do. `br_mode` remains2 or3 for the whole player.

## Distinct skip masks are mandatory

Reproduce the existing `self.prune && na>1` test independently for each output.
For the average output, an action is skippable if its sigma is zero for all169
classes. For BR, that same skip applies except the traverser's own actions may
not be skipped when:

- br_mode2, including frozen or point-locked own nodes; or
- br_mode3 at an own node with no forced sigma and no frozen seat.

Pass `needs.br && !skip_br[a]` and `needs.avg && !skip_avg[a]` into the child.
If neither output is needed, return the zero pair without descending.
Do not replace this with one shared "reachable" flag, nor use computed BR
child values as average values when average would have pruned that branch.
For individual hands with zero sigma in a non-pruned action, retain the old
multiplication/addition rather than adding a new per-hand shortcut.

The actor reach scales by the same sigma and is restored as in current
traversal. At parallel fan-out, each action still receives its own reach copy.
Collect results in action-index order using the same indexed Rayon iterator.

## Upward combination table

| Node/output | Combination |
|---|---|
| Actor is not p, either output | Add child values in original action order; opponent sigma is already in reach |
| Actor is p, average | Sigma-weighted child sum in original action order |
| Actor is p, br_mode2 | Max child BR value starting at f32 negative infinity, regardless of frozen/forced policy |
| Actor is p, br_mode3, no forced sigma and not frozen | Same max |
| Actor is p, br_mode3, forced or frozen | Sigma-weighted BR sum |

This intentionally preserves the distinction between unrestricted bleed for
fixed/frozen players and the adaptive model's constrained gap. Point locks
still supply sigma; whether BR may deviate from that sigma is determined by
the same mode2/mode3 condition, not a new blanket rule.

At root preserve the **existing CPU aggregation literally**:

```text
g += class_prob(h) as f64 * (br[h] - avg[h]) as f64;
v += class_prob(h) as f64 * avg[h] as f64;
```

The subtraction occurs in f32 before promotion. Replacing it with separate
f64 dot products and subtracting afterward changes rounding and is outside
scope. All local products/sums and quadrature precision remain unchanged.

## Cancellation and memory limits

Check the existing stop flag at the same fan-out depth boundary before
descending, returning zero pairs. A pre-set stop must match the old result.
No learning arena writes are allowed under any stop condition. Exact bitwise
agreement under an asynchronously raised stop cannot be promised: the old
method completes part/all of BR before starting average, while the paired
method interleaves them and visits fewer nodes. This is a timing-dependent
partial-result behavior already present; document it explicitly. Ensure the
caller does not publish a stopped partial checkpoint as a completed result.
If that distinction is unacceptable, propagate a canceled marker and retain
the current public cancellation contract deliberately before adoption.

The pair doubles live child-result payload versus one old traversal, although
it avoids a second traversal and duplicate reaches. Peak recursive/Rayon
frontier memory must be measured; it is not automatically lower. Avoid a
persistent per-terminal cache: at676 bytes per result and805,640 terminals,
that would be about544.6MB per player before metadata. Do not cache across
learning sweeps or solve iterations.

## Focused regression matrix

1. **Reference parity at every stage.** On identical solver state, compare
   paired root br/avg arrays for every player to existing `traverse` mode2/3
   and mode1 arrays by f32 bits. Compare final gap/EV f64 bits too. Snapshot
   full regret and strategy arenas before and after each checkpoint; unchanged.
2. **Reachable and pruned branches.** Run with pruning both on and off, at
   iteration0 and after several actual learning updates. Include sparse
   average sigma with entire zero actions and mixed per-hand zero entries.
   A zero-own-reach branch must remain available to unrestricted BR.
3. **Model/rules.** Small2-seat HU,3/4-seat coupled and legacy-product games;
   calibrated HU with chips behind and all-in terminals; raked/fold-win paths.
   Keep all1024 coupled samples, not a reduced-sample test fixture.
4. **Policy semantics.** Adapt setups from existing tests:
   `frozen_seat_stops_adapting`, `point_lock_roundtrip`,
   `frozen_average_survives_hero_cycles`,
   `adaptive_profiles_learn_large_responses_and_preserve_locks`, and
   `adaptive_gap_respects_fixed_actions_instead_of_reporting_their_bleed`.
   Cover fully ruled seats, frozen seats, hero exemption, adaptive learned
   versus forced nodes, and point locks at root/deeper nodes.
5. **Invocation proof.** Test-only terminal counter or trace on a small
   pruning-disabled fixture verifies shared terminals are evaluated once
   per node/player rather than twice. The counter must compile out of
   production. Require output parity as well; call count alone is inadequate.
6. **Parallel and cancellation.** Compare single-thread and normal Rayon
   execution, each against its existing reference. Pre-set stop returns old
   zeros and no arena changes. A controlled mid-run stop terminates cleanly,
   does not publish a completed checkpoint, and permits subsequent normal
   evaluation to match reference after the flag is cleared.

After these gates, use frozen CPU3/4/6 and whole9 fixtures, reporting checkpoint
wall time separately from learning-iteration time and peak memory. Iteration
timing should be unaffected; any change there suggests a confound. Compare
at the same saved state and same gap target. Exact clean423 baseline outputs
remain the acceptance oracle. This larger change merits an independent commit
and can be deferred if the remaining research window is too short for these
checks.
