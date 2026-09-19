# Reach audit for the frozen-source transfer

Read-only diagnostic on the completed ten-flop AB development reference.
No held-out results were accessed and no probabilities or convergence gates
were changed. The broader47 result remains pending.

An aggregate postflop gap weights decisions by how often the frozen source
reaches them. It can be small while some rare decisions remain poorly
determined. Full preflop deviations may enter those decisions. They are
still valid deviations against the reported policy, but should not be
interpreted as a direct measurement of one preflop source's intrinsic
full-deck strength.

The audit enumerates compatible physical private-hand pairs, averages the
source panel's complete suit orbits, and walks each player's path
probabilities separately. It reproduces the independent root normalizer
and checks that terminal probabilities sum to one. Controls cover a
never-called branch, an undefined conditional distribution when the
opponent never reaches, and a mixed-hand call distribution.

| Continuation | Actual entry probability | Seat | Counterfactual hand mass with own path probability <= 1e-6 |
|---|---:|---|---:|
| Call the 3-bet, pot39.5 | 12.09% | OOP | 56.69% |
| Call the 3-bet, pot39.5 | 12.09% | IP | 0.00% |
| 4-bet then call, pot93.5 | 5.27% | OOP | 58.48% |
| 4-bet then call, pot93.5 | 5.27% | IP | 25.92% |

Counterfactual mass here keeps the opponent's earlier actions fixed and
removes the named seat's own path actions. It is **not** the proportion of
hands actually arriving in the pot. Exactly-zero shares are zero in this
averaged source; the table concerns very small nonzero probabilities.
Other fixed descriptive bands (0.001 and0.01) are included in the JSON.

This does not show an implementation error, invalidate a best response,
or prove that all low-reach hands have inaccurate values. Counterfactual
updates can still learn values for rare hands. It identifies a limitation
of reading a single reach-weighted residual as a per-hand guarantee.
Do not add arbitrary calling floors or smooth away this evidence.

When the broader source and transfer results complete, inspect this audit
alongside the full deviation, postflop residual, and root-only hand-level
decision values. Any targeted off-path robustness experiment needs its
own clearly stated strategy-completion rule and validation; it must not
silently change the current frozen-source comparison.

Evidence: `development-ab-reach-diagnostics.json`. Reusable helper:
`tools/research/continuation_reach_diagnostics.py SUBTREE SOURCE OUTPUT`.
The helper requires a completed2000-iteration source and uses only that
source's own declared development panel.
