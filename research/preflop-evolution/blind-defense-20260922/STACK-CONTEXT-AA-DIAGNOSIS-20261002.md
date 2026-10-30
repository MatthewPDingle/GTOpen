# Why the experimental model folds AA: traced evidence

The 400bb AA anomaly has a concrete cause in the experimental policy: **a single retained losing training visit becomes a pure-fold lookup override, and that override survives across 45 played generations.** This is a sparse synthetic training-target problem, not evidence that Ignition players fold AA or that the additional river inputs are inherently wrong. Production on port 56708 remains unchanged.

## The chain from a physical deal to the displayed range

In run B's candidate, generation 18 had no retained AA lookup row at BB's response to BTN's 4-bet. Its frozen policy called at this visit. Cycle 19 sampled BB with AA, BTN with K8, and a board with ranks K-T-8-4-2. BTN made two pair and AA lost. The archived native trace records BB's conditional Fold value as **-6bb** and Call value as **-400bb** under that physical deal and frozen continuation policy. Their difference is +394bb in favor of folding on this one outcome.

The resulting centered advantage target is `[394, 0]` for Fold/Call. Both the original sampled target and the archived conditional-action target agree. This specific case is not explained by sampling the subsequent betting actions: the conditional trace gives the same result. The remaining chance variation includes the opponent's cards and the runout; one losing runout is not AA's expected value across those possibilities.

The weighted preflop lookup converts positive mean advantages into action probabilities. **One row is enough to override the neural policy completely**; there is no evidence-strength blending at this boundary. With one positive Fold advantage and zero Call advantage, its recommendation becomes 100% Fold. Root and initial-BTN overrides do not replace this later BB branch.

I authenticated all 256 already-played model files and read AA lookup rows at all five fitting depths. At this specific branch, every played generation from **19 through 63** retains a one-visit row with that same +394/0 target and a pure-fold policy. No generation 64 model was used in the played-bank analysis.

Existing reservoir checkpoints at generations 19 and 63 independently confirm the same retained slot, **16967**, still carries **visit iteration 19** and `[394, 0, 0, 0]`. At generation 63, this BB/context reservoir has seen **209,338 total visits** but keeps **32,768**, shared across decision nodes and hands. A large overall training collection therefore does not guarantee adequate coverage of a particular hand at a particular branch.

## How that produces 91.16% folding

The average weights each played model by its generation weight and AA's own earlier 3-bet probability. Its total weight at the branch is **1821.599413329**. The table's folding contributions, plus the initial uniform model, account for **91.157059%** folding, matching the verified export to within 1e-12. The remaining neural-fallback generations contribute no measurable extra folding. The anomaly is thus directly accounted for by the lookup overrides and the declared averaging rule; it is not a mislabeled chart or missing normalization.

AA's 87.58% own-history support describes how often the averaged policies send AA through its own earlier action. **It does not mean that the learner has many independent AA targets here.** Model reuse and real training-visit counts must be reported separately when assessing learned range reliability.

## Memory retention is only part of the problem

I also decoded the relevant original batch at **all 64 training cycles**, using eight independent archive reads and retaining the file identities. Those cycles contain 64 physical AA deals but just **10 positive visits to this particular 4-bet response**. Of those ten, only the cycle-19 target is retained in the generation-63 lookup.

Keeping all ten original targets would still leave mean advantages of **30.7900bb for Fold** and **-27.9975bb for Call**. Two losing 400bb outcomes dominate the small collection. Retaining every preflop target would remove arbitrary forgetting, but **it would not by itself fix this case**. Those means combine targets centered under changing frozen policies; they are regret-like training quantities, not standalone action EVs or a confidence interval.

## What should change next

1. Preserve cumulative preflop evidence separately from the shared visit reservoir, so rare branch/hand observations are not randomly displaced by abundant other visits. Keep correct source-deal and counterfactual weighting; do not reinterpret sampled advantages as action EVs.
2. Give later preflop branches expected continuation targets across multiple legal opponent holdings and runouts, rather than relying on a handful of visited physical deals. The current board-integrated BB-root update offers an architectural starting point, but extending it to later branches still needs derivation, resource estimates and controls. Replacing this case's sampled action target with its already-recorded conditional-action target alone would leave the +394 target unchanged.
3. Track actual branch/hand visit counts and target dispersion independently of own-history mixture support. Verify supported premium responses and independent-run agreement before another full training comparison. A minimum-count blend can prevent a one-visit override, but it cannot qualify a poorly learned neural fallback and is not the complete solution.

No premium-hand rule, forced calling floor, policy edit, new trial or deployment was introduced. This analysis is a post hoc causal trace of existing evidence, not a new accuracy comparison. The original failed improvement criterion and uncertainty remain unchanged. The native trace was decoded and authenticated, not independently recomputed, so a separate payoff/learning diagnostic is still appropriate before accepting a corrected learner.

Evidence: [all played AA table rows](stack-context-aa-existing-targets-20261002-v1.csv), [original losing visit](stack-context-aa-archived-visit-20261002-v1.json), [all 64-cycle branch visits](stack-context-aa-archive-coverage-20261002-v1.json), and this document's [identity and arithmetic receipt](STACK-CONTEXT-AA-DIAGNOSIS-20261002-receipt.json). The earlier [comparison findings](STACK-CONTEXT-FINDINGS-20261002.md) remain preserved.
