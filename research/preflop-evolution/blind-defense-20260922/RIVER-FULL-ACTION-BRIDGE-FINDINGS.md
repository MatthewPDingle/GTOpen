# Full-action river bridge: native controls passed

Completed 2026-09-28. A new research-only native exporter now supplies the
complete downstream river action tree for a fixed visible decision and all
990 compatible opponent hands. It compiles independently of the server.
The reader computes complete action values under one explicitly identified
policy, with opponent-history weighting and one common regret baseline.

## Evidence

Nine configurations passed: eight preselected old-training positions plus a
zero-rake version. These cover both actors, free checks, ordinary bets with
raising available, no further raises, and facing an all-in. Across exports:
8,910 opponent-pair cases, 38,510 query rows and 52,470 tree nodes. Counts sum
over fixtures and are not unique information sets across the study.

- Terminal accounting matched independent commitment/rake/offset reconstruction
  exactly, including ties and uncalled-bet refunds.
- Full action values matched independent terminal-path sums within 1.78e-15 bb.
- The old Fold/Call reference matched within 2.85e-14 bb under identical
  visible-key policies and opponent histories.
- All 18 uniform/hand-history policy checks and their 18 zero-own-reach
  counterparts passed. Removing an earlier own action's probability did not
  erase an otherwise supported target or change its complete action vector.
- All 54 policy identity/probability rejection checks passed. Three malformed
  native requests were rejected without creating output. Empty opponent
  support was reported explicitly in every configuration.
- Canonical visible features, actual own histories, public action transitions,
  pair compatibility, legal actions and stack-limit flags passed readback.

The primary controls ran in 14.47 seconds and retained 19.88 MB. No training,
GPU allocation, production change or old archive deletion was involved.

## Source-inventory correction

Post-run audit found that the first runner searched for tree/evaluator source
directories while those dependencies are tree.rs and evaluator.rs. Its native
binary and Python sources were registered, but its Rust source inventory was
incomplete. The original source, registration and result remain unchanged.

A separately registered replay included the full solver source inventory,
Cargo manifests/lock, helpers, unchanged binary and exact original artifacts.
All nine native exports were byte-identical, and all three malformed requests
were rejected again. Replay took 1.76 seconds and retained 19.79 MB. Both
runs together retained approximately 39.67 MB. See the provenance plan and
registration; the original incomplete manifest is not retroactively repaired.

## Interpretation and next step

This qualifies the exported values and reader on the declared fixtures. It
does not qualify a sampled self-play walker, demonstrate improved preflop
ranges, or prove faster convergence. Policies here are deterministic test
recipes, not learned strategies. The eight original positions come from two
old training deals in one restricted 200bb context. All-in coverage here is
facing/calling a jam; add a geometry-selected jam-as-bet/raise control before
claiming that action coverage separately. Cross-stack/rake/sizing accuracy,
folded-card effects and full-game quality remain unresolved.

Next run a bounded fixed-current-policy pilot using the exact last played
generation from each audited research arm, with the same model pair supplying
history probabilities and downstream decisions. Do not silently use the
78-generation average in place of a current self-play policy. Check CPU/GPU
inference agreement, quantify posterior support and full-vector target
variance, and time preparation, inference and value propagation separately.
Then integrate a new visit-preserving native walker and test complete ancestor
returns and updates before self-play and a fresh full-policy evaluation.

Evidence: river-full-action-control-v1-{registration,result}.json and
river-full-action-provenance-v1-{registration,result}.json. Raw exports and
per-case checks remain in their corresponding local evidence directories.
