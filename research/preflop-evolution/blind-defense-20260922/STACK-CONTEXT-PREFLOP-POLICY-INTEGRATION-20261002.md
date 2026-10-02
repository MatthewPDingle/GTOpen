# Connecting complete preflop learning state to played policies

The new cumulative preflop state now has a typed played-policy format and a native-target adapter with passed software checks. Every fitted preflop decision uses the cumulative state, including later responses after a raise. The new format refuses the old sparse retained tables and separate legacy root/BTN overrides. This addresses the policy-routing part of the diagnosed AA problem; it does **not** show that real AA ranges or overall poker accuracy have improved.

Shared postflop network calculations retain the existing visible-input and public-price checks. A context held out from fitting has no local cumulative state and uses the shared network. That behavior is explicit; no nearest-stack table is silently substituted. Model averaging weights each played strategy by the hand's own earlier actions, and excludes the final unplayed model using the completed-cycle boundary supplied by the checkpoint caller. A complete on-disk training checkpoint is still required before that boundary can be authenticated in a real run.

The target adapter retains all 1,081 board-legal holdings per actor, including zero-entry-weight hands. It verifies ordered hand rows, visible board prefixes, actor, action menu and public history before scoring. Each board contribution is bound to the raw tree bytes, frozen model and parent cumulative state. Native executable/context/request authentication is still the worker caller's responsibility; a tree hash alone does not prove the correct native process produced it.

## What passed

| Control | Coverage | Result |
| --- | --- | --- |
| Published native transport | 20bb and 200bb; complete 1,081-hand domains | Exact target transport agreement, unchanged postflop policy, exact update/restoration; 20 invalid cases refused |
| Typed model | 5,304 physical preflop rows at 20bb and 6,630 at 200bb | Every fitted row uses cumulative state; held-out 60bb uses network only; 15 invalid cases refused |
| Typed target producer | 20bb preserved native topology expanded to the complete private domain | All-node values match the previously checked transport exactly; postflop probabilities unchanged |
| Played-policy averaging and storage | Two synthetic generations at both fitted depths | Independent row-by-row own-history average matches; content-addressed model round-trip exact |
| CPU/CUDA parity | 362- and 387-input models at 20bb/200bb; native flop, turn and river rows | Zero observed prediction differences for all four cases |

The GPU control used nonuniform synthetic network weights and synthetic cumulative updates. It ran on the RTX 3090 with TF32 disabled, allocating about 34 MiB of CUDA tensors at peak. The CPU and CUDA controls ran independently in parallel after publication. Their durations were small software-control measurements, **not throughput benchmarks or evidence of faster learning**.

The original native controls exported only two test holdings per actor. Their topology, cashflows and visible-prefix rows are preserved. The expanded trees use synthetic strengths; they are not independent validations of the full native poker payoff oracle. Earlier expected-component tests independently checked the reduction mathematics, but these integration controls do not establish real range accuracy.

An earlier control stopped during setup because it supplied an unsupported `chance` constructor argument. Its exact source and failure are retained separately. The corrected control changed that setup call; the transport provider remained unchanged. The additional typed policy and typed target adapter are separately versioned. No original scientific source, result or improvement gate was changed.

## What remains

Next is the actual worker and complete training-cycle integration: authenticate native exports, collect every fitting context against the same frozen played model, publish cumulative states and both fitted networks together, and restore all sampling/reservoir state at a completed boundary. Then measure representative CPU/GPU/RAM/storage use and register a stability comparison with an explicit board-sampling budget before starting it.

These components are prepared for the existing heads-up BB-versus-BTN continuation family. They do not yet solve stack-specific opening ranges, add five-bets, establish multiway accuracy or demonstrate agreement with GTO Wizard. The original comparison failed its improvement criterion and remains unchanged. No scientific training run was started, no production behavior changed, and nothing was deployed on port 56708.

Evidence: [typed policy](../../../tools/research/preflop_expected_policy_v1.py), [typed target adapter](../../../tools/research/preflop_expected_native_targets_v2.py), [CPU control](preflop-expected-policy-check-v1-result.json), [CUDA control](preflop-expected-policy-cuda-check-v1-result.json), [transport control](preflop-expected-native-targets-check-v3-result.json), [review receipt](preflop-expected-policy-review-v1.json), and [AA diagnosis](STACK-CONTEXT-AA-DIAGNOSIS-20261002.md).
