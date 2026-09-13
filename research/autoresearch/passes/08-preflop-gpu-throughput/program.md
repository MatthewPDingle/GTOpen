# GPU preflop throughput autoresearch

Continue the user's performance goal with the experiment/measure/keep-or-discard
loop described at https://github.com/karpathy/autoresearch. This adapts the loop
to the existing Rust/CUDA solver; it does not install or run its LLM trainer.

## Objective and fixed evaluation

Improve complete GPU preflop solve time without changing the mathematical
problem, particle count/order, precision, betting menus, policies, stopping
targets or learning rules. CPU performance is excluded. A kernel speedup is
only a diagnostic until matched complete-iteration/check measurements improve.
Large-game convergence quality remains unqualified in pass 07; do not count
faster execution of inaccurate output as resolving that outstanding goal.

Baseline source is ae10c1d6dc6cf3286528917be510d99fe8def625. Production port
56708 stays read-only. One build/test/GPU workload at a time. Reuse pass 07's
live-status guard, process ownership, immutable inputs and time caps. Preserve
failed trials. No new ten-hour deadline is inferred from this follow-up.

## Loop

1. State one mechanism and bounded screen before running it; check earlier
   rejections to avoid repeating unchanged ideas.
2. Prove numerical/state invariants on adversarial fixtures. Prefer exact
   terminal and whole-arena agreement; any changed rounding needs separate
   trajectory and conditional-quality validation before acceptance.
3. Measure alternating control/candidate runs, same saved state and work.
   At least three pairs for retention; require >=3% median end-to-end benefit
   on a target large fixture with no material regression on the other fixture.
   Record cold initialization, warm iteration, check, synchronization, memory,
   executable/source/input hashes and complete outputs. Count setup costs.
4. Keep verified improvements; otherwise revert only the candidate code while
   retaining evidence. Full default solver and native GPU equivalence suites
   are required before a retained code change is recommended.
5. Commit and push research results; no live deployment by this loop.

## D01: exact distribution duplicate inventory

Earlier static reach-source keys had no duplicate equity tasks within a
traverser. They do not answer whether distinct current reach vectors normalize
to identical 169-float distributions. Count exact bitwise duplicates after
the existing GPU normalization, with full equality after hash lookup.

Inspect immutable small and large native saves, current and average policies,
all traversers. Do not advance learning. Use the current prepare mask even for
average inventory to distinguish positive counterfactual terminals from work
the ungated evaluator schedules. Include folded-opponent probability in the
mask and never prune for zero own reach.

Count active CDF slots, exact unique distributions, positive multiway terminal
tasks and exact unique ordered opponent-distribution tuples. Preserve opponent
order and multiplicity; pot/investment/probability are not reusable equity
work, so this is only a potential reuse count. It is not measured speed.
Keep both unweighted and opponent-count-weighted terminal counts.

Add a synthetic classifier test including single-bit differences, duplicate
vectors, hash collisions, order and multiplicity. Verify the GPU diagnostic
leaves all learning arenas and iteration unchanged. Cap each saved inventory
at 180 seconds and require normalized scratch <=1 GiB. Reject this direction
if mature large-state counts show neither 20% CDF duplicates nor 20% weighted
terminal duplicates. A survivor admits a separately designed device-side
implementation, not a speed or convergence claim.
