# Fixed strategies can now be evaluated on complete physical deals

The new research evaluator integrates every legal action branch for a fixed
pair of strategies and a complete nine-card deal. It returns both players'
expected payoffs. Cards are known to the payoff evaluator, but each policy
lookup receives only its own visible observation and legal-action count. There
is no maximizing action selection, no look-ahead policy fitting and no claim
that the result is a best response.

This supplies the physical payoff calculation needed for later paired policy
and independently trained response comparisons. It does not train a new model,
change a saved strategy or establish poker strength.

## Independent checks

Ten fixed profiles were evaluated on the existing eight-deal checkpoint
fixture: the saved two-model average; all four independent player-model pairs;
three analytic-action controls; and two profiles replacing only one player's
policy while retaining the other player's average.

Two distinct calculations agree:

- A backward expectation recursion uses the frozen research terminal payout
  functions and value offsets.
- A forward terminal-mass traversal computes net payoffs from actual player
  investments, dead money, returned unmatched bets and the configured rake.
  It does not call the payout function or use the value offsets. The action
  transition model and card evaluator remain shared dependencies.

Maximum payoff disagreement is **2.70e-13 bb**. Terminal probability sums to one,
and the two player EVs plus expected rake equal the 0.5 bb dead small blind,
within **7.95e-14 bb**. These are numerical consistency checks, not estimates
of modeling accuracy.

The saved behavioral average produces the same per-deal EV as independently
drawing each player's played model at the root and holding it through the hand:
maximum difference **2.84e-14 bb**. This extends the earlier own-reach/terminal
distribution control to actual payoffs. The unused next-generation model is
still excluded from the average.

The analytic controls verify:

- BB folding at the root always gives BB -1 bb and BTN +1.5 bb, without rake.
- BB calling and both players checking down produces 0.225 bb rake on 4.5 bb.
- BB jamming and BTN calling reaches the 2 bb rake cap.
- Every evaluated payoff lies within the previously enumerated terminal bounds.

Six invalid transports are rejected: stale context, stale batch, duplicate
profile names, a wrong observation owner, an unnormalized policy, and a missing
policy row. No output is published for these rejected inputs.

## Paired evaluation boundary

The control also passes per-deal differences through the existing bounded
interval accumulator and verifies their means directly. **These eight deals
were already inspected and the tiny source models are strategically
unqualified.** The saved intervals exercise plumbing only; they are not
independent evidence of improvement, generalization or convergence.

A real evaluation must freeze candidate policies, independently trained
responders, the compatible-deal distribution, sample sizes and comparisons
before drawing fresh evaluation data. This executable expects externally
supplied query-aligned probabilities; its checks cannot establish whether their
producer used hidden information. The visible-observation model interface and
source registration remain essential.

The observations supplied to the interval calculation are complete-deal
conditional expectations, integrating action randomness. They are not individual
action records or independent samples from every branch. A tested response's
gain remains a lower bound on the best-response gain, not an upper bound on
exploitability. The new evaluation path does not close that remaining research
requirement.

## Evidence and limits

Source: `crates/solver/examples/hu_sampled_profile_evaluation.rs` and
`tools/research/hu_sampled_profile_evaluation_control_20260922.py`.
Frozen evidence prefix: `sampled-profile-evaluation-v1`. Seventeen inputs were
hash-verified; the complete control finished in 6.06 seconds. Release compilation
succeeded; expected unused-code warnings come from the frozen reference modules.

The command accepts context, batch, fixed-profile transport and output paths.
It uses the same fixed postflop menu as the sampled BB research context and
bounded query enumeration. It is not an arbitrary production-tree evaluator.
No larger-bank throughput or GPU evaluation claim follows from this small
control. The combined CUDA pipeline remains separately queued; production and
the range preview are unchanged.
