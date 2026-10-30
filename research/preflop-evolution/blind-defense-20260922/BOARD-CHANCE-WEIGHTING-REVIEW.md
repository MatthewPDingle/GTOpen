# Board chance weighting review

The next model's public-board calculation preserves the original incoming
distribution of compatible private hands. No implementation change is indicated
by this audit. It checks the probability calculation, not learned poker strength.

For a compatible pair of two-card holdings, the legal public runouts come from
48 cards. The board proposal samples from all 52 cards. Illegal combinations
contribute zero, and the surviving contribution is multiplied by

`C(52, 5) / C(48, 5) = 1.517814593670283`.

The board representation sorts the flop and keeps the turn and river ordered.
There are 20 such orderings per five-card set under both probability laws, so
that factor cancels. The same ratio is
`C(52, 3) * 49 * 48 / (C(48, 3) * 45 * 44)`.

The denominator remains the original joint private-hand mass and the original
BB class mass. Renormalizing the surviving private ranges independently on each
sampled board would change the question being averaged. The incoming ranges
make some boards more likely than others; a uniform board proposal does not
remove that dependence.

`board_chance_weighting_audit_v1.py` independently enumerated a ten-card deck
with two private cards per player, five public cards, nonuniform private-hand
weights and an order-dependent synthetic payoff. Both enumeration orders
covered 151,200 complete outcomes: 1,260 compatible private pairs and 5,040
public runouts. Seven hand groups and two synthetic actions were checked.

- Correct importance weighting: maximum difference **1.42e-14**.
- Omitting the chance correction: maximum difference **146.45**.
- Renormalizing surviving private ranges by board: maximum difference **7.20**.

Those differences use synthetic payoff units, not poker EV. This control took
3.031 seconds, used no GPU and drew none of the prospective study's test deals.
See `board-chance-weighting-audit-v1-result.json` for source bindings and details.

The existing actual-poker component control also remains relevant. Its six
one-board policy cases agreed with a separate forward traversal within
1.60e-13; the separately integrated preflop terms agreed within 1.07e-14.
The 20 code/executable bindings in that result were reverified during this
review. This remains a one-board component check, not full training evidence.

Source review also confirms that the pipeline adds the exact preflop terms
once, averages the four board contributions, subtracts the played-policy
value, and scales the resulting advantages by the original class mass and
the matched 512-deal learning budget. The previous sampled root regret sum
is not added again. Physical network-training targets remain a separate path.

Remaining questions are empirical: whether four boards per update reduce the
variation enough, whether the learned continuation strategies improve, and
whether the complete averaged policies gain against their matched controls.
The registered complete training and fresh fixed evaluation address those
questions. This audit alone establishes none of those outcomes.
