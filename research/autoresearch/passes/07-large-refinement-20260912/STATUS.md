# Qualification status

Large-game GPU convergence remains unqualified. The live app on 56708 is
unchanged. The objective is faster large-game solving with BOTH global gap
and fixed per-hand conditional branch accuracy; earlier preview availability
does not satisfy it. CPU performance is outside the current work.

- Normalized pair correction qualified on four small-fixture seeds, with
  measured complete times 2.54-4.40x faster than the full-particle small control.
  See NORMALIZED_PAIR_TAIL_RESULTS.md. This is not a large-game speed claim.
- The large normalized-pair run failed: gap 0.4641 bb and 11/27 branches at
  3000 iterations. See LARGE_NORMALIZED_PAIR_RESULTS.md.
- Changing averaging alone preserved all 264,950,257 regret entries exactly
  but failed large accuracy. Nine failed branches had zero current opponent
  reach in both runs; other failures had positive reach. See
  LARGE_AVERAGING_DIAGNOSTIC_RESULTS.md and raw/large-averaging-reach-verified.json.
- Accumulated-opponent learning was numerically verified but failed both
  small seeds (0/6 branches). See AVERAGE_OPPONENT_RESULTS.md.
- Fresh native-payoff regret matching+ is also rejected: full-particle and
  two sampled runs all reached very small global gaps but failed conditional
  coverage after 3000 iterations. See RM_PLUS_RESULTS.md. No large run admitted.

- Predictive regret matching+ passed independent numerical recursion, compressed
  history, capture and evaluation tests, but failed all three convergence cases.
  The matched zero-prediction case also failed conditional coverage. See
  PREDICTIVE_RESULTS.md. No large predictive solve is admitted.
- Exact large-tree geometry reduces predictive extra storage to 2.91 GB,
  within the 4 GiB cap. This is an inventory, not a tested large GPU allocation.

- Non-root policy-only repairs also fail the registered screen. All five
  strengths improve the conditional objective while violating the global gap;
  no update is accepted. All regrets and unselected averages are preserved,
  and saved-file audits agree exactly. See CONDITIONAL_POLICY_REPAIR_RESULTS.md.

The broad global-update and direct local-policy variants tried so far have not
met both requirements. Do not extend those rejected budgets unchanged. Before
another candidate, review the existing GPU cost/variance evidence and identify
a distinct mechanism with a numerical or cost advantage that can be screened.
The objective remains active; no large-game speed improvement is qualified.

Initial refinement history remains in STAGE1.md, PROTOCOL.md and raw evidence.
Conditional gates measure one-action deviations under the canonical coupled
continuation, not full physical-deal equity or subgame best responses. No
partial result here authorizes deployment or ordinary resume of research saves.
