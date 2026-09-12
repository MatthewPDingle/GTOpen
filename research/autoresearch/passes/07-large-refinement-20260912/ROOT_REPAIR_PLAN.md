# Root-only bounded response mixture

Motivation: the GPU frontier audit found a 0.02580205-bb root one-step gain in
the compact sampled policy, against its 0.02953004-bb unrestricted global gap.
Joint ancestor updates worsened multiple neighboring decisions. Test whether
changing only the root can improve global consistency with less disturbance.

Registered before execution:

- Inputs: the same sampled/native compact-v1 final saves.
- Compute the root's per-hand best response against fixed average continuation
  using canonical full-1,024 GPU action values. Within 1e-8 bb of the maximum,
  retain the old relative probabilities; use a uniform tie only if their old
  combined probability is negligible.
- Test mixtures with the original root at fractions 0, 1/16, 1/8, 1/4, 1/2, 1.
  All candidates start from the same root baseline; this is not a sequence of
  cumulative best-response updates. Later policy and regret blocks stay exact.
- Evaluate unrestricted global gaps and all 27 conditional paths for each.
  Select the lowest full global gap, independently of local pass counts.
- Gates remain <=0.005 bb global and all 27 conditional tail checks together.
  No deployment or normal global resume is supported by the edited history.
- Save only the selected candidate, verify exact roundtrip, then independently
  reload and audit all 27 paths. Per-input process cap 600 seconds.
- First run a small correctness test for fixed constraints, invalid inputs,
  nonroot preservation, unchanged global age, and full CPU/GPU value agreement.
  CPU is only a correctness reference, never a speed benchmark.

This is an empirical consistency experiment, not a multiplayer convergence or
safe subgame-refinement guarantee. Failure does not justify weaker gates.
