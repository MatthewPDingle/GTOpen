# Card-compatible two-player accounting gate

19 September 2026. Offline research, no production integration.

The current Wizard-case audit finds large all-in call-value changes after
conditioning on the caller's cards. A local response check does not validate
an iterative solver's chance, fold-payoff and counterfactual accounting.

Construct a deliberately small Bayesian push/fold game. Player 0 can fold or
jam; player 1 can fold or call a jam. Each knows its own 169-class hand.
Joint chance is proportional to both supplied range weights times the exact
number of compatible ordered physical hand pairs. The cached class equity
table supplies showdown expectation and stays fixed across all comparisons.
This is a card-compatible class abstraction, not an exact full-poker game.

Use zero rake so total utility is constant and an independent linear program
can certify the minimax value. Test: uniform 10bb, the saved 200bb entering
ranges/pot/bet amounts with rake removed, and overlapping premium ranges.
Both players' policies adapt. No call or non-all-in raise option is present;
these policies must not be presented as recommendations for the original game.

Implement linear-weighted alternating CFR+ with a maximum 50,000 iterations.
Compare with independent primal and dual linear programs. Report the two-sided
best-response gap, value error and runtime. Gate: primal/dual value difference
<=1e-6bb and CFR gap <=0.001bb. Do not change the gate after seeing results.
Also report the independent-class baseline evaluated in the compatible game.

Verify exact card-count identities, legal probabilities, zero-weight handling,
constant total utility, and random-policy payoff agreement with direct physical
combo-pair enumeration. In particular, a fold does not make the folded player's
cards disappear from chance probabilities. Preserve all input hashes and results.

A passing gate supports the small reference implementation only. It does not
validate 3+ players, nonzero rake, learned postflop values, GPU integration or
whole-tree performance. Any production integration needs separate equivalence
and speed checks; port 56708 remains unchanged.
