# Next research direction: change the local regret minimizer

Status: this sequence has now been executed. Native-payoff RM+ and predictive
RM+ passed numerical validation but failed conditional convergence screens.
See RM_PLUS_RESULTS.md and PREDICTIVE_RESULTS.md. The proposed sequence below
is retained as design history; NEXT_CONDITIONAL_REPAIR.md is the next direction.

The accumulated-opponent candidate failed both small seeds. The large averaging
discriminator also failed with identical learned regrets. Stop varying those
two mechanisms for now. Investigate a different local regret minimizer while
retaining native counterfactual payoff weights and the tested pair estimator.

The primary reference is Farina, Kroer and Sandholm,
[Faster Game Solving via Predictive Blackwell Approachability](https://arxiv.org/html/2007.14358),
Algorithm 5 and Appendix F. It distinguishes predictive regret matching+ from
simply counting the last regret twice. Its counterfactual predictions incorporate
the newly selected descendant strategies. The paper reports strong results on
many benchmarks but DCFR remains better on most tested poker games. Those
zero-sum results do not establish convergence or a speedup for this multiway
approximate game.

Implementation sequence proposed from the current GTOpen code:

1. Add an isolated, fresh-state GPU regret-matching+ baseline, with native
   counterfactual increments, clipping only after each observed regret update.
   Define averaging and discount timing explicitly; test against independent
   host arithmetic before measuring convergence. Keep sampled and full-particle
   controls, locks, frozen seats and canonical final evaluation.
2. Before predictive integration, inventory required persistent prediction
   storage on the large fixture. Do not assume the current scratch slots can
   retain prior terminal/action values: they are reused during upward traversal.
3. Match the paper's prediction/update order in small deterministic tests, then
   assess whether sample noise defeats prediction. Keep ordinary saved-state
   evaluation independent of any transient predictive-policy buffers.

This design note itself is not an acceptance gate. The subsequent RM_PLUS and
PREDICTIVE plans registered numerical tests, memory caps, learning schedules and
matched convergence cases before execution. The original large global/conditional
requirements and no-deployment status remain unchanged.
