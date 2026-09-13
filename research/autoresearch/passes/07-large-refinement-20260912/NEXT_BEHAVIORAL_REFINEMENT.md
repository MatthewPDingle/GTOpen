# Next candidate: consistent behavioral perturbation

Design only: no GPU implementation, timing claim or large admission yet.

## Why this is distinct

The previous exploration experiment mixed only opponents' reaches. It did not
alter traverser continuation or accumulated strategy. Both seeds still passed
only two of the six conditional checks. Shared-reference variance reduction
also failed conditional coverage despite very small global gaps. Neither
experiment should be extended unchanged.

The next hypothesis is to maintain temporary support for legal actions in
every learning player's behavior, consistently throughout the recursion.
Fixed player models and point locks remain exact. Canonical acceptance still
requires the unrestricted full-particle game and all fixed conditional audits.

## Primary reference and limits

[Farina, Kroer and Sandholm (2017), Algorithm 2 and Section 9](https://proceedings.mlr.press/v70/farina17a/farina17a.pdf)
formulate regret minimization on perturbed behavioral strategy spaces. Their
algorithm accounts for both own and opponent behavior, including the local
regret transformation and reach-weighted average. They also identify difficulties
with decreasing perturbations: the feasible strategy space changes over time.
Their two-player zero-sum results do not establish convergence for GTOpen's
multi-player coupled-deck approximation or its discounted update schedule.

The algebra below is our proposed uniform-mixture specialization. A finite
annealing schedule would be an empirical candidate, not an EFPE guarantee.

## Local transformation to validate

For n legal actions, let sigma be the ordinary regret-matching distribution,
epsilon in [0,1), u the uniform distribution and tau = 1-epsilon.

    mu = tau * sigma + epsilon * u

Both traverser and learning opponents use mu for prefix reach and continuation.
Given physical child counterfactual payoffs Q (already in native opponent-reach
units), define the virtual pure-action payoffs:

    L[a] = tau * Q[a] + epsilon * mean(Q)
    v = dot(mu, Q) = dot(sigma, L)
    delta_regret[a] = L[a] - v
                    = tau * (Q[a] - dot(sigma, Q))

Accumulate actual behavior with own mu-prefix reach, not sigma-prefix reach.
Do not replace regret with Q[a]-dot(mu,Q): that omits the transformed action
space. Native epsilon-zero execution must take the original kernel path for
exact compatibility. Full evaluation must bypass perturbation.

## Admission work before performance

1. Independently enumerate a small extensive-form tree whose traverser acts
   at two levels. Compare virtual-action recursion with the formulas above,
   including hand-dependent policies, zero native support, frozen opponents,
   point locks and own-reach averaging. Cover several fixed epsilon values.
2. Match full GPU arenas to that independent reference; check eager/captured
   parity, read-only canonical evaluation and native epsilon-zero equivalence.
   Reject incompatible research modes. Keep this research-feature-only.
3. Register a bounded fixed-epsilon diagnostic first. Record both constrained
   and unrestricted gaps and all six conditional checks. A constrained gap
   cannot qualify the result. Use a matched epsilon-zero control.
4. Only after understanding that diagnostic, register a transition to epsilon
   zero with explicit regret/average treatment. Reusing old-coordinate histories
   is not automatically justified when epsilon changes. Either derive the
   transformation or label and test the schedule as a heuristic. Include all
   pretraining and transition time in the final comparison.

The existing small-screen and large 27-path gates remain unchanged. Failure
ends the registered budget. No live server changes, CPU performance work or
second hardware workload is authorized by this design note.
