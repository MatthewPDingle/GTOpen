# Conditional postflop residuals: descriptive audit

An overall postflop residual weights each hand by its actual probability of
arriving. The existing reach audit showed that some supported hands have
extremely small own preflop path probabilities. This additional read-only
diagnostic measures their postflop deviation gains conditional on arriving,
without pruning them or changing the original acceptance rules.

The tool first audits a complete frozen-policy panel. It independently
enumerates the legal physical private pairs and all 24 suit relabelings of
each board, applies the registered chance weights, and propagates each
player's preflop path probabilities separately. For each called branch,
player and hand class, it divides the averaged best-response-minus-average
CFV by compatible opposing reach. It retains the entry hand distribution
and opponent's preflop actions while removing this player's own earlier
action probabilities. Reapplying those probabilities must reconstruct both
players' complete postflop residuals within 0.000001 bb.

Every supported hand remains in JSON. The Markdown tables list the largest
conditional residuals, alongside counterfactual mass and own path probability.
This prevents a tiny overall contribution from being mistaken for an accurate
conditional answer. No mass threshold changes the calculation or drops hands.

## First completed observations

| Evaluation | Call branch, OOP maximum | Call branch, IP maximum | Called 4-bet, OOP maximum | Called 4-bet, IP maximum |
|---|---:|---:|---:|---:|
| Reserved10, source47 | 0.009441 | 0.005977 | 0.038687 | 0.004459 |
| Independent95, source10 | 0.018696 | 0.005416 | 0.021383 | 0.003630 |

Numbers are bb conditional on the hand reaching that branch, averaged over
the specified panel. Maxima include tiny entering masses. The complete
residuals reconstructed to the registered results: 0.000140574 bb and
0.000967534 bb respectively.

These two checks do not show large panel-averaged hand-level postflop
convergence errors. They therefore narrow one possible explanation for the
multi-bb preflop deviation gains. They do **not** establish accurate full-deck
values, certify every individual board, or prove that different postflop
equilibrium selections are interchangeable when preflop changes. In particular,
small gains against a fixed opponent do not guarantee robustness against a
different entering range. The matched training-panel reinitialization
diagnostic remains useful for separating these effects from board transfer.

Evidence: `reserved10-report47-conditional-residuals.{json,md}` and
`validation95-ab-conditional-residuals.{json,md}`, including source and worker
hashes. Reproduction tool: `tools/research/transfer_conditional_residuals.py`.
The independent95 source47 comparison was still running when this diagnostic
and interpretation were added. No GPU work or production changes were needed.

## Completed independent95 source47 audit

After the full original queue completed, the identical audit found conditional
maxima of 0.010631 / 0.008518 bb in the call branch and 0.022227 / 0.004512 bb
in the called 4-bet branch (OOP / IP). These are panel-averaged maxima over all
supported hands, including very small counterfactual masses. The reconstructed
overall residual is 0.000145706382 bb. This third evaluation likewise does not
show a large conditional mean numerical residual; the qualifications above
remain unchanged. Evidence: validation95-report47-conditional-residuals.json
and .md, with exact input hashes.
