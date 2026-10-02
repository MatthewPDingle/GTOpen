# Expected targets for later preflop decisions

The sparse AA diagnosis points to a learning problem: rare preflop decisions receive too few representative outcomes. A new isolated calculation now extends the existing board-integrated BB-root method to **every preflop decision for both players** in the current heads-up context. It integrates all compatible opponent holdings on each supplied fixed board and preserves the weights needed for learning. Software controls passed; no new model has been trained or scientifically admitted, and production remains unchanged.

## The target and its weighting

The initial private-pair law is proportional to the two original entry weights, excluding overlapping cards. Let `m[c]` be the acting player's initial class marginal, after private-card compatibility. At decision `I`, for candidate action `a`, the target `Q[c,a]` averages future payoffs conditional on that initial class, multiplying the opponent's earlier action probabilities. Future actions follow the same supplied frozen policy.

The acting player's **own earlier action probabilities are excluded** from this target. This lets the learner evaluate a candidate at a branch even if its current strategy rarely reaches it. The opponent's earlier probabilities remain in the target; normalizing those away would change the scale of counterfactual regrets. Once targets are available, the centered advantage is `Q[c,a] - sum_b sigma[c,b] Q[c,b]`. A cumulative update would multiply by the original class marginal and the declared common generation scale. This new component computes the targets and advantages, but implements no update or policy replacement.

The component reports own-history probability, opponent-history probability and original class support separately. A class with no initial entry support has a zero placeholder and an explicit unsupported mask. A branch with zero opponent history has zero counterfactual targets. Zero own-history probability alone does not remove a supported counterfactual target. These are learning quantities; a played-range view still needs genuine arriving support.

## Exact endpoints and sampled boards

Preflop folds use their original chip utilities. All-in endpoints use the existing exact class-pair matrices, with the current context's terminal economics. The component checks pair support, marginal consistency, cashflow conservation and original chip bounds. The current topology validator refuses all-in endpoints with different economics rather than silently reusing one matrix.

For postflop leaves, a supplied five-card board has all **1,081 legal private holdings per player**. The existing terminal reducer excludes shared private cards and integrates the opponent's holdings. Both actor vectors from each branch evaluation are retained. The class reduction weights each hero holding by its original entry weight; it does not multiply by that hero's earlier action probability.

An unconditional board draw uses the correction `C(52,5) / C(48,5)`. The same ratio follows independently from chronological flop, turn and river domains: `C(52,3)*49*48 / (C(48,3)*45*44)`. Together with the original private-pair normalizer and class marginal, this yields one importance-weighted chance contribution. **A single board contribution is not a full expected action EV.** Multiple draws must come from a prospectively specified chance law, preserve duplicate draws and use the same frozen generation policy before averaging. The new component does not choose or draw boards.

A reverse traversal of the preflop tree converts terminal vectors into all decision/action targets. At a hero node it averages the hero's future actions; at an opponent node it sums child vectors because the opponent probabilities are already included in their prefix reach. Child pointers define topology, so node-number ordering is irrelevant.

## What the controls establish

The controls use synthetic class-dependent policies, synthetic hand strengths and synthetic postflop payoffs on the existing 20, 40, 100, 200 and 400bb topologies. An independent forward enumeration forces every candidate action and sums physical private-pair outcomes. It checks all 24 decision nodes and 4,056 class rows in each exact and board component, including the later BB 4-bet response.

The largest difference from that independent enumeration is **5.68e-13bb**. The BB-root outputs agree with the previous implementation to **2.84e-14bb**. Additional controls verify zero own-history behavior, zero opponent-history behavior, proportional opponent-reach scaling, absent entry classes, source-policy snapshots, reordered node IDs and compatibility with the native export's terminal schema. The stronger component refuses 27 malformed cases, including cycles, altered cashflow offsets, incomplete policies, missing physical holdings and unsupported entry mass.

The two published control runs finished in 4.344 and 4.297 seconds while running independently in parallel. These are small software-control durations, **not a speedup benchmark or a training-time estimate**. No native executable, scientific model inference, GPU workload or new scientific deals were used. Preserved staging evidence is separate from the final published control receipts.

## Resource implications and remaining work

The extension reuses both actor vectors already produced by each existing fixed-board branch evaluation. It adds class-sized preflop reductions rather than launching a separate postflop simulation for each hand or decision. This is a source-level efficiency opportunity; actual runtime, inference batching, memory and throughput still need measurement on representative native trees. Increasing the number of board draws can still increase total work substantially.

Before scientific training, the component needs integration with authenticated native trees, the original entry population, visible-only current-policy inference and immutable generation identities. A persistent preflop accumulator must replace the one-visit override mechanism without treating chance draws as actual hand-history observations. It needs complete-generation publication, restart controls and separate evidence counts. The next stability comparison needs prospectively declared board budgets, independent runs and evaluation gates; none has been registered or started here.

This is preparation for the current BB-versus-BTN continuation model. It does not establish accurate learned poker ranges, stack-specific opening ranges, multiway postflop values or agreement with GTO Wizard. The completed comparison's failed improvement criterion remains unchanged. There is no arbitrary premium-hand calling rule and no installation on port 56708.

Sources and controls: [new component](../../../tools/research/stack_context_preflop_expected_components_v2.py), [independent controls](../../../tools/research/stack_context_preflop_expected_components_check_v2.py), [published control result](stack-context-preflop-expected-components-check-v2-result.json), and [prior AA diagnosis](STACK-CONTEXT-AA-DIAGNOSIS-20261002.md). The accompanying review receipt binds all consumed source and result identities.
