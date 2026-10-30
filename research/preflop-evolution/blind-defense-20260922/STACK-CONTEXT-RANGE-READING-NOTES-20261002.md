# Reading the eventual preflop range exports

Source review only, prepared while the seven-stack evaluation is running.
No live exported probabilities or interim payoff estimates were inspected.
This does not change the registered analysis or authorize another experiment.

Each of the 28 exports uses one frozen training arm's bank for **both** players.
For example, A-relative describes candidate BB against candidate BTN from run
A. These descriptive arrivals are different from the payoff experiment's
crossings, which hold one opponent fixed while replacing the other player.
A change in an export's overall call frequency can therefore reflect a change
in the opponent's earlier actions and arriving cards as well as the acting
player's conditional policy. Keep these explanations separate.

The export propagates the compatible-card entry population through the actual
preflop tree. For each node:

| Field | Meaning |
| --- | --- |
| `probability_of_reaching_node` | Joint entry mass that reaches this public history. |
| `entry_mass_by_class` | Acting player's class marginal at this history; sums to node reach. |
| `conditional_range_by_class` | Class marginal divided by node reach. |
| `action_probabilities_by_class` | Policy conditional on this hand and history; not a dealt-hand entry range. |
| `conditional_action_frequencies` | Each class's action policy weighted by its actual arriving marginal, divided by node reach. |
| `own_history_weighted_model_support_by_class` | Sum of each generation's actor weight times that generation's own action-history reach. It is a model-mixture denominator, not a hand count or joint node reach. |
| `in_arriving_range` | Whether a class has strictly positive arriving marginal, without a new reporting cutoff. |

The played generations are 0–63 and their weights are 1–64, summing to 2,080
per actor. With no earlier action by that actor, the model-support denominator
is 2,080. Dividing it by 2,080 gives the behavioral average's own-history
reach; it still excludes the opponent's strategy and private-card population.
The independent reader checks this perfect-recall identity separately from
joint physical arrival and action-frequency calculations.

At a zero-reach node the conditional range and action frequencies are `None`.
The averaged policy may still carry a legal uniform fallback for unsupported
queries. Neither that fallback nor a policy shown for a zero-arrival class is
a supported hand recommendation. Very small positive support also needs
context; do not invent a test-driven threshold or rescale the source evidence.

For final interpretation, compare baseline and candidate exports at identical
depth, public history and legal menu within each run. Show joint node reach,
actual conditional frequencies and hand-level policies together. Across depths,
match histories by their actual actions and amounts: node IDs or action-column
indices alone need not refer to the same situation after stack clamping.
Separate stable changes seen in both runs from inconsistent boundary hands.

Do not average the 169 classes equally, pool all nodes as one range, or sum
conditional percentages across different histories. Full compatible-card
weights and all preflop branches must conserve the entry population. The
reader's complete catalog replay and physical-combo audit remain required.
These ranges describe this fixed BB-versus-BTN entry family; plausible-looking
charts are not an external accuracy test or a complete multiway solution.
