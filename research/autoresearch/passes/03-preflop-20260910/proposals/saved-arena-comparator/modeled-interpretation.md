# Modeled iteration-6 batch-30 versus batch-32 interpretation

Evidence: `raw/saved-comparator-modeled-a.log`; native headers and a few reported outlier arena entries were inspected read-only. Original uses the original implementation plus common forced-policy budget accounting at batch 30. Optimized uses compact/normalized storage at batch 32. Both have five Ignition adaptive profiles, BTN on Solver, six iterations, no frozen seats/hero/point locks.

## What the report establishes

861,384 action nodes / 145,573,896 node-hand classes / 311,892,711 action-hand entries were compared. All compared values are finite, with no invalid effective probabilities or current-reach classes. 94.7782% of effective entries match bit-for-bit. Mean class total variation is 4.9421e-8; decision-reach-weighted TV is 1.33306e-8 from either reference state. These are descriptive global summaries, not conditional guarantees or EV-loss bounds.

The largest conditional difference is real: BTN J4s fold changes from 21.62046% to 49.82775% (28.20729 percentage points), with the complementary call change. It occurs at node 361525 on path [1,0,1,1,2,0,1,1,3,1,1,3], with current factorized class reach about 1.44349e-12.

**This is not the average-strategy uniform fallback.** Its accumulated masses are about 1.901838e-5 and 1.901836e-5, well above the existing 1e-12 denominator cutoff. Their totals barely differ, but mass is redistributed between actions. Zero accumulated-mass classes are exactly identical in both runs. Moreover, eight action entries above one percentage-point difference have accumulated mass above 1e-3; that stratum's maximum is 19.78022 percentage points. Tiny current joint reach is not synonymous with zero/unlearned own strategy mass.

## Reach strata (same bin in both states)

These are observed maxima within the report's descriptive bins, not accepted tolerances.

| Current factorized class reach | Classes | Maximum absolute frequency difference | Percentage points |
| --- | ---: | ---: | ---: |
| Exactly zero | 84,055,032 | 2.98023e-8 | 0.00000298023 |
| (0, 1e-15] | 2,404,386 | 0.176196 | 17.6196 |
| (1e-15, 1e-12] | 20,700,093 | 0.233991 | 23.3991 |
| (1e-12, 1e-9] | 32,445,344 | 0.282073 | 28.2073 |
| (1e-9, 1e-6] | 5,762,434 | 0.00145790 | 0.145790 |
| Above 1e-6 | 206,603 | 0.0000444353 | 0.00444353 |

Four individual classes move across adjacent small-reach bin boundaries; their action differences are zero. All 78 action-hand entries with differences greater than 0.01 have reach at most 1e-9 in both states. There are 2,949 entries in (1e-4, 1e-2]. Counts are action-hand entries, not independent hands, decisions, observations or users.

The small reach weights explain why global weighted summaries barely move. They do not prove that displayed conditional policies are interchangeable, locally near-optimal, or safe to carry into a differently conditioned scenario.

## Plausible mechanism; what is and is not proven

Read-only scalar inspection at iteration 6:

- J4s original regrets: fold -1.63425e-12, call +1.34049e-12; candidate: fold -8.15348e-13, call +1.55994e-12.
- 94o node 124041 original regrets: fold +2.34381e-12, call -5.05107e-12; candidate: fold +2.73008e-12, call -5.04397e-12.

These are on the scale of the existing current-strategy positive-regret-sum cutoff (1e-12). Small changed terminal accumulation can therefore plausibly change earlier regret-matching decisions and leave a large difference in the average mixture. At iteration 6 both J4s current positive sums are above the cutoff and favor call, so this snapshot alone does NOT prove a cutoff crossing or identify the first divergent update. Some other outliers have larger current regrets. Do not reduce the explanation to a single asserted threshold event without a trace.

## Bounded next gates, in order

1. **Matched batch 30 exact control first.** Same native initial state, model artifacts, source-specific implementation and 23 GB budget; force only the optimized diagnostic accumulation batch to 30. Require the already-defined exact full arena/effective policy/gap/EV checks. If a difference remains, stop attributing it solely to batch grouping and locate the first differing stage before acceptance.
2. **Production compatibility planner candidate.** Derive the original union planner's B using the same corrected forced-memory accounting, but store compact CDFs at that B when physically feasible. Preserve original HU-cache mode initially. Make normalization optional at the required B; do not silently shrink or enlarge B to retain normalization. This retains the original arithmetic grouping where the old planner had a supported GPU path. Test 19/21/23 GB and existing all-solver controls before claiming compatibility.
3. **Same-target and shared-iteration long-run checks.** Keep established accuracy target/cadence unchanged. Record actual first-target iteration/time for each path, and save both at common checkpoints for valid same-iteration comparison. If target iterations differ, do not defeat comparator header checks to compare unlike states. Verify conditional strata do not hide new divergence in the compatibility path; reach-weighted means alone are insufficient.
4. **Only if batch-changing behavior remains under consideration:** audit a bounded set of conditional outliers: J4s node361525, 94o node124041, HJ Q6s node249394 (reach5.86e-10), and CO22 node1186349 (accumulated mass0.001525). For each, compare branch action values under a common fixed continuation/range state. Record raw counterfactual values and values divided by positive opponent reach mass, not by the actor's own hand reach. Report undefined if mass is zero; do not add an epsilon denominator. Measure the two policies' conditional value difference under both frozen continuation references. This can determine whether the local mix difference lies between effectively tied actions; global gap does not establish that. These are deep, small subtrees and can be bounded without a whole CPU solve.
5. If mechanism tracing is needed, log only those nodes' per-action regrets/current sigma/strategy sums at each of the first six updates, before and after discounting. A tiny targeted GPU readback is preferable to creating twelve multi-gigabyte saves. Compare the first divergence against common-state terminal values and the existing positive-regret-sum cutoff. Do not tune the cutoff or relax tolerances as part of a performance pass.

Recommendation: do not accept the batch-changing default on weighted means alone. Prefer preserving the established batch grouping where feasible; classify newly fitting layouts separately and retain all original model/accuracy gates.
