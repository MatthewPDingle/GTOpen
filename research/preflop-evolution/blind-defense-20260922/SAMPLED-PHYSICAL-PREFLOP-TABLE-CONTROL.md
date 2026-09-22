# Direct preflop estimates: representation control

The fitting diagnosis found that the old network substantially distorted its
own retained preflop regret targets. This prototype can preserve those targets
directly while retaining the neural policy for postflop observations. It does
not assign hand ranges or assume the targets are correct poker values.

For every observed preflop decision and hand, store the mean retained sampled
regret for each legal action. Use the same positive-regret matching and
highest-legal-score fallback as the neural adapter. Unobserved preflop rows keep
the neural policy. The table uses only the player's cards and public decision;
future-board fields must be unknown and all visible features must match the key.

## Completed correctness control

The old 16-deal fixture and saved baseline generations 77/78 were used, with an
initial uniform model as a third averaging component. This is a synthetic
three-model transport control, **not** the evaluated played bank or a candidate
strength test. It adds no training or test deals.

- All **1,335 table rows** matched independently recomputed raw reservoir means;
  maximum discrepancy was 8.53e-14 bb.
- The fixture contained **7,277 observations**. Both trained models matched 77
  preflop query rows; their individual postflop probabilities remained exact.
- Own-history-weighted averaging and support matched an independent explicit
  calculation exactly, including unequal player/model weights.
- It matters where the substitution happens: keeping the old preflop reach
  weights while changing the policy produced a maximum 0.771 probability error
  on this fixture. The prototype applies tables **before** propagating reach.
- Native cached traversal agreed exactly with the independent direct reference
  for all **32 updater traversals** using the hybrid averaged policy.
- Empty tables preserved neural policies exactly. Future-card contamination,
  duplicate keys, wrong action menus, context mismatches and invalid counts were
  rejected. CPU random-number state was unchanged.

This ran on two CPU threads as a correctness check; it is not CPU performance
work. The running larger-data GPU trial, production and preview were untouched.

## Versioned save/load control

Hybrid models and checkpoints now use **format 2**, including an explicit policy
type and game identity. Original format-1 readers reject both kinds; hybrid
readers reject network-only models. Tables cannot be silently discarded.

A synthetic two-step control used old fixture updates and fixed networks, not a
new training run. Restoring and continuing produced the exact same checkpoint
hash as uninterrupted continuation, including table contents, retained arrays,
deal/action/reservoir random states and the played/unused model boundary.
Save and restore also reconstruct each current table from its retained data;
a table with altered estimates is rejected even when its metadata still matches.
Changed context/configuration, reordered generations and wrong hashes were
rejected. No GPU work was needed for this serialization control.

Evidence: `sampled-physical-hybrid-checkpoint-control-v1-{registration,result}.json`.

## Remaining work before a training comparison

The table module, serialization and CPU averaging reference are prototypes only.
A hybrid experiment still needs training integration and a CUDA bank
that propagates overridden preflop reach, and numerical/transport checks.
Then register its comparison and fresh evaluation streams before training.
Complete the current larger-data trial first; do not retrofit tables into its
bank or call this control an improvement in poker strength.

Even perfect reproduction of retained estimates leaves noisy regret targets,
limited postflop play and fixed incoming ranges. It addresses an identified
representation error, not every source of range error.

Evidence: `sampled-physical-preflop-table-control-v1-{registration,result,models,policies,native}.json`.
