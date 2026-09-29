# Current-policy and board-target adapters: implementation checks passed

The new shared-context worker adapter passed seven CPU/native implementation
tests in 10.889 seconds (10.906 seconds including recording). This is integration
evidence, not a trained model or an improvement in preflop accuracy.

`stack_context_current_policy_v1.py` freezes one complete played model and context.
It caches widened network weights and the existing preflop, exact BTN and BB root
overrides, with their original precedence. Native batches retain real ancestor
links. Fixed-board postflop rows can be scored without ancestor links, but cannot
be used as played-policy averages or silently acquire invented histories.

`stack_context_board_components_v1.py` follows each context's actual preflop tree.
The old scoped provider hardcodes the 200bb topology. At 20bb a re-raise becomes
an all-in and one postflop branch disappears. The new provider derives paths,
fold payoffs and path-dependent hand weights from the actual context; it rejects
different showdown economics that would require separate exact matrices.

`stack_context_board_targets_v1.py` connects this decomposition to current-policy
scoring and requires all 1,326 physical private holdings at every preflop node.
Its complete prepare/draw-record/generation-evidence flow is still unqualified.

Checks covered:

- Both input representations at seven depths, both actors and all streets;
  feature equality and policy agreement with the existing reference interface.
- Retained generation-77 trained policies as well as synthetic multi-context
  routing states; held-out contexts remain free of learned local overrides.
- Two complete native physical preflop catalogs and two small native fixed-board
  trees at 20bb and 200bb, each scored by both representations.
- Synthetic exact-value decomposition versus independent class-pair recursion
  at all seven depths; agreement with the old closed form at 200bb.
- Tiny-board contributions versus the old formula at 200bb and an explicit
  two-branch formula at 20bb, without board-specific renormalization.
- Rejection of wrong keys, menus, contexts, histories, incomplete catalogs,
  foreign prepared rows, invalid topology/economics and missing board branches.

The earlier staging attempts exposed a test fixture field-name typo and an
over-broad score-only test that included preflop rows. The adapter now explicitly
requires real histories for preflop rows and reports missing histories clearly.
Those were implementation tests, not retried scientific experiments.

Evidence: `stack-context-native-adapters-v1-cpu-attempt.json` and
`stack-context-native-adapters-v1-cpu-tests.json`. Source/fixture identities were
verified; four native output hashes are recorded. Native outputs were not retained
for independent numerical readback. The new cached CUDA worker path, full worker
provenance, complete target preparation, joint native cycle, and cycle restart
are not yet qualified. Existing short fitter controls do not cover these gaps.

Next connect the versioned board and posterior64 workers, prepare context-specific
catalog/matrix resources with their true identities, and qualify a complete
cycle/restart before registering a matched learning comparison. No scientific
training, deployment, GitHub push, or change to production 56708 occurred.
