# Why value accuracy and settling need separate checks

Primary-source review, 2026-09-16. This note does not change any frozen model,
experiment or acceptance threshold.

ReBeL represents the game state using public information and beliefs over
private states. Its search uses a vector of information-state values, related
to the public-belief value function through supergradients. Its convergence
results concern two-player zero-sum games. Range dependence is therefore not
inherently an error: accurate continuation values can legitimately change with
the ranges. Removing that dependence is a modeling restriction, not a general
repair prescribed by this work.
[ReBeL, Sections 4-5 and Theorem 1](https://proceedings.neurips.cc/paper/2020/file/c61f571dbd2fb949d3fe5ae1608dd48b-Paper.pdf).

DeepStack's analysis separates subgame solving error from value-estimation
error. Lemma S6 requires a bound on relevant information-state errors across
players, subtrees and iterations. A small mean error on a finite collection of
flops is not that bound. The supplement also explicitly distinguishes its
best-response-value theorem from the implementation's use of self-play values.
We should not transfer either guarantee to GTOpen's approximate multiway model.
[DeepStack supplement, Lemma S6 and the discussion on page 19](https://poker.cs.ualberta.ca/publications/17science-supplementary.pdf).

Our evidence so far is narrower. N20 passes its four changed-range accuracy
cases, but at 1,500 preflop iterations its frozen-value gap remains 0.07841 bb,
versus 0.00062 bb for the ordinary baseline. These are gaps in different
approximate continuation games, not independent full-game exploitability
measurements. The ordinary path passed both registered intervals; the candidate
failed both, despite little chart movement in the final interval.
[Completed result](../policy-stability-20260916/result.json).

The practical implication is to keep testing both outcomes. N24 separates the
card-accounting interface from the learned predictor. N25 tests a fixed pairwise
value model with fewer dependencies, but must retain the existing accuracy
thresholds. N25 subsequently failed all three fixed training screens: its best
mean error was 12.582% of pot versus 6.284% for N15. No candidate was promoted.

If the settling issue persists, the next diagnostic should compare the learned
and exact continuation values inside the same small heads-up game with exact
chance. That isolates value approximation from multiway card accounting and
allows a real end-to-end exploitability check. This is a proposed next study,
not a result or permission to weaken tonight's gates. More generic random-range
training is not an evidence-supported fix after N03, N22 and N23.

## Average-belief search is a distinct experiment

ReBeL's supplement, Appendix I, compares current-belief CFR-D with CFR-AVG,
which solves continuations at averaged beliefs. Its efficient implementation
also adjusts the returned values to account for the difference between the
input beliefs and the current policy. The authors explicitly leave that
efficient variant's depth-limited theoretical guarantee open. Merely replacing
current ranges with averages in our kernel is therefore not the algorithm
described there. Its two-player results do not establish multiway correctness.
[Supplement, Appendix I and Figure 6](https://proceedings.neurips.cc/paper_files/paper/2020/file/c61f571dbd2fb949d3fe5ae1608dd48b-Supplemental.pdf).

Our inference is to first compare direct continuation solves and the full small
game, then evaluate any averaging change with the same independent full-game
best responses. N37's current/average terminal-range audit can identify whether
this is a promising direction; it cannot validate such a change. Neither a
scalar-value-network redesign nor simple range freezing has been shown to fix
GTOpen by tonight's evidence.
