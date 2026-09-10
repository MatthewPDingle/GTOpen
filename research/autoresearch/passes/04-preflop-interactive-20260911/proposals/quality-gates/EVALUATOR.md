# Policy evaluator implementation

Lab-only source files:

- `crates/solver/src/preflop/preview_quality.rs`
- `crates/solver/examples/preflop_preview_quality.rs`

The parent owns the single `pub mod preview_quality;` declaration in `preflop/mod.rs`. No other shared source is edited by this task.

The standalone executable accepts exactly:

```
preflop_preview_quality CANDIDATE.gtop REFERENCE.gtop EQUITY_CACHE THREADS [PATHS.json]
```

Both native inputs go through `load_game` without header rewriting or payoff-identity overrides. An unsupported preview save must remain rejected until the actual model loader supports it. The reference must identify `coupled_deck_v1` and have all 1,024 particles. Inputs must have identical config, tree shape, profiles, frozen flags, hero, point locks, equity-table Arc, and realization fit. Frozen average policies must match. The example refuses missing calibrated fits and verifies its existing equity cache did not change.

The method creates a **fresh local evaluation workspace**, using the full reference payoff table and exact policy constraints. It copies average-strategy sums, never candidate regrets. The workspace is never returned, saved, or iterated. Inputs remain intact. This permits counterfactual evaluation of a policy from another payoff approximation without pretending its learned regret state belongs to the reference game.

Outputs include reference and candidate full-reference gaps/EVs, their summed learning-seat gap difference, and each learning seat's unilateral replacement EV against reference opponents. Signed per-seat losses are retained; aggregate loss gates average/max the positive losses so gains cannot cancel another seat's failure. Relative-gate pass and `passes_global_policy_gates_with_converged_reference` are separate. This name intentionally does not imply full preview acceptance.

Optional `PATHS.json` contains up to eight selected action-index paths, such as `[[],[1,1]]`. Each selected node evaluates every legal action and all169 hands, using the same full-reference arriving ranges and reference future play. Counterfactual values are divided by the current opponent reach mass to give conditional bb values. Results include action values, conditional hand mass, independent-model joint reach, candidate action-loss tail and reference action loss. A constrained/frozen node's local tail gate is null because its fixed policy is not a learning recommendation. Unreachable paths are labeled and not assigned a passing numeric score. This is a one-step deviation check, not a solved subgame BR. The existing saved BB JSON reference tests remain the cheap way to audit the large historical closing-call node without rebuilding its million-node game.

Physical equity, unselected node tails, and interactive timing remain explicitly unmeasured.

Safety/performance bound: <=20,000 nodes and <=128 MiB of regret+strategy arenas for each input, plus a 140 MiB native-file precheck. The workspace is another tree/arena allocation. Root owns benchmark scheduling; this task has not launched a build/test as of implementation handoff. There is a focused self-policy zero-loss/input-immutability/cancellation test to run when released. This is a research API, with no production UI/server callers.

Pending validation must include compilation against the active candidate model API and at least the same-policy control before using its scores. The registered thresholds in `corpus.json` remain unchanged by this implementation.
